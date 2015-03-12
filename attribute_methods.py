import ast


class AttributeBase(object):

    def __init__(self, current_target, active_buffs):
        self.current_target = current_target
        self.active_buffs = active_buffs

    def _x_value(self, x_name, x_type, x_owner):
        """
        Searches value of x based

        Returns:
            (num)
        """

        if x_owner == 'player':
            owner = x_owner
        else:
            owner = self.current_target

        if x_type == 'buff':
            buff_act_dct = self.active_buffs[owner][x_name]

            try:
                val = buff_act_dct['current_stacks']



    def _formula_to_value(self, formula, x_name, x_type, x_owner):
        """

        """

        try:
            value = ast.literal_eval(formula)
            return value

        except NameError:

            x = self._x_value(x_name, x_type, x_owner)







    def abilities_effects(self):

        return self.ABILITIES_EFFECTS