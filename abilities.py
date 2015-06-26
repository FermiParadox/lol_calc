import buffs
import timers
import runes
import app_champions_base_stats
import palette

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import operator
import copy


class EnemyTargetsDeadError(Exception):
    """
    To be used (and handled) when no other valid targets are available for an event application.
    """
    pass


class EventsGeneral(buffs.DeathAndRegen):

    NATURAL_REGEN_START_TIME = 0.5

    def __init__(self,
                 champion_lvls_dct,
                 selected_champions_dct,
                 max_targets_dct,
                 max_combat_time,
                 initial_active_buffs,
                 initial_current_stats,
                 req_buff_dct_func,
                 chosen_items_lst,
                 req_dmg_dct_func,
                 ability_lvls_dct,
                 selected_masteries_dct,):

        # (User defined dict containing number of targets affected by abilities.)
        self.max_targets_dct = max_targets_dct
        self.event_times = {}
        self.current_target = None
        # (Used to note that a periodic event might have been added between current events and last action.)
        self.intermediate_events_changed = None

        buffs.DeathAndRegen.__init__(self,
                                     selected_champions_dct=selected_champions_dct,
                                     champion_lvls_dct=champion_lvls_dct,
                                     max_combat_time=max_combat_time,
                                     initial_current_stats=initial_current_stats,
                                     initial_active_buffs=initial_active_buffs,
                                     chosen_items_lst=chosen_items_lst,
                                     req_dmg_dct_func=req_dmg_dct_func,
                                     ability_lvls_dct=ability_lvls_dct,
                                     req_buff_dct_func=req_buff_dct_func,
                                     selected_masteries_dct=selected_masteries_dct)

        self.resource_used = app_champions_base_stats.CHAMPION_BASE_STATS[selected_champions_dct['player']][
            'resource_used']

    def add_event_to_first_tar(self, effect_name, start_time):
        """
        Applies a dmg event to the first target.

        Modifies:
            event_times
        Returns:
            (None)
        """

        # If the event's time doesn't exist it creates it.
        if start_time not in self.event_times:
            self.event_times.update({start_time: {self.current_target: [effect_name]}})

        else:
            # If the time exists in the dictionary,
            # checks if the target is inside the time.
            if self.current_target in self.event_times[start_time]:
                self.event_times[start_time][self.current_target].append(effect_name)
            else:
                # If not, it adds the target as well.
                self.event_times[start_time].update({self.current_target: [effect_name]})

    def add_regenerations(self):
        """
        Adds hp5 (both event and buff) for all targets, and resource per 5 for player.

        Modifies:
            event_times
            active_buffs
        Returns:
            (None)
        """

        for self.current_target in self.all_target_names:
            # ENEMY
            if self.current_target != 'player':
                self.add_buff(buff_name='enemy_hp5_buff', tar_name=self.current_target)
                # HP5
                self.add_event_to_first_tar(effect_name='enemy_hp5_dmg',
                                            start_time=self.NATURAL_REGEN_START_TIME)

            # PLAYER
            else:
                self.add_buff(buff_name='player_hp5_buff', tar_name=self.current_target)
                # HP5
                self.add_event_to_first_tar(effect_name='player_hp5_dmg',
                                            start_time=self.NATURAL_REGEN_START_TIME)

                # RESOURCE
                regen_event_name = None
                if self.resource_used == 'energy':
                    regen_event_name = 'ep5_dmg'
                    self.add_buff(buff_name='ep5_buff', tar_name=self.current_target)

                elif self.resource_used == 'mp':
                    regen_event_name = 'mp5_dmg'
                    self.add_buff(buff_name='mp5_buff', tar_name=self.current_target)

                # Checks if player's resource can regenerate per 5.
                if regen_event_name:
                    self.add_event_to_first_tar(effect_name=regen_event_name,
                                                start_time=self.NATURAL_REGEN_START_TIME)

    def add_aoe_events(self, effect_name, start_time):
        """
        Adds an aoe dmg event to affected target. If all unaffected targets are dead raises exception.

        Modifies:
            event_times
            targets_already_hit
            current_target
        Returns:
            (None)
        Raises:
            EnemyTargetsDeadException: No viable targets exist.
        """

        # NEXT TARGET
        # If next target is None (because no valid targets exist) the loop breaks.
        self.next_target(enemy_tar_names=self.enemy_target_names)
        if self.current_target is None:
            raise EnemyTargetsDeadError

        self.targets_already_hit += 1

        # ADD EVENT
        # Checks if the target is inside the time.
        if self.current_target in self.event_times[start_time]:
            self.event_times[start_time][self.current_target].append(effect_name)
        else:
            self.event_times[start_time].update({self.current_target: [effect_name]})

    def add_events(self, effect_name, start_time):
        """
        Adds a dmg event (e.g. Brand W) to all affected targets.

        Modifies:
            event_times
            targets_already_hit
            current_target
        Structure:
            event_times: {0.: {'player': ['w_dmg',],},}
        Returns:
            (None)
        """

        effect_dct = self.req_dmg_dct_func(effect_name)
        # Changes event start if needed.
        eff_delay = effect_dct['delay']
        if eff_delay:
            start_time += eff_delay

        # Adds event to first target.
        self.add_event_to_first_tar(effect_name=effect_name, start_time=start_time)

        self.targets_already_hit = 1

        # AOE DMG
        # Aoe dmg has 'max_targets' in dmg dct. It can also additionally have externally set max_targets.
        # Tries to add events to targets.
        try:
            # External max targets.
            if effect_name in self.max_targets_dct:
                max_tars_val = self.max_targets_dct[effect_name]

            else:
                max_tars_val = effect_dct['usual_max_targets']
                if max_tars_val == 'unlimited':
                    # If targets are unlimited applies to everyone.
                    max_tars_val = len(self.enemy_target_names)

            # While the last target number is less than max targets, adds event.
            while self.targets_already_hit < max_tars_val:
                self.add_aoe_events(effect_name=effect_name, start_time=start_time)

        except EnemyTargetsDeadError:
            pass

    def refresh_periodic_event(self, dmg_name, tar_name, dmg_dct):
        """
        Re-adds a periodic effect and notes the change.

        Refreshed only if buff ending time is higher than event ending time,
        or if it's a permanent buff.

        Returns:
            (None)
        """

        tar_act_buffs = self.active_buffs[tar_name]
        buff_name = dmg_dct['dot']['buff_name']
        buff_dct = self.req_buff_dct_func(buff_name=buff_name)

        # Checks dot's buff.
        if buff_name in tar_act_buffs:
            if ((tar_act_buffs[buff_name]['ending_time'] == 'permanent') or
                    (tar_act_buffs[buff_name]['ending_time'] > self.current_time)):

                self.add_events(effect_name=dmg_name,
                                start_time=self.current_time + buff_dct['dot']['period'])

                self.intermediate_events_changed = True

    def add_next_periodic_event(self, tar_name, dmg_name, only_temporary=False):
        """
        Adds next periodic tick.

        Checks active_buffs for the dot buff, then adds event if the buff still exists.

        Modifies:
            event_times
        Args:
            only_temporary: (boolean) Used for filtering out permanent dots (e.g. sunfire) if needed.
        Returns:
            (None)
        """

        dmg_dct = self.req_dmg_dct_func(dmg_name=dmg_name)

        # Checks if event is periodic.
        if dmg_dct['dot']:
            # If only temporary periodic events are re-applied..
            if only_temporary:
                # ..checks if their duration is not permanent.
                if dmg_dct['duration'] != 'permanent':
                    self.refresh_periodic_event(dmg_name=dmg_name, tar_name=tar_name, dmg_dct=dmg_dct)

            # Otherwise checks both permanent and temporary dots.
            else:
                self.refresh_periodic_event(dmg_name=dmg_name, tar_name=tar_name, dmg_dct=dmg_dct)


