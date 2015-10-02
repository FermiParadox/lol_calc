import operator
import copy
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import buffs
import timers
import runes
from champions import app_champions_base_stats
import palette
import skills_points
import items_folder.items_data as items_data


# Sets font size on all plt graphs.
plt.rcParams['font.size'] = 12


BUFFS_AND_DMGS_IMPLEMENTED_BY_METHODS = set()
BUFFS_AND_DMGS_IMPLEMENTED_BY_METHODS.update(items_data.ITEMS_BUFFS_AND_DMGS_EXPRESSED_BY_METHOD)


class EnemyTargetsDeadError(Exception):
    """
    To be used (and handled) when no other valid targets are available for an event application.
    """
    pass


class EventsGeneral(buffs.DeathAndRegen):

    def __init__(self,
                 champion_lvls_dct,
                 selected_champions_dct,
                 max_targets_dct,
                 max_combat_time,
                 initial_enemies_total_stats,
                 initial_active_buffs,
                 initial_current_stats,
                 req_buff_dct_func,
                 chosen_items_dct,
                 req_dmg_dct_func,
                 ability_lvls_dct,
                 selected_masteries_dct,
                 _reversed_combat_mode):

        # (User defined dict containing number of targets affected by abilities.)
        self.max_targets_dct = max_targets_dct
        self.event_times = {}
        # (first examined target is always 'enemy_1')
        self.current_enemy = 'enemy_1'
        # (Used to note that a periodic event might have been added between current events and last action.)
        self.intermediate_events_changed = None

        buffs.DeathAndRegen.__init__(self,
                                     selected_champions_dct=selected_champions_dct,
                                     champion_lvls_dct=champion_lvls_dct,
                                     max_combat_time=max_combat_time,
                                     initial_current_stats=initial_current_stats,
                                     initial_active_buffs=initial_active_buffs,
                                     chosen_items_dct=chosen_items_dct,
                                     req_dmg_dct_func=req_dmg_dct_func,
                                     ability_lvls_dct=ability_lvls_dct,
                                     req_buff_dct_func=req_buff_dct_func,
                                     selected_masteries_dct=selected_masteries_dct,
                                     initial_enemies_total_stats=initial_enemies_total_stats,
                                     _reversed_combat_mode=_reversed_combat_mode)

    def add_event_to_single_tar(self, target_name, effect_name, start_time):
        """
        Applies a dmg event to the first target.

        :return: (None)
        """

        # If the event's time doesn't exist it creates it.
        if start_time not in self.event_times:
            self.event_times.update({start_time: {target_name: [effect_name]}})

        else:
            # If the time exists in the dictionary,
            # checks if the target is inside the time.
            if target_name in self.event_times[start_time]:
                self.event_times[start_time][target_name].append(effect_name)
            else:
                # If not, it adds the target as well.
                self.event_times[start_time].update({target_name: [effect_name]})

    def add_regenerations(self):
        """
        Adds hp5 (both event and buff) for all targets, and resource per 5 for player.

        :return: (None)
        """

        # ENEMY
        for self.current_enemy in self.enemy_target_names:
            self.add_buff(buff_name='enemy_hp5_buff', tar_name=self.current_enemy)

        # PLAYER
        self.add_buff(buff_name='player_hp5_buff', tar_name='player')

        # RESOURCE
        if self.RESOURCE_USED == 'energy':
            self.add_buff(buff_name='ep5_buff', tar_name='player')

        elif self.RESOURCE_USED == 'mp':
            self.add_buff(buff_name='mp5_buff', tar_name='player')
        else:
            raise NotImplementedError('Other resources need to be added as well.')

    def add_aoe_event(self, effect_name, start_time, tar_name):
        """
        Adds an aoe dmg event to affected target.

        :return: (None)
        """

        self.targets_already_hit += 1

        # ADD EVENT
        # Checks if the target is inside the time.
        if tar_name in self.event_times[start_time]:
            self.event_times[start_time][tar_name].append(effect_name)
        else:
            self.event_times[start_time].update({tar_name: [effect_name]})

    def add_events(self, effect_name, start_time, tar_name):
        """
        Adds a dmg event (e.g. Brand W) to all affected targets.

        Structure:
            event_times: {0.: {'player': ['w_dmg',],},}

        :return: (None)
        """

        dmg_dct = self.req_dmg_dct_func(dmg_name=effect_name)
        dmg_cat = dmg_dct['dmg_category']
        # Changes event start if needed.
        dmg_delay = dmg_dct['delay']
        if dmg_delay:
            start_time += dmg_delay

        if dmg_cat != 'ring_dmg':
            # Adds event to first target.
            self.add_event_to_single_tar(target_name=tar_name, effect_name=effect_name, start_time=start_time)
            self.targets_already_hit = 1
        else:
            self.targets_already_hit = 0

        # AOE DMG
        # (Aoe is always applied to enemies.)

        # No aoe will be applied by dmgs originating from reverse combat mode.
        if self._reversed_combat_mode:
            return

        # External max targets.
        if effect_name in self.max_targets_dct:
            max_tars_val = self.max_targets_dct[effect_name]

        # (Aoe dmg has 'max_targets' in dmg dct. It can also additionally have externally set max_targets.)
        else:
            max_tars_val = dmg_dct['usual_max_targets']
            if max_tars_val == 'unlimited':
                # If targets are unlimited applies to everyone.
                max_tars_val = len(self.enemy_target_names)

        # While the last target number is less than max targets, adds event.
        prev_enemy = self.current_enemy
        while self.targets_already_hit < max_tars_val:

            next_enemy = self.next_alive_enemy(current_tar=prev_enemy)
            if next_enemy is None:
                break

            self.current_enemy = next_enemy
            self.add_aoe_event(effect_name=effect_name, start_time=start_time, tar_name=next_enemy)

            prev_enemy = next_enemy

    def refresh_periodic_event(self, dmg_name, dmg_owner_name, dmg_dct):
        """
        Re-adds a periodic event and notes the change.

        Refreshed only if buff ending time is higher than event ending time,
        or if it's a permanent buff.

        :return: (None)
        """

        # Buff owner can be different than the dmg owner.
        # (e.g. sunfire's immolate is a buff on player, that dmgs enemies)
        buff_name = dmg_dct['dot']['buff_name']
        buff_dct = self.req_buff_dct_func(buff_name=buff_name)
        buff_owner_type = buff_dct['target_type']
        buff_owner_name = self.player_or_current_enemy(tar_type=buff_owner_type)

        buff_owner_act_buffs = self.active_buffs[buff_owner_name]

        # Checks dot's buff is active.
        if buff_name in buff_owner_act_buffs:
            buff_ending_time = buff_owner_act_buffs[buff_name]['ending_time']
            if (buff_ending_time == 'permanent') or (buff_ending_time > self.current_time):

                start_time = self.current_time + buff_dct['dot']['period']
                self.add_event_to_single_tar(target_name=dmg_owner_name,
                                             effect_name=dmg_name,
                                             start_time=start_time)

                self.intermediate_events_changed = True

    def add_next_periodic_event(self, tar_name, dmg_name, dmg_dct, only_temporary=False):
        """
        Adds next periodic tick.

        Checks active_buffs for the dot buff, then adds event if the buff still exists.

        :param only_temporary: (boolean) Used for filtering out permanent dots (e.g. sunfire) if needed.
        :return: (None)
        """

        # Checks if event is periodic.
        if dmg_dct['dot']:
            # If only temporary periodic events are re-applied..
            if only_temporary:
                # ..checks if their duration is not permanent.
                buff_dct = self.req_buff_dct_func(dmg_dct['dot']['buff_name'])
                if buff_dct['duration'] != 'permanent':
                    self.refresh_periodic_event(dmg_name=dmg_name, dmg_owner_name=tar_name, dmg_dct=dmg_dct)

            # Otherwise checks both permanent and temporary dots.
            else:
                self.refresh_periodic_event(dmg_name=dmg_name, dmg_owner_name=tar_name, dmg_dct=dmg_dct)


_DPS_BY_ENEMIES_DMGS_NAMES = [dmg_type + '_dps_by_enemy_dmg' for dmg_type in ('true', 'magic', 'non_aa_physical', 'aa')]

_DPS_BY_ENEMIES_BUFF_BASE = copy.deepcopy(buffs.REGEN_BUFF_DCT_BASE)
_DPS_BY_ENEMIES_BUFF_BASE['target_type'] = 'player'
# obsolete comment: (duration set a non 'permanent', stable value, to ensure independence of initial current hp)
_DPS_BY_ENEMIES_BUFF_BASE['duration'] = 'permanent'
_DPS_BY_ENEMIES_BUFF_BASE['dot']['period'] = buffs.NATURAL_REGEN_PERIOD
_DPS_BY_ENEMIES_BUFF_BASE['buff_source'] = 'enemies_dps'

# Adds all dmgs' names in dot buff.
for dps_dmg_name in _DPS_BY_ENEMIES_DMGS_NAMES:
    _DPS_BY_ENEMIES_BUFF_BASE['dot']['dmg_names'].append(dps_dmg_name)

_DPS_BY_ENEMIES_DMG_BASE = {i: None for i in palette.dmg_dct_base_deepcopy() if i not in ('dmg_type', 'dmg_values')}
_DPS_BY_ENEMIES_DMG_BASE['target_type'] = 'player'
_DPS_BY_ENEMIES_DMG_BASE['dmg_category'] = 'standard_dmg'
_DPS_BY_ENEMIES_DMG_BASE['resource_type'] = 'hp'
_DPS_BY_ENEMIES_DMG_BASE['dmg_source'] = 'dps_by_enemies'
_DPS_BY_ENEMIES_DMG_BASE['mods'] = {}
_DPS_BY_ENEMIES_DMG_BASE['life_conversion_type'] = None
_DPS_BY_ENEMIES_DMG_BASE['radius'] = None
_DPS_BY_ENEMIES_DMG_BASE['dot'] = {'buff_name': 'dps_by_enemies_dot_buff'}
_DPS_BY_ENEMIES_DMG_BASE['max_targets'] = 1
_DPS_BY_ENEMIES_DMG_BASE['usual_max_targets'] = 1
_DPS_BY_ENEMIES_DMG_BASE['delay'] = 0
_DPS_BY_ENEMIES_DMG_BASE['heal_for_dmg_amount'] = False
_DPS_BY_ENEMIES_DMG_BASE['crit_type'] = None


class EnemiesDmgToPlayer(EventsGeneral):
    """
    TOTAL ENEMIES:
        Number of enemies doesn't matter for survivability under the assumption that more enemies
        would also mean more allies, therefor distributing dmg over more targets
        and finally canceling out the dmg increase.

    ENEMIES' DPS:
        Enemies' dps is raw dps without any mitigation (since target's defenses are set to 0),
        meaning it can be directly applied as dmg to player over the main combat.
    """

    DPS_BY_ENEMIES_DMG_BASE = _DPS_BY_ENEMIES_DMG_BASE
    DPS_ENHANCER_COEF = 1

    FLAT_SURVIVABILITY_FACTORS = dict(
        flash=1
    )

    def __init__(self,
                 enemies_originating_dmg_data,
                 champion_lvls_dct,
                 selected_champions_dct,
                 max_targets_dct,
                 max_combat_time,
                 initial_enemies_total_stats,
                 initial_active_buffs,
                 initial_current_stats,
                 req_buff_dct_func,
                 chosen_items_dct,
                 req_dmg_dct_func,
                 ability_lvls_dct,
                 selected_masteries_dct,
                 _reversed_combat_mode):

        self.IGNORED_DMG_NAMES += _DPS_BY_ENEMIES_DMGS_NAMES

        self.enemies_originating_dmg_data = enemies_originating_dmg_data
        self._true_dps_by_enemy_dmg = {}
        self._non_aa_physical_dps_by_enemy_dmg = {}
        self._aa_dps_by_enemy_dmg = {}
        self._magic_dps_by_enemy_dmg = {}

        EventsGeneral.__init__(self,
                               champion_lvls_dct,
                               selected_champions_dct,
                               max_targets_dct,
                               max_combat_time,
                               initial_enemies_total_stats,
                               initial_active_buffs,
                               initial_current_stats,
                               req_buff_dct_func,
                               chosen_items_dct,
                               req_dmg_dct_func,
                               ability_lvls_dct,
                               selected_masteries_dct,
                               _reversed_combat_mode=_reversed_combat_mode)

    @staticmethod
    def dps_by_enemies_dot_buff():
        return _DPS_BY_ENEMIES_BUFF_BASE

    def _enemies_dps_values_dct(self, ):
        """
        Creates a dict containing dps values for all dmg types (AA, magic, true, physical).

        :return:
        """

        all_enemies_total_dmg = 0
        all_enemies_magic_dmg = 0
        all_enemies_physical_dmg = 0
        all_enemies_true_dmg = 0
        all_enemies_aa_dmg = 0
        all_enemies_added_dps = 0

        total_enemies = len(self.enemies_originating_dmg_data)

        for enemy_name in self.enemies_originating_dmg_data:
            dmg_data_dct = self.enemies_originating_dmg_data[enemy_name]['player']

            all_enemies_total_dmg += dmg_data_dct['total_dmg_done']
            all_enemies_magic_dmg += dmg_data_dct['total_magic']
            all_enemies_physical_dmg += dmg_data_dct['total_physical']
            all_enemies_true_dmg += dmg_data_dct['total_true']
            all_enemies_added_dps += dmg_data_dct['dps']

            source_dct = dmg_data_dct['source']
            all_enemies_aa_dmg += source_dct['AA']

        average_dps = all_enemies_added_dps / total_enemies
        percent_magic = all_enemies_magic_dmg / all_enemies_total_dmg
        percent_physical = all_enemies_physical_dmg / all_enemies_total_dmg
        percent_true = all_enemies_true_dmg / all_enemies_total_dmg
        percent_aa = all_enemies_aa_dmg / all_enemies_total_dmg

        dct = {}
        dct.update({'magic_dps': percent_magic})
        dct.update({'non_aa_physical_dps': percent_physical-percent_aa})
        dct.update({'aa_dps': percent_aa})
        dct.update({'true_dps': percent_true})
        for dps_type in dct:
            dct[dps_type] *= average_dps * self.DPS_ENHANCER_COEF * buffs.NATURAL_REGEN_PERIOD

        return dct

    def _create_enemies_dps_dmgs_dcts(self):
        dps_values_dct = self._enemies_dps_values_dct()

        true_dps_val = dps_values_dct['true_dps']
        self._true_dps_by_enemy_dmg = {'dmg_values': true_dps_val}
        self._true_dps_by_enemy_dmg.update({'dmg_type': 'true'})
        self._true_dps_by_enemy_dmg.update(self.DPS_BY_ENEMIES_DMG_BASE)

        magic_dps_val = dps_values_dct['magic_dps']
        self._magic_dps_by_enemy_dmg = {'dmg_values': magic_dps_val}
        self._magic_dps_by_enemy_dmg.update({'dmg_type': 'magic'})
        self._magic_dps_by_enemy_dmg.update(self.DPS_BY_ENEMIES_DMG_BASE)

        non_aa_physical_dps_val = dps_values_dct['non_aa_physical_dps']
        self._non_aa_physical_dps_by_enemy_dmg = {'dmg_values': non_aa_physical_dps_val}
        self._non_aa_physical_dps_by_enemy_dmg.update({'dmg_type': 'physical'})
        self._non_aa_physical_dps_by_enemy_dmg.update(self.DPS_BY_ENEMIES_DMG_BASE)

        aa_dps_val = dps_values_dct['aa_dps']
        self._aa_dps_by_enemy_dmg = {'dmg_values': aa_dps_val}
        self._aa_dps_by_enemy_dmg.update({'dmg_type': 'AA'})
        self._aa_dps_by_enemy_dmg.update(self.DPS_BY_ENEMIES_DMG_BASE)

    def true_dps_by_enemy_dmg(self):
        return self._true_dps_by_enemy_dmg

    def non_aa_physical_dps_by_enemy_dmg(self):
        return self._non_aa_physical_dps_by_enemy_dmg

    def aa_dps_by_enemy_dmg(self):
        return self._aa_dps_by_enemy_dmg

    def magic_dps_by_enemy_dmg(self):
        return self._magic_dps_by_enemy_dmg

    def add_dps_dot_by_enemies(self):

        self._create_enemies_dps_dmgs_dcts()
        self.add_buff(buff_name='dps_by_enemies_dot_buff', tar_name='player')

    def survivability(self):
        """
        Survivability is defined as 'estimated time required to kill the player'.

        It is independent of initial starting hp, while it depends on max hp.

        :return: (float)
        """

        max_hp = self.request_stat(target_name='player', stat_name='hp')
        current_hp = self.request_stat(target_name='player', stat_name='current_hp')
        combat_duration = self.combat_duration

        try:
            starting_hp = self.initial_current_stats['player']['current_hp']
        except KeyError:
            starting_hp = max_hp

        hp_lost_per_sec = (starting_hp - current_hp) / combat_duration

        if hp_lost_per_sec > 0:
            return max_hp / hp_lost_per_sec
        else:
            # If player heals exceeded the dmg he took.
            return 999999

    def note_survivability(self):
        self.combat_results['player'].update({'survivability': self.survivability()})


class ConditionalsTranslator(EnemiesDmgToPlayer):

    OPERATORS_STR_MAP = {
        '<': operator.lt,
        '<=': operator.le,
        '==': operator.eq,
        '!=': operator.ne,
        '>=': operator.ge,
        '>': operator.gt,
        }

    # Matches requested object type to object key names in abilities' effects dct.
    EFF_TYPE_TO_OBJ_KEY_NAME_MAP = {
        'abilities_effects': 'ability_name',
        'abilities_gen_attributes': 'ability_name',
        'items_effects': 'item_name',
        'buffs': 'buff_name',
        'dmgs': 'dmg_name',
    }

    # ("abstract" class variables)
    ABILITIES_ATTRIBUTES = None
    ABILITIES_EFFECTS = None
    ABILITIES_CONDITIONALS = None

    def __init__(self,
                 ability_lvls_dct,
                 champion_lvls_dct,
                 selected_champions_dct,
                 action_on_cd_func,
                 max_targets_dct,
                 max_combat_time,
                 initial_enemies_total_stats,
                 initial_active_buffs,
                 initial_current_stats,
                 chosen_items_dct,
                 selected_masteries_dct,
                 enemies_originating_dmg_data,
                 _reversed_combat_mode
                 ):

        self.ability_lvls_dct = ability_lvls_dct
        self.current_target_num = None
        self.action_on_cd_func = action_on_cd_func

        self.__castable_spells_shortcuts = None

        EnemiesDmgToPlayer.__init__(self,
                                    enemies_originating_dmg_data=enemies_originating_dmg_data,
                                    champion_lvls_dct=champion_lvls_dct,
                                    selected_champions_dct=selected_champions_dct,
                                    max_targets_dct=max_targets_dct,
                                    max_combat_time=max_combat_time,
                                    initial_active_buffs=initial_active_buffs,
                                    initial_current_stats=initial_current_stats,
                                    chosen_items_dct=chosen_items_dct,
                                    ability_lvls_dct=ability_lvls_dct,
                                    req_dmg_dct_func=self.request_dmg,
                                    req_buff_dct_func=self.request_buff,
                                    selected_masteries_dct=selected_masteries_dct,
                                    initial_enemies_total_stats=initial_enemies_total_stats,
                                    _reversed_combat_mode=_reversed_combat_mode)

    def _x_value(self, x_name, x_type, x_owner):
        """
        Determines value of x in a condition trigger.

        Returns:
            (num)
        """

        if x_owner == 'player':
            owner = x_owner
        else:
            owner = self.current_enemy

        # BUFF STACKS VALUE
        if x_type == 'buff':
            # If buff is active, returns stacks.
            if x_name in self.active_buffs[owner]:
                return self.active_buffs[owner][x_name]['current_stacks']
            # Otherwise returns 0.
            else:
                return 0

        # STAT VALUE
        elif x_type == 'stat':
            return self.request_stat(target_name=x_owner, stat_name=x_name)

        # ABILITY LVL
        elif x_type == 'ability_lvl':
            return self.ability_lvls_dct[x_name]

    def _x_formula_to_value(self, x_formula, x_name, x_type, x_owner):
        """
        Converts condition trigger formula to value.

        Returns:
            (str)
            (bool)
            (num)
            (sequence)
            (None)
        """

        x = self._x_value(x_name, x_type, x_owner)
        return eval(x_formula)

    def _trigger_value_comparison(self, operator_as_str, trig_val, checked_val):
        """
        Compares trigger value to checked value based on the operator.

        Returns:
            (bool)
        """

        return self.OPERATORS_STR_MAP[operator_as_str](checked_val, trig_val)

    def _trig_attr_owner(self, trig_dct):
        """
        Determines trigger attribute owner.

        Returns:
            (str) e.g. 'player', 'enemy_1', ..
        """
        if trig_dct['owner_type']:
            return 'player'
        else:
            return self.current_enemy

    def _check_abilities_cond_triggers_state(self, cond_name):
        """
        Checks if ALL triggers for given condition are present.

        Returns:
            (bool)
        """

        triggers_dct = self.ABILITIES_CONDITIONALS[cond_name]['triggers']

        # (if any trigger is False, returns False ending method before reaching bottom)
        for trig_name in triggers_dct:
            trig_dct = triggers_dct[trig_name]
            trig_type = trig_dct['trigger_type']
            trig_op = trig_dct['operator']

            # BUFF
            if trig_type == 'buff':
                buff_name = trig_dct['buff_name']
                owner = self._trig_attr_owner(trig_dct=trig_dct)

                try:
                    stacks = self.active_buffs[owner][buff_name]['current_stacks']
                except KeyError:
                    stacks = 0

                if self._trigger_value_comparison(trig_val=trig_dct['stacks'],
                                                  operator_as_str=trig_op,
                                                  checked_val=stacks):
                    pass
                else:
                    return False

            # STAT
            elif trig_type == 'stat':
                stat_name = trig_dct['stat_name']
                owner = self._trig_attr_owner(trig_dct=trig_dct)

                try:
                    stat_val = self.current_stats[owner][stat_name]
                except KeyError:
                    stat_val = self.request_stat(target_name=owner, stat_name=stat_name)

                if self._trigger_value_comparison(trig_val=trig_dct['value'], operator_as_str=trig_op,
                                                  checked_val=stat_val):
                    pass
                else:
                    return False

            # SPELL LVL
            elif trig_type == 'spell_lvl':
                spell_name = trig_dct['spell_name']

                try:
                    spell_lvl = self.ability_lvls_dct[spell_name]
                except KeyError:
                    spell_lvl = 0

                if self._trigger_value_comparison(trig_val=trig_dct['spell_lvl'], operator_as_str=trig_op,
                                                  checked_val=spell_lvl):
                    pass
                else:
                    return False

            elif trig_type == 'on_cd':
                spell_name = trig_dct['spell_name']
                if self.action_on_cd_func(action_name=spell_name) is True:
                    pass
                else:
                    return False

            else:
                raise palette.UnexpectedValueError

        # (if no trigger is false, method reaches this)
        return True

    def _ability_effects_updater(self, con_eff_dct, modified_dct, obj_name):
        """
        Creates new ability effects dct or updates existing with changes caused by effects.

        :param modified_dct: It is the new dict given instead of the static class variable dict.
        :param obj_name: (str) ability or item name

        Returns:
            (None)
        """

        # Then checks if new dict is empty.
        if not modified_dct:
            modified_dct.update(copy.deepcopy(self.ABILITIES_EFFECTS[obj_name]))

        # DATA MODIFICATION
        mod_operation = con_eff_dct['mod_operation']
        cat_type = con_eff_dct['lst_category']
        eff_contents = con_eff_dct['names_lst']

        # (it always modifies actives)

        if mod_operation == 'append':
            modified_dct['actives'][cat_type] += eff_contents
        elif mod_operation == 'remove':
            old_lst = modified_dct[obj_name]['actives'][cat_type]
            modified_dct['actives'][cat_type] = [i for i in old_lst if i not in eff_contents]

    def _on_hit_effect_buff_updater(self, eff_dct, modified_dct, buff_name):
        """
        Creates new buff dct or updates existing with changes caused by effects.

        Args:
            modified_dct: It is the new dict given instead of the static class variable dict.

        Returns:
            (None)
        """

        # Checks if modified dct is empty.
        if not modified_dct:
            modified_dct.update(copy.deepcopy(self.ABILITIES_ATTRIBUTES['buffs'][buff_name]))

        # DATA MODIFICATION
        mod_operation = eff_dct['mod_operation']
        eff_contents = eff_dct['names_lst']
        cat_type = eff_dct['lst_category']

        lst_of_on_hit_effects = modified_dct['on_hit'][cat_type]

        if mod_operation == 'append':
            lst_of_on_hit_effects += eff_contents

        elif mod_operation == 'remove':
            for eff_to_remove in eff_contents:
                if eff_to_remove in lst_of_on_hit_effects:
                    lst_of_on_hit_effects.remove(eff_to_remove)

    @staticmethod
    def _modified_attr_value(mod_operation, mod_val, old_val):
        """
        Returns the new value after modification.

        Args:
            mod_val: The value that is to be replaced, added, multiplied etc.

        Returns:
            (literal)
        """

        # OPERATOR
        if mod_operation == 'replace':
            return mod_val

        elif mod_operation == 'add':
            func = operator.add
        else:
            func = operator.mul

        # VALUE CREATION
        # (mod is tuple -> old is tuple)
        if type(mod_val) is tuple:
            return [func(i, j) for i, j in zip(mod_val, old_val)]
        # (old is num->mod is num)
        elif type(old_val) is not tuple:
            return func(old_val, mod_val)
        # (else old is tuple and mod is num)
        else:
            return [func(i, mod_val) for i in old_val]

    def _property_updater(self, con_eff_dct, modified_dct, initial_dct):
        """
        Creates new properties' dct or updates existing with changes caused by condition-effects.


        :param modified_dct: It is the new dict given instead of the static class variable dict.
        :param initial_dct: (dct) "ABILITIES_ATTRIBUTES['general_attributes']['w']", "ITEM_ATTRIBUTES['item_name']"
        :return: (None)
        """

        # Checks if modified dct is empty.
        if not modified_dct:
            modified_dct.update(copy.deepcopy(initial_dct))

        # DATA MODIFICATION
        mod_operation = con_eff_dct['mod_operation']
        modified_attr_name = con_eff_dct['attr_name']
        if con_eff_dct['formula_type'] == 'constant_value':
            mod_val = con_eff_dct['values_tpl']
        else:
            mod_val = self._x_formula_to_value(x_formula=con_eff_dct['x_formula'],
                                               x_name=con_eff_dct['x_name'],
                                               x_type=con_eff_dct['x_type'],
                                               x_owner=con_eff_dct['x_owner'],)

        modified_dct[modified_attr_name] = self._modified_attr_value(
            mod_operation=mod_operation,
            mod_val=mod_val,
            old_val=modified_dct[modified_attr_name])

    def initial_buff_or_dmg_dct(self, obj_name, dmgs_or_buffs):
        """
        Returns initial dict of a dmg or buff.


        :param obj_name: (str) Buff or dmg name.
        :param dmgs_or_buffs: (str) 'buffs', 'dmgs'
        :return: (dict) Module dict of dmg or buff.
        """

        if obj_name in self.ABILITIES_ATTRIBUTES[dmgs_or_buffs]:
            return

    @staticmethod
    def _check_condition_affects_object(searched_obj_name, cond_eff_dct):
        """
        Checks if object in condition dict is the one needed.

        :param searched_obj_name: str
        :param cond_eff_dct: dict
        :return: bool
        """
        if searched_obj_name == cond_eff_dct['obj_name']:
            return True
        else:
            return False

    def _attrs_or_effs_base(self, obj_name, searched_obj_type, initial_dct, conditionals_dct):
        """
        Loops each condition. Then each effect of a condition.
        If single effect of interest is detected, all triggers for given condition are checked.
        If trigger state is false, condition stops being checked.

        :param obj_name: (str) name of the buff, dmg, or ability
        :param searched_obj_type: (str) 'general_attributes', 'ability_effect', 'buffs' or 'dmgs'
            Name of effect type being searched for.

        :return: (dict)
        """

        # Creates a dict that will hold the new values, replacing the "default" module dict.
        new_dct = {}

        # Checks if given ability name has conditions affecting its effects
        # All effects of all conditions on an element are applied one after the other.
        for cond in conditionals_dct:
            single_cond_dct = conditionals_dct[cond]

            trig_state = None
            for eff in single_cond_dct['effects']:

                cond_eff_dct = single_cond_dct['effects'][eff]

                # CHECK OBJ NAME IN COND
                if self._check_condition_affects_object(searched_obj_name=obj_name, cond_eff_dct=cond_eff_dct):

                    # TRIGGERS
                    # Trigger check is done ONCE on ALL triggers,
                    # right after a single effect affecting given object is detected.
                    if trig_state is None:
                        trig_state = self._check_abilities_cond_triggers_state(cond_name=cond)
                        # (if triggers are false, ends current condition checks)
                        if trig_state is False:
                            break

                    # Effect type of condition-effect.
                    cond_eff_type = cond_eff_dct['effect_type']

                    # TODO: create 'item_effect' related functionality in factory.
                    if searched_obj_type in ('abilities_effects', 'items_effects'):
                        if cond_eff_type in ('ability_effect', 'item_effect'):
                            self._ability_effects_updater(con_eff_dct=cond_eff_dct, modified_dct=new_dct,
                                                          obj_name=obj_name)
                    elif (searched_obj_type == 'buffs') and (cond_eff_type == 'buff_on_hit'):
                        self._on_hit_effect_buff_updater(eff_dct=cond_eff_dct,
                                                         modified_dct=new_dct,
                                                         buff_name=obj_name)

                    elif (searched_obj_type == 'general_attributes') and (cond_eff_dct == 'ability_attr'):
                        self._property_updater(con_eff_dct=cond_eff_dct, modified_dct=new_dct,
                                               initial_dct=initial_dct)

        if new_dct:
            returned_dct = new_dct
        else:
            returned_dct = initial_dct

        return returned_dct

    def abilities_effects(self, ability_name):
        """
        Checks if ability effects are affected by any conditionals.
        If not, returns member variable dict. Otherwise returns different version of the dict.

        Returns:
            (dict)
        """

        return self._attrs_or_effs_base(obj_name=ability_name,
                                        searched_obj_type='abilities_effects',
                                        initial_dct=self.ABILITIES_EFFECTS[ability_name],
                                        conditionals_dct=self.ABILITIES_CONDITIONALS)

    def items_effects(self, item_name):
        return self._attrs_or_effs_base(obj_name=item_name,
                                        searched_obj_type='items_effects',
                                        initial_dct=items_data.ITEMS_EFFECTS[item_name],
                                        conditionals_dct=items_data.ITEMS_CONDITIONALS[item_name])

    def item_attributes(self, item_name):
        return self._attrs_or_effs_base(obj_name=item_name,
                                        searched_obj_type='item_attr',
                                        initial_dct=items_data.ITEMS_EFFECTS[item_name],
                                        conditionals_dct=items_data.ITEMS_CONDITIONALS[item_name])

    def abilities_attributes(self, ability_name):
        """
        Checks if ability attributes are affected by any conditionals.
        If not, returns member variable dict. Otherwise returns different version of the dict.

        Returns:
            (dict)
        """

        return self._attrs_or_effs_base(obj_name=ability_name,
                                        searched_obj_type='general_attributes',
                                        initial_dct=self.ABILITIES_ATTRIBUTES['general_attributes'][ability_name],
                                        conditionals_dct=self.ABILITIES_CONDITIONALS)

    def request_buff(self, buff_name):
        """
        Returns buff dict after checking possible conditionals.

        Buffs can be related to champion, item, mastery, summoner spells, dragon, baron.

        Returns:
            (dict)
        """

        if buff_name in self.ABILITIES_ATTRIBUTES['buffs']:
            initial_dct = self.ABILITIES_ATTRIBUTES
            conditionals_dct = self.ABILITIES_CONDITIONALS

        elif buff_name in BUFFS_AND_DMGS_IMPLEMENTED_BY_METHODS:
            return getattr(self, buff_name)()

        elif buff_name in items_data.ITEMS_BUFFS_NAMES:
            item_name = items_data.ITEMS_BUFFS_NAMES[buff_name]
            initial_dct = items_data.ITEMS_ATTRIBUTES[item_name]
            conditionals_dct = items_data.ITEMS_CONDITIONALS[item_name]

        else:
            return getattr(self, buff_name)()

        return self._attrs_or_effs_base(obj_name=buff_name,
                                        searched_obj_type='buffs',
                                        initial_dct=initial_dct['buffs'][buff_name],
                                        conditionals_dct=conditionals_dct)

    def request_dmg(self, dmg_name):
        """
        Returns buff dict after checking possible conditionals.

        Buffs can be related to champion, item, mastery, summoner spells, dragon, baron.

        Returns:
            (dict)
        """

        if dmg_name in self.ABILITIES_ATTRIBUTES['dmgs']:
            initial_dct = self.ABILITIES_ATTRIBUTES
            conditionals_dct = self.ABILITIES_CONDITIONALS

        elif dmg_name in BUFFS_AND_DMGS_IMPLEMENTED_BY_METHODS:
            return getattr(self, dmg_name)()

        elif dmg_name in items_data.ITEMS_DMGS_NAMES:
            item_name = items_data.ITEMS_DMGS_NAMES[dmg_name]
            initial_dct = items_data.ITEMS_ATTRIBUTES[item_name]
            conditionals_dct = items_data.ITEMS_CONDITIONALS[item_name]

        else:
            return getattr(self, dmg_name)()

        return self._attrs_or_effs_base(obj_name=dmg_name,
                                        searched_obj_type='dmgs',
                                        initial_dct=initial_dct['dmgs'][dmg_name],
                                        conditionals_dct=conditionals_dct)

    @property
    def castable_spells_shortcuts(self):
        if self.__castable_spells_shortcuts:
            pass
        # Else creates contents.
        else:
            spells_set = set(self.ABILITIES_ATTRIBUTES['general_attributes']) & set(palette.ALL_POSSIBLE_SPELL_SHORTCUTS)
            self.__castable_spells_shortcuts = tuple(i for i in spells_set)

        return self.__castable_spells_shortcuts


class Actions(ConditionalsTranslator, timers.Timers, runes.RunesFinal):

    AA_COOLDOWN = 0.4   # TODO: replace functionality with 'wind_up'

    def __init__(self,
                 rotation_lst,
                 max_targets_dct,
                 selected_champions_dct,
                 champion_lvls_dct,
                 ability_lvls_dct,
                 max_combat_time,
                 selected_masteries_dct,
                 chosen_items_dct,
                 selected_summoner_spells,
                 initial_enemies_total_stats,
                 initial_active_buffs,
                 initial_current_stats,
                 selected_runes,
                 enemies_originating_dmg_data,
                 _reversed_combat_mode):

        self._reversed_combat_mode = _reversed_combat_mode
        self.rotation_lst = rotation_lst
        self.selected_summoner_spells = selected_summoner_spells
        self.everyone_dead = None
        self.__all_dead_or_max_time_exceeded = False
        self.reversed_precombat_player_stats = {}
        self.reversed_precombat_enemy_buffs = {}

        runes.RunesFinal.__init__(self,
                                  player_lvl=champion_lvls_dct['player'],
                                  selected_runes=selected_runes)

        ConditionalsTranslator.__init__(self,
                               ability_lvls_dct=ability_lvls_dct,
                               champion_lvls_dct=champion_lvls_dct,
                               selected_champions_dct=selected_champions_dct,
                               action_on_cd_func=self.spell_on_cd,
                               max_targets_dct=max_targets_dct,
                               max_combat_time=max_combat_time,
                               initial_active_buffs=initial_active_buffs,
                               initial_current_stats=initial_current_stats,
                               chosen_items_dct=chosen_items_dct,
                               selected_masteries_dct=selected_masteries_dct,
                               initial_enemies_total_stats=initial_enemies_total_stats,
                               enemies_originating_dmg_data=enemies_originating_dmg_data,
                               _reversed_combat_mode=_reversed_combat_mode)

        timers.Timers.__init__(self,
                               ability_lvls_dct=ability_lvls_dct,
                               req_dmg_dct_func=self.request_dmg,
                               req_abilities_attrs_func=self.abilities_attributes)

    # TODO: single call memo
    def stats_dependencies(self):

        dct = {}
        dct.update({'masteries': self.masteries_stats_dependencies()})
        dct.update({'champion': self.CHAMPION_STATS_DEPENDENCIES})
        dct.update({'items': self.player_items_instance.items_stats_dependencies()})

        return dct

    def spell_on_cd(self, action_name):
        """
        Checks if given spell is on cd.

        Starts from last casted action, and checks them until it finds searched spell.
        Then checks its cd end.

        :return: (bool)
        """

        for action_time in sorted(self.actions_dct, reverse=True):
            if self.actions_dct[action_time]['action_name'] == action_name:

                # (if the spell has been casted before, the loop ends)
                if self.actions_dct[action_time]['cd_end'] > self.current_time:
                    return True
                else:
                    return False

        # If it hasn't been casted before, then it is not on cd.
        else:
            return False

    def reduce_action_cd(self, action_name, reduction_value):
        """
        Reduces an action's cd.

        :return: (None)
        """

        for action_time in sorted(self.actions_dct, reverse=True):
            action_dct = self.actions_dct[action_time]
            if action_dct['action_name'] == action_name:

                # (if the spell has been casted before, the loop ends)
                if action_dct['cd_end'] > self.current_time:
                    action_dct['cd_end'] -= reduction_value

    def _target_of_dmg_by_name(self, dmg_name):
        tar_type_of_dmg = self.request_dmg(dmg_name=dmg_name)['target_type']
        return self.player_or_current_enemy(tar_type=tar_type_of_dmg)

    def _target_of_buff_by_name(self, buff_name):
        tar_type_of_buff = self.request_buff(buff_name=buff_name)['target_type']
        return self.player_or_current_enemy(tar_type=tar_type_of_buff)

    # COSTS
    def non_toggled_action_cost_dct(self, action_name):
        """
        Creates a dict containing each resource used,
        it's value cost, buff name cost and number of buff's stacks.

        Not to be used for abilities with toggled cost.

        Returns:
            (dict)
        """

        returned_cost_dct = {}

        # CASTABLE SPELLS
        if action_name in palette.ALL_POSSIBLE_SPELL_SHORTCUTS:
            spell_gen_attrs_dct = self.request_ability_gen_attrs_dct(ability_name=action_name)

            if spell_gen_attrs_dct['castable']:
                spell_cost_dct = spell_gen_attrs_dct['cost']
                spell_lvl = self.ability_lvls_dct[action_name]

                # NORMAL COST
                standard_cost_dct = spell_cost_dct['standard_cost']

                # Check if ability has a fixed cost,
                # or one that scales per ability_lvl,
                # or no resource cost (none of the if's are true).
                if standard_cost_dct:
                    resource_type = standard_cost_dct['resource_type']
                    resource_cost_val = standard_cost_dct['values'][spell_lvl - 1]
                    returned_cost_dct.update({resource_type: resource_cost_val})

                # STACK COST
                # (e.g. Akali R stacks)
                stack_cost_dct = spell_cost_dct['stack_cost']
                if stack_cost_dct:
                    buff_cost_name = stack_cost_dct['buff_name']
                    stack_cost_val = stack_cost_dct['values'][spell_lvl - 1]
                    returned_cost_dct.update({buff_cost_name: stack_cost_val})

        return returned_cost_dct

    def cost_sufficiency(self, action_name):
        """
        Determines whether there are enough resources to cast the action or not.

        Returns:
            (boolean)
        """

        sufficiency = True

        for cost_name in self.non_toggled_action_cost_dct(action_name):
            cost_value = self.non_toggled_action_cost_dct(action_name)[cost_name]

            if cost_name in self.RESOURCE_TO_CURRENT_RESOURCE_MAP:
                resource_name = self.RESOURCE_TO_CURRENT_RESOURCE_MAP[cost_name]
                if self.current_stats['player'][resource_name] < cost_value:
                    sufficiency = False

            else:
                if cost_name not in self.active_buffs['player']:
                    sufficiency = False

        return sufficiency

    def apply_action_cost(self, action_name):
        """
        Deducts the cost of an action (resource and/or buff stack).

        Modifies:
            current_stats['player']
            active_buffs
        Returns:
            (None)
        """

        for cost_name in self.non_toggled_action_cost_dct(action_name):
            cost_value = self.non_toggled_action_cost_dct(action_name)[cost_name]

            # RESOURCE COST
            if cost_name in self.RESOURCE_TO_CURRENT_RESOURCE_MAP:
                resource_name = self.RESOURCE_TO_CURRENT_RESOURCE_MAP[cost_name]
                self.current_stats['player'][resource_name] -= cost_value

                self.note_non_hp_resource_in_history(resource_name)

            # STACK COST
            else:
                del self.active_buffs['player'][cost_name]
                # TODO make it remove only one stack
                raise NotImplementedError

    def _last_action_name(self):
        """
        Returns name of last action casted. If no action has been casted yet, it returns None.

        :return: (str) (None)
        """

        if self.actions_dct:

            last_action_time = max(self.actions_dct)
            last_action_name = self.actions_dct[last_action_time]['action_name']

            return last_action_name

        else:
            return None

    # MOVEMENT
    def between_action_walking(self):
        """
        Calculates movement between actions and adds them to distance player moved.

        Returns:
            (None)
        """

        sorted_action_times = sorted(self.actions_dct, reverse=True)

        # Last action's cast start.
        time_final = sorted_action_times[0]

        # Checks if there was only one action (therefor lower limit should be 0)
        if len(sorted_action_times) == 1:
            pre_last_action_start = 0
        else:
            pre_last_action_start = sorted_action_times[1]

        pre_last_action_dct = self.actions_dct[pre_last_action_start]
        pre_last_action_name = pre_last_action_dct['action_name']

        # Movement starts after cast (or channelling) ends,
        # unless action allows movement during cast.
        if pre_last_action_name in self.castable_spells_shortcuts:
            move_while_cast_val = self.request_ability_gen_attrs_dct(
                ability_name=pre_last_action_name)['move_while_casting']
            if move_while_cast_val:
                time_initial = pre_last_action_start
            else:
                time_initial = pre_last_action_dct['cast_end']

        elif 'channel_end' in pre_last_action_dct:
            time_initial = pre_last_action_dct['channel_end']

        else:
            time_initial = pre_last_action_dct['cast_end']

        # Calculates and adds meaningful (above a minimum) values.
        move_value = (time_final-time_initial) * self.request_stat(target_name='player', stat_name='move_speed')
        if move_value > 0.1:
            self.total_movement += move_value

    def add_action_dash(self):
        """
        Adds last action's dash distance.

        Returns:
            (None)
        """
        last_action_time = sorted(self.actions_dct, reverse=True)[0]
        last_action_name = self.actions_dct[last_action_time]['action_name']

        # Abilities
        if last_action_name in self.castable_spells_shortcuts:
            ability_gen_stats = self.request_ability_gen_attrs_dct(ability_name=last_action_name)
            dash_val = ability_gen_stats['dashed_distance']
            if dash_val:
                self.total_movement += dash_val

    def add_kalista_dash(self):
        """
        Adds Kalista's dash after an AA.
        
        Returns:
            (None)
        """

        if self.selected_champions_dct['player'] == 'kalista':
            self.total_movement += app_champions_base_stats.CHAMPION_BASE_STATS['kalista']['dashed_distance_on_aa']

    # ABILITIES
    def check_and_reset_aa_cd(self, action_attrs_dct):
        """
        Removes an AA's cd after an AA-resetting ability is casted.

        :return: (None)
        """

        if action_attrs_dct['resets_aa']:

            for action_time in sorted(self.actions_dct, reverse=True):

                # If an AA has been casted earlier...
                if 'AA' == self.actions_dct[action_time]['action_name']:
                    # ..sets its cd_end to current_time.
                    self.actions_dct[action_time]['cd_end'] = self.current_time
                    break

    @staticmethod
    def __end_name_function(action_dct):
        """
        :return: (str)
        """
        if 'channel_end' in action_dct:
            string = 'channel_end'
        else:
            string = 'cast_end'
        return string

    def _action_cd_end(self, action_name):
        """
        Calculates action's cd end, or returns 0 if action hasn't been casted.

        :return:
            (float)
        """

        cd_end = 0

        for action_time in sorted(self.actions_dct, reverse=True):

            # If the examined action has been casted earlier...
            if action_name == self.actions_dct[action_time]['action_name']:
                cd_end = self.actions_dct[action_time]['cd_end']
                break

        return cd_end

    def action_cast_start(self, given_action_name):
        """
        Calculates cast_start of an action, based on other actions' cast_end and this action's cd.

        Returns:
            (float)
        """

        cast_start = self.current_time

        # If a previous action exists...
        if self.actions_dct:
            # (If the examined action has not been casted earlier it's 0)
            given_action_cd_end = self._action_cd_end(action_name=given_action_name)

            last_action_cast_start = max(self.actions_dct)

            end_name = self.__end_name_function(action_dct=self.actions_dct[last_action_cast_start])
            last_action_cast_end = self.actions_dct[max(self.actions_dct)][end_name]

            # ..compare which ends last
            cast_start = max(given_action_cd_end, last_action_cast_end)
            # (tiny amount added to avoid action overwriting)
            cast_start += 0.00000001

        return cast_start

    def _add_new_spell_or_item_action(self, action_name, action_attrs_dct, cast_start, str_spell_or_item):
        """
        Inserts new action when action is spell or item active.

        :return: (None)
        """

        cast_end = self.cast_end(action_gen_attrs_dct=action_attrs_dct, action_cast_start=cast_start)

        self.actions_dct.update(
            {cast_start: dict(
                cast_end=cast_end,
                action_name=action_name,)})

        if str_spell_or_item == 'spell':
            cd_end = self.ability_cd_end(ability_name=action_name,
                                         cast_start=cast_start,
                                         stats_function=self.request_stat,
                                         actions_dct=self.actions_dct)

            self.activate_spellblade()

        else:
            cd_end = action_attrs_dct['base_cd']

        # (cd_end is applied later since it requires cast_end)
        self.actions_dct[cast_start].update(dict(
            cd_end=cd_end))

        # CHANNEL
        channel_val = action_attrs_dct['channel_time']
        if channel_val:
            channel_end_time = self.actions_dct[cast_start]['cast_end'] + channel_val

            self.actions_dct[cast_start].update({"channel_end": channel_end_time})

        # Checks if ability resets AA's cd_end, and applies it.
        self.check_and_reset_aa_cd(action_attrs_dct=action_attrs_dct)

    def add_new_action(self, action_name):
        """
        Inserts a new action.

        First dictionary has current action's cast start as keyword,
        and a dictionary as value.

        The second dictionary contains the time the action's animation ends (cast_end),
        the time the action's application ends, the action's name and the time its cooldown ends.

        :return: (None)
        """

        # (cast_start is the moment the action is 'clicked')
        cast_start = self.action_cast_start(given_action_name=action_name)

        # Skips action if exceeds max combat time.
        if cast_start > self.max_combat_time:
            return

        self.apply_action_cost(action_name=action_name)

        # CHAMPION ABILITIES
        if action_name in palette.ALL_POSSIBLE_SPELL_SHORTCUTS:
            spell_dct = self.abilities_attributes(ability_name=action_name)
            self._add_new_spell_or_item_action(action_name=action_name, action_attrs_dct=spell_dct,
                                               cast_start=cast_start, str_spell_or_item='spell')

            # Movement
            self.add_action_dash()

        # AAs
        elif action_name == 'AA':
            self.actions_dct.update({
                cast_start: dict(
                    cd_end=cast_start + 1./self.request_stat(target_name='player', stat_name='att_speed'),
                    action_name=action_name,
                    cast_end=cast_start + self.AA_COOLDOWN)})

            self.add_kalista_dash()

        # ITEMS
        elif action_name in self.chosen_items_dct['player']:
            item_attrs_dct = items_data.ITEMS_ATTRIBUTES[action_name]['general_attributes']
            self._add_new_spell_or_item_action(action_name=action_name, action_attrs_dct=item_attrs_dct,
                                               cast_start=cast_start, str_spell_or_item='item')

        # SUMMONER SPELLS
        else:
            # (cast_end is the same as cast_start)
            # (summoner spells have too high cooldowns, so they are set to a high value)
            self.actions_dct.update({cast_start: dict(
                cast_end=cast_start,
                cd_end=360,
                action_name=action_name)})

    def add_buff(self, buff_name, tar_name, stack_increment=1, initial_stacks_increment=1):
        """
        (Overrides previous method)

        Additionally, checks if buff applied is a dot buff and adds periodic event (unless dot already active).

        Returns:
            (None)
        """

        # Checks if (dot) event already applied.
        is_new = True
        if buff_name in self.active_buffs[tar_name]:
            is_new = False

        super().add_buff(buff_name=buff_name, tar_name=tar_name,
                         stack_increment=stack_increment, initial_stacks_increment=initial_stacks_increment)

        # If it's a new dot..
        if is_new:
            buff_dct = self.req_buff_dct_func(buff_name=buff_name)
            buff_dot_dct = buff_dct['dot']

            # If the buff is a dot, applies dmg event as well.
            if buff_dot_dct:
                dmg_dot_names = buff_dot_dct['dmg_names']
                for dmg_name in dmg_dot_names:
                    first_tick = self.first_dot_tick(current_time=self.current_time, dmg_name=dmg_name)

                    tar_of_dmg = self._target_of_dmg_by_name(dmg_name=dmg_name)
                    self.add_events(effect_name=dmg_name, start_time=first_tick, tar_name=tar_of_dmg)

    def change_cd_before_buff_removal(self, buff_dct):
        """
        Refreshes the cd expiration of corresponding action if given buff prohibits its cd.

        (e.g. Jax w_buff delays start of W cd)

        Modifies:
            active_buffs
            actions_dict
        Return:
            (None)
        """

        if 'prohibit_cd_start' in buff_dct:
            prohibit_cd_start_val = buff_dct['prohibit_cd_start']

            # Checks if buff delays the start of an action's cd.
            if prohibit_cd_start_val:

                # Finds the affected action..
                for action_time in sorted(self.actions_dct, reverse=True):
                    if self.actions_dct[action_time]['action_name'] == prohibit_cd_start_val:

                        # .. and applies the new cd.
                        self.actions_dct[action_time]['cd_end'] = self.ability_cooldown(
                            ability_name=self.actions_dct[action_time]['action_name'],
                            stats_function=self.request_stat)

                        break

    def _remove_expired_buffs(self):
        """
        Removes all expired buffs.

        Modifies:
            active_buffs
        Return:
            (None)
        """

        for tar_name in self.all_target_names:
            tar_act_buffs = self.active_buffs[tar_name]

            for buff_name in sorted(tar_act_buffs):
                tar_buff_dct_in_act_buffs = tar_act_buffs[buff_name]

                if tar_buff_dct_in_act_buffs['ending_time'] == 'permanent':
                    continue

                elif tar_buff_dct_in_act_buffs['ending_time'] < self.current_time:

                    # Applies cd before removing.
                    buff_dct = self.request_buff(buff_name=buff_name)
                    self.change_cd_before_buff_removal(buff_dct=buff_dct)

                    # Removes the buff.
                    del tar_act_buffs[buff_name]

    def remove_expired_buffs_and_refresh_bonuses(self):
        """
        Buffs and bonuses must be refreshed after an event has been applied.

        :return: (None)
        """

        self._remove_expired_buffs()
        self.refresh_stats_bonuses()

    def apply_on_hit_effects(self):
        """
        Applies on hit effects.

        On hit effects can be dmg and buffs application, or buff removal.

        Iterates throughout all active buffs, and applies:
            -on_hit dmg (e.g. Warwick's innate dmg),
            -on_hit buffs (e.g. Black Cleaver armor reduction),
            -and finally removes buffs that are removed on hit.


        :return: (None)
        """

        for buff_name in sorted(self.active_buffs['player']):
            buff_dct = self.req_buff_dct_func(buff_name=buff_name)
            on_hit_dct = buff_dct['on_hit']

            if on_hit_dct:

                # DMG CAUSED ON HIT.
                for dmg_name in on_hit_dct['cause_dmg']:

                    tar_of_dmg = self._target_of_dmg_by_name(dmg_name=dmg_name)
                    self.add_events(effect_name=dmg_name, start_time=self.current_time, tar_name=tar_of_dmg)

                # BUFFS APPLIED ON HIT.
                for buff_applied_on_hit in on_hit_dct['apply_buff']:
                    tar_type = self.request_buff(buff_name=buff_applied_on_hit)['target_type']
                    tar_name = self.player_or_current_enemy(tar_type=tar_type)
                    self.add_buff(buff_name=buff_applied_on_hit, tar_name=tar_name)

                # BUFFS REMOVED ON HIT.
                for buff_removed_on_hit in on_hit_dct['remove_buff']:

                    # Checks if the buff exists on the player.
                    if buff_removed_on_hit in self.active_buffs['player']:
                        self.change_cd_before_buff_removal(buff_dct=buff_dct)
                        del self.active_buffs['player'][buff_removed_on_hit]

                    # Checks if the buff exists on current enemy target.
                    elif buff_removed_on_hit in self.active_buffs[self.current_enemy]:
                        del self.active_buffs[self.current_enemy][buff_removed_on_hit]

                # MODIFIED CDS.
                cds_modifications_dct = on_hit_dct['cds_modified']
                for modified_action_cd_name in cds_modifications_dct:
                    reduction_value = cds_modifications_dct[modified_action_cd_name]
                    self.reduce_action_cd(action_name=modified_action_cd_name, reduction_value=reduction_value)

    def apply_on_hit_effects_and_aa(self, current_time):
        """
        Applies AA effects from buffs and adds AA dmg event.

        :return: (None)
        """

        # Applies on_hit effects.
        self.apply_on_hit_effects()

        # Applies direct dmg.
        self.add_events('aa_dmg', current_time, tar_name=self.current_enemy)

    def apply_ability_or_item_effects(self, eff_dct):
        """
        Applies an action's (abilities, item actives or summoner actives) effects.

        Target is automatically chosen.

        :param: tar_type: (str) 'player' or 'enemy'
        :return: (None)
        """

        # BUFFS
        for buff_name in eff_dct['actives']['buffs']:
            tar_of_buff = self._target_of_buff_by_name(buff_name=buff_name)
            self.add_buff(buff_name=buff_name, tar_name=tar_of_buff)

        # DMGS
        dmg_effects = eff_dct['actives']['dmg']
        for dmg_name in dmg_effects:
            tar_of_dmg = self._target_of_dmg_by_name(dmg_name=dmg_name)
            self.add_events(effect_name=dmg_name, start_time=self.current_time, tar_name=tar_of_dmg)

        if dmg_effects:
            self.activate_liandrys()

        # BUFF REMOVAL
        for buff_name_to_remove in eff_dct['actives']['remove_buff']:
            tar_of_buff = self._target_of_buff_by_name(buff_name=buff_name_to_remove)
            tar_act_buffs = self.active_buffs[tar_of_buff]

            if buff_name_to_remove in tar_act_buffs:
                del tar_act_buffs[buff_name_to_remove]

    def apply_action_effects(self, action_name):
        """
        Applies an action's effects.

        :return: (None)
        """

        # AA
        if action_name == 'AA':
            # ..applies AA physical dmg, and applies (or removes) on_hit buffs and dmg.
            self.activate_rage_speed_buff()
            self.apply_on_hit_effects_and_aa(current_time=self.current_time)

        # ABILITY
        elif action_name in self.castable_spells_shortcuts:
            self.apply_ability_or_item_effects(eff_dct=self.abilities_effects(ability_name=action_name))

        # ITEM ACTIVE - SUMMONER SPELL
        else:
            self.apply_ability_or_item_effects(eff_dct=self.items_effects(action_name))

    def apply_pre_action_events(self):
        """
        Applies all events preceding last action's application start.

        If a periodic event is refreshed and ticks before the last action,
        then event_times changes and is checked again.
        If all targets die, the loop stops.

        :return: (None)
        """

        self.intermediate_events_changed = True

        while self.intermediate_events_changed:

            self.intermediate_events_changed = False

            # If for loop ends with new events being added,
            # then intermediate_events_changed will be set to true,
            # and the for loop will repeat.          

            initial_events = sorted(self.event_times)

            # EVENTS BEFORE ACTION
            for event in initial_events:
                # Checks if event's application time exceeds last action's application start.
                # (cast_end and application start are different for channelled abilities)
                if event <= self.actions_dct[max(self.actions_dct)]['cast_end']:

                    # (must change to ensure buffs are checked)
                    self.current_time = event

                    self.remove_expired_buffs_and_refresh_bonuses()

                    # Applies all dmg effects for all targets.
                    for examined_tar in sorted(self.event_times[self.current_time]):
                        if examined_tar == 'player':
                            # (if all enemies are dead, focuses on last enemy)
                            self.current_enemy = self.first_alive_enemy() or self.enemy_target_names[-1]
                        else:
                            self.current_enemy = examined_tar

                        for dmg_name in self.event_times[self.current_time][examined_tar]:
                            dmg_dct = self.request_dmg(dmg_name=dmg_name)
                            self.apply_dmg_or_heal(dmg_name=dmg_name, dmg_dct=dmg_dct, target_name=examined_tar)

                            if self.is_alive(tar_name=examined_tar):
                                self.add_next_periodic_event(tar_name=examined_tar,
                                                             dmg_name=dmg_name,
                                                             dmg_dct=dmg_dct,
                                                             only_temporary=False)

                        # After dmg has been applied checks if target has died.
                        self.apply_death(tar_name=examined_tar)

                    # Deletes the event after it's applied.
                    del self.event_times[self.current_time]

                    # If new events are added it exits and checks them all over again.
                    if self.intermediate_events_changed:
                        break

                # EXIT INNER LOOP
                # Exits loop after all events prior to an action are applied.
                else:
                    break

                # DEATHS
                self.everyone_dead = True
                # Checks if alive enemies exist.
                for tar_name in self.enemy_target_names:
                    if 'dead_buff' not in self.active_buffs[tar_name]:
                        self.everyone_dead = False
                        break

                # EXIT METHOD
                # If everyone has died, stops applying following events.
                if self.everyone_dead:
                    return

    def apply_single_action(self, new_action):
        """
        Applies a single new action, and events in between,
        until everyone is dead or the max_time is exceeded.

        :param new_action: (str)
        :return: (bool)
        """

        self.remove_expired_buffs_and_refresh_bonuses()

        self.add_new_action(new_action)

        # (movement distance)
        self.between_action_walking()

        self.apply_pre_action_events()

        # If everyone died, stops applying actions as well.
        if self.everyone_dead:
            self.__all_dead_or_max_time_exceeded = True
            return

        self.current_enemy = self.first_alive_enemy()

        # Sets current_time to current action's cast end.
        last_action_end = self._last_action_end()
        self.current_time = last_action_end

        # If max time exceeded, exits loop.
        if self.max_combat_time:
            if self.current_time > self.max_combat_time:
                self.__all_dead_or_max_time_exceeded = True
                return

        # After previous events are applied, applies action effects.
        self.apply_action_effects(action_name=self.actions_dct[max(self.actions_dct)]['action_name'])

    def _apply_all_actions_by_rotation(self):
        """
        Applies all actions when a rotation (instead of priorities) is used.

        :return: (None)
        """

        for new_action in self.rotation_lst:

            # COST REQUIREMENTS
            # (more costly to run this before cd check)
            if not self.cost_sufficiency(action_name=new_action):
                # If the cost is too high, action is skipped.
                continue

            self.apply_single_action(new_action=new_action)

            if self.__all_dead_or_max_time_exceeded:
                return

    def _actions_priorities_triggers_state(self, triggers_dct):
        """
        Checks all triggers in given triggers' dict.

        WARNING: If owner type of a buff is enemy, it targets self.current_target.

        :param triggers_dct:
        :return: (bool)
        """

        for trig_name in triggers_dct:
            trig_dct = triggers_dct[trig_name]
            trig_type = trig_dct['trigger_type']

            # PREVIOUS ACTION
            if trig_type == 'previous_action':
                prev_action_required = trig_dct['obj_name']

                if prev_action_required == self._last_action_name():
                    pass
                else:
                    return False

            # BUFFS
            elif trig_type == 'active_buffs':
                buff_name = trig_dct['obj_name']
                required_stacks = trig_dct['stacks_at_least']

                # Owner
                owner_type = trig_dct['owner_type']
                if owner_type == 'enemy':
                    owner_name = self.current_enemy
                else:
                    owner_name = owner_type

                # Checks active buffs.
                owner_buffs = self.active_buffs[owner_name]
                if buff_name in owner_buffs:
                    buff_stacks = owner_buffs[buff_name]
                    if buff_stacks < required_stacks:
                        return False

            else:
                raise palette.UnexpectedValueError(trig_type)
        # If loop hasn't ended prematurely then all triggers are active.
        else:
            return True

    def _items_and_summoner_spells_priorities_lst(self):
        """
        Creates a list with castable items and summoner spells
        that "should" be cast always at the start of the combat.

        :return: (list)
        """

        queue_set = set()
        items_attrs_dct = items_data.ITEMS_ATTRIBUTES

        # SUMMONER'S SPELLS
        for spell_name in sorted(self.selected_summoner_spells):
            # TODO: Create 'castable_summoner_spells' and 'summoner_spells_at_combat_start' in a new class
            if spell_name in items_data.CASTABLE_ITEMS:
                queue_set.add(spell_name)

        # ITEMS
        for item_name in self.player_items:
            if items_attrs_dct[item_name]['general_attributes']['castable']:
                queue_set.add(item_name)

        return list(queue_set)

    def _action_priorities_after_effects(self):
        """
        Creates action priorities lst after applying all priorities' effects.

        'proceed' and 'succeed' are applied first.
        'top' is applied last.

        :return:
        """

        old_priorities_lst = self._items_and_summoner_spells_priorities_lst() + list(self.DEFAULT_ACTIONS_PRIORITY)

        new_priorities_lst = old_priorities_lst[:]

        for cond_name in sorted(self.ACTION_PRIORITIES_CONDITIONALS):
            old_priorities_lst = new_priorities_lst[:]

            conditional_dct = self.ACTION_PRIORITIES_CONDITIONALS[cond_name]
            triggers_dct = conditional_dct['triggers']

            if self._actions_priorities_triggers_state(triggers_dct=triggers_dct) is True:
                effects_dct = conditional_dct['effects']

                for eff_name in sorted(effects_dct):
                    eff_dct = effects_dct[eff_name]
                    eff_type = eff_dct['effect_type']

                    # SUCCEED TYPE
                    if eff_type == 'succeed':
                        first_action = eff_dct['first']
                        second_action = eff_dct['second']

                        for action_name in old_priorities_lst:
                            # Preceding action is added followed by succeeding action.
                            if action_name == first_action:
                                new_priorities_lst += [first_action, second_action]

                            # Succeeding action found in old priorities is not appended (on its own) in new priorities.
                            elif action_name == second_action:
                                continue

                            # The rest of the actions are appended normally.
                            else:
                                new_priorities_lst.append(action_name)

                    elif eff_type == 'precede':
                        first_action = eff_dct['first']
                        second_action = eff_dct['second']

                        for action_name in old_priorities_lst:
                            # Preceding action is added followed by succeeding action.
                            if action_name == second_action:
                                new_priorities_lst += [first_action, second_action]

                            # Preceding action found in old priorities is not appended (on its own) in new priorities.
                            elif action_name == first_action:
                                continue

                            # The rest of the actions are appended normally.
                            else:
                                new_priorities_lst.append(action_name)

                    elif eff_type == 'top_priority':
                        top_action = eff_dct['obj_name']
                        new_priorities_lst = [top_action] + [i for i in old_priorities_lst if i != top_action]

                    else:
                        raise palette.UnexpectedValueError(eff_type)

        return new_priorities_lst

    def _apply_all_actions_by_priority(self):
        """
        Applies all actions when no rotation is given, meaning priorities are to be used.

        :return: (None)
        """

        while self.current_time <= self.max_combat_time:
            # After each action application, priority is recalculated.
            current_priority_sequence = self._action_priorities_after_effects()

            # Tries all actions until it manages to apply one (then recalculates priority).
            for action_name in current_priority_sequence:

                # CD
                if self._action_cd_end(action_name=action_name) > self.current_time:
                    continue

                # COST REQUIREMENTS
                # (more costly to run this before cd check)
                if not self.cost_sufficiency(action_name=action_name):
                    # If the cost is too high, action is skipped.
                    continue

                self.apply_single_action(new_action=action_name)

                if self.__all_dead_or_max_time_exceeded:
                    return

            # If no action was available, adds a set amount of time before retrying.
            else:
                self.current_time += 0.1

    def _apply_all_actions(self):
        """
        Applies all actions, and events in between,
        until everyone is dead or the max_time is exceeded.

        NOTE: To be overridden by a method that chooses "preferred" action.

        Returns:
            (None)
        """

        if self.rotation_lst:
            self._apply_all_actions_by_rotation()
        else:
            self._apply_all_actions_by_priority()

        self.combat_duration = self._last_action_end()

    def apply_events_after_actions(self):
        """
        Applies events after all actions have finished.

        Non permanent dots are refreshed and their events fully applied.
        Applies death to each viable target.

        :return: (None)
        """

        self.intermediate_events_changed = True

        while self.intermediate_events_changed:

            # If for loop ends with new events being added,
            # then 'self.intermediate_events_changed' will be set to true,
            # and the for loop will repeat.
            # Above process will repeat until all events have been marked as applied.
            self.intermediate_events_changed = False

            initial_events = sorted(self.event_times)

            for event in initial_events:

                # (must change to ensure buffs are checked)
                self.current_time = event

                self.remove_expired_buffs_and_refresh_bonuses()

                # Applies all dmg effects to alive targets.
                for examined_tar in self.event_times[self.current_time]:
                    if examined_tar == 'player':
                        # (if all enemies are dead, focuses on last enemy)
                        self.current_enemy = self.first_alive_enemy() or self.enemy_target_names[-1]
                    else:
                        self.current_enemy = examined_tar

                    for dmg_name in self.event_times[self.current_time][examined_tar]:
                        dmg_dct = self.req_dmg_dct_func(dmg_name=dmg_name)
                        self.apply_dmg_or_heal(dmg_name=dmg_name, dmg_dct=dmg_dct, target_name=examined_tar)

                        # Extends dots.
                        if self.is_alive(tar_name=examined_tar):
                            self.add_next_periodic_event(tar_name=examined_tar,
                                                         dmg_name=dmg_name,
                                                         dmg_dct=dmg_dct,
                                                         only_temporary=True)
                # Deletes the event after it's applied.
                del self.event_times[self.current_time]

        # DEATHS
        for tar_name in self.enemy_target_names:
            self.apply_death(tar_name=tar_name)

    def _apply_runes_static_buff(self):
        if self.selected_runes:
            self.add_buff(buff_name='runes_buff', tar_name='player')

    def _apply_masteries_static_buff(self):
        if self.selected_masteries_dct:
            self.add_buff(buff_name='masteries_static_stats_buff', tar_name='player')

    def _apply_items_static_buff(self):
        if self.player_items:
            self.add_buff(buff_name='items_static_stats_buff', tar_name='player')

    def run_combat_preparation_without_regen(self):
        """
        Applies everything excluding hp5 and mp5 regen needed before a combat begins.

        NOTE: Created to be used when reversing enemies
            to evaluate their stats and buffs (regen excluded to speed it up).

        :return: (None)
        """
        self.current_time = 0

        self._apply_runes_static_buff()

        self._apply_items_static_buff()

        self._apply_masteries_static_buff()

        # Adds passive buffs from abilities.
        self.add_abilities_and_items_passive_buffs(abilities_effects_dct_func=self.abilities_effects,
                                                   abilities_lvls=self.ability_lvls_dct)

        # (Bonuses have to be applied here instead of in their normal methods for noting reasons)
        self.refresh_stats_bonuses()

        # (current stats must be created after bonuses are applied otherwise initial hp will be incorrect)
        self.set_current_stats()

    def run_combat_preparation(self):
        self.run_combat_preparation_without_regen()

        # Adds hp5 and mp5.
        self.add_regenerations()

    def run_combat_preparation_and_note(self):
        """
        Prepares everything for combat and notes stats and buffs.

        :return: (None)
        """

        self.run_combat_preparation()

        self.note_pre_combat_stats_in_results()
        self.note_precombat_active_buffs()

    def _main_combat(self):
        # Applies actions or events based on which occurs first.
        self._apply_all_actions()

        # Applies events after all actions have finished.
        self.apply_events_after_actions()

    def _run_reversed_combat(self):
        """
        Stores enemy's "base" stats, reverted player's buffs and dmg taken,
        in when combat is reversed.

        That is, 'enemy_x' has become 'player' in order to determine enemy-originating buffs.
        Base stats are derived from reversed combats, since it's much more speedy
        than calculating them in the normal combat.

        :return: (None)
        """

        self.rotation_lst = []  # Rotation of enemies is always independent of player's rotation.

        self.run_combat_preparation_without_regen()

        stats_dct = {i: self.request_stat(target_name='player', stat_name=i) for i in self.ENEMY_BASE_STATS_NAMES}
        all_enemy_active_buffs = self.active_buffs['enemy_1']

        non_dead_buff_enemy_buffs = {key: val for key, val in all_enemy_active_buffs.items()}

        # Stores stats player's (that is, 'enemy_x' for normal combat) stats
        # and 'enemy_1' (that is, 'player' for normal combat) active buffs, before the combat starts.
        self.reversed_precombat_player_stats = stats_dct
        self.reversed_precombat_enemy_buffs = non_dead_buff_enemy_buffs

        self._main_combat()
        self.note_dmg_totals_movement_and_heals_in_results()

    def _run_normal_combat(self):
        """
        :return: (None)
        """

        self.run_combat_preparation_and_note()

        self.add_dps_dot_by_enemies()

        self._main_combat()

        # Postcombat
        self.note_dmg_totals_movement_and_heals_in_results()
        self.note_post_combat_stats_in_results()
        self.note_postcombat_active_buffs()
        self.note_survivability()

    def run_combat(self):
        if self._reversed_combat_mode:
            self._run_reversed_combat()
        else:
            self._run_normal_combat()

    def rotation_followed(self):
        rot = []

        for action_time in sorted(self.actions_dct):
            action_name = self.actions_dct[action_time]['action_name']
            rot.append(action_name)

        return rot


