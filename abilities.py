import operator
import copy
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import abc
import os

import buffs
import timers
import runes
from champions import app_champions_base_stats
import palette
import skills_points
import items_folder.items_data as items_data_module
from palette import placeholder


# Sets font size on all plt graphs.
plt.rcParams['font.size'] = 12


BUFFS_AND_DMGS_IMPLEMENTED_BY_METHODS = set()
BUFFS_AND_DMGS_IMPLEMENTED_BY_METHODS.update(items_data_module.ITEMS_BUFFS_AND_DMGS_EXPRESSED_BY_METHOD)


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
        self.events = {}
        # (first examined target is always 'enemy_1')
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

    def add_single_event(self, event_time, event_name, event_type, event_target):
        self.events.setdefault(event_time, [])

        self.events[event_time].append({'event_name': event_name,
                                        'event_type': event_type,
                                        'target_name': event_target})

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
            self.add_single_event(event_time=start_time, event_name=effect_name, event_type='dmg', event_target=tar_name)
            targets_already_hit = 1
        else:
            targets_already_hit = 0

        # AOE DMG
        # (Aoe can only be applied to enemies.)

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
        while targets_already_hit < max_tars_val:

            next_enemy = self.next_alive_enemy(current_tar=prev_enemy)
            if next_enemy is None:
                break

            self.current_enemy = next_enemy
            self.add_single_event(event_time=start_time, event_name=effect_name, event_type='dmg', event_target=next_enemy)
            targets_already_hit += 1

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
                self.add_single_event(event_time=start_time,
                                      event_name=dmg_name,
                                      event_type='dmg',
                                      event_target=dmg_owner_name)

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

_DPS_BY_ENEMIES_BUFF_BASE = palette.SafeBuff(dict(
        target_type='player',
        duration='permanent',
        max_stacks=1,
        stats={},
        on_hit={},
        prohibit_cd_start={},
        buff_source='enemies_dps',
        max_targets=1,
        usual_max_targets=1,
        dot=palette.BUFF_DOT_ATTRS
    ))

_DPS_BY_ENEMIES_BUFF_BASE['dot']['period'] = buffs.NATURAL_REGEN_PERIOD
_DPS_BY_ENEMIES_BUFF_BASE['dot']['always_on_x_targets'] = False
_DPS_BY_ENEMIES_BUFF_BASE['dot']['dmg_names'] = []
# Adds all dmgs' names in dot buff.
for dps_dmg_name in _DPS_BY_ENEMIES_DMGS_NAMES:
    _DPS_BY_ENEMIES_BUFF_BASE['dot']['dmg_names'].append(dps_dmg_name)