class AttributeBase(EventsGeneral):

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
                 initial_active_buffs,
                 initial_current_stats,
                 chosen_items_lst,
                 selected_masteries_dct
                 ):

        self.ability_lvls_dct = ability_lvls_dct
        self.current_target_num = None
        self.action_on_cd_func = action_on_cd_func

        self.__castable_spells_shortcuts = None

        EventsGeneral.__init__(self,
                               champion_lvls_dct=champion_lvls_dct,
                               selected_champions_dct=selected_champions_dct,
                               max_targets_dct=max_targets_dct,
                               max_combat_time=max_combat_time,
                               initial_active_buffs=initial_active_buffs,
                               initial_current_stats=initial_current_stats,
                               chosen_items_lst=chosen_items_lst,
                               ability_lvls_dct=ability_lvls_dct,
                               req_dmg_dct_func=self.request_dmg,
                               req_buff_dct_func=self.request_buff,
                               selected_masteries_dct=selected_masteries_dct)

    def _x_value(self, x_name, x_type, x_owner):
        """
        Determines value of x in a condition trigger.

        Returns:
            (num)
        """

        if x_owner == 'player':
            owner = x_owner
        else:
            owner = self.current_target

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
            return self.current_target

    def _check_triggers_state(self, cond_name):
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
        tar_type = con_eff_dct['tar_type']
        mod_operation = con_eff_dct['mod_operation']
        cat_type = con_eff_dct['lst_category']
        eff_contents = con_eff_dct['names_lst']

        # (it always modifies actives)

        if mod_operation == 'append':
            modified_dct[tar_type]['actives'][cat_type] += eff_contents
        elif mod_operation == 'remove':
            old_lst = modified_dct[obj_name][tar_type]['actives'][cat_type]
            modified_dct[tar_type]['actives'][cat_type] = [i for i in old_lst if i not in eff_contents]

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
                        trig_state = self._check_triggers_state(cond_name=cond)
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
                                        initial_dct=self.ITEMS_EFFECTS[item_name],
                                        conditionals_dct=self.ITEMS_CONDITIONALS[item_name])

    def item_attributes(self, item_name):
        return self._attrs_or_effs_base(obj_name=item_name,
                                        searched_obj_type='item_attr',
                                        initial_dct=self.ITEMS_EFFECTS[item_name],
                                        conditionals_dct=self.ITEMS_CONDITIONALS[item_name])

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

        elif buff_name in self.ITEMS_BUFFS_NAMES:
            item_name = self.ITEMS_BUFFS_NAMES[buff_name]
            initial_dct = self.ITEMS_ATTRIBUTES[item_name]
            conditionals_dct = self.ITEMS_CONDITIONALS[item_name]

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

        elif dmg_name in self.ITEMS_DMGS_NAMES:
            item_name = self.ITEMS_DMGS_NAMES[dmg_name]
            initial_dct = self.ITEMS_ATTRIBUTES[item_name]
            conditionals_dct = self.ITEMS_CONDITIONALS[item_name]

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


