import dmgs_buffs_categories
import copy
import operator


class ChampionAttributeBase(dmgs_buffs_categories.DmgCategories):

    def __init__(self,
                 current_target,
                 act_buffs,
                 ability_lvls_dct,
                 req_stats_func,
                 current_stats,
                 champion_lvls_dct,
                 current_target_num,):

        self.current_target = current_target
        self.act_buffs = act_buffs
        self.ability_lvls_dct = ability_lvls_dct
        self.request_stat = req_stats_func
        self.current_stats = current_stats
        self.champion_lvls_dct = champion_lvls_dct
        self.current_target_num = current_target_num

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
            if x_name in self.act_buffs[owner]:
                return self.act_buffs[owner][x_name]['current_stacks']
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

    def _ability_effect_creator(self, eff_dct, modified_dct, ability_name):
        """
        Checks given effect dict for ability name and correct effect_type.
        If so, creates appropriate ability effect dict.

        Returns:
            (None)
        """

        if eff_dct['effect_type'] == 'ability_effect':

            # Then checks if a new dct has been created.
            if not modified_dct:
                modified_dct = copy.deepcopy(self.ABILITIES_EFFECTS[ability_name])

            # DATA MODIFICATION
            tar_type = eff_dct['tar_type']
            mod_operation = eff_dct['mod_operation']
            cat_type = eff_dct['category']
            eff_contents = eff_dct['names_lst']

            # (it always modifies actives)

            if mod_operation == 'append':
                modified_dct[ability_name][tar_type]['actives'][cat_type] += eff_contents
            elif mod_operation == 'replace':
                modified_dct[ability_name][tar_type]['actives'][cat_type] = eff_contents

    def abilities_effects(self, ability_name):
        """
        Checks if ability effects are affected by any conditionals.
        If not, returns member variable dict. Otherwise returns different version of the dict.

        Returns:
            (dict)
        """

        new_dct = {}
        # Checks if given ability name has conditions affecting its effects.
        for cond in self.ABILITIES_CONDITIONS:
            for eff in self.ABILITIES_CONDITIONS[cond]['effects']:

                eff_dct = self.ABILITIES_CONDITIONS[cond]['effects'][eff]
                if ability_name == eff_dct['ability_name']:
                    self._ability_effect_creator(eff_dct=eff_dct, modified_dct=new_dct, ability_name=ability_name)

        if new_dct:
            return new_dct
        else:
            return self.ABILITIES_EFFECTS

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
        elif mod_operation == 'multiply':
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

    def _abilities_attr_creator(self, eff_dct, modified_dct, ability_name):
        """
        Checks given effect dict for ability name and correct effect_type.
        If so, creates appropriate ability attr dict.

        Args:
            modified_dct: It is the new dict given instead of the static member variable dict.
        Returns:
            (None)
        """

        if eff_dct['effect_type'] == 'ability_attrs':

            # Then checks if a new dct has been created.
            if not modified_dct:
                modified_dct = copy.deepcopy(self.ABILITIES_ATTRIBUTES['general_attributes'][ability_name])

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

            modified_dct[ability_name][attr_name] = self._modified_attr_value(mod_operation=mod_operation,
                                                                              mod_val=mod_val,
                                                                              old_val=modified_dct[ability_name][attr_name])

    def abilities_attributes(self, ability_name):
        """
        Checks if ability attributes are affected by any conditionals.
        If not, returns member variable dict. Otherwise returns different version of the dict.

        Returns:
            (dict)
        """

        new_dct = {}
        # Checks if given ability name has conditions affecting its effects.
        for cond in self.ABILITIES_CONDITIONS:
            for eff in self.ABILITIES_CONDITIONS[cond]['effects']:

                eff_dct = self.ABILITIES_CONDITIONS[cond]['effects'][eff]
                if ability_name == eff_dct['ability_name']:
                    self._abilities_attr_creator(eff_dct=eff_dct,
                                                 modified_dct=new_dct, ability_name=ability_name)

        if new_dct:
            return new_dct
        else:
            return self.ABILITIES_ATTRIBUTES['general_attributes']



child_class_as_str = """class ChampionAttributes(attribute_methods.ChampionAttributeBase):
    DEFAULT_ACTIONS_PRIORITY = ()
    ABILITIES_ATTRIBUTES = ABILITIES_ATTRIBUTES
    ABILITIES_EFFECTS = ABILITIES_EFFECTS
    ABILITIES_CONDITIONS = ABILITIES_CONDITIONS
    def __init__(self, kwargs, external_vars_dct=CHAMPION_EXTERNAL_VARIABLES):
        for i in external_vars_dct:
            setattr(ChampionAttributes, i, external_vars_dct[i])
        super().__init__(**kwargs)"""