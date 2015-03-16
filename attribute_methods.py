class AttributeBase(object):

    def __init__(self,
                 current_target,
                 active_buffs,
                 ability_lvls_dct,
                 request_stat_func):

        self.current_target = current_target
        self.active_buffs = active_buffs
        self.ability_lvls_dct = ability_lvls_dct
        self.request_stat = request_stat_func

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

    def _formula_to_value(self, formula, x_name, x_type, x_owner, formula_type):
        """
        Converts condition trigger formula to value.

        Returns:
            (str)
            (bool)
            (num)
            (sequence)
            (None)
        """

        if formula_type == 'constant_value':
            return eval(formula)

        else:
            x = self._x_value(x_name, x_type, x_owner)
            return eval(formula)

    def abilities_effects(self):
        """
        Checks if ability effects are affected by any conditionals.
        If not, returns member variable dict. Otherwise returns different version of the dict.
        """

        return self.ABILITIES_EFFECTS