class Actions(AttributeBase, timers.Timers, runes.RunesFinal):

    AA_COOLDOWN = 0.4   # TODO: replace functionality with 'wind_up'

    def __init__(self,
                 rotation_lst,
                 max_targets_dct,
                 selected_champions_dct,
                 champion_lvls_dct,
                 ability_lvls_dct,
                 max_combat_time,
                 selected_masteries_dct,
                 chosen_items_lst,
                 initial_active_buffs,
                 initial_current_stats,
                 selected_runes):

        self.rotation_lst = rotation_lst
        self.everyone_dead = None
        self.total_movement = 0

        runes.RunesFinal.__init__(self,
                                  player_lvl=champion_lvls_dct['player'],
                                  selected_runes=selected_runes)

        AttributeBase.__init__(self,
                               ability_lvls_dct=ability_lvls_dct,
                               champion_lvls_dct=champion_lvls_dct,
                               selected_champions_dct=selected_champions_dct,
                               action_on_cd_func=self.spell_on_cd,
                               max_targets_dct=max_targets_dct,
                               max_combat_time=max_combat_time,
                               initial_active_buffs=initial_active_buffs,
                               initial_current_stats=initial_current_stats,
                               chosen_items_lst=chosen_items_lst,
                               selected_masteries_dct=selected_masteries_dct)

        timers.Timers.__init__(self,
                               ability_lvls_dct=ability_lvls_dct,
                               req_dmg_dct_func=self.request_dmg,
                               req_abilities_attrs_func=self.abilities_attributes)

    def action_gen_attrs(self, action_name):
        if action_name in self.castable_spells_shortcuts:
            return self.request_ability_gen_attrs_dct(ability_name=action_name)
        elif action_name in self.chosen_items_lst:
            return  # TODO

    def spell_on_cd(self, action_name):
        """
        Checks if given spell is on cd.

        Starts from last casted action, and checks them until if finds searched spell.
        Then checks its cd end.

        Returns:
            (bool)
        """

        for action_time in reversed(self.actions_dct):
            if self.actions_dct[action_time]['action_name'] == action_name:

                # (if the spell has been casted before, the loop ends)
                if self.actions_dct[action_time]['cd_end'] > self.current_time:
                    return True
                else:
                    return False

        # If it hasn't been casted before, then it is not on cd.
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

            if cost_name in ('mp', 'energy', 'hp'):
                if self.current_stats['player']['current_'+cost_name] < cost_value:
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
            if cost_name in ('hp', 'mp', 'energy', 'rage'):
                self.current_stats['player']['current_' + cost_name] -= cost_value

            # STACK COST
            else:
                del self.active_buffs['player'][cost_name]
                # TODO make it remove only one stack
                raise NotImplementedError

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
    def reset_aa_cd(self, action_name):
        """
        Removes an AA's cd after an AA-resetting ability is casted.

        Modifies:
            actions_dict
        Returns:
            (None)
        """

        if self.request_ability_gen_attrs_dct(ability_name=action_name)['resets_aa']:

            for action_time in sorted(self.actions_dct, reverse=True):

                # If an AA has been casted earlier...
                if 'AA' == self.actions_dct[action_time]['action_name']:
                    # ..sets its cd_end to current_time.
                    self.actions_dct[action_time]['cd_end'] = self.current_time
                    break

    def action_cast_start(self, action_name):
        """
        Calculates cast_start of an action, based on other actions' cast_end and this action's cd.

        Returns:
            (float)
        """

        def end_name(action_dct):
            """
            Returns:
                (str)
            """
            if 'channel_end' in action_dct:
                string = 'channel_end'
            else:
                string = 'cast_end'
            return string

        cast_start = self.current_time

        # If a previous action exists...
        if self.actions_dct:

            casted_earlier = None

            # ..checks all actions inside dict from last to first.
            for action_time in sorted(self.actions_dct, reverse=True):

                name = end_name(action_dct=self.actions_dct[action_time])

                # If the examined action has been casted earlier...
                if action_name == self.actions_dct[action_time]['action_name']:

                    # ..compare which ends last;
                    # the examined action's cd or or the last action's cast end.
                    cast_start = max(
                        self.actions_dct[action_time]['cd_end'],
                        # (tiny amount added to avoid action overwriting)
                        self.actions_dct[max(self.actions_dct)][name]) + 0.00000001

                    casted_earlier = True
                    break

            # If it hasn't been casted earlier, it starts when last action's cast ends.
            if not casted_earlier:
                last_action_time = max(self.actions_dct)
                name = end_name(action_dct=self.actions_dct[last_action_time])
                # (tiny amount added to avoid action overwriting)
                cast_start = self.actions_dct[last_action_time][name] + 0.00000001

        return cast_start

    def add_new_action(self, action_name):
        """
        Inserts a new action.

        First dictionary has current action's cast start as keyword,
        and a dictionary as value.

        The second dictionary contains the time the action's animation ends (cast_end),
        the time the action's application ends, the action's name and the time its cooldown ends.

        Modifies:
            actions_dct
        Returns:
            (None)
        """

        # (cast_start is the moment the action is 'clicked')
        cast_start = self.action_cast_start(action_name=action_name)

        # CHAMPION ABILITIES
        if action_name in palette.ALL_POSSIBLE_SPELL_SHORTCUTS:
            spell_dct = self.abilities_attributes(ability_name=action_name)
            self.actions_dct.update(
                {cast_start: dict(
                    cast_end=self.cast_end(action_gen_attrs_dct=spell_dct, action_cast_start=cast_start),
                    action_name=action_name,)})

            # (cd_end is applied later since it requires cast_end)
            self.actions_dct[cast_start].update(dict(
                cd_end=self.ability_cd_end(ability_name=action_name,
                                           cast_start=cast_start,
                                           stats_function=self.request_stat,
                                           actions_dct=self.actions_dct)))

            # CHANNEL
            channel_val = self.abilities_attributes(ability_name=action_name)['channel_time']
            if channel_val:
                channel_end_time = self.actions_dct[cast_start]['cast_end'] + channel_val

                self.actions_dct[cast_start].update({"channel_end": channel_end_time})

            # Checks if ability resets AA's cd_end, and applies it.
            self.reset_aa_cd(action_name=action_name)
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

        # ITEM ACTIVES OR SUMMONER SPELLS
        else:
            # (cast_end is the same as cast_start)
            # (item actives and summoner spells have too high cooldowns, so they are set to a high value)
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
        new_event = True
        if buff_name in self.active_buffs[tar_name]:
            new_event = False

        super().add_buff(buff_name=buff_name, tar_name=tar_name,
                         stack_increment=stack_increment, initial_stacks_increment=initial_stacks_increment)

        # If it's a new dot..
        if new_event:
            # If the buff is a dot, applies event as well.
            buff_dct = self.req_buff_dct_func(buff_name=buff_name)
            buff_dot_dct = buff_dct['dot']
            if buff_dot_dct:
                dmg_dot_name = buff_dot_dct['dmg_name']
                first_tick = self.first_dot_tick(current_time=self.current_time, dmg_name=dmg_dot_name)

                self.add_events(effect_name=dmg_dot_name, start_time=first_tick)

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

    def remove_expired_buffs(self):
        """
        Removes all expired buffs.

        Modifies:
            active_buffs
        Return:
            (None)
        """

        for tar_name in self.active_buffs:
            tar_act_buffs = self.active_buffs[tar_name]

            for buff_name in sorted(tar_act_buffs):
                tar_buff_dct_in_act_buffs = tar_act_buffs[buff_name]

                if tar_buff_dct_in_act_buffs['ending_time'] != 'permanent':
                    if tar_buff_dct_in_act_buffs['ending_time'] < self.current_time:

                        # Applies cd before removing.
                        buff_dct = self.request_buff(buff_name=buff_name)
                        self.change_cd_before_buff_removal(buff_dct=buff_dct)

                        # Removes the buff.
                        del tar_buff_dct_in_act_buffs

    def apply_on_hit_effects(self):
        """
        Applies on hit effects.

        On hit effects can be dmg and buffs application, or buff removal.

        Iterates throughout all active buffs, and applies:
            -on_hit dmg (e.g. Warwick's innate dmg),
            -on_hit buffs (e.g. Black Cleaver armor reduction),
            -and finally removes buffs that are removed on hit.


        Modifies:
            active_buffs
            event_times
        Returns:
            (None)
        """

        # (can't iter over active_buffs itself since it gets modified)
        for buff_name in frozenset(self.active_buffs['player']):
            buff_dct = self.req_buff_dct_func(buff_name=buff_name)

            if buff_dct['on_hit']:

                # DMG CAUSED ON HIT.
                for dmg_name in buff_dct['on_hit']['cause_dmg']:

                    self.switch_to_first_alive_enemy()
                    self.add_events(effect_name=dmg_name, start_time=self.current_time)

                # BUFFS APPLIED ON HIT.
                for buff_applied_on_hit in buff_dct['on_hit']['apply_buff']:

                    self.add_buff(buff_name=buff_applied_on_hit,
                                  tar_name=self.request_buff(buff_name=buff_applied_on_hit)['target_type'])

                # BUFFS REMOVED ON HIT.
                for buff_removed_on_hit in buff_dct['on_hit']['remove_buff']:

                    # Checks if the buff exists on the player.
                    if buff_removed_on_hit in self.active_buffs['player']:
                        self.change_cd_before_buff_removal(buff_dct=buff_dct)
                        del self.active_buffs['player'][buff_removed_on_hit]

                    # Checks if the buff exists on current enemy target.
                    elif buff_removed_on_hit in self.active_buffs[self.current_target]:
                        del self.active_buffs[self.current_target][buff_removed_on_hit]

    def apply_aa_effects(self, current_time):
        """
        Applies AA effects from buffs and AA dmg event.

        Modifies:
            active_buffs
            event_times
        Returns:
            (None)
        """

        # Applies on_hit effects.
        self.apply_on_hit_effects()

        # Applies direct dmg.
        self.switch_to_first_alive_enemy()
        self.add_events('aa_dmg', current_time)

    def apply_ability_actives_on_tar(self, tar_type, eff_dct):
        """
        Applies an action's effects on target.

        Target is automatically chosen.

        Args:
            tar_type: (str) 'player' or 'enemy'
        Returns:
            (None)
        """

        # BUFFS
        for buff_name in eff_dct[tar_type]['actives']['buffs']:
            self.add_buff(buff_name=buff_name, tar_name=self.current_target)

        # DMGS
        for dmg_name in eff_dct[tar_type]['actives']['dmg']:
            self.add_events(effect_name=dmg_name, start_time=self.current_time)

        # BUFF REMOVAL
        for buff_name_to_remove in eff_dct[tar_type]['actives']['remove_buff']:
            tar_act_buffs = self.active_buffs[tar_type]
            if buff_name_to_remove in tar_act_buffs:
                del tar_act_buffs[buff_name_to_remove]

    def apply_ability_effects(self, eff_dct):
        """
        Applies an action's effects.

        Used for abilities, item actives or summoner actives.

        Chooses the first viable enemy for actives on enemies.

        Modifies:
            active_buffs
            event_times
            current_target
        Returns:
            (None)
        """

        if 'player' in eff_dct:

            self.current_target = 'player'
            self.apply_ability_actives_on_tar(tar_type='player', eff_dct=eff_dct)

        if 'enemy' in eff_dct:

            self.switch_to_first_alive_enemy()
            self.apply_ability_actives_on_tar(tar_type='enemy', eff_dct=eff_dct)

    def apply_action_effects(self, action_name):
        """
        Applies an action's effects (buffs, dmg, buff removal).

        Modifies:
            active_buffs
            event_times
        Returns:
            (None)
        """

        # AA
        if action_name == 'AA':
            # ..applies AA physical dmg, and applies (or removes) on_hit buffs and dmg.
            self.apply_aa_effects(current_time=self.current_time)

        # ABILITY
        elif action_name in self.castable_spells_shortcuts:
            self.apply_ability_effects(eff_dct=self.abilities_effects(ability_name=action_name))

        # ITEM ACTIVE - SUMMONER SPELL
        else:
            self.apply_ability_effects(eff_dct=self.items_effects(action_name))

    def apply_pre_action_events(self):
        """
        Applies all events preceding last action's application start.

        If a periodic event is refreshed and ticks before the last action,
        then event_times changes and is checked again.
        If all targets die, the loop stops.

        Modifies:
            current_time
            event_times
            active_buffs
            intermediate_events_changed
        Returns:
            (None)
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

                    self.remove_expired_buffs()

                    # Applies all dmg effects for all targets.
                    for self.current_target in self.event_times[self.current_time]:
                        for dmg_name in self.event_times[self.current_time][self.current_target]:
                            self.apply_dmg_or_heal(dmg_name, self.current_target)
                            self.add_next_periodic_event(tar_name=self.current_target, dmg_name=dmg_name)

                        # After dmg has been applied checks if target has died.
                        self.apply_death(tar_name=self.current_target)

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
                # Checks if alive targets exist.
                for tar_name in self.champion_lvls_dct:
                    if tar_name != 'player':
                        if 'dead_buff' not in self.active_buffs[tar_name]:
                            self.everyone_dead = False
                            break

                # EXIT METHOD
                # If everyone has died, stops applying following events.
                if self.everyone_dead:
                    # TODO: check if "return" can replace below code
                    # (break outer loop)
                    self.intermediate_events_changed = False
                    # (break inner loop)
                    break

    def apply_single_action(self, new_action):
        """
        Applies a single new action, and events in between,
        until everyone is dead or the max_time is exceeded.

        :param new_action: (str)
        :return: (bool)
        """
        # Checks if action meets the cost requirements.
        if not self.cost_sufficiency(action_name=new_action):
            # If the cost is too high, action is skipped.
            # TODO: Make it a new method (ignore mode, wait mode)
            return False

        self.apply_action_cost(action_name=new_action)

        self.add_new_action(new_action)

        # (movement distance)
        self.between_action_walking()

        self.apply_pre_action_events()

        # If everyone died, stops applying actions as well.
        if self.everyone_dead:
            return True

        # Sets current_time to current action's cast end.
        self.current_time = self.actions_dct[max(self.actions_dct)]['cast_end']

        # If max time exceeded, exits loop.
        if self.max_combat_time:
            if self.current_time > self.max_combat_time:
                return True

        # After previous events are applied, applies action effects.
        self.apply_action_effects(action_name=self.actions_dct[max(self.actions_dct)]['action_name'])

    def apply_all_actions(self):
        """
        Applies all actions, and events in between,
        until everyone is dead or the max_time is exceeded.

        NOTE: To be overridden by a method that chooses "preferred" action.

        Returns:
            (None)
        """

        for new_action in self.rotation_lst:

            # (used for champions that action application is affected by existing buffs)
            self.remove_expired_buffs()

            if self.apply_single_action(new_action=new_action):
                break

    def apply_events_after_actions(self, fully_apply_dots=False):
        """
        Applies events after all actions have finished.

        Non permanent dots are refreshed and their events fully applied.
        Applies death to each viable target.

        Modifies:
            current_time
            event_times
            active_buffs
            intermediate_events_changed
        Returns:
            (None)
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

                self.remove_expired_buffs()

                # Applies all dmg effects to alive targets.
                for self.current_target in self.event_times[self.current_time]:
                    if self.current_stats[self.current_target]['current_hp'] > 0:
                        for dmg_name in self.event_times[self.current_time][self.current_target]:
                            self.apply_dmg_or_heal(dmg_name=dmg_name, target_name=self.current_target)

                            # Extends dots.
                            if fully_apply_dots:
                                self.add_next_periodic_event(tar_name=self.current_target,
                                                             dmg_name=dmg_name,
                                                             only_temporary=True)
        # DEATHS
        for tar_name in self.enemy_target_names:
            self.apply_death(tar_name=tar_name)

    def combat_loop(self):
        """
        Returns:
            (None)
        """

        self.current_time = 0

        # Adds runes buff.
        if self.selected_runes:
            self.add_buff(buff_name='runes_buff', tar_name='player')

        # Adds items stats buff.
        if self.chosen_items_lst:
            self.add_buff(buff_name='items_static_stats_buff', tar_name='player')

        # Masteries stats buff
        if self.selected_masteries_dct:
            self.add_buff(buff_name='masteries_static_stats_buff', tar_name='player')

        # Adds hp5 and mp5.
        self.add_regenerations()

        # Adds passive buffs from abilities.
        self.add_passive_buffs(abilities_effects_dct_func=self.abilities_effects, abilities_lvls=self.ability_lvls_dct)

        # Stores precombat stats.
        self.note_pre_combat_stats_in_results()

        # Applies actions or events based on which occurs first.
        self.apply_all_actions()

        # Applies events after all actions have finished.
        self.apply_events_after_actions()

        # Stores postcombat stats.
        self.note_dmg_totals_in_results()
        self.note_post_combat_stats_in_results()


class VisualRepresentation(Actions):

    PLAYER_STATS_DISPLAYED = ('ap', 'ad', 'armor', 'mr', 'hp', 'mp', 'att_speed')
    ENEMY_STATS_DISPLAYED = ('armor', 'mr', 'physical_dmg_taken', 'magic_dmg_taken',)

    def __init__(self,
                 rotation_lst,
                 max_targets_dct,
                 selected_champions_dct,
                 champion_lvls_dct,
                 ability_lvls_dct,
                 max_combat_time,
                 selected_masteries_dct,
                 chosen_items_lst,
                 initial_active_buffs,
                 initial_current_stats,
                 selected_runes):

        Actions.__init__(self,
                         rotation_lst=rotation_lst,
                         max_targets_dct=max_targets_dct,
                         selected_champions_dct=selected_champions_dct,
                         champion_lvls_dct=champion_lvls_dct,
                         ability_lvls_dct=ability_lvls_dct,
                         max_combat_time=max_combat_time,
                         chosen_items_lst=chosen_items_lst,
                         initial_active_buffs=initial_active_buffs,
                         initial_current_stats=initial_current_stats,
                         selected_runes=selected_runes,
                         selected_masteries_dct=selected_masteries_dct)

    @staticmethod
    def __set_table_font_size(table_obj, font_size):
        table_obj.auto_set_font_size(False)
        table_obj.set_fontsize(font_size)

    def subplot_pie_chart_dmg_types(self, subplot_name):

        dmg_values = []
        slice_names = []

        for dmg_total_name in ('total_physical', 'total_magic', 'total_true'):

            # Filters out 0 value dmg.
            if self.combat_results['player'][dmg_total_name] > 0:

                slice_names.append(dmg_total_name.replace('total_', ''))
                dmg_values.append(self.combat_results['player'][dmg_total_name])

        subplot_name.pie(x=dmg_values, labels=slice_names, autopct='%1.1f%%', colors=('r', 'b', 'w'))

    def subplot_pie_chart_sources(self, subplot_name):

        dmg_values = []
        slice_names = []

        for source_name in sorted(self.combat_results['player']['source']):

            # Filters out 0 value dmg.
            if self.combat_results['player']['source'][source_name] > 0:

                slice_names.append(source_name)
                dmg_values.append(self.combat_results['player']['source'][source_name])

        subplot_name.pie(x=dmg_values, labels=slice_names, autopct='%1.1f%%')

    def add_actions_on_plot(self, subplot_name, annotated=True):
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
                subplot_name.annotate(self.actions_dct[x_var]['action_name'], xy=(x_var, -70 + higher_y), color='grey')

            previous_action_name_x = x_var

            # Action vertical lines
            plt.axvline(x=x_var, color='grey', linestyle='dashed', alpha=0.6)

    def subplot_dmg_graph(self, subplot_name):

        subplot_name.grid(b=True)

        # Line at y=0, and at x=0.
        plt.axhline(y=0, color='black')
        plt.axvline(x=0, color='black')

        plt.ylabel('hp')

        color_counter_var = 0
        color_lst = ('b', 'g', 'y', 'orange', 'red')

        # Creates graph for each target.
        for tar_name in self.enemy_target_names:

            hp_change_times = sorted(self.combat_history[tar_name]['current_hp'])
            max_hp = self.request_stat(target_name=tar_name, stat_name='hp')

            # Inserts initial point.
            subplot_name.plot([0], max_hp, color=color_lst[color_counter_var], alpha=0.8,
                              label=tar_name)

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

            subplot_name.plot(x_values, y_values, color=color_lst[color_counter_var], alpha=0.7)
            color_counter_var += 1

        self.add_actions_on_plot(subplot_name=subplot_name, annotated=True)

    def subplot_resource_vamp_lifesteal_graph(self, subplot_name):

        subplot_name.grid(b=True)

        # Line at y=0.
        plt.axhline(y=0, color='black')
        # Line at x=0.
        plt.axvline(x=0, color='black')

        plt.xlabel('time')
        plt.ylabel('value')

        # LIFESTEAL, SPELLVAMP, RESOURCE
        stat_color = {'lifesteal': 'orange', 'spellvamp': 'g', 'resource': 'b'}

        # Places initial resource.
        subplot_name.plot([0], self.request_stat(target_name='player', stat_name=self.resource_used),
                          color=stat_color['resource'], marker='.')

        for examined in stat_color:
            # Inserts each time and value into graph.
            if examined == 'resource':
                # (Sets initial value of resource)
                x_val = [0, ]
                y_val = [self.request_stat(target_name='player', stat_name=self.resource_used), ]

            else:
                x_val = []
                y_val = []

            for event_time in sorted(self.combat_history['player'][examined]):
                x_val.append(event_time)
                y_val.append(self.combat_history['player'][examined][event_time])

            subplot_name.plot(x_val, y_val, color=stat_color[examined], marker='.', label=examined)

        self.add_actions_on_plot(subplot_name=subplot_name, annotated=False)

    def subplot_player_stats_table(self, subplot_name):
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
            precombat_value = round(precombat_value, 4)

            postcombat_value = self.combat_results['player']['post_combat_stats'][stat_name]
            postcombat_value = round(postcombat_value, 4)

            line_tpl = (stat_name+': ', precombat_value, postcombat_value)

            # Inserts in data to be displayed
            table_lst.append(line_tpl)

        subplot_name.axis('off')
        table_obj = subplot_name.table(
            cellText=table_lst,
            cellLoc='left',
            loc='center')

        self.__set_table_font_size(table_obj=table_obj, font_size=8)

    def subplot_enemy_stats_table(self, subplot_name):
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

                precombat_value = self.combat_results[tar_name]['pre_combat_stats'][stat_name]
                precombat_value = round(precombat_value, 4)

                line_tpl = (stat_name+': ', precombat_value)

                # Inserts in data to be displayed
                table_lst.append(line_tpl)

        subplot_name.axis('off')

        table_obj = subplot_name.table(
            cellText=table_lst,
            cellLoc='left',
            loc='center')

        self.__set_table_font_size(table_obj=table_obj, font_size=8)

    def subplot_preset_and_results_table(self, subplot_name):

        # Rotation
        table_lst = [('ROTATION',), (self.rotation_lst,), ('DPS',)]

        # Dps
        dps_value = self.combat_results['player']['dps']
        # (too short combat time results in string dps)
        if type(dps_value) is not str:
            dps_value = round(dps_value, 1)
        table_lst.append((dps_value,))

        # Movement
        table_lst.append(('MOVEMENT',))
        table_lst.append((int(self.total_movement),))

        subplot_name.axis('off')
        table_obj = subplot_name.table(
            cellText=table_lst,
            cellLoc='left',
            loc='center')

        self.__set_table_font_size(table_obj=table_obj, font_size=8)

    def represent_results_visually(self):

        gs = gridspec.GridSpec(3, 3)

        # Graphs
        self.subplot_dmg_graph(subplot_name=plt.figure(1).add_subplot(gs[:1, :1]))
        self.subplot_resource_vamp_lifesteal_graph(subplot_name=plt.figure(1).add_subplot(gs[1:2, :1]))

        # Pies
        self.subplot_pie_chart_dmg_types(subplot_name=plt.figure(1).add_subplot(gs[:1, 1:2]))
        self.subplot_pie_chart_sources(subplot_name=plt.figure(1).add_subplot(gs[:1, 2:3]))

        # Tables
        self.subplot_player_stats_table(subplot_name=plt.figure(1).add_subplot(gs[2, :1]))
        self.subplot_enemy_stats_table(subplot_name=plt.figure(1).add_subplot(gs[2, 1:2]))
        self.subplot_preset_and_results_table(subplot_name=plt.figure(1).add_subplot(gs[2, 2:3]))