_DPS_BY_ENEMIES_DMG_BASE = palette.SafeDmg(dict(
    target_type='player',
    dmg_category='standard_dmg',
    resource_type='hp',
    dmg_type=placeholder,
    dmg_values=placeholder,
    dmg_source='dps_by_enemies',
    mods={},
    life_conversion_type=None,
    radius=None,
    dot={'buff_name': 'dps_by_enemies_dot_buff'},
    max_targets=1,
    usual_max_targets=1,
    delay=0,
    crit_type=None,
    heal_for_dmg_amount=False
))
_DPS_BY_ENEMIES_DMG_BASE.delete_keys(['dmg_type', 'dmg_values'])


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
    DPS_ENHANCER_COEF = 2   # (used to make player take dmg of e.g. 2 enemies)

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

        all_enemies_total_dmg = 0.1     # (Small non 0 value in order to avoid ZeroDivisionError)
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
            if 'AA' in source_dct:
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
    ABILITIES_ATTRIBUTES = {}
    ABILITIES_EFFECTS = {}
    ABILITIES_CONDITIONALS = {}

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

        self.current_target_num = None
        self.action_on_cd_func = action_on_cd_func

        self.castable_spells_shortcuts = None
        self.not_castable_spells_shortcuts = None

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

    def _unsafe_x_formula_to_value(self, x_formula, x_name, x_type, x_owner):
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
        if type(x_formula) is palette.TrustedStr:
            return eval(x_formula)
        else:
            raise palette.UnexpectedValueError('Non trusted string given.')

    def _trigger_value_comparison(self, operator_as_str, trig_val, checked_val):
        """
        Compares trigger value to checked value based on the operator.

        :return: (bool)
        """

        return self.OPERATORS_STR_MAP[operator_as_str](checked_val, trig_val)

    def _trig_attr_owner(self, trig_dct):
        """
        Determines trigger attribute owner.

        :return: (str) e.g. 'player', 'enemy_1', ..
        """
        if trig_dct['owner_type'] == 'player':
            return 'player'
        else:
            return self.current_enemy

    def _check_abilities_cond_triggers_state(self, cond_name):
        """
        Checks if ALL triggers for given condition are present.

        :return: (bool)
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
        :return: (None)
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

        :param modified_dct: It is the new dict given instead of the static class variable dict.
        :return: (None)
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

        :param mod_val: The value that is to be replaced, added, multiplied etc.
        :return: (literal)
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
        :param initial_dct: (dict) "ABILITIES_ATTRIBUTES['general_attributes']['w']", "ITEM_ATTRIBUTES['item_name']"
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
            x_formula = palette.TrustedStr(con_eff_dct['x_formula'])
            mod_val = self._unsafe_x_formula_to_value(x_formula=x_formula,
                                                      x_name=con_eff_dct['x_name'],
                                                      x_type=con_eff_dct['x_type'],
                                                      x_owner=con_eff_dct['x_owner'], )

        modified_dct[modified_attr_name] = self._modified_attr_value(
            mod_operation=mod_operation,
            mod_val=mod_val,
            old_val=modified_dct[modified_attr_name])

    @staticmethod
    def _check_condition_affects_object(searched_obj_name, cond_eff_dct):
        """
        Checks if object in condition dict is the one needed.

        :param searched_obj_name: str
        :param cond_eff_dct: dict
        :return: bool
        """
        return searched_obj_name == cond_eff_dct['obj_name']

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

        :return: (dict)
        """

        return self._attrs_or_effs_base(obj_name=ability_name,
                                        searched_obj_type='abilities_effects',
                                        initial_dct=self.ABILITIES_EFFECTS[ability_name],
                                        conditionals_dct=self.ABILITIES_CONDITIONALS)

    def items_effects(self, item_name):
        return self._attrs_or_effs_base(obj_name=item_name,
                                        searched_obj_type='items_effects',
                                        initial_dct=items_data_module.ITEMS_EFFECTS[item_name],
                                        conditionals_dct=items_data_module.ITEMS_CONDITIONALS[item_name])

    def item_attributes(self, item_name):
        return self._attrs_or_effs_base(obj_name=item_name,
                                        searched_obj_type='item_attr',
                                        initial_dct=items_data_module.ITEMS_EFFECTS[item_name],
                                        conditionals_dct=items_data_module.ITEMS_CONDITIONALS[item_name])

    def abilities_attributes(self, ability_name):
        """
        Checks if ability attributes are affected by any conditionals.
        If not, returns member variable dict. Otherwise returns different version of the dict.

        :return: (dict)
        """

        return self._attrs_or_effs_base(obj_name=ability_name,
                                        searched_obj_type='general_attributes',
                                        initial_dct=self.ABILITIES_ATTRIBUTES['general_attributes'][ability_name],
                                        conditionals_dct=self.ABILITIES_CONDITIONALS)

    def request_buff(self, buff_name):
        """
        Returns buff dict after checking possible conditionals.

        Buffs can be related to champion, item, mastery, summoner spells, dragon, baron.

        :return: (dict)
        """

        if buff_name in self.ABILITIES_ATTRIBUTES['buffs']:
            initial_dct = self.ABILITIES_ATTRIBUTES
            conditionals_dct = self.ABILITIES_CONDITIONALS

        elif buff_name in BUFFS_AND_DMGS_IMPLEMENTED_BY_METHODS:
            return getattr(self, buff_name)()

        elif buff_name in items_data_module.ITEMS_BUFFS_NAMES:
            item_name = items_data_module.ITEMS_BUFFS_NAMES_TO_ITEMS_NAMES_MAP[buff_name]
            initial_dct = items_data_module.ITEMS_ATTRIBUTES[item_name]
            conditionals_dct = items_data_module.ITEMS_CONDITIONALS[item_name]

        elif buff_name in SUMMONER_SPELLS_BUFFS_NAMES_TO_SPELL_MAP:
            spell_name = SUMMONER_SPELLS_BUFFS_NAMES_TO_SPELL_MAP[buff_name]
            return SummonerSpells.SUMMONER_SPELLS_ATTRIBUTES_BASE[spell_name]['buffs'][buff_name]

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

        :return: (dict)
        """

        if dmg_name in self.ABILITIES_ATTRIBUTES['dmgs']:
            initial_dct = self.ABILITIES_ATTRIBUTES
            conditionals_dct = self.ABILITIES_CONDITIONALS

        elif dmg_name in BUFFS_AND_DMGS_IMPLEMENTED_BY_METHODS:
            return getattr(self, dmg_name)()

        elif dmg_name in items_data_module.ITEMS_DMGS_NAMES:
            item_name = items_data_module.ITEMS_DMGS_NAMES_TO_ITEMS_NAMES_MAP[dmg_name]
            initial_dct = items_data_module.ITEMS_ATTRIBUTES[item_name]
            conditionals_dct = items_data_module.ITEMS_CONDITIONALS[item_name]

        elif dmg_name in SUMMONER_SPELLS_DMGS_NAMES_TO_SPELL_MAP:
            spell_name = SUMMONER_SPELLS_DMGS_NAMES_TO_SPELL_MAP[dmg_name]
            return SummonerSpells.SUMMONER_SPELLS_ATTRIBUTES_BASE[spell_name]['dmgs'][dmg_name]

        else:
            return getattr(self, dmg_name)()

        return self._attrs_or_effs_base(obj_name=dmg_name,
                                        searched_obj_type='dmgs',
                                        initial_dct=initial_dct['dmgs'][dmg_name],
                                        conditionals_dct=conditionals_dct)

    def create_castable_and_non_castable_spells_shortcuts(self):
        """
        Creates player's castable and not castable spells.

        WARNING: Assumes that conditionally castable spells are always set to `castable: True`
        and the conditional turns them off where needed.

        :return: (None)
        """
        self.castable_spells_shortcuts = set()
        self.not_castable_spells_shortcuts = set()

        for ability_name, ability_dct in self.ABILITIES_ATTRIBUTES['general_attributes'].items():

            if ability_name != 'inn':
                if ability_dct['castable']:
                    if self.ability_lvls_dct[ability_name]:

                        self.castable_spells_shortcuts.add(ability_name)
                        continue

                self.not_castable_spells_shortcuts.add(ability_name)


class SummonerSpells(ConditionalsTranslator):

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
                 _reversed_combat_mode):

        ConditionalsTranslator.__init__(self,
                                        ability_lvls_dct=ability_lvls_dct,
                                        champion_lvls_dct=champion_lvls_dct,
                                        selected_champions_dct=selected_champions_dct,
                                        action_on_cd_func=action_on_cd_func,
                                        max_targets_dct=max_targets_dct,
                                        max_combat_time=max_combat_time,
                                        initial_enemies_total_stats=initial_enemies_total_stats,
                                        initial_active_buffs=initial_active_buffs,
                                        initial_current_stats=initial_current_stats,
                                        chosen_items_dct=chosen_items_dct,
                                        selected_masteries_dct=selected_masteries_dct,
                                        enemies_originating_dmg_data=enemies_originating_dmg_data,
                                        _reversed_combat_mode=_reversed_combat_mode)

        self.summoner_spell_effects = None
        self._create_summoner_spell_effects()

    ALL_SUMMONER_SPELL_NAMES = ('smite', 'exhaust', 'ignite', 'heal', 'flash', 'ghost', 'teleport',
                                'clairvoyance', 'cleanse')

    ITEMS_MAKING_SMITE_CASTABLE = {items_data_module.ITEMS_NAMES['stalkers_blade'],
                                   items_data_module.ITEMS_NAMES['skirmishers_sabre']}

    _CASTABLE_SUMMONER_SPELLS_BASE = frozenset({'exhaust', 'ignite', 'heal', 'flash', 'ghost', 'teleport'})

    # Summoner spells that must ALWAYS be casted at the start of combat (ordered from highest to lowest priority)
    SUMMONER_SPELLS_AT_COMBAT_START_BY_PRIORITY = ('teleport',)

    def castable_summoner_spells(self):

        castable_summoner_spells = set()
        castable_summoner_spells.update(self._CASTABLE_SUMMONER_SPELLS_BASE)

        for item_name in self.ITEMS_MAKING_SMITE_CASTABLE:
            if item_name in self.player_items:
                castable_summoner_spells.add('smite')

        return castable_summoner_spells

    # -----------------------------------------------------------------------------------------------------------------
    # Ghost
    GHOST_SPEED_BUFF_NO_ENCHANTMENT = palette.SafeBuff({'buff_source': 'ghost',
                                                        'dot': False,
                                                        'duration': 10,
                                                        'max_stacks': 1,
                                                        'max_targets': 1,
                                                        'usual_max_targets': 1,
                                                        'on_hit': {},
                                                        'stats': {'move_speed': {'percent': {'stat_mods': {},
                                                                                             'stat_values': 0.27}}},
                                                        'target_type': 'player'})
    GHOST_SPEED_BUFF_WITH_ENCHANTMENT = copy.deepcopy(GHOST_SPEED_BUFF_NO_ENCHANTMENT)
    GHOST_SPEED_BUFF_WITH_ENCHANTMENT['stats']['move_speed']['percent']['stat_values'] = 0.4

    def ghost_speed_buff(self):
        if items_data_module.ITEMS_NAMES['enchantment_distortion'] in self.player_items:
            return self.GHOST_SPEED_BUFF_WITH_ENCHANTMENT
        else:
            return self.GHOST_SPEED_BUFF_NO_ENCHANTMENT

    # -----------------------------------------------------------------------------------------------------------------
    # Flash
    _FLASH_EFFECTS_WITH_DISTORTION_ENCHANTMENT = palette.frozen_keys_spell_effects()
    _FLASH_EFFECTS_WITH_DISTORTION_ENCHANTMENT['actives']['buffs'].append('move_speed_after_flash_buff')

    MOVE_SPEED_AFTER_FLASH_BUFF = palette.SafeBuff({'buff_source': 'flash',
                                                    'dot': False,
                                                    'duration': 1,
                                                    'max_stacks': 1,
                                                    'max_targets': 1,
                                                    'usual_max_targets': 1,
                                                    'on_hit': {},
                                                    'stats': {'move_speed': {'percent': {'stat_mods': {},
                                                                                         'stat_values': 0.2}}},
                                                    'target_type': 'player',
                                                    'prohibit_cd_start': {}})

    def move_speed_after_flash_buff(self):
        return self.MOVE_SPEED_AFTER_FLASH_BUFF

    def _flash_effects_dct(self):
        if items_data_module.ITEMS_NAMES['enchantment_distortion'] in self.player_items:
            return self._FLASH_EFFECTS_WITH_DISTORTION_ENCHANTMENT
        else:
            return {}

    # -----------------------------------------------------------------------------------------------------------------
    # Teleport
    _TELEPORT_EFFECTS_WITH_DISTORTION_ENCHANTMENT = {
        'actives': {'buffs': ['teleport_distortion_speed_buff'],
                    'dmg': [],
                    'remove_buff': []},
        'passives': {'buffs': [],
                     'dmg': [],
                     'remove_buff': []}
    }

    _TELEPORT_EFFECTS_WITH_HOMEGUARD_ENCHANTMENT = {
        'actives': {'buffs': ['teleport_homeguard_speed_buff'],
                    'dmg': [],
                    'remove_buff': []},
        'passives': {'buffs': [],
                     'dmg': [],
                     'remove_buff': []}
    }

    _TELEPORT_EFFECTS_NO_ENCHANTMENT = {}

    def _teleport_effects_dct(self):

        if items_data_module.ITEMS_NAMES['enchantment_homeguard'] in self.player_items:
            return self._TELEPORT_EFFECTS_WITH_HOMEGUARD_ENCHANTMENT

        elif items_data_module.ITEMS_NAMES['enchantment_distortion'] in self.player_items:
            return self._TELEPORT_EFFECTS_WITH_DISTORTION_ENCHANTMENT

        else:
            return self._SMITE_EFFECTS_NO_AFFECTING_ITEM

    # -----------------------------------------------------------------------------------------------------------------
    # Smite
    _SMITE_EFFECTS_WITH_SKIRMISHER_ITEM = {
        'actives': {'buffs': ['smite_skirmisher_initiator_buff', 'smite_skirmisher_mark_buff'],
                    'dmg': [],
                    'remove_buff': []},
        'passives': {'buffs': [],
                     'dmg': [],
                     'remove_buff': []}
    }

    _SMITE_EFFECTS_WITH_STALKER_ITEM = {
        'actives': {'buffs': ['chilling_smite_slow_buff'],
                    'dmg': ['chilling_smite_dmg'],
                    'remove_buff': []},
        'passives': {'buffs': [],
                     'dmg': [],
                     'remove_buff': []}
    }

    _SMITE_EFFECTS_NO_AFFECTING_ITEM = {}

    def _smite_effects_dct(self):

        if items_data_module.ITEMS_NAMES['skirmishers_sabre'] in self.player_items:
            return self._SMITE_EFFECTS_WITH_SKIRMISHER_ITEM

        elif items_data_module.ITEMS_NAMES['stalkers_blade'] in self.player_items:
            return self._SMITE_EFFECTS_WITH_STALKER_ITEM

        else:
            return self._SMITE_EFFECTS_NO_AFFECTING_ITEM

    # -----------------------------------------------------------------------------------------------------------------
    # Ignite
    IGNITE_TICKS = 6
    IGNITE_DURATION = 5

    # Duration is set independently for each usage of it, since multiple effects can cause this buff.
    _GRIEVOUS_WOUNDS_BUFF_BASE = palette.SafeBuff({'buff_source': placeholder,
                                                   'dot': False,
                                                   'duration': placeholder,
                                                   'max_stacks': 1,
                                                   'max_targets': 1,
                                                   'usual_max_targets': 1,
                                                   'on_hit': {},
                                                   'stats': {'percent_healing_reduction': {'additive': {'stat_mods': {},
                                                                                                        'stat_values': 0.5}}},
                                                   'target_type': 'enemy',
                                                   'prohibit_cd_start': {}})
    _GRIEVOUS_WOUNDS_BUFF_BASE.delete_keys(['buff_source', 'duration'])

    IGNITE_GRIEVOUS_WOUNDS_BUFF = {}
    IGNITE_GRIEVOUS_WOUNDS_BUFF.update(_GRIEVOUS_WOUNDS_BUFF_BASE)
    IGNITE_GRIEVOUS_WOUNDS_BUFF.update({'buff_source': 'ignite'})
    IGNITE_GRIEVOUS_WOUNDS_BUFF.update({'duration': IGNITE_DURATION})

    def ignite_grievous_wounds_buff(self):
        return self.IGNITE_GRIEVOUS_WOUNDS_BUFF

    # -----------------------------------------------------------------------------------------------------------------
    # ATTRIBUTES

    SUMMONER_SPELLS_ATTRIBUTES_BASE = {
            'ignite': {'general_attributes': {'base_cd': 210,
                                              'cast_time': 0,
                                              'castable': True,
                                              'channel_time': None,
                                              'dashed_distance': None,
                                              'independent_cast': True,
                                              'move_while_casting': True,
                                              'range': 500,
                                              'resets_aa': False,
                                              'toggled': False,
                                              'travel_time': None},
                       'buffs': {'ignite_dot_buff': {'buff_source': 'ignite',
                                                     'dot': {'always_on_x_targets': 0,
                                                             'dmg_names': ['ignite_dmg'],
                                                             'period': IGNITE_DURATION/IGNITE_TICKS},
                                                     'duration': IGNITE_DURATION,
                                                     'max_stacks': 1,
                                                     'max_targets': 1,
                                                     'usual_max_targets': 1,
                                                     'on_hit': {},
                                                     'stats': {},
                                                     'target_type': 'enemy'},
                                 'ignite_grievous_wounds_buff': 'expressed_by_method'},
                       'dmgs': {'ignite_dmg': {'crit_type': None,
                                               'delay': None,
                                               'dmg_category': 'standard_dmg',
                                               'dmg_source': 'ignite',
                                               'dmg_type': 'true',
                                               'dmg_values': 50/IGNITE_TICKS,
                                               'dot': {'buff_name': 'ignite_dot_buff'},
                                               'heal_for_dmg_amount': False,
                                               'life_conversion_type': None,
                                               'max_targets': 1,
                                               'mods': {'enemy': {},
                                                        'player': {'champion_lvl': {'additive': 20/IGNITE_TICKS}}},
                                               'radius': None,
                                               'resource_type': 'hp',
                                               'target_type': 'enemy',
                                               'usual_max_targets': 1}}},
            'exhaust': {'general_attributes': {'base_cd': 210,
                                               'cast_time': 0,
                                               'castable': True,
                                               'channel_time': None,
                                               'dashed_distance': None,
                                               'independent_cast': True,
                                               'move_while_casting': True,
                                               'range': 500,
                                               'resets_aa': False,
                                               'toggled': False,
                                               'travel_time': None},
                        'buffs': {'exhaust_buff': {'buff_source': 'exhaust',
                                                   'dot': False,
                                                   'duration': 2.5,
                                                   'max_stacks': 1,
                                                   'max_targets': 1,
                                                   'usual_max_targets': 1,
                                                   'on_hit': {},
                                                   'stats': {'flat_armor_reduction': {'additive': {'stat_mods': {},
                                                                                                   'stat_values': 10}},
                                                             'flat_magic_reduction': {'additive': {'stat_mods': {},
                                                                                                   'stat_values': 10}}},
                                                   'target_type': 'enemy'}},
                        'dmgs': {}},
            'clairvoyance': {'general_attributes': {'castable': False},
                             'dmgs': {},
                             'buffs': {}},
            'smite': {'general_attributes': {'castable': False},
                      'dmgs': {'chilling_smite_dmg': {'crit_type': None,
                                                      'delay': None,
                                                      'dmg_category': 'standard_dmg',
                                                      'dmg_source': 'smite',
                                                      'dmg_type': 'true',
                                                      'dmg_values': 20,
                                                      'dot': {},
                                                      'heal_for_dmg_amount': False,
                                                      'life_conversion_type': 'lifesteal',
                                                      'max_targets': 1,
                                                      'mods': {'enemy': {},
                                                               'player': {'champion_lvl': {'additive': 8}}},
                                                      'radius': None,
                                                      'resource_type': 'hp',
                                                      'target_type': 'enemy',
                                                      'usual_max_targets': 1},
                               'challenging_smite_dot_dmg': {'crit_type': None,
                                                             'delay': None,
                                                             'dmg_category': 'standard_dmg',
                                                             'dmg_source': 'smite',
                                                             'dmg_type': 'true',
                                                             'dmg_values': 18,
                                                             'dot': {'buff_name': 'challenging_smite_dot_buff'},
                                                             'heal_for_dmg_amount': False,
                                                             'life_conversion_type': 'lifesteal',
                                                             'max_targets': 1,
                                                             'mods': {'enemy': {},
                                                                      'player': {'champion_lvl': {'additive': 2}}},
                                                             'radius': None,
                                                             'resource_type': 'hp',
                                                             'target_type': 'enemy',
                                                             'usual_max_targets': 1}},
                      'buffs': {'challenging_smite_mark_buff': {'buff_source': 'smite',
                                                                'dot': False,
                                                                'duration': 4,
                                                                'max_stacks': 1,
                                                                'max_targets': 1,
                                                                'usual_max_targets': 1,
                                                                'on_hit': {},
                                                                'stats': {},
                                                                'target_type': 'enemy',
                                                                'prohibit_cd_start': {},
                                                                'on_being_hit': {'apply_buff': ['challenging_smite_dot_buff'],
                                                                                 'cause_dmg': [],
                                                                                 'cds_modified': {},
                                                                                 'remove_buff': []}},
                                'challenging_smite_dot_buff': {'buff_source': 'smite',
                                                               'dot': False,
                                                               'duration': 4,
                                                               'max_stacks': 1,
                                                               'max_targets': 1,
                                                               'usual_max_targets': 1,
                                                               'on_hit': {},
                                                               'stats': {},
                                                               'target_type': 'enemy',
                                                               'prohibit_cd_start': {}
                                                               }}},
            'cleanse': {'general_attributes': {'castable': False},
                        'dmgs': {},
                        'buffs': {}},
            'flash': {'general_attributes': {'base_cd': 300,
                                             'cast_time': 0,
                                             'castable': True,
                                             'channel_time': None,
                                             'dashed_distance': 450,
                                             'independent_cast': True,
                                             'move_while_casting': True,
                                             'range': 450,
                                             'resets_aa': False,
                                             'toggled': False,
                                             'travel_time': None},
                      'dmgs': {},
                      'buffs': {}},
            'teleport': {'general_attributes': {'castable': False},
                         'dmgs': {},
                         'buffs': {}},
            'clarity': {'general_attributes': {'base_cd': 180,
                                               'cast_time': 0,
                                               'castable': True,
                                               'channel_time': None,
                                               'dashed_distance': None,
                                               'independent_cast': True,
                                               'move_while_casting': True,
                                               'range': 500,
                                               'resets_aa': False,
                                               'toggled': False,
                                               'travel_time': None},
                        'dmgs': {'clarity_mana_regen': {'crit_type': None,
                                                        'delay': None,
                                                        'dmg_category': 'standard_dmg',
                                                        'dmg_source': 'clarity',
                                                        'dmg_type': 'true',
                                                        'dmg_values': 0,
                                                        'dot': False,
                                                        'heal_for_dmg_amount': False,
                                                        'life_conversion_type': None,
                                                        'max_targets': 1,
                                                        'mods': {'enemy': {},
                                                                 'player': {'mp': {'additive': -0.4}}},
                                                        'radius': None,
                                                        'resource_type': 'mp',
                                                        'target_type': 'player',
                                                        'usual_max_targets': 1}},
                        'buffs': {}},
            'ghost': {'general_attributes': {'base_cd': 210,
                                             'cast_time': 0,
                                             'castable': True,
                                             'channel_time': None,
                                             'dashed_distance': None,
                                             'independent_cast': True,
                                             'move_while_casting': True,
                                             'range': 500,
                                             'resets_aa': False,
                                             'toggled': False,
                                             'travel_time': None},
                      'buffs': {'ghost_buff': 'expressed_by_method'},
                      'dmgs': {}},
        }

    SUMMONER_SPELLS_BUFFS_AND_DMGS_IMPLEMENTED_BY_METHODS = set()
    for item_name in SUMMONER_SPELLS_ATTRIBUTES_BASE:
        for buff_name in SUMMONER_SPELLS_ATTRIBUTES_BASE[item_name]['buffs']:
            if SUMMONER_SPELLS_ATTRIBUTES_BASE[item_name]['buffs'][buff_name] == 'expressed_by_method':
                SUMMONER_SPELLS_BUFFS_AND_DMGS_IMPLEMENTED_BY_METHODS.add(buff_name)
        for dmg_name in SUMMONER_SPELLS_ATTRIBUTES_BASE[item_name]['dmgs']:
            if SUMMONER_SPELLS_ATTRIBUTES_BASE[item_name]['dmgs'][dmg_name] == 'expressed_by_method':
                SUMMONER_SPELLS_BUFFS_AND_DMGS_IMPLEMENTED_BY_METHODS.add(dmg_name)

    # ---------------------------------------------------------------------------------------------------------------------
    # EFFECTS

    _SUMMONER_SPELLS_EFFECTS_BASE = {
        'ignite': {'actives': {'buffs': ['ignite_dot_buff', 'ignite_grievous_wounds_buff'],
                               'dmg': [],
                               'remove_buff': []},
                   'passives': {'buffs': [],
                                'dmg': [],
                                'remove_buff': []}},
        'exhaust': {'actives': {'buffs': ['exhaust_buff'],
                                'dmg': [],
                                'remove_buff': []},
                    'passives': {'buffs': [],
                                 'dmg': [],
                                 'remove_buff': []}},
        'clarity': {'actives': {'buffs': [],
                                'dmg': ['clarity_mana_regen'],
                                'remove_buff': []},
                    'passives': {'buffs': [],
                                 'dmg': [],
                                 'remove_buff': []}},
        'clairvoyance': {},
        'ghost': {'actives': {'buffs': ['ghost_speed_buff'],
                              'dmg': [],
                              'remove_buff': []},
                  'passives': {'buffs': [],
                               'dmg': [],
                               'remove_buff': []}},
    }

    def _create_summoner_spell_effects(self):
        self.summoner_spell_effects = {
            'teleport': self._teleport_effects_dct(),
            'smite': self._smite_effects_dct(),
            'flash': self._flash_effects_dct(),
        }

        self.summoner_spell_effects.update(self._SUMMONER_SPELLS_EFFECTS_BASE)


BUFFS_AND_DMGS_IMPLEMENTED_BY_METHODS.update(SummonerSpells.SUMMONER_SPELLS_BUFFS_AND_DMGS_IMPLEMENTED_BY_METHODS)

SUMMONER_SPELLS_BUFFS_NAMES_TO_SPELL_MAP = palette.items_or_masteries_buffs_or_dmgs_names_dct(
    str_buffs_or_dmgs='buffs', attrs_dct=SummonerSpells.SUMMONER_SPELLS_ATTRIBUTES_BASE)
SUMMONER_SPELLS_BUFFS_NAMES = palette.XToX(seq=SUMMONER_SPELLS_BUFFS_NAMES_TO_SPELL_MAP)

SUMMONER_SPELLS_DMGS_NAMES_TO_SPELL_MAP = palette.items_or_masteries_buffs_or_dmgs_names_dct(
    str_buffs_or_dmgs='dmgs', attrs_dct=SummonerSpells.SUMMONER_SPELLS_ATTRIBUTES_BASE)
SUMMONER_SPELLS_DMGS_NAMES = palette.XToX(seq=SUMMONER_SPELLS_DMGS_NAMES_TO_SPELL_MAP)


class Actions(SummonerSpells, timers.Timers, runes.RunesFinal, metaclass=abc.ABCMeta):

    AA_COOLDOWN = 0.4   # TODO: replace functionality with 'wind_up'
    ACTION_DELAY = 0.1

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
        self.reversed_precombat_player_stats = {}
        self.reversed_precombat_enemy_buffs = {}
        self._applied_dmgs = {}
        self._reverse_rotation_copy = self.rotation_lst[::-1]

        runes.RunesFinal.__init__(self,
                                  player_lvl=champion_lvls_dct['player'],
                                  selected_runes=selected_runes)

        SummonerSpells.__init__(self,
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

    @abc.abstractmethod
    def activate_rage_speed_buff(self):
        pass

    @abc.abstractmethod
    def activate_liandrys(self):
        pass

    @abc.abstractmethod
    def activate_spellblade(self):
        pass

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

        Cd_end can be set to a value lower than cast_start which is incorrect,
        but should have no effect at all.

        :return: (None)
        """

        for action_time in sorted(self.actions_dct, reverse=True):
            action_dct = self.actions_dct[action_time]
            if action_dct['action_name'] == action_name:

                # (if the spell has been casted before, the loop ends)
                if action_dct['cd_end'] > self.current_time:

                    # (it will reduce or "reset" cd end)
                    if reduction_value == 'reset':
                        action_dct['cd_end'] = 0
                    else:
                        action_dct['cd_end'] -= reduction_value

                    return

    def _target_of_dmg_by_name(self, dmg_name):
        tar_type_of_dmg = self.request_dmg(dmg_name=dmg_name)['target_type']
        return self.player_or_current_enemy(tar_type=tar_type_of_dmg)

    def _target_of_buff_by_name(self, buff_name):
        tar_type_of_buff = self.request_buff(buff_name=buff_name)['target_type']
        return self.player_or_current_enemy(tar_type=tar_type_of_buff)

    def max_time_exceeded(self):
        if self.current_time > self.max_combat_time:
            return True
        else:
            return False

    def all_dead_or_max_time_exceeded(self):
        if self.all_enemies_dead() or self.max_time_exceeded():
            return True
        else:
            return False

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

    def remove_buff_end(self, buff_name):
        """
        Removes buff_end from events.

        :param buff_name:
        :return: (None)
        """
        for event_time in sorted(self.events):
            events_at_given_time = self.events[event_time]

            for list_num, event_dict in enumerate(events_at_given_time):
                event_type = event_dict['event_type']
                event_name = event_dict['event_name']

                if event_type == 'buff_end':
                    if event_name == buff_name:
                        del events_at_given_time[list_num]
                        return

    def remove_buff(self, tar_name, buff_name, buff_dct=None):
        """
        Removes a buff from target's active buffs.

        Additionally removes buff's-end.
        The alternative would be to ignore buff-end if the buff doesn't exist but this could cause bugs.
        (e.g. if buff_1 is removed but its end isn't,
        a further application of buff_1 can be accidentally removed because of the obsolete buff-end)

        :param tar_name:
        :param buff_name:
        :param buff_dct: Optional argument, used for performance when buff dict has been previously called.
        :return: (None)
        """

        # CD CHANGES BEFORE REMOVAL
        if tar_name == 'player':
            # (requests buff dict if not given)
            if not buff_dct:
                buff_dct = self.request_buff(buff_name=buff_name)

            self.change_action_cd_before_buff_removal(buff_dct=buff_dct)

        # REMOVAL OF BUFF
        del self.active_buffs[tar_name][buff_name]

        # REMOVAL OF BUFF-END
        # (..that possibly could follow;
        # used when buffs are prematurely removed e.g. by on_x effects)
        self.remove_buff_end(buff_name=buff_name)

    def remove_one_stack_from_buff(self, buff_owner, buff_name):
        """
        Removes a buff's stack. If it's stacks are to become 0, it removes the buff instead.

        :return: (None)
        """

        current_stacks = self.active_buffs[buff_owner][buff_name]['current_stacks']
        if current_stacks > 1:
            self.active_buffs[buff_owner][buff_name]['current_stacks'] = current_stacks - 1
        else:
            self.remove_buff(tar_name=buff_owner, buff_name=buff_name)

    def apply_action_cost(self, action_name):
        """
        Deducts the cost of an action (resource and/or buff stack).

        WARNING: Costs are applied separately from the rest of the events. This might potentially cause bugs!

        :return: (None)
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
                self.remove_one_stack_from_buff(buff_owner='player', buff_name=cost_name)

    def _last_action_cast_start(self):
        return max(self.actions_dct)

    def _last_action_name(self):
        """
        Returns name of last action casted. If no action has been casted yet, it returns None.

        :return: (str) (None)
        """

        if self.actions_dct:
            last_action_name = self.actions_dct[self._last_action_cast_start()]['action_name']

            return last_action_name

        else:
            return None

    # MOVEMENT
    def between_action_walking(self):
        """
        Calculates movement between actions and adds them to distance player moved.

        :return: (None)
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

    def add_action_cast_end_in_events(self, event_time, event_name):
        self.add_single_event(event_time=event_time,
                              event_name=event_name,
                              event_type='action_cast_end',
                              event_target='player')

    def add_action_channel_end_in_events(self, event_time, event_name):
        self.add_single_event(event_time=event_time,
                              event_name=event_name,
                              event_type='action_channel_end',
                              event_target='player')

    def add_buff_end_in_events(self, buff_end_time, buff_name, tar_name):
        self.add_single_event(event_time=buff_end_time,
                              event_name=buff_name,
                              event_type='buff_end',
                              event_target=tar_name)

    def old_buff_end_in_events(self, buff_name, tar_name):
        """
        Searches events for given buff's end time.

        :return: (float) Buff end time.
        """

        for event_time in self.events:
            events_lst = self.events[event_time]

            for event_dct in events_lst:
                if (event_dct['event_name'] == buff_name) and (event_dct['target_name'] == tar_name):
                    return event_time

    def change_buff_duration_in_events(self, new_end_time, buff_name, tar_name):
        """
        Removes old buff end event, and creates a new event.

        :return: (None)
        """

        # DEL OLD BUFF-END EVENT
        self.remove_buff_end(buff_name=buff_name)

        # INSERT NEW EVENT
        self.add_buff_end_in_events(buff_end_time=new_end_time, buff_name=buff_name, tar_name=tar_name)

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

            self.actions_dct[cast_start].update({'channel_end': channel_end_time})

        # Checks if ability resets AA's cd_end, and applies it.
        self.check_and_reset_aa_cd(action_attrs_dct=action_attrs_dct)

    def _add_new_action(self, action_name):
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
            item_attrs_dct = items_data_module.ITEMS_ATTRIBUTES[action_name]['general_attributes']
            self._add_new_spell_or_item_action(action_name=action_name, action_attrs_dct=item_attrs_dct,
                                               cast_start=cast_start, str_spell_or_item='item')

        elif action_name == 'action_delayer':
            self.add_action_cast_end_in_events(event_time=self.current_time + self.ACTION_DELAY, event_name=action_name)
            # (rest of method is redundant since only cast end in events is needed as a marker to retry action cast)
            return

        # SUMMONER SPELLS
        else:
            # (cast_end is the same as cast_start)
            # (summoner spells have too high cooldowns, so they are set to a high value)
            self.actions_dct.update({cast_start: dict(
                cast_end=cast_start,
                cd_end=300,
                action_name=action_name)})

        # MODIFIES EVENTS
        action_dct = self.actions_dct[cast_start]

        # (if it is channeled, cast_end is ignored,
        # since only the time after which the action is castable again is needed in events)
        if 'channel_end' in action_dct:
            self.add_action_channel_end_in_events(event_time=action_dct['channel_end'], event_name=action_name)
        else:
            self.add_action_cast_end_in_events(event_time=action_dct['cast_end'], event_name=action_name)

    def add_new_action_and_movement_since_previous_action(self, action_name):
        self._add_new_action(action_name=action_name)

        # (adds movement distance)
        self.between_action_walking()

    def _add_new_buff(self, buff_name, buff_attrs_dct, tar_name, initial_stacks_increment=1):
        """
        Inserts a new buff in active_buffs dictionary.

        :param buff_attrs_dct: Dict containing all buff attributes (e.g. duration, on_hit etc)
        :return: (None)
        """

        tar_active_buffs = self.active_buffs[tar_name]

        # Inserts the new buff.
        tar_active_buffs.update(
            {buff_name: dict(
                starting_time=self.current_time)})

        buff_dct_in_active_buffs = tar_active_buffs[buff_name]

        # DURATION
        # If non permanent buff.
        if buff_attrs_dct['duration'] != 'permanent':

            buff_end = self.current_time + self.buff_duration(buff_dct=buff_attrs_dct)
            # ..creates and inserts its duration.
            buff_dct_in_active_buffs.update(dict(
                ending_time=buff_end))

            # (non permanent buff's end is also noted in events)
            self.add_buff_end_in_events(buff_end_time=buff_end, buff_name=buff_name, tar_name=tar_name)

        else:
            # ..otherwise sets its duration to 'permanent'.
            buff_dct_in_active_buffs.update(dict(
                ending_time='permanent'))

        # STACKS
        buff_dct_in_active_buffs.update(dict(current_stacks=initial_stacks_increment))

        # SHIELD
        if 'shield' in buff_attrs_dct:
            shield_attrs_dct = buff_attrs_dct['shield']
            if shield_attrs_dct:

                initial_shield_value = self.shield_or_dmg_value_after_mods(dmg_or_shield_dct=shield_attrs_dct,
                                                                           mods_dct=shield_attrs_dct['shield_mods'],
                                                                           value=shield_attrs_dct['shield_value'])

                shield_type = shield_attrs_dct['shield_type']

                buff_dct_in_active_buffs.update({'shield': {'shield_type': shield_type,
                                                            'shield_value': initial_shield_value}})

        # ON-NTH
        if 'every_nth_hit' in buff_attrs_dct:
            every_nth_dct = buff_attrs_dct['every_nth_hit']

            if every_nth_dct:
                self.insert_nth_related_in_actives_buffs(every_nth_dct=every_nth_dct,
                                                         buff_dct_in_active_buffs=buff_dct_in_active_buffs)

    def _refresh_already_active_buff(self, buff_name, buff_dct, tar_name, stack_increment=1):
        """
        Changes an existing buff in active_buffs dictionary,
        by refreshing its duration and increasing its stacks.

        :return: (None)
        """

        tar_buff_dct_in_act_buffs = self.active_buffs[tar_name][buff_name]

        # DURATION
        # If non permanent buff, refreshes its duration.
        if buff_dct['duration'] != 'permanent':

            tar_buff_dct_in_act_buffs['ending_time'] = self.current_time + buff_dct['duration']

            self.change_buff_duration_in_events(new_end_time=tar_buff_dct_in_act_buffs['ending_time'],
                                                buff_name=buff_name,
                                                tar_name=tar_name)

        # STACKS
        # If max_stacks have not been reached..
        if tar_buff_dct_in_act_buffs['current_stacks'] < buff_dct['max_stacks']:

            # ..adds +1 to the stacks (unless increment is different).
            tar_buff_dct_in_act_buffs['current_stacks'] += stack_increment

            # Ensures max_stacks aren't exceeded for stack_increments larger than 1.
            if stack_increment > 1:

                if tar_buff_dct_in_act_buffs['current_stacks'] > buff_dct['max_stacks']:
                    # If max_stacks exceeded, set to max_stacks.
                    tar_buff_dct_in_act_buffs['current_stacks'] = buff_dct['max_stacks']

    def _add_buff_on_single_target(self, buff_name, buff_dct, tar_name, initial_stacks_increment, stack_increment):

        # NEW BUFF
        if buff_name not in self.active_buffs[tar_name]:

            self._add_new_buff(buff_name=buff_name,
                               buff_attrs_dct=buff_dct,
                               tar_name=tar_name,
                               initial_stacks_increment=initial_stacks_increment)

            # Dot
            buff_dot_dct = buff_dct['dot']
            # If the buff is a dot, applies dmg event as well.
            if buff_dot_dct:
                dmg_dot_names = buff_dot_dct['dmg_names']
                for dmg_name in dmg_dot_names:
                    first_tick = self.first_dot_tick(current_time=self.current_time, dmg_name=dmg_name)

                    tar_of_dmg = self._target_of_dmg_by_name(dmg_name=dmg_name)
                    self.add_events(effect_name=dmg_name, start_time=first_tick, tar_name=tar_of_dmg)

        # EXISTING BUFF
        else:
            self._refresh_already_active_buff(buff_name=buff_name,
                                              buff_dct=buff_dct,
                                              tar_name=tar_name,
                                              stack_increment=stack_increment)

    def add_buff(self, buff_name, tar_name, stack_increment=1, initial_stacks_increment=1):
        """
        Adds a new buff or refreshes an existing buff (duration and stacks), on all targets.

        Additionally, checks if buff applied is a dot buff and adds periodic event (unless dot already active).

        :return: (None)
        """

        buff_dct = self.req_buff_dct_func(buff_name=buff_name)

        self._add_buff_on_single_target(buff_name=buff_name,
                                        buff_dct=buff_dct,
                                        tar_name=tar_name,
                                        initial_stacks_increment=initial_stacks_increment,
                                        stack_increment=stack_increment)
        self.targets_already_buffed = 1

        # AOE BUFF
        # (Aoe can only be applied to enemies.)

        # No aoe will be applied by dmgs originating from reverse combat mode.
        if self._reversed_combat_mode:
            return

        # External max targets.
        if buff_name in self.max_targets_dct:
            max_tars_val = self.max_targets_dct[buff_name]

        # (Aoe buff has 'max_targets' in buff dct. It can also additionally have externally set max_targets.)
        else:
            max_tars_val = buff_dct['usual_max_targets']
            if max_tars_val == 'unlimited':
                # If targets are unlimited applies to everyone.
                max_tars_val = len(self.enemy_target_names)

        # While the last target number is less than max targets, adds event.
        prev_enemy = tar_name
        while self.targets_already_buffed < max_tars_val:

            next_enemy = self.next_alive_enemy(current_tar=prev_enemy)
            if next_enemy is None:
                break

            self._add_buff_on_single_target(buff_name=buff_name,
                                            buff_dct=buff_dct,
                                            tar_name=next_enemy,
                                            initial_stacks_increment=initial_stacks_increment,
                                            stack_increment=stack_increment)

            prev_enemy = next_enemy

    def change_action_cd_before_buff_removal(self, buff_dct):
        """
        Refreshes the cd expiration of corresponding action if given buff prohibits its cd.

        (e.g. Jax w_buff delays start of W cd)

        :return: (None)
        """

        if 'prohibit_cd_start' in buff_dct:
            prohibit_cd_start_val = buff_dct['prohibit_cd_start']

            # Checks if buff delays the start of an action's cd.
            if prohibit_cd_start_val:

                # Finds the affected action..
                for action_time in sorted(self.actions_dct, reverse=True):
                    if self.actions_dct[action_time]['action_name'] == prohibit_cd_start_val:

                        # .. and applies the new cd.
                        ability_cd = self.ability_cooldown(ability_name=self.actions_dct[action_time]['action_name'],
                                                           stats_function=self.request_stat)
                        self.actions_dct[action_time]['cd_end'] = ability_cd + self.current_time

                        break

    def _remove_expired_buffs(self):
        """
        Removes all expired buffs.

        :return: (None)
        """

        for tar_name in self.all_target_names:
            tar_act_buffs = self.active_buffs[tar_name]

            for buff_name in sorted(tar_act_buffs):
                tar_buff_dct_in_act_buffs = tar_act_buffs[buff_name]

                if tar_buff_dct_in_act_buffs['ending_time'] == 'permanent':
                    continue

                elif tar_buff_dct_in_act_buffs['ending_time'] < self.current_time:
                    self.remove_buff(tar_name=tar_name, buff_name=buff_name)

    def remove_expired_buffs_and_refresh_bonuses(self):
        """
        Buffs and bonuses must be refreshed after an event has been applied.

        :return: (None)
        """

        self._remove_expired_buffs()
        self.refresh_stats_bonuses()

    # ON_X_EFFECTS
    def _apply_on_x_effects(self, on_x_dct):
        """
        Applies on x effects. X can be "on_action", "on_hit", "on_being_hit", "on_dealing_dmg" etc.

        Effects applied can be dmg and buffs application, buff removal, or cd modification.

        Iterates throughout all active buffs, and applies:
            -on_hit dmg (e.g. Warwick's innate dmg),
            -on_hit buffs (e.g. Black Cleaver armor reduction),
            -and finally removes buffs that are removed on hit.

        :return: (None)
        """
        # DMG CAUSED ON HIT.
        for dmg_name in on_x_dct['cause_dmg']:

            tar_of_dmg = self._target_of_dmg_by_name(dmg_name=dmg_name)
            # (only_temporary_dots is irrelevant below since there are no on-hit dmgs that cause permanent dots)
            self._apply_dmg_event(event_name=dmg_name, event_target=tar_of_dmg, only_temporary_dots=False)

        # BUFFS APPLIED ON HIT.
        for buff_applied_on_hit in on_x_dct['apply_buff']:
            tar_type = self.request_buff(buff_name=buff_applied_on_hit)['target_type']
            tar_name = self.player_or_current_enemy(tar_type=tar_type)
            self.add_buff(buff_name=buff_applied_on_hit, tar_name=tar_name)

        # BUFFS REMOVED ON HIT.
        for buff_removed_on_hit in on_x_dct['remove_buff']:
            removed_buff_dct = self.request_buff(buff_name=buff_removed_on_hit)
            tar_type = removed_buff_dct['target_type']
            tar_name = self.player_or_current_enemy(tar_type=tar_type)
            self.remove_buff(tar_name=tar_name, buff_name=buff_removed_on_hit, buff_dct=removed_buff_dct)
            self.remove_event(tar_name=tar_name, event_name=buff_removed_on_hit)

        # MODIFIED CDS.
        cds_modifications_dct = on_x_dct['cds_modified']
        for modified_action_cd_name in cds_modifications_dct:
            reduction_value = cds_modifications_dct[modified_action_cd_name]
            self.reduce_action_cd(action_name=modified_action_cd_name, reduction_value=reduction_value)

    def apply_on_x_effects_of_single_buff(self, buff_dct, x_eff_name):
        """
        :param x_eff_name: "on_action", "on_hit", "on_being_hit", "on_dealing_dmg" etc.
        :return: (None)
        """

        if x_eff_name in buff_dct:
            on_x_dct = buff_dct[x_eff_name]

            if on_x_dct:
                self._apply_on_x_effects(on_x_dct=on_x_dct)

    def apply_on_hit_effects(self):
        # If a buff is removed on-hit and has on-hit effects of its own,
        # the "secondary" on-hit effects will be applied.
        for buff_name in sorted(self.active_buffs['player']):
            buff_dct = self.req_buff_dct_func(buff_name=buff_name)

            # Contrary to above comment, n-th type buffs that were removed by a on-hit effect will be ignored.
            if buff_name in self.active_buffs['player']:
                self.apply_or_update_nth(buff_name=buff_name, buff_dct=buff_dct)

            self.apply_on_x_effects_of_single_buff(buff_dct=buff_dct, x_eff_name='on_hit')

    def apply_on_being_hit_effects(self, target_name):
        for buff_name in sorted(self.active_buffs[target_name]):
            buff_dct = self.req_buff_dct_func(buff_name=buff_name)

            self.apply_on_x_effects_of_single_buff(buff_dct=buff_dct, x_eff_name='on_being_hit')

    @staticmethod
    def _dmg_type_matches_expected_type(given_dmg_type, on_dealing_dmg_dct):
        dmg_type_expected = on_dealing_dmg_dct['dmg_type']

        if dmg_type_expected == 'any':
            return True
        elif dmg_type_expected == given_dmg_type:
            return True
        # If type doesn't match expected, skips this buff.
        else:
            return False

    @staticmethod
    def _dmg_source_matches_expected_source(given_source, on_dealing_dmg_dct):
        sources_expected_lst = on_dealing_dmg_dct['source_types_or_names']

        for expected_source_name in sources_expected_lst:

            if expected_source_name == 'any':
                return True
            elif expected_source_name == given_source:
                return True
            elif (expected_source_name == 'champion_ability') and (given_source in palette.ALL_POSSIBLE_ABILITIES_SHORTCUTS):
                return True
            elif (expected_source_name == 'champion_spell') and (given_source in palette.ALL_POSSIBLE_SPELL_SHORTCUTS):
                return True
            elif (expected_source_name == 'item') and (given_source in palette.ALL_POSSIBLE_SPELL_SHORTCUTS):
                return True

        # If non of the expected sources matches given source:
        return False

    def apply_on_dealing_dmg_effects(self, given_dmg_type, given_source):

        for buff in self.active_buffs['player']:
            buff_dct = self.request_buff(buff_name=buff)

            if 'on_dealing_dmg' in buff_dct:
                on_dealing_dmg_dct = buff_dct['on_dealing_dmg']

                if on_dealing_dmg_dct:
                    # DMG TYPE
                    if not self._dmg_type_matches_expected_type(given_dmg_type=given_dmg_type, on_dealing_dmg_dct=on_dealing_dmg_dct):
                        continue

                    # DMG SOURCE
                    if not self._dmg_source_matches_expected_source(given_source=given_source, on_dealing_dmg_dct=on_dealing_dmg_dct):
                        continue

    @staticmethod
    def _causes_of_death_match_expected(dmgs_that_caused_death, on_enemy_death_dct):
        expected_causes_of_death = on_enemy_death_dct['causes_of_death']

        if 'any' in expected_causes_of_death:
            return True

        for expected_cause in expected_causes_of_death:
            if expected_cause in dmgs_that_caused_death:
                return True

        return False

    def on_enemy_death_effects(self, dmgs_that_caused_death):
        """
        Applies all effects that are triggered by enemy death.

        :param dmgs_that_caused_death: Dmg names that occurred on time of target's death.
        :return: (None)
        """
        for buff_name in self.active_buffs['player']:
            buff_dct = self.request_buff(buff_name=buff_name)

            if 'on_enemy_death' in buff_dct:
                on_enemy_death_dct = buff_dct['on_enemy_death']

                if self._causes_of_death_match_expected(dmgs_that_caused_death=dmgs_that_caused_death, on_enemy_death_dct=on_enemy_death_dct):

                    self.apply_on_x_effects_of_single_buff(buff_dct=buff_dct, x_eff_name='on_enemy_death')

    def apply_deaths_and_on_death_effects(self, examined_time):
        if examined_time in self._applied_dmgs:
            dmgs_that_caused_death = self._applied_dmgs[examined_time]

            if self._apply_death_to_all_viable_enemies():
                self.on_enemy_death_effects(dmgs_that_caused_death=dmgs_that_caused_death)

    # ON NTH HIT
    # nth-type buffs are used for buffs that have a counter (named 'n') which increases on hit or movement.
    # This includes both on-nth attack buffs of an ability (e.g. Jax R)
    # as well as items with counter-stacks (e.g. static shiv).
    def insert_nth_related_in_actives_buffs(self, every_nth_dct, buff_dct_in_active_buffs):
        """
        Inserts nth related data into active buffs.

        :return: (None)
        """

        max_n = every_nth_dct['max_n']

        starting_n = every_nth_dct['starting_n']
        if starting_n == 'max':
            starting_n = max_n
        else:
            pass

        buff_dct_in_active_buffs.update({
            'max_n': max_n,
            'current_n': starting_n,
            'counter_reset_time': self.current_time + every_nth_dct['counter_duration'],
            'last_target': self.current_enemy,
            'reset_on_aa_target_change': every_nth_dct['reset_on_aa_target_change'],
            'movement_marker': self.total_movement
        })

    def _update_current_n(self, buff_dct_in_active_buffs, stacks_per_hit, new_n=None):
        """
        If counter duration hasn't expired, increments by 1 the n-counter or sets it to given value.

        :return: (None)
        """

        if buff_dct_in_active_buffs['counter_reset_time'] < self.current_time:
            buff_dct_in_active_buffs['current_n'] = 0
            return

        if new_n is None:
            buff_dct_in_active_buffs['current_n'] += stacks_per_hit
        else:
            buff_dct_in_active_buffs['current_n'] = new_n

    def apply_every_nth_effects(self, every_nth_dct, buff_dct_in_active_buffs):
        self._apply_on_x_effects(on_x_dct=every_nth_dct['on_hit'])
        # Resets counter
        self._update_current_n(buff_dct_in_active_buffs=buff_dct_in_active_buffs,
                               stacks_per_hit=None,     # Not needed since new_n is provided
                               new_n=0)

    def apply_or_update_nth(self, buff_name, buff_dct):
        """
        Applies on nth hit effects and updates the buff's dict in active buffs.

        :param buff_dct: The dict containing all buff's attributes.
        :return: (None)
        """

        if 'every_nth_hit' not in buff_dct:
            return

        every_nth_dct = buff_dct['every_nth_hit']
        if not every_nth_dct:
            return

        # (on_hit buffs are always owned by the player)
        buff_dct_in_active_buffs = self.active_buffs['player'][buff_name]

        # TARGET-RESETTING COUNTERS
        reset_on_aa_target_change = every_nth_dct['reset_on_aa_target_change']
        if reset_on_aa_target_change:
            # If enemy has changed resets stacks and noted target.
            if self.current_enemy != buff_dct_in_active_buffs['last_target']:
                buff_dct_in_active_buffs['last_target'] = self.current_enemy
                buff_dct_in_active_buffs['current_n'] = 0
                return

        # MOVEMENT CAUSED STACKS
        stacks_per_movement_unit = every_nth_dct['stacks_per_movement_unit']
        if stacks_per_movement_unit:
            # Current value of movement is deducted from stored value and stacks corresponding are applied.
            distance_delta = self.total_movement - buff_dct_in_active_buffs['movement_marker']
            buff_dct_in_active_buffs['current_n'] += int(distance_delta * stacks_per_movement_unit)
            # (updates to new value the marker)
            buff_dct_in_active_buffs['movement_marker'] = self.total_movement

        # STACKS BY HIT
        stacks_per_hit = every_nth_dct['stacks_per_hit']
        # (on-nth are applied at n-1 stacks since during this hit it would reach n stacks anyway;
        # applying +1 first and then resetting it to 0 would be redundant)
        if stacks_per_hit:
            self._update_current_n(buff_dct_in_active_buffs=buff_dct_in_active_buffs,
                                   stacks_per_hit=stacks_per_hit)

        # CHECK AND APPLY NTH EFFECTS
        if buff_dct_in_active_buffs['current_n'] >= every_nth_dct['max_n']:
            self.apply_every_nth_effects(every_nth_dct, buff_dct_in_active_buffs)

    # -----------------------------------------------------
    def apply_ability_or_item_effects(self, eff_dct):
        """
        Applies an action's (abilities, item actives or summoner actives) effects.

        Target is automatically chosen.

        :return: (None)
        """

        if not eff_dct:
            return

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
                self.remove_buff(tar_name=tar_of_buff, buff_name=buff_name_to_remove)

    def apply_action_effects(self, action_name):
        """
        Applies an action's effects.

        :return: (None)
        """

        # AA
        if action_name == 'AA':
            # ..applies AA physical dmg, and applies (or removes) on_hit buffs and dmg.
            self.activate_rage_speed_buff()
            # Applies on_hit effects.
            self.apply_on_hit_effects()

            # Applies direct dmg.
            self.add_events(effect_name='aa_dmg', start_time=self.current_time, tar_name=self.current_enemy)

        # ABILITY
        elif action_name in self.castable_spells_shortcuts:
            self.apply_ability_or_item_effects(eff_dct=self.abilities_effects(ability_name=action_name))

        # ITEM ACTIVE - SUMMONER SPELL
        else:
            if action_name in self.ALL_SUMMONER_SPELL_NAMES:
                eff_dct = self.summoner_spell_effects[action_name]
            else:
                eff_dct = self.items_effects(action_name)

            self.apply_ability_or_item_effects(eff_dct=eff_dct)

    def remove_event(self, tar_name, event_name):
        for event_time in self.events:

            events_lst = self.events[event_time]

            for dct_num, event_dct in enumerate(events_lst):
                if (event_dct['event_name'] == event_name) and (event_dct['target_name'] == tar_name):
                    del events_lst[dct_num]

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

    # TODO memo (static result throughout instance)
    def _items_and_summoner_spells_priorities_lst(self):
        """
        Creates a list with castable items and summoner spells
        that "should" be cast always at the start of the combat.

        :return: (list)
        """

        # (not using a list from the beginning to remove duplicates)
        queue_set = set()

        # SUMMONER'S SPELLS
        for spell_name in sorted(self.selected_summoner_spells):
            if spell_name in self.castable_summoner_spells():
                queue_set.add(spell_name)

        # ITEMS
        for item_name in self.player_items:
            if item_name in items_data_module.CASTABLE_ITEMS:
                queue_set.add(item_name)

        queue_lst = []
        # (Selected summoner spells are highest priority)
        # (They are inserted based on their top priority order)
        for summoner_spell_name in self.SUMMONER_SPELLS_AT_COMBAT_START_BY_PRIORITY:
            if summoner_spell_name in queue_set:
                queue_lst.append(summoner_spell_name)

        for action_name in sorted(queue_set):
            if action_name not in queue_lst:
                queue_lst.append(action_name)

        return queue_lst

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

    def next_action_name_by_priority(self):
        """
        Determines next action based on actions' priorities.

        :return: (str) action name or 'action_delayer'
        """

        # After each action application, priority is recalculated.
        current_priority_sequence = self._action_priorities_after_effects()

        # Tries all actions until it manages to apply one (then recalculates priority).
        for action_name in current_priority_sequence:

            if action_name in self.not_castable_spells_shortcuts:
                continue

            # CD
            if self._action_cd_end(action_name=action_name) > self.current_time:
                continue

            # COST REQUIREMENTS
            # (more costly to run this before cd check)
            if not self.cost_sufficiency(action_name=action_name):
                # If the cost is too high, action is skipped.
                continue

            return action_name

        # No action was available.
        return 'action_delayer'

    def rotation_followed(self):
        rot = []

        for action_time in sorted(self.actions_dct):
            action_name = self.actions_dct[action_time]['action_name']
            rot.append(action_name)

        return rot

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

    def add_next_action(self):
        """
        Adds next action based on whether a specific or automatic rotation is chosen.

        :return: (None)
        """
        if not self.rotation_lst:
            next_action = self.next_action_name_by_priority()
            self.add_new_action_and_movement_since_previous_action(action_name=next_action)

        else:
            # (if rotation copy has been emptied then there are no actions left to add)
            if self._reverse_rotation_copy:
                next_action = self._reverse_rotation_copy.pop()
                self.add_new_action_and_movement_since_previous_action(action_name=next_action)

    def _apply_dmg_event(self, event_name, event_target, only_temporary_dots):
        dmg_dct = self.request_dmg(dmg_name=event_name)
        self.apply_dmg_or_heal(dmg_name=event_name, dmg_dct=dmg_dct, target_name=event_target)

        self._applied_dmgs.setdefault(self.current_time, set())
        self._applied_dmgs[self.current_time].add(event_name)

        # (periodic events are refreshed only on alive targets;
        # player periodic events are always refreshed to ensure enemies' dps is fully applied)
        if self.is_alive(tar_name=event_target) or event_target == 'player':
            self.add_next_periodic_event(tar_name=event_target,
                                         dmg_name=event_name,
                                         dmg_dct=dmg_dct,
                                         only_temporary=only_temporary_dots)

    def apply_single_event(self, event_dct, only_temporary_dots):
        """
        Applies event given by its dict.
        If only temporary dots are applied following periodic refreshing will not occur.

        :param only_temporary_dots: (bool)
        :return: (None)
        """
        event_type = event_dct['event_type']
        event_name = event_dct['event_name']
        event_target = event_dct['target_name']

        self.set_current_enemy(examined_tar=event_target)

        if event_type == 'dmg':
            self._apply_dmg_event(event_name=event_name,
                                  event_target=event_target,
                                  only_temporary_dots=only_temporary_dots)

        elif event_type == 'buff_end':
            self.remove_buff(tar_name=event_target, buff_name=event_name)

        elif event_type == 'action_cast_end':
            if event_name != 'action_delayer':
                self.apply_action_effects(action_name=event_name)

            self.add_next_action()

        elif event_type == 'action_channel_end':
            self.add_next_action()

        else:
            raise palette.UnexpectedValueError()

    def apply_events_on_given_time(self, examined_time, only_temporary_dots=False):
        """
        Applies all events that occur on given time.

        :param examined_time: (float)
        :param only_temporary_dots: (bool)
        :return: (None)
        """
        events_lst_on_examined_time = self.events[examined_time]

        while events_lst_on_examined_time:

            event_dct = events_lst_on_examined_time.pop(0)
            self.apply_single_event(event_dct=event_dct, only_temporary_dots=only_temporary_dots)

    def all_actions_in_rotation_applied(self):
        """
        Checks if all actions in given rotation have been applied.
        If no rotation is given, returns False.

        :return: (bool)
        """
        if self.rotation_lst:
            return self.rotation_lst == self.rotation_followed()
        else:
            return False

    def determine_combat_duration(self):
        """
        Checks and stores how long the combat lasted. Combat end is defined as "when the last action's cast ended".

        If combat duration is 0, sets it to a very small amount to avoid ZeroDivisionErrors.

        :return: (None)
        """

        last_action_end_time = self._last_action_end()
        if last_action_end_time:
            self.combat_duration = self._last_action_end()
        else:
            self.combat_duration = 0.00000000001

    def _main_combat(self):

        # Inserts first action.
        self.add_next_action()

        while self.events:
            self.current_time = min(self.events)

            if not self.all_actions_in_rotation_applied():
                self.apply_events_on_given_time(examined_time=self.current_time, only_temporary_dots=False)
            else:
                # After all actions are applied, permanent dots are not applied,
                # so that they are not refreshed and combat can end.
                self.apply_events_on_given_time(examined_time=self.current_time, only_temporary_dots=True)

            # (Deaths are applied after events at given time are fully applied,
            # so that dps is estimated more accurately.)
            self.apply_deaths_and_on_death_effects(examined_time=self.current_time)

            del self.events[self.current_time]

            if self.all_dead_or_max_time_exceeded():
                break

        self.determine_combat_duration()

    def _run_reversed_combat(self):
        """
        Stores enemy's "base" stats and dmg taken,
        in when combat is reversed.

        That is, 'enemy_x' has become 'player' in order to determine enemy-originating buffs.
        Base stats are derived from reversed combats, since it's much more speedy
        than calculating them in the normal combat.

        :return: (None)
        """

        self.rotation_lst = []  # Rotation of enemies is always independent of player's rotation.

        self.run_combat_preparation_without_regen()

        stats_dct = {i: self.request_stat(target_name='player', stat_name=i) for i in self.ENEMY_BASE_STATS_NAMES}

        # Stores stats player's (that is, 'enemy_x' for normal combat) stats
        self.reversed_precombat_player_stats = stats_dct

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
            return


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

        super().__init__(rotation_lst=rotation_lst,
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
    GUINSOOS_BELOW_HALF_HP_BUFF = palette.SafeBuff({'buff_source': 'guinsoos_rageblade',
                                                    'dot': False,
                                                    'duration': 'permanent',
                                                    'max_stacks': 1,
                                                    'max_targets': 1,
                                                    'usual_max_targets': 1,
                                                    'on_hit': {},
                                                    'stats': {'att_speed': {'percent': {'stat_mods': {},
                                                                                        'stat_values': 0.2}},
                                                              'lifesteal': {'additive': {'stat_mods': {},
                                                                                         'stat_values': 0.1}},
                                                              'spellvamp': {'additive': {'stat_mods': {},
                                                                                         'stat_values': 0.1}}},
                                                    'target_type': 'player',
                                                    'prohibit_cd_start': {}})

    def activate_guinsoos_rageblade_low_hp_buff(self):

        if items_data_module.ITEMS_NAMES['guinsoos_rageblade'] not in self.player_items:
            # (player doesn't have the item)
            return

        if 'guinsoos_rageblade_low_hp_buff' in self.active_buffs['player']:
            # (already active)
            return

        # (when initially called during item passives application current stats aren't created yet)
        if 'player' in self.current_stats:

            half_max_hp = self.request_stat(target_name='player', stat_name='hp') / 2
            if self.current_stats['player']['current_hp'] < half_max_hp:

                self.add_buff(buff_name='guinsoos_rageblade_low_hp_buff', tar_name='player')

    def guinsoos_rageblade_low_hp_buff(self):
        return self.GUINSOOS_BELOW_HALF_HP_BUFF

    # SPELLBLADE
    SPELLBLADE_ITEMS_PRIORITY_SORTED = ('lich_bane', 'trinity_force', 'iceborn_gauntlet', 'sheen')
    items_data_module.ensure_in_items_names(SPELLBLADE_ITEMS_PRIORITY_SORTED)
    # (ensures names used exist, otherwise methods below will function incorrectly)

    SPELLBLADE_BUFF_NAMES_MAP = {'inhibitor': 'spellblade_inhibitor',
                                 'triggered': 'spellblade_triggered'}
    items_data_module.ensure_in_items_buffs(SPELLBLADE_BUFF_NAMES_MAP.values())

    SPELLBLADE_INITIATOR_WITHOUT_ON_HIT_BUFF = palette.SafeBuff(dict(
        target_type='player',
        duration='permanent',
        max_stacks=1,
        stats={},
        on_hit={},
        prohibit_cd_start={},
        buff_source='sheen',
        max_targets=1,
        usual_max_targets=1,
        dot=False
    ))
    SPELLBLADE_INITIATOR_WITHOUT_ON_HIT_BUFF.delete_keys(('on_hit',))

    # (they are used purely as tags)
    SPELLBLADE_INHIBITOR_BUFF = palette.SafeBuff(dict(
        target_type='player',
        duration=1.5,
        max_stacks=1,
        stats={},
        on_hit={},
        prohibit_cd_start={},
        buff_source='sheen',
        max_targets=1,
        usual_max_targets=1,
        dot=False
    ))

    SPELLBLADE_TRIGGERED_BUFF = palette.SafeBuff(dict(
        target_type='player',
        duration=7,
        max_stacks=1,
        stats={},
        on_hit={},
        prohibit_cd_start={},
        buff_source='sheen',
        max_targets=1,
        usual_max_targets=1,
        dot=False
    ))

    # TODO: single call memo
    def spellblade_dmgs_lst(self):
        dmgs_lst = []
        # Ring dmg is applied regardless of other items.
        if items_data_module.ITEMS_NAMES['iceborn_gauntlet'] in self.player_items:
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
    RAGE_SPEED_BUFF_MELEE = palette.SafeBuff(dict(
        target_type='player',
        duration=2,
        max_stacks=1,
        stats={'move_speed': {'additive': {'stat_mods': {},
                                           'stat_values': 20}}},
        on_hit={},
        prohibit_cd_start={},
        buff_source='phage',
        max_targets=1,
        usual_max_targets=1,
        dot=False
    ))

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

    RAGE_INITIATOR_BUFF = palette.SafeBuff(dict(
        target_type='player',
        duration='permanent',
        max_stacks=1,
        stats={},
        on_hit=dict(
            apply_buff=[placeholder, ],
            cause_dmg=[placeholder, ],
            cds_modified={},
            remove_buff=[placeholder, ]
        ),
        prohibit_cd_start={},
        buff_source='phage',
        max_targets=1,
        usual_max_targets=1,
        dot=False
    ))
    for i in RAGE_INITIATOR_BUFF['on_hit']:
        RAGE_INITIATOR_BUFF['on_hit'][i] = []
    RAGE_INITIATOR_BUFF['on_hit']['apply_buff'] = ['rage_speed_buff']

    def rage_initiator_buff(self):
        return self.RAGE_INITIATOR_BUFF

    # BLACK CLEAVER
    BLACK_CLEAVER_ARMOR_REDUCTION_BUFF = palette.SafeBuff(dict(
        target_type='enemy',
        duration=5,
        max_stacks=6,
        stats={'percent_armor_reduction': {'additive': {'stat_mods': {},
                                                        'stat_values': 0.05}}},
        on_hit={},
        prohibit_cd_start={},
        buff_source='the_black_cleaver',
        max_targets=1,
        usual_max_targets=1,
        dot=False
    ))

    def black_cleaver_armor_reduction_buff(self):
        return self.BLACK_CLEAVER_ARMOR_REDUCTION_BUFF

    BLACK_CLEAVER_REDUCTION_BUFFS_NAMES = ['black_cleaver_armor_reduction_'+str(i) for i in range(1, 7)]

    BLACK_CLEAVER_INITIATOR_BUFF = palette.SafeBuff(dict(
        target_type='player',
        duration='permanent',
        max_stacks=1,
        stats={},
        on_hit={},
        prohibit_cd_start={},
        buff_source='the_black_cleaver',
        max_targets=1,
        usual_max_targets=1,
        dot=False
    ))

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
    IMMOLATE_BUFF = palette.SafeBuff(dict(
        target_type='player',
        duration='permanent',
        max_stacks=1,
        stats={},
        on_hit={},
        prohibit_cd_start={},
        buff_source=placeholder,
        max_targets=1,
        usual_max_targets=1,
        dot=placeholder
    ))
    IMMOLATE_BUFF.delete_keys({'dot', 'buff_source'})

    # (highest to lowest priority)
    ORDERED_IMMOLATE_ITEMS = ('sunfire_cape', 'enchantment_cinderhulk_dmg', 'bamis_cinder',)
    IMMOLATE_ITEMS_TO_DMG_NAME_MAP = {i: i+'_immolate_dmg' for i in ORDERED_IMMOLATE_ITEMS}
    items_data_module.ensure_in_items_names(set(ORDERED_IMMOLATE_ITEMS) | set(IMMOLATE_ITEMS_TO_DMG_NAME_MAP))

    REVERSED_IMMOLATE_ITEMS_TO_DMG_NAME_MAP = {v: k for k, v in IMMOLATE_ITEMS_TO_DMG_NAME_MAP.items()}

    # TODO: memo (it only has to be checked once, at the start; then it remains the same through the instance)
    def immolate_buff(self):
        """
        Creates immolate buff based on highest priority item. Its dmg is the only dmg applied.
        :return: (dict)
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
                buff_dct.update(buff_source=immolate_item)

                return buff_dct

    IMMOLATE_DMG_BASE = palette.SafeDmg(dict(
        target_type='enemy',
        dmg_category='standard_dmg',
        resource_type='hp',
        dmg_type='magic',
        dmg_values=placeholder,
        dmg_source=placeholder,
        mods={},
        life_conversion_type=None,
        radius=500,
        dot={'buff_name': 'immolate_buff'},
        max_targets=3,
        usual_max_targets=3,
        delay=1,
        crit_type=None,
        heal_for_dmg_amount=False
    ))
    IMMOLATE_DMG_BASE.delete_keys(['dmg_values', 'dmg_source'])

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
        return self._immolate_dmg_base(dmg_name='bamis_cinder_immolate_dmg', dmg_values=dmg_values)

    def enchantment_cinderhulk_dmg(self):
        dmg_values = 15 + 0.6 * self.player_lvl
        return self._immolate_dmg_base(dmg_name='enchantment_cinderhulk_dmg', dmg_values=dmg_values)

    # LIANDRYS TORMENT
    LIANDRYS_NAME = 'liandrys_torment'
    items_data_module.ensure_in_items_names((LIANDRYS_NAME,))

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
        self.create_castable_and_non_castable_spells_shortcuts()

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

    # (`img` dir is set in project parent because it's required in the server)
    TEMP_COMBAT_RESULT_IMAGES_DIRECTORY = os.path.join(palette.PROJECT_PARENT_PATH, 'img')

    PLAYER_STATS_DISPLAYED = ('ap', 'ad', 'armor', 'mr', 'current_hp', 'mp', 'att_speed', 'cdr')
    ENEMY_STATS_DISPLAYED = ('armor', 'mr', 'physical_dmg_taken', 'magic_dmg_taken', 'current_hp')
    PLAYER_STATS_HEADERS = ('PLAYER STATS', 'PRE', 'POST')

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

        # (created only if instance is run in image-creation mode)
        self.temp_combat_results_image_path = None
        self.temp_image_name = None

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
        color_lst = ('black', 'b', 'g', 'y', 'orange', 'red')

        # Creates graph for each target.
        for tar_name in ('player',) + self.enemy_target_names:

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

    def player_stats_table(self):
        table_lst = [self.PLAYER_STATS_HEADERS, ]

        # Creates lines.
        for stat_name in self.PLAYER_STATS_DISPLAYED:

            precombat_value = self.combat_results['player']['pre_combat_stats'][stat_name]
            precombat_value = precombat_value

            postcombat_value = self.combat_results['player']['post_combat_stats'][stat_name]
            postcombat_value = postcombat_value

            line_tpl = (stat_name+': ', precombat_value, postcombat_value)

            # Inserts in data to be displayed
            table_lst.append(line_tpl)

        return table_lst

    def subplot_player_stats_table(self, subplot_obj):
        """
        Subplots player's pre and post combat stats.

        Stat values are rounded.

        :returns: (None)
        """

        subplot_obj.axis('off')
        table_obj = subplot_obj.table(
            cellText=self.player_stats_table(),
            cellLoc='left',
            loc='center')

        self.__set_table_font_size(table_obj=table_obj)

    def enemy_stats_table(self):
        table_lst = []

        for tar_name in self.enemy_target_names:
            tar_lvl = self.champion_lvls_dct[tar_name]
            tar_champ = self.selected_champions_dct[tar_name]
            table_lst.append((tar_name.upper(), ''))
            table_lst.append((tar_champ.upper(), 'Lvl: {}'.format(tar_lvl)))

            # Creates lines.
            for stat_name in self.ENEMY_STATS_DISPLAYED:

                postcombat_value = self.combat_results[tar_name]['post_combat_stats'][stat_name]
                postcombat_value = round(postcombat_value, 4)

                line_tpl = (stat_name+': ', postcombat_value)

                # Inserts in data to be displayed
                table_lst.append(line_tpl)

        return table_lst

    def subplot_enemy_stats_table(self, subplot_obj):
        """
        Subplots player's pre combat stats.

        Stat values are rounded.

        Returns:
            (None)
        """

        subplot_obj.axis('off')

        table_obj = subplot_obj.table(
            cellText=self.enemy_stats_table(),
            cellLoc='left',
            loc='center')

        self.__set_table_font_size(table_obj=table_obj)

    def rotation_followed_as_single_str(self, chars_limit):
        """
        Turns rotation into a string, which is separated by new lines based on char limited provided.

        :return: (str)
        """
        rot_lst = self.rotation_followed()

        lines_lst = []
        line_as_str = ''

        for action_name in rot_lst:
            # (splits the str with comma after each new action name)
            if line_as_str:
                line_as_str += ', '

            if len(line_as_str) + len(action_name) + 2 <= chars_limit:
                line_as_str += action_name

            else:
                lines_lst.append(line_as_str)
                line_as_str = ''
        else:
            # (after for loop ends any remaining line_as_str needs to be added)
            lines_lst.append(line_as_str)

        return '\n'.join(lines_lst)

    def preset_and_results_table(self):

        # Rotation
        table_lst = [('ROTATION',), (self.rotation_followed_as_single_str(chars_limit=50),)]

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

        return table_lst

    def subplot_preset_and_results_table(self, subplot_obj):

        subplot_obj.axis('off')

        table_obj = plt.table(
            cellText=self.preset_and_results_table(),
            cellLoc='left',
            loc='center')

        table_properties = table_obj.properties()
        cells = table_properties['celld']
        rotation_cell = cells[(1, 0)]
        rotation_cell.set_height(rotation_cell.get_height()*2)

        table_subplot_obj = subplot_obj.add_table(table_obj)

        self.__set_table_font_size(table_obj=table_subplot_obj)

    def _create_results_visual_representation(self):
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

    def store_results_as_image(self):
        self._create_results_visual_representation()

        # Creates image name in a way that would be unique
        # so that it does not overwrite accidentally images from other concurrent instances.
        self.temp_image_name = 'temp_image_{}.png'.format(id(self))
        self.temp_combat_results_image_path = os.path.join(self.TEMP_COMBAT_RESULT_IMAGES_DIRECTORY, self.temp_image_name)
        plt.savefig(self.temp_combat_results_image_path)
        plt.close()

    def delete_stored_results_image(self):
        os.remove(self.temp_combat_results_image_path)

    def represent_results_visually(self):

        self._create_results_visual_representation()
        plt.show()