class SpecialItems(Actions):

    def __init__(self,
                 rotation_lst,
                 max_targets_dct,
                 selected_champions_dct,
                 champion_lvls_dct,
                 ability_lvls_dct,
                 max_combat_time,
                 selected_masteries_dct,
                 chosen_items_dct,
                 selected_summoner_spells,
                 initial_enemies_total_stats,
                 initial_active_buffs,
                 initial_current_stats,
                 selected_runes,
                 enemies_originating_dmg_data,
                 _reversed_combat_mode):

        self._last_time_black_cleaver_applied = 0

        Actions.__init__(self,
                         rotation_lst=rotation_lst,
                         max_targets_dct=max_targets_dct,
                         selected_champions_dct=selected_champions_dct,
                         champion_lvls_dct=champion_lvls_dct,
                         ability_lvls_dct=ability_lvls_dct,
                         max_combat_time=max_combat_time,
                         selected_masteries_dct=selected_masteries_dct,
                         chosen_items_dct=chosen_items_dct,
                         selected_summoner_spells=selected_summoner_spells,
                         initial_active_buffs=initial_active_buffs,
                         initial_current_stats=initial_current_stats,
                         selected_runes=selected_runes,
                         initial_enemies_total_stats=initial_enemies_total_stats,
                         _reversed_combat_mode=_reversed_combat_mode,
                         enemies_originating_dmg_data=enemies_originating_dmg_data)

    # GUINSOOS RAGEBLADE
    GUINSOOS_BELOW_HALF_HP_BUFF = {'buff_source': 'guinsoos_rageblade',
                                   'dot': False,
                                   'duration': 'permanent',
                                   'max_stacks': 1,
                                   'on_hit': {},
                                   'stats': {'att_speed': {'percent': {'stat_mods': {},
                                                                       'stat_values': 0.2}},
                                             'lifesteal': {'additive': {'stat_mods': {},
                                                                        'stat_values': 0.1}},
                                             'spellvamp': {'additive': {'stat_mods': {},
                                                                        'stat_values': 0.1}}},
                                   'target_type': 'player'}
    GUINSOOS_ABOVE_HALF_HP_BUFF = {k: v for k, v in GUINSOOS_BELOW_HALF_HP_BUFF.items() if k != 'stats'}
    GUINSOOS_ABOVE_HALF_HP_BUFF.update({'stats': {}})

    def guinsoos_rageblade_low_hp_buff(self):
        # BELOW 50%
        # (when initially called during item passives application current stats aren't created yet)
        if 'player' in self.current_stats:
            half_max_hp = self.request_stat(target_name='player', stat_name='hp') / 2
            if self.current_stats['player']['current_hp'] < half_max_hp:
                return self.GUINSOOS_BELOW_HALF_HP_BUFF

        # ABOVE 50%
        return self.GUINSOOS_ABOVE_HALF_HP_BUFF

    # SPELLBLADE
    SPELLBLADE_ITEMS_PRIORITY_SORTED = ('lich_bane', 'trinity_force', 'iceborn_gauntlet', 'sheen')
    items_data.ensure_in_items_names(SPELLBLADE_ITEMS_PRIORITY_SORTED)
    # (ensures names used exist, otherwise methods below will function incorrectly)

    SPELLBLADE_ITEMS_NAMES_MAP = {'iceborn_gauntlet': 'iceborn_gauntlet',
                                  'sheen': 'sheen',
                                  'lich_bane': 'lich_bane',
                                  'trinity_force': 'trinity_force'}
    items_data.ensure_in_items_names(SPELLBLADE_ITEMS_NAMES_MAP.values())

    SPELLBLADE_BUFF_NAMES_MAP = {'inhibitor': 'spellblade_inhibitor',
                                 'triggered': 'spellblade_triggered'}
    items_data.ensure_in_items_buffs(SPELLBLADE_BUFF_NAMES_MAP.values())

    SPELLBLADE_INITIATOR_WITHOUT_ON_HIT_BUFF = palette.buff_dct_base_deepcopy()
    SPELLBLADE_INITIATOR_WITHOUT_ON_HIT_BUFF['buff_source'] = 'sheen'
    SPELLBLADE_INITIATOR_WITHOUT_ON_HIT_BUFF['dot'] = False
    SPELLBLADE_INITIATOR_WITHOUT_ON_HIT_BUFF['duration'] = 'permanent'
    SPELLBLADE_INITIATOR_WITHOUT_ON_HIT_BUFF['target_type'] = 'player'
    SPELLBLADE_INITIATOR_WITHOUT_ON_HIT_BUFF['max_stacks'] = 1
    SPELLBLADE_INITIATOR_WITHOUT_ON_HIT_BUFF['stats'] = {}
    SPELLBLADE_INITIATOR_WITHOUT_ON_HIT_BUFF['prohibit_cd_start'] = {}

    # (they are used purely as tags)
    SPELLBLADE_INHIBITOR_BUFF = palette.buff_dct_base_deepcopy()
    SPELLBLADE_INHIBITOR_BUFF['buff_source'] = 'sheen'
    SPELLBLADE_INHIBITOR_BUFF['dot'] = False
    SPELLBLADE_INHIBITOR_BUFF['duration'] = 1.5
    SPELLBLADE_INHIBITOR_BUFF['target_type'] = 'player'
    SPELLBLADE_INHIBITOR_BUFF['max_stacks'] = 1
    SPELLBLADE_INHIBITOR_BUFF['stats'] = {}
    SPELLBLADE_INHIBITOR_BUFF['on_hit'] = {}
    SPELLBLADE_INHIBITOR_BUFF['prohibit_cd_start'] = {}

    SPELLBLADE_TRIGGERED_BUFF = palette.buff_dct_base_deepcopy()
    SPELLBLADE_TRIGGERED_BUFF['buff_source'] = 'sheen'
    SPELLBLADE_TRIGGERED_BUFF['dot'] = False
    SPELLBLADE_TRIGGERED_BUFF['duration'] = 7
    SPELLBLADE_TRIGGERED_BUFF['target_type'] = 'player'
    SPELLBLADE_TRIGGERED_BUFF['max_stacks'] = 1
    SPELLBLADE_TRIGGERED_BUFF['stats'] = {}
    SPELLBLADE_TRIGGERED_BUFF['on_hit'] = {}
    SPELLBLADE_TRIGGERED_BUFF['prohibit_cd_start'] = {}

    # TODO: single call memo
    def spellblade_dmgs_lst(self):
        dmgs_lst = []
        # Ring dmg is applied regardless of other items.
        if self.SPELLBLADE_ITEMS_NAMES_MAP['iceborn_gauntlet'] in self.player_items:
            dmgs_lst.append('iceborn_gauntlet_ring_dmg')

        # Spellblade is applied only once, by prioritized item.
        for spellblade_item in self.SPELLBLADE_ITEMS_PRIORITY_SORTED:
            if spellblade_item in self.player_items:
                # (by convention spellblade main dmg should be 'item_name_dmg_0')
                dmgs_lst.append(spellblade_item + '_dmg_0')

        return dmgs_lst

    def spellblade_initiator(self):

        final_buff_dct = {}
        final_buff_dct.update(self.SPELLBLADE_INITIATOR_WITHOUT_ON_HIT_BUFF)

        player_active_buffs = self.active_buffs['player']

        inhibitor_buff_name = self.SPELLBLADE_BUFF_NAMES_MAP['inhibitor']
        if inhibitor_buff_name in player_active_buffs:
            final_buff_dct.update({'on_hit': {}})

        else:
            on_hit = copy.deepcopy(palette.ON_HIT_EFFECTS)

            triggered_buff_name = self.SPELLBLADE_BUFF_NAMES_MAP['triggered']
            inhibitor_buff_name = self.SPELLBLADE_BUFF_NAMES_MAP['inhibitor']

            if triggered_buff_name in player_active_buffs:
                on_hit['cause_dmg'] = self.spellblade_dmgs_lst()
                on_hit['remove_buff'].append(triggered_buff_name)
                on_hit['apply_buff'].append(inhibitor_buff_name)

            final_buff_dct.update({'on_hit': on_hit})

        return final_buff_dct

    def spellblade_triggered(self):
        return self.SPELLBLADE_TRIGGERED_BUFF

    def spellblade_inhibitor(self):
        return self.SPELLBLADE_INHIBITOR_BUFF

    def activate_spellblade(self):

        player_active_buffs = self.active_buffs['player']
        if 'spellblade_initiator' in player_active_buffs:
            if 'spellblade_inhibitor' not in player_active_buffs:
                self.add_buff(buff_name='spellblade_triggered', tar_name='player')

    # RAGE BUFF
    RAGE_SPEED_BUFF_MELEE = palette.buff_dct_base_deepcopy()
    RAGE_SPEED_BUFF_MELEE['buff_source'] = 'phage'
    RAGE_SPEED_BUFF_MELEE['dot'] = False
    RAGE_SPEED_BUFF_MELEE['duration'] = 2
    RAGE_SPEED_BUFF_MELEE['target_type'] = 'player'
    RAGE_SPEED_BUFF_MELEE['max_stacks'] = 1
    RAGE_SPEED_BUFF_MELEE['stats'] = {'move_speed': {'additive': {'stat_mods': {}, 'stat_values': 20}}}
    RAGE_SPEED_BUFF_MELEE['on_hit'] = {}
    RAGE_SPEED_BUFF_MELEE['prohibit_cd_start'] = {}

    RAGE_SPEED_BUFF_RANGED = copy.deepcopy(RAGE_SPEED_BUFF_MELEE)
    RAGE_SPEED_BUFF_RANGED['stats']['move_speed']['additive']['stat_values'] /= 2

    def rage_speed_buff(self):
        if self.player_range_type == 'melee':
            return self.RAGE_SPEED_BUFF_MELEE
        else:
            return self.RAGE_SPEED_BUFF_RANGED

    def activate_rage_speed_buff(self):
        player_active_buffs = self.active_buffs['player']
        if 'rage_initiator_buff' in player_active_buffs:

            self.add_buff(buff_name='rage_speed_buff', tar_name='player')

    RAGE_INITIATOR_BUFF = palette.buff_dct_base_deepcopy()
    RAGE_INITIATOR_BUFF['buff_source'] = 'phage'
    RAGE_INITIATOR_BUFF['dot'] = False
    RAGE_INITIATOR_BUFF['duration'] = 'permanent'
    RAGE_INITIATOR_BUFF['target_type'] = 'player'
    RAGE_INITIATOR_BUFF['max_stacks'] = 1
    RAGE_INITIATOR_BUFF['stats'] = {}
    RAGE_INITIATOR_BUFF['prohibit_cd_start'] = {}
    for i in RAGE_INITIATOR_BUFF['on_hit']:
        RAGE_INITIATOR_BUFF['on_hit'][i] = []
    RAGE_INITIATOR_BUFF['on_hit']['apply_buff'] = ['rage_speed_buff']

    def rage_initiator_buff(self):
        return self.RAGE_INITIATOR_BUFF

    # BLACK CLEAVER
    BLACK_CLEAVER_ARMOR_REDUCTION_BUFF = palette.buff_dct_base_deepcopy()
    BLACK_CLEAVER_ARMOR_REDUCTION_BUFF['buff_source'] = 'the_black_cleaver'
    BLACK_CLEAVER_ARMOR_REDUCTION_BUFF['dot'] = False
    BLACK_CLEAVER_ARMOR_REDUCTION_BUFF['duration'] = 5
    BLACK_CLEAVER_ARMOR_REDUCTION_BUFF['target_type'] = 'enemy'
    BLACK_CLEAVER_ARMOR_REDUCTION_BUFF['max_stacks'] = 6
    BLACK_CLEAVER_ARMOR_REDUCTION_BUFF['stats'] = {'percent_armor_reduction': {'additive': {'stat_mods': {},
                                                                                            'stat_values': 0.05}}}
    BLACK_CLEAVER_ARMOR_REDUCTION_BUFF['on_hit'] = {}
    BLACK_CLEAVER_ARMOR_REDUCTION_BUFF['prohibit_cd_start'] = {}

    def black_cleaver_armor_reduction_buff(self):
        return self.BLACK_CLEAVER_ARMOR_REDUCTION_BUFF

    BLACK_CLEAVER_REDUCTION_BUFFS_NAMES = ['black_cleaver_armor_reduction_'+str(i) for i in range(1, 7)]

    BLACK_CLEAVER_INITIATOR_BUFF = palette.buff_dct_base_deepcopy()
    BLACK_CLEAVER_INITIATOR_BUFF['buff_source'] = 'the_black_cleaver'
    BLACK_CLEAVER_INITIATOR_BUFF['dot'] = False
    BLACK_CLEAVER_INITIATOR_BUFF['duration'] = 'permanent'
    BLACK_CLEAVER_INITIATOR_BUFF['target_type'] = 'player'
    BLACK_CLEAVER_INITIATOR_BUFF['max_stacks'] = 1
    BLACK_CLEAVER_INITIATOR_BUFF['stats'] = {}
    BLACK_CLEAVER_INITIATOR_BUFF['prohibit_cd_start'] = {}
    BLACK_CLEAVER_INITIATOR_BUFF['on_hit'] = {}

    def black_cleaver_initiator_buff(self):
        return self.BLACK_CLEAVER_INITIATOR_BUFF

    def activate_black_cleaver_armor_reduction_buff(self, dmg_type, target_name):
        """
        Applies buff of armor reduction buff by black cleaver.

        :return: (None)
        """

        if ('the_black_cleaver' in self.player_items) and (target_name == 'player'):

            if dmg_type in ('physical', 'aa'):
                if self._last_time_black_cleaver_applied != self.current_time:

                    self._last_time_black_cleaver_applied = self.current_time
                    black_cleavers_count = self.player_items.count('the_black_cleaver')
                    lst_applied = self.BLACK_CLEAVER_REDUCTION_BUFFS_NAMES[:black_cleavers_count]

                    for black_cleaver_red_buff_name in lst_applied:
                        self.add_buff(buff_name=black_cleaver_red_buff_name, tar_name=self.current_enemy)

    # IMMOLATE
    IMMOLATE_BUFF = palette.buff_dct_base_deepcopy()
    IMMOLATE_BUFF['buff_source'] = 'sunfire'
    IMMOLATE_BUFF['duration'] = 'permanent'
    IMMOLATE_BUFF['target_type'] = 'player'
    IMMOLATE_BUFF['max_stacks'] = 1
    IMMOLATE_BUFF['stats'] = {}
    IMMOLATE_BUFF['prohibit_cd_start'] = {}
    IMMOLATE_BUFF['on_hit'] = {}
    del IMMOLATE_BUFF['dot']

    ORDERED_IMMOLATE_ITEMS = ('sunfire_cape', 'enchantment_cinderhulk', 'bamis_cinder',)  # (highest to lowest priority)
    IMMOLATE_ITEMS_TO_DMG_NAME_MAP = {i: i+'_immolate_dmg' for i in ORDERED_IMMOLATE_ITEMS}
    items_data.ensure_in_items_names(set(ORDERED_IMMOLATE_ITEMS) | set(IMMOLATE_ITEMS_TO_DMG_NAME_MAP))

    REVERSED_IMMOLATE_ITEMS_TO_DMG_NAME_MAP = {v: k for k, v in IMMOLATE_ITEMS_TO_DMG_NAME_MAP.items()}

    def immolate_buff(self):
        """
        Creates immolate buff based on highest priority item. Its dmg is the only dmg applied.
        :return:
        """

        dot_attrs_dct = {'period': 1,
                         'dmg_names': [],
                         'always_on_x_targets': 3}

        buff_dct = {'dot': dot_attrs_dct}
        buff_dct.update(self.IMMOLATE_BUFF)

        for immolate_item in self.ORDERED_IMMOLATE_ITEMS:
            # (when a match is found, it adds its dmg_name and exits method)
            if immolate_item in self.player_items:
                dmg_name = self.IMMOLATE_ITEMS_TO_DMG_NAME_MAP[immolate_item]

                buff_dct['dot']['dmg_names'].append(dmg_name)

                return buff_dct

    IMMOLATE_DMG_BASE = palette.dmg_dct_base_deepcopy()
    IMMOLATE_DMG_BASE['target_type'] = 'enemy'
    IMMOLATE_DMG_BASE['dmg_category'] = 'standard_dmg'
    IMMOLATE_DMG_BASE['resource_type'] = 'hp'
    IMMOLATE_DMG_BASE['mods'] = {}
    IMMOLATE_DMG_BASE['life_conversion_type'] = None
    IMMOLATE_DMG_BASE['radius'] = 500
    IMMOLATE_DMG_BASE['dot'] = {'buff_name': 'immolate_buff'}
    IMMOLATE_DMG_BASE['max_targets'] = 3
    IMMOLATE_DMG_BASE['usual_max_targets'] = 3
    IMMOLATE_DMG_BASE['delay'] = 1
    IMMOLATE_DMG_BASE['heal_for_dmg_amount'] = False
    IMMOLATE_DMG_BASE['crit_type'] = None
    IMMOLATE_DMG_BASE['dmg_type'] = 'magic'
    del IMMOLATE_DMG_BASE['dmg_source']
    del IMMOLATE_DMG_BASE['dmg_values']

    def _immolate_dmg_base(self, dmg_name, dmg_values):
        dmg_source = self.REVERSED_IMMOLATE_ITEMS_TO_DMG_NAME_MAP[dmg_name]

        dct = {'dmg_source': dmg_source,
               'dmg_values': dmg_values}

        dct.update(self.IMMOLATE_DMG_BASE)

        return dct

    def sunfire_cape_immolate_dmg(self):
        dmg_values = 25 + self.player_lvl
        return self._immolate_dmg_base(dmg_name='sunfire_cape_immolate_dmg', dmg_values=dmg_values)

    def bamis_cinder_immolate_dmg(self):
        dmg_values = 5 + self.player_lvl
        return self._immolate_dmg_base(dmg_name='sunfire_cape_immolate_dmg', dmg_values=dmg_values)

    def enchantment_cinderhulk(self):
        dmg_values = 15 + 0.6 * self.player_lvl
        return self._immolate_dmg_base(dmg_name='sunfire_cape_immolate_dmg', dmg_values=dmg_values)

    # LIANDRYS TORMENT
    LIANDRYS_NAME = 'liandrys_torment'
    items_data.ensure_in_items_names((LIANDRYS_NAME,))

    def activate_liandrys(self):
        """
        Applies liandry's dot if item present in player's items.

        Dot is applied on ability or item actives only.

        :return:
        """

        if self.LIANDRYS_NAME in self.player_items:
            self.add_buff(buff_name='liandrys_torment_dot_buff', tar_name=self.current_enemy)


for i in SpecialItems.BLACK_CLEAVER_REDUCTION_BUFFS_NAMES:
    setattr(SpecialItems, i, SpecialItems.black_cleaver_armor_reduction_buff)


class Presets(SpecialItems):

    def __init__(self,
                 rotation_lst,
                 max_targets_dct,
                 selected_champions_dct,
                 champion_lvls_dct,
                 ability_lvls_dct,
                 max_combat_time,
                 selected_masteries_dct,
                 chosen_items_dct,
                 selected_summoner_spells,
                 initial_enemies_total_stats,
                 initial_active_buffs,
                 initial_current_stats,
                 selected_runes,
                 enemies_originating_dmg_data,
                 _reversed_combat_mode):

        SpecialItems.__init__(self,
                              rotation_lst=rotation_lst,
                              max_targets_dct=max_targets_dct,
                              selected_champions_dct=selected_champions_dct,
                              champion_lvls_dct=champion_lvls_dct,
                              ability_lvls_dct=ability_lvls_dct,
                              max_combat_time=max_combat_time,
                              selected_masteries_dct=selected_masteries_dct,
                              chosen_items_dct=chosen_items_dct,
                              selected_summoner_spells=selected_summoner_spells,
                              initial_active_buffs=initial_active_buffs,
                              initial_current_stats=initial_current_stats,
                              selected_runes=selected_runes,
                              initial_enemies_total_stats=initial_enemies_total_stats,
                              _reversed_combat_mode=_reversed_combat_mode,
                              enemies_originating_dmg_data=enemies_originating_dmg_data)

        self._setup_ability_lvls()

    def _setup_ability_lvls(self):
        """
        If no abilities' lvls are given, it automatically sets them.

        :return: (None)
        """
        if not self.ability_lvls_dct:
            skill_inst = skills_points.SkillsLvlUp(skill_lvl_up_data_dct=self.SPELL_LVL_UP_PRIORITIES)

            ability_points_on_all_lvls = skill_inst.skills_points_on_all_lvls()

            self.ability_lvls_dct = ability_points_on_all_lvls[self.champion_lvls_dct['player']]


class VisualRepresentation(Presets):

    PLAYER_STATS_DISPLAYED = ('ap', 'ad', 'armor', 'mr', 'current_hp', 'mp', 'att_speed', 'cdr')
    ENEMY_STATS_DISPLAYED = ('armor', 'mr', 'physical_dmg_taken', 'magic_dmg_taken', 'current_hp')

    def __init__(self,
                 rotation_lst,
                 max_targets_dct,
                 selected_champions_dct,
                 champion_lvls_dct,
                 ability_lvls_dct,
                 max_combat_time,
                 selected_masteries_dct,
                 chosen_items_dct,
                 selected_summoner_spells,
                 initial_enemies_total_stats,
                 initial_active_buffs,
                 initial_current_stats,
                 selected_runes,
                 enemies_originating_dmg_data,
                 _reversed_combat_mode):

        Presets.__init__(self,
                         rotation_lst=rotation_lst,
                         max_targets_dct=max_targets_dct,
                         selected_champions_dct=selected_champions_dct,
                         champion_lvls_dct=champion_lvls_dct,
                         ability_lvls_dct=ability_lvls_dct,
                         max_combat_time=max_combat_time,
                         chosen_items_dct=chosen_items_dct,
                         selected_summoner_spells=selected_summoner_spells,
                         initial_active_buffs=initial_active_buffs,
                         initial_current_stats=initial_current_stats,
                         selected_runes=selected_runes,
                         selected_masteries_dct=selected_masteries_dct,
                         initial_enemies_total_stats=initial_enemies_total_stats,
                         _reversed_combat_mode=_reversed_combat_mode,
                         enemies_originating_dmg_data=enemies_originating_dmg_data)

    @staticmethod
    def __set_table_font_size(table_obj, font_size=8):
        table_obj.auto_set_font_size(False)
        table_obj.set_fontsize(font_size)

    @staticmethod
    def __set_pie_font_size(pie_obj, font_size=8):
        # (pie object is a list, second item are the labels, 3rd item are the values)
        for i in pie_obj[1]:
            i.set_fontsize(font_size)

        for i in pie_obj[2]:
            i.set_fontsize(font_size)

    def __set_plot_x_lim(self, x_start=-0.2):
        plt.xlim([x_start, self.max_combat_time])

    def subplot_pie_chart_dmg_types(self, subplot_obj):

        dmg_values = []
        slice_names = []

        for dmg_total_name in ('total_physical', 'total_magic', 'total_true'):

            # Filters out 0 value dmg.
            if self.combat_results['player'][dmg_total_name] > 0:

                slice_names.append(dmg_total_name.replace('total_', ''))
                dmg_values.append(self.combat_results['player'][dmg_total_name])

        pie_obj = subplot_obj.pie(x=dmg_values, labels=slice_names, autopct='%1.1f%%', colors=('r', 'b', 'w'))
        self.__set_pie_font_size(pie_obj=pie_obj)

    def subplot_pie_chart_sources(self, subplot_obj):

        dmg_values = []
        slice_names = []

        for source_name in sorted(self.combat_results['player']['source']):

            # Filters out 0 value dmg.
            if self.combat_results['player']['source'][source_name] > 0:

                slice_names.append(source_name)
                dmg_values.append(self.combat_results['player']['source'][source_name])

        pie_obj = subplot_obj.pie(x=dmg_values, labels=slice_names, autopct='%1.1f%%')

        self.__set_pie_font_size(pie_obj=pie_obj)

    def add_actions_on_plot(self, subplot_obj, annotated=True):
        # ACTIONS IN PLOT
        x_actions = []
        y_actions = []
        previous_action_name_x = -100
        prev_high = False

        for x_var in sorted(self.actions_dct):
            x_actions.append(x_var)
            y_actions.append(0)

            # If names are too close..
            if x_var - previous_action_name_x < 1:

                # ..and if previous was low..
                if not prev_high:

                    # ..increases the height of the name.
                    higher_y = 40
                    prev_high = True

                else:
                    prev_high = False
                    higher_y = 0
            else:
                # If names are too far, it sets it on the lowest height.
                prev_high = False
                higher_y = 0

            # ANNOTATE
            if annotated is True:
                subplot_obj.annotate(self.actions_dct[x_var]['action_name'], xy=(x_var, -70 + higher_y), color='grey',
                                     size=8, rotation=45)

            previous_action_name_x = x_var

            # Action vertical lines
            plt.axvline(x=x_var, color='grey', linestyle='dashed', alpha=0.6)

    def subplot_dmg_graph(self, subplot_obj):

        subplot_obj.grid(b=True)

        # Line at y=0, and at x=0.
        plt.axhline(y=0, color='black')
        self.__set_plot_x_lim()

        plt.ylabel('hp')

        color_counter_var = 0
        color_lst = ('b', 'g', 'y', 'orange', 'red')

        # Creates graph for each target.
        for tar_name in self.enemy_target_names:

            hp_change_times = sorted(self.combat_history[tar_name]['current_hp'])
            max_hp = self.request_stat(target_name=tar_name, stat_name='hp')

            # Inserts initial point.
            subplot_obj.plot([0], max_hp, color=color_lst[color_counter_var], alpha=0.8, label=tar_name)

            # Left boundary is initially set to max hp.
            x_1 = 0
            current_hp = max_hp

            x_values = []
            y_values = []

            for event_time in hp_change_times:

                # (x values for same-height-points cluster)
                x_area_lst = [i for i in range(int(x_1 * 100), int((event_time + 0.01) * 100))]

                for x_element in x_area_lst:
                    x_values.append(x_element/100)
                    y_values.append(current_hp)

                current_hp = self.combat_history[tar_name]['current_hp'][event_time]
                x_1 = event_time

            if hp_change_times:
                # When events finish, adds one last point so that last event cluster is included.
                x_values.append(hp_change_times[-1])
                y_values.append(current_hp)

            subplot_obj.plot(x_values, y_values, color=color_lst[color_counter_var], alpha=0.7)
            color_counter_var += 1

        self.add_actions_on_plot(subplot_obj=subplot_obj, annotated=True)

    def subplot_resource_vamp_lifesteal_graph(self, subplot_obj):

        subplot_obj.grid(b=True)

        # Line at y=0.
        plt.axhline(y=0, color='black')
        self.__set_plot_x_lim()

        plt.xlabel('time')
        plt.ylabel('value')

        # LIFESTEAL, SPELLVAMP, RESOURCE
        stat_color_map = {'lifesteal': 'orange', 'spellvamp': 'g', 'resource': 'b'}

        # Places initial value of resource.
        subplot_obj.plot([0], self.request_stat(target_name='player', stat_name=self.RESOURCE_USED),
                         color=stat_color_map['resource'], marker='.')

        for examined in stat_color_map:

            if examined == 'resource':
                # (Sets initial value of resource)
                x_val = [0, ]
                y_val = [self.request_stat(target_name='player', stat_name=self.RESOURCE_USED), ]
            else:
                x_val = []
                y_val = []

            # Inserts each time and value into graph.
            for event_time in sorted(self.combat_history['player'][examined]):
                x_val.append(event_time)
                y_val.append(self.combat_history['player'][examined][event_time])

            subplot_obj.plot(x_val, y_val, color=stat_color_map[examined], marker='.', label=examined)

        self.add_actions_on_plot(subplot_obj=subplot_obj, annotated=False)

    def subplot_player_stats_table(self, subplot_obj):
        """
        Subplots player's pre and post combat stats.

        Stat values are rounded.

        Returns:
            (None)
        """

        table_lst = [('PLAYER STATS', 'PRE', 'POST'), ]

        # Creates lines.
        for stat_name in self.PLAYER_STATS_DISPLAYED:

            precombat_value = self.combat_results['player']['pre_combat_stats'][stat_name]
            precombat_value = precombat_value

            postcombat_value = self.combat_results['player']['post_combat_stats'][stat_name]
            postcombat_value = postcombat_value

            line_tpl = (stat_name+': ', precombat_value, postcombat_value)

            # Inserts in data to be displayed
            table_lst.append(line_tpl)

        subplot_obj.axis('off')
        table_obj = subplot_obj.table(
            cellText=table_lst,
            cellLoc='left',
            loc='center')

        self.__set_table_font_size(table_obj=table_obj)

    def subplot_enemy_stats_table(self, subplot_obj):
        """
        Subplots player's pre combat stats.

        Stat values are rounded.

        Returns:
            (None)
        """

        table_lst = []

        for tar_name in self.enemy_target_names:
            tar_lvl = self.champion_lvls_dct[tar_name]
            tar_champ = self.selected_champions_dct[tar_name]
            table_lst.append(('%s' % tar_name.upper(), ''))
            table_lst.append((tar_champ.upper(), 'Lvl: %s' % tar_lvl))

            # Creates lines.
            for stat_name in self.ENEMY_STATS_DISPLAYED:

                postcombat_value = self.combat_results[tar_name]['post_combat_stats'][stat_name]
                postcombat_value = round(postcombat_value, 4)

                line_tpl = (stat_name+': ', postcombat_value)

                # Inserts in data to be displayed
                table_lst.append(line_tpl)

        subplot_obj.axis('off')

        table_obj = subplot_obj.table(
            cellText=table_lst,
            cellLoc='left',
            loc='center')

        self.__set_table_font_size(table_obj=table_obj)

    def subplot_preset_and_results_table(self, subplot_obj):

        # Rotation
        table_lst = [('ROTATION',), (self.rotation_followed(),)]

        # Dps
        dps_value = self.combat_results['player']['dps']
        try:
            dps_value = round(dps_value, 2)
        # (val can be string when time too short)
        except TypeError:
            pass
        dps_str = 'DPS: {}'.format(dps_value)
        table_lst.append((dps_str,))

        for metric_name in ('total_dmg_done', 'total_movement', 'movement_per_sec', 'survivability', 'heals'):
            val = self.combat_results['player'][metric_name]
            val = round(val, 2)
            metric_str = '{}: {}'.format(metric_name, val)
            table_lst.append((metric_str, ))

        combat_duration_str = 'Fight duration: {}'.format(self.combat_duration)
        table_lst.append((combat_duration_str,))

        subplot_obj.axis('off')
        table_obj = subplot_obj.table(
            cellText=table_lst,
            cellLoc='left',
            loc='center')

        self.__set_table_font_size(table_obj=table_obj)

    def represent_results_visually(self):

        gs_main = gridspec.GridSpec(6, 6)

        # Graphs
        self.subplot_dmg_graph(subplot_obj=plt.figure(1).add_subplot(gs_main[:2, :4]))
        self.subplot_resource_vamp_lifesteal_graph(subplot_obj=plt.figure(1).add_subplot(gs_main[2:4, :4]))

        # Pies
        self.subplot_pie_chart_dmg_types(subplot_obj=plt.figure(1).add_subplot(gs_main[5, :1]))
        self.subplot_pie_chart_sources(subplot_obj=plt.figure(1).add_subplot(gs_main[5, 1:2]))

        # Tables
        self.subplot_player_stats_table(subplot_obj=plt.figure(1).add_subplot(gs_main[5, 2:4]))
        self.subplot_enemy_stats_table(subplot_obj=plt.figure(1).add_subplot(gs_main[:4, 4:6]))
        self.subplot_preset_and_results_table(subplot_obj=plt.figure(1).add_subplot(gs_main[5, 4:6]))

        plt.figure(1).set_size_inches(11, 8, forward=True)
        plt.show()

        return