if __name__ == '__main__':
    import importlib

    class TestCounters(object):

        def __init__(self,
                     player_champ='jax'):

            """
            Values must NOT be assigned here.
            """

            self.player_champ = player_champ

            self.DELIMITER = '\n' + '-'*100
            self.filtered_stats_max = {'crit_chance': 1., 'speed': None, 'att_speed': 2.5, 'cdr': 0.4}

            self.rotation_lst = None
            self.max_targets_dct = None
            self.selected_champions_dct = None
            self.champion_lvls_dct = None
            self.ability_lvls_dct = None
            self.initial_active_buffs = None
            self.initial_current_stats = None
            self.current_target_num = None
            self.chosen_items_lst = ['hextech_gunblade', 'hextech_gunblade']
            self.selected_runes = None
            self.max_combat_time = None
            self.selected_masteries_dct = None

        def set_up(self):

            self.selected_champions_dct = dict(
                player=self.player_champ,
                enemy_1='jax',
                enemy_2='jax',
                enemy_3='jax')

            self.champion_lvls_dct = dict(
                player=18,
                enemy_1=18,
                enemy_2=17,
                enemy_3=16
            )

            self.ability_lvls_dct = dict(
                q=5,
                w=5,
                e=5,
                r=3)

            self.max_targets_dct = {}

            self.selected_masteries_dct = dict(archmage=3)

        def subclass_jax_actions(self):

            player_champ_name = self.selected_champions_dct['player']
            player_champ_module = importlib.import_module('champions.'+player_champ_name)
            player_champ_tot_attr_class = getattr(player_champ_module, 'ChampionAttributes')

            class CombinerClass(player_champ_tot_attr_class, VisualRepresentation):

                def __init__(self,
                             rotation_lst,
                             max_targets_dct,
                             selected_champions_dct,
                             champion_lvls_dct,
                             ability_lvls_dct,
                             max_combat_time,
                             selected_masteries_dct,
                             initial_active_buffs,
                             initial_current_stats,
                             items_lst=self.chosen_items_lst,
                             selected_runes=self.selected_runes):

                    VisualRepresentation.__init__(self,
                                                  rotation_lst=rotation_lst,
                                                  max_targets_dct=max_targets_dct,
                                                  selected_champions_dct=selected_champions_dct,
                                                  champion_lvls_dct=champion_lvls_dct,
                                                  ability_lvls_dct=ability_lvls_dct,
                                                  max_combat_time=max_combat_time,
                                                  initial_active_buffs=initial_active_buffs,
                                                  initial_current_stats=initial_current_stats,
                                                  chosen_items_lst=items_lst,
                                                  selected_runes=selected_runes,
                                                  selected_masteries_dct=selected_masteries_dct)

                    player_champ_module.ChampionAttributes.__init__(self)

            return CombinerClass

        def test_loop(self, rotation, use_runes=True):

            self.set_up()

            msg = self.DELIMITER

            self.rotation_lst = rotation

            if use_runes:
                self.selected_runes = dict(
                    red=dict(
                        ad_per_lvl=dict(
                            additive=2)))

            inst = self.subclass_jax_actions()(rotation_lst=self.rotation_lst,
                                               max_targets_dct=self.max_targets_dct,
                                               selected_champions_dct=self.selected_champions_dct,
                                               champion_lvls_dct=self.champion_lvls_dct,
                                               ability_lvls_dct=self.ability_lvls_dct,
                                               initial_active_buffs=self.initial_active_buffs,
                                               initial_current_stats=self.initial_current_stats,
                                               selected_runes=self.selected_runes,
                                               max_combat_time=self.max_combat_time,
                                               selected_masteries_dct=self.selected_masteries_dct,)

            msg += '\nTesting method: combat_loop\n'
            msg += '\nrotation: %s\n' % inst.rotation_lst

            # Runs loop.
            inst.combat_loop()

            msg += 'actions dict: %s\n' % sorted(inst.actions_dct)
            msg += 'actions dict: %s\n\n' % inst.actions_dct

            msg += 'active_buffs: %s\n' % inst.active_buffs
            msg += 'player active_buffs: %s\n\n' % inst.active_buffs['player']

            msg += 'player att_speed: %s\n' % inst.request_stat(target_name='player', stat_name='att_speed')

            if use_runes:
                msg += 'used runes: %s\n' % inst.runes_buff()
                msg += 'player ad: %s\n' % inst.request_stat(target_name='player', stat_name='ad')

            msg += 'enemy_1: \nmax hp: %s, ' % inst.request_stat(target_name='enemy_1', stat_name='hp')
            msg += ('enemy_1 current_stats: %s \n'
                    'all current_stats: %s\n') % (inst.current_stats['enemy_1'], inst.current_stats)

            msg += '\ncombat_history: %s' % inst.combat_history

            msg += '\ntotal dmg types: %s' % inst.refined_combat_history()

            msg += '\ntimes of death: %s' % inst.times_of_death()

            msg += '\ntotal movement distance: %s' % str(inst.total_movement)

            return msg

        def test_dmg_graphs(self, rotation_lst, item_lst):
            self.set_up()

            self.chosen_items_lst = item_lst

            inst = self.subclass_jax_actions()(rotation_lst=rotation_lst,
                                               max_targets_dct=self.max_targets_dct,
                                               selected_champions_dct=self.selected_champions_dct,
                                               champion_lvls_dct=self.champion_lvls_dct,
                                               max_combat_time=self.max_combat_time,
                                               ability_lvls_dct=self.ability_lvls_dct,
                                               initial_active_buffs=self.initial_active_buffs,
                                               initial_current_stats=self.initial_current_stats,
                                               selected_runes=self.selected_runes,
                                               selected_masteries_dct=self.selected_masteries_dct)

            inst.combat_loop()
            inst.add_dmg_tot_history()

            msg = '\nrotation: %s\n' % inst.rotation_lst
            msg += '\ntotal dmg types: %s' % inst.refined_combat_history()
            msg += '\ntimes of death: %s' % inst.times_of_death()
            msg += '\nactions: %s' % sorted(inst.actions_dct)
            msg += '\ndps: %s' % inst.dps()
            msg += '\nmax mp: %s, current_mp: %s' % (inst.request_stat('player', 'mp'),
                                                     inst.current_stats['player']['current_mp'])

            msg += '\nlifesteal: %s, spellvamp: %s' % (inst.request_stat('player', 'lifesteal'),
                                                       inst.request_stat('player', 'spellvamp'))

            msg += '\nlifesteal history: %s' % inst.combat_history['player']['lifesteal']

            msg += '\ntotal movement distance: %s' % str(inst.total_movement)

            msg += '\nhistory: %s' % inst.combat_history['enemy_1']['current_hp']

            print(msg)

            inst.represent_results_visually()
            plt.show()

            del inst.combat_results['player']['pre_combat_stats']
            del inst.combat_results['player']['post_combat_stats']

        def __repr__(self):

            msg = self.DELIMITER

            msg += self.test_loop(['q'])
            msg += self.DELIMITER

            # At 3 AAs there should be more dmg from passive R.
            msg += self.test_loop(['AA', 'AA', 'AA'])
            msg += self.DELIMITER

            # Time between AAs should become progressively shorter up to 6 AAs because of att_speed increase.
            msg += self.test_loop(['AA', 'AA', 'AA', 'AA', 'AA', 'AA'])
            msg += self.DELIMITER

            # Action 'w' on its own does not cause dmg.
            msg += self.test_loop(['w', 'w'])
            msg += self.DELIMITER

            # AA after 'w' causes aa_dmg plus w_dmg.
            msg += self.test_loop(['w', 'AA'])
            msg += self.DELIMITER

            msg += self.test_loop(['w', 'AA', 'q', 'w', 'AA'])
            msg += self.DELIMITER

            msg += self.test_loop(['AA', 'AA', 'e'])
            msg += self.DELIMITER

            # Since Jax's E is AoE it causes dmg to other targets as well.
            # Also, its total dmg is 3 times greater than single.
            msg += self.test_loop(['e'])
            msg += self.DELIMITER

            msg += self.test_loop(['e'], use_runes=True)
            msg += self.DELIMITER

            # When a target dies it switches to next target until all targets are dead.
            msg += self.test_loop(['AA', 'w', 'AA', 'AA', 'AA', 'AA', 'AA', 'AA', 'w', 'AA', 'AA', 'AA'])
            msg += self.DELIMITER

            return msg

    print(TestCounters())

    rot1 = ['e', 'r', 'q', 'AA', 'w', 'AA', 'AA', 'hextech_gunblade', 'AA', 'AA', 'AA', 'AA', 'AA', 'w', 'AA', 'AA',
            'AA', 'AA', 'w', 'AA', 'q']
    rot2 = ['w', 'AA', 'e', 'AA', 'AA', 'AA']
    rot3 = ['AA', 'AA', 'AA']
    rot4 = ['AA']
    rot5 = ['e', 'e']
    rot6 = ['q', 'AA']
    rot7 = ['q', 'q']

    itemLst0 = []
    itemLst1 = ['hextech_gunblade']
    itemLst2 = ['hextech_gunblade', 'hextech_gunblade']

    if 1:
        TestCounters().test_dmg_graphs(rotation_lst=rot1, item_lst=itemLst2)

    if 0:
        # Crude time testing.
        import cProfile
        test_text = 'TestCounters().test_loop(rotation=rot1, use_runes=True)\n'*100
        cProfile.run(test_text, 'cprof_results', sort='cumtime')

        import pstats
        results_run = pstats.Stats('cprof_results').sort_stats('cumtime')
        results_run.strip_dirs().sort_stats('cumtime').print_stats(5)
        # print(results_run.strip_dirs().sort_stats('cumtime').stats)


# rot1, itemLst2
# dps: 331.07415420245394 (after changing dps method)
# dps: 338.4234113818222 (unexpected change, after changing bonus_ad method to get stats by 'evaluate' instead of direct)
# dps: 414.08610981856975 (rotation and targets changed) 1.1sec / 100 rotations
# dps: 414.1, 2434 movement, 1.1sec / 100 rotations
# MAJOR CHANGES
# dps: 320.3, 2631 movement, 2.8sec / 100 rotations
# dps: 336.8, 2463 movement, 2.9sec / 100 rotations (fixed inn buff)
# dps: 331.2, 2463 movement, 2.9sec / 100 rotations (changed base and bonus stat methods)
# dps: 333.7, 2463 movement, 2.9sec / 100 rotations (masteries used)
