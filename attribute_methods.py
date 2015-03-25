import dmgs_buffs_categories
import copy
import operator
import palette


class ChampionAttributeBase(dmgs_buffs_categories.DmgCategories):

    OPERATORS_STR_MAP = {
        '<': operator.lt,
        '<=': operator.le,
        '==': operator.eq,
        '!=': operator.ne,
        '>=': operator.ge,
        '>': operator.gt,
        }

    # Matches object types to object key names in abilities effects dct.
    EFF_TYPE_TO_OBJ_KEY_NAME_MAP = {
        'ability_effect': 'ability_name',
        'ability_attr': 'ability_name',

    }

    # ("abstract" class variables)
    ABILITIES_ATTRIBUTES = None
    ABILITIES_EFFECTS = None
    ABILITIES_CONDITIONS = None

    def __init__(self,
                 current_target,
                 act_buffs,
                 ability_lvls_dct,
                 req_stats_func,
                 current_stats,
                 champion_lvls_dct,
                 current_target_num,
                 action_on_cd_func,
                 ):

        self.current_target = current_target
        self.ability_lvls_dct = ability_lvls_dct
        self.request_stat = req_stats_func
        self.current_stats = current_stats
        self.champion_lvls_dct = champion_lvls_dct
        self.current_target_num = current_target_num
        self.action_on_cd_func = action_on_cd_func

        dmgs_buffs_categories.DmgCategories.__init__(self,
                                                     req_stats_func=req_stats_func,
                                                     current_stats=current_stats,
                                                     current_target=current_target,
                                                     champion_lvls_dct=champion_lvls_dct,
                                                     current_target_num=current_target_num,
                                                     active_buffs=act_buffs)

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

        return self.OPERATORS_STR_MAP[operator_as_str](trig_val, checked_val)

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
        Checks if all triggers for given condition are present.

        Returns:
            (bool)
        """

        triggers_dct = self.ABILITIES_CONDITIONS[cond_name]['triggers']

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

    def _ability_effects_creator(self, eff_dct, modified_dct, ability_name):
        """
        Creates new ability effects dct or updates existing with changes caused by effects.

        Args:
            modified_dct: It is the new dict given instead of the static class variable dict.

        Returns:
            (None)
        """

        # Then checks if new dict is empty.
        if not modified_dct:
            modified_dct = copy.deepcopy(self.ABILITIES_EFFECTS[ability_name])

        # DATA MODIFICATION
        tar_type = eff_dct['tar_type']
        mod_operation = eff_dct['mod_operation']
        cat_type = eff_dct['lst_category']
        eff_contents = eff_dct['names_lst']

        # (it always modifies actives)

        if mod_operation == 'append':
            modified_dct[ability_name][tar_type]['actives'][cat_type] += eff_contents
        elif mod_operation == 'replace':
            modified_dct[ability_name][tar_type]['actives'][cat_type] = eff_contents

    def _on_hit_effect_buff_creator(self, eff_dct, modified_dct, buff_name):
        """
        Creates new buff dct or updates existing with changes caused by effects.

        Args:
            modified_dct: It is the new dict given instead of the static class variable dict.

        Returns:
            (None)
        """

        # Checks if modified dct is empty.
        if not modified_dct:
            modified_dct = copy.deepcopy(self.ABILITIES_ATTRIBUTES['buffs'][buff_name])

        # DATA MODIFICATION
        mod_operation = eff_dct['mod_operation']
        eff_contents = eff_dct['names_lst']
        cat_type = eff_dct['lst_category']

        if mod_operation == 'append':
            modified_dct[buff_name]['on_hit'][cat_type] += eff_contents
        elif mod_operation == 'replace':
            modified_dct[buff_name]['on_hit'][cat_type] = eff_contents

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

    def _attr_creator(self, eff_dct, modified_dct, obj_name, obj_category):
        """
        Creates new attrs dct or updates existing with changes caused by effects.

        Args:
            modified_dct: It is the new dict given instead of the static class variable dict.
            obj_category: 'general_attributes', 'buffs', 'dmgs'
        Returns:
            (None)
        """

        # Checks if modified dct is empty.
        if not modified_dct:
            modified_dct = copy.deepcopy(self.ABILITIES_ATTRIBUTES[obj_category][obj_name])

        # DATA MODIFICATION
        mod_operation = eff_dct['mod_operation']
        attr_name = eff_dct['attr_name']
        if eff_dct['formula_type'] == 'constant_value':
            mod_val = eff_dct['values_tpl']
        else:
            mod_val = self._x_formula_to_value(x_formula=eff_dct['x_formula'],
                                               x_name=eff_dct['x_name'],
                                               x_type=eff_dct['x_type'],
                                               x_owner=eff_dct['x_owner'],)

        modified_dct[obj_name][attr_name] = self._modified_attr_value(mod_operation=mod_operation,
                                                                      mod_val=mod_val,
                                                                      old_val=modified_dct[obj_name][attr_name])

    def _ability_attr_or_eff_base(self, obj_name, searched_effect_type, main_dct):
        """
        Loops each condition. Then each effect of a condition.
        If single effect of interest is detected, all triggers for given condition are checked.
        If trigger state is false, condition stops being checked.

        Args:
            obj_name: (str) name of the buff, dmg, or ability
            obj_name_dct_key: (str) 'ability_name', 'buff_name', 'dmg_name'
                                    Name of the key pointing to the object name.
            searched_effect_type: (str) 'ability_attr', 'ability_effect', 'buff' or 'dmg'
                                        Name of effect type being searched for.

        Returns:
            (dict)
        """

        obj_name_dct_key = self.EFF_TYPE_TO_OBJ_KEY_NAME_MAP[searched_effect_type]

        new_dct = {}
        # Checks if given ability name has conditions affecting its effects
        # All effects of all conditions on an element are applied one after the other.
        for cond in main_dct:

            trig_state = None
            for eff in main_dct[cond]['effects']:

                eff_dct = main_dct[cond]['effects'][eff]
                if obj_name == eff_dct[obj_name_dct_key]:

                    # Trigger check is done once,
                    # right after a single effect affecting given object is detected.
                    if trig_state is None:
                        trig_state = self._check_triggers_state(cond_name=cond)
                        # (if triggers are false, ends current condition checks)
                        if trig_state is False:
                            break

                    if searched_effect_type == 'ability_effect':
                        self._ability_effects_creator(eff_dct=eff_dct, modified_dct=new_dct, ability_name=obj_name)

                    elif searched_effect_type == 'ability_attr':
                        self._attr_creator(eff_dct=eff_dct, modified_dct=new_dct, obj_name=obj_name,
                                           obj_category='general_attributes')

                    elif searched_effect_type == 'buff':
                        self._attr_creator(eff_dct=eff_dct, modified_dct=new_dct, obj_name=obj_name,
                                           obj_category='buffs')
                        self._on_hit_effect_buff_creator(eff_dct=eff_dct, modified_dct=new_dct, buff_name=obj_name)

                    elif searched_effect_type == 'dmg':
                        self._attr_creator(eff_dct=eff_dct, modified_dct=new_dct, obj_name=obj_name,
                                           obj_category='dmgs')
                    else:
                        raise palette.UnexpectedValueError

        if new_dct:
            return new_dct
        else:
            return main_dct[obj_name]

    def abilities_effects(self, ability_name):
        """
        Checks if ability effects are affected by any conditionals.
        If not, returns member variable dict. Otherwise returns different version of the dict.

        Returns:
            (dict)
        """

        return self._ability_attr_or_eff_base(obj_name=ability_name,
                                              searched_effect_type='ability_effect', main_dct=self.ABILITIES_EFFECTS)

    def abilities_attributes(self, ability_name):
        """
        Checks if ability attributes are affected by any conditionals.
        If not, returns member variable dict. Otherwise returns different version of the dict.

        Returns:
            (dict)
        """

        return self._ability_attr_or_eff_base(obj_name=ability_name,
                                              searched_effect_type='ability_attr', main_dct=self.ABILITIES_ATTRIBUTES)

    def request_buff(self, buff_name):
        """
        Returns buff dict after checking possible conditionals.

        Buffs can be related to champion, item, mastery, summoner spells, dragon, baron.

        Returns:
            (dict)
        """

        return self._ability_attr_or_eff_base(obj_name=buff_name,
                                              searched_effect_type='buff',
                                              main_dct=self.ABILITIES_EFFECTS)

    def request_dmg(self, buff_name):
        """
        Returns buff dict after checking possible conditionals.

        Buffs can be related to champion, item, mastery, summoner spells, dragon, baron.

        Returns:
            (dict)
        """

        return self._ability_attr_or_eff_base(obj_name=buff_name,
                                              searched_effect_type='dmg',
                                              main_dct=self.ABILITIES_EFFECTS)


child_class_as_str = """class ChampionAttributes(object):
    DEFAULT_ACTIONS_PRIORITY = ()
    ABILITIES_ATTRIBUTES = ABILITIES_ATTRIBUTES
    ABILITIES_EFFECTS = ABILITIES_EFFECTS
    ABILITIES_CONDITIONS = ABILITIES_CONDITIONS
    def __init__(self, external_vars_dct=CHAMPION_EXTERNAL_VARIABLES):
        for i in external_vars_dct:
            setattr(ChampionAttributes, i, external_vars_dct[i])"""