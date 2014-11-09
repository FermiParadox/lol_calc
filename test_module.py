"""Contains classes that test each module.
"""


class TestChampionStats(object):

    """
    Tests if the base stats of a champion are within reasonable limits.
    """

    def __init__(self, champion_name):
        """
        (string)
        """
        self.champion_name = champion_name

    @staticmethod
    def standard_base_stats():
        """Returns dictionary containing lists.

        Each list contains a stat value considered normal,
        and a modifier defining the max and min for accepted values.
        """
        # TODO: add energy, rage etc.
        return dict(
            hp=[463, 2],
            hp_per_lvl=[98, 2],

            hp5=[7.45, 3],
            hp5_per_lvl=[0.55, 5],

            mana=[230, 4],
            mana_per_lvl=[35, 6],

            mp5=[6.4, 6],
            mp5_per_lvl=[0.7, 6],

            range=[300, 4],

            ad=[56.3, 2],
            ad_per_lvl=[3.375, 4],

            base_att_speed=[0.638, 3],
            att_speed_per_lvl=[3.4/100., 3],

            armor=[22, 3],
            armor_per_lvl=[3.5, 2],

            magic_resist=[30, 1],   # magic_resist is the same for all champions
            magic_resist_per_lvl=[0.5, 3],
            speed=[350, 1.5]
        )

    def imported_module_name(self):
        """Returns the module.
        """
        return __import__(self.champion_name)

    def champ_base_stats(self):
        """Returns dictionary, containing champion's base stats.
        """
        return getattr(self.imported_module_name(), 'CHAMPION_BASE_STATS')

    def test_champ_base_stats(self):
        """
        () -> string

        Returns 'Champion base stat Error: ' or 'No Champion base stat errors detected'.
        Checks if champion stats have values withing specific boundaries.

        """
        wrong_stats_lst = []

        for stat in self.champ_base_stats():

            if stat in self.standard_base_stats():

                stat_value = self.champ_base_stats()[stat]
                upper_limit = self.standard_base_stats()[stat][0] * self.standard_base_stats()[stat][1]
                lower_limit = self.standard_base_stats()[stat][0] / float(self.standard_base_stats()[stat][1])
                if (stat_value < lower_limit) or (stat_value > upper_limit):
                    wrong_stats_lst.append(stat)

        # Checks range_type
        if self.champ_base_stats()['range_type'] != 'ranged':
            if self.champ_base_stats()['range_type'] != 'melee':
                wrong_stats_lst.append(self.champ_base_stats()['range_type'])

        # Returns a string based on errors found.
        if not wrong_stats_lst:
            return '%s base stats: Ok.' % self.champion_name
        else:
            error_message = ('%s base stats: Error\n'
                             'Wrong stats: ' + ''.join(wrong_stats_lst)) % self.champion_name
            return error_message

    def __repr__(self):
        return '\n%s\n' % self.test_champ_base_stats()


if __name__ == '__main__':
    print(TestChampionStats('jax'))