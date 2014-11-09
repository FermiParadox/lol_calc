import math
import copy


class DifferentCombinations(object):
    """Calculates possible combinations for items, runes, masteries, champions.
    """
    ITEM_SLOTS = 6

    RED_SLOTS = 9
    YELLOW_SLOTS = 9
    BLUE_SLOTS = 9
    QUINT_SLOTS = 3

    def __init__(self,
                 different_items,

                 different_red,
                 different_yellow,
                 different_blue,
                 different_quint,

                 champions,
                 ):

        self.different_items = different_items
        self.different_red = different_red
        self.different_yellow = different_yellow
        self.different_blue = different_blue
        self.different_quint = different_quint
        self.champions = champions

    @staticmethod
    def ordered_combinations(n, k):
        """Returns total combinations if there are n different elements and k choices,
        when element order is irrelevant.
        """
        return math.factorial(n) / (math.factorial(k) * math.factorial(n-k))

    def item_combinations(self):
        return self.ordered_combinations(n=self.different_items, k=self.ITEM_SLOTS)

    def total_rune_combinations(self):

        k_name = lambda color: getattr(self, color.upper() + '_SLOTS')
        n_name = lambda color: getattr(self, 'different_' + color)

        combinations = lambda color: self.ordered_combinations(n=n_name(color), k=k_name(color))

        tot_combs = 1

        for color_name in ('red', 'blue', 'yellow', 'quint'):
            tot_combs *= combinations(color_name)

        return tot_combs

    def total_combinations(self):
        return self.total_rune_combinations() * self.item_combinations() * self.champions

    def __repr__(self):
        msg = '\nitem combinations: %s' % '{:.2e}'.format(self.item_combinations())

        msg += '\nrune combinations: %s' % '{:.2e}'.format(self.total_rune_combinations())

        msg += '\nTOTAL COMBINATIONS: %s' % '{:.2e}'.format(self.total_combinations())

        return msg


class NormalCombinations(object):

    SETUP_PARAMETERS = dict(
        # ITEMS
        different_items=273,

        # RUNES
        different_red=12,
        different_yellow=12,
        different_blue=12,
        different_quint=12,

        # CHAMPIONS
        champions=119,)

    def instance(self):

        return DifferentCombinations(**self.SETUP_PARAMETERS)

    def __repr__(self):
        msg = '\n-----------------------------'
        msg += '\nNORMAL COMBINATIONS'

        msg += self.instance().__repr__()

        return msg


class ManalessCombinations(object):

    SETUP_PARAMETERS = copy.deepcopy(NormalCombinations.SETUP_PARAMETERS)
    SETUP_PARAMETERS['champions'] -= 19

    SETUP_PARAMETERS['different_items'] -= 2

    SETUP_PARAMETERS['different_red'] -= 2
    SETUP_PARAMETERS['different_yellow'] -= 2
    SETUP_PARAMETERS['different_blue'] -= 2
    SETUP_PARAMETERS['different_quint'] -= 2

    def instance(self):

        return DifferentCombinations(**self.SETUP_PARAMETERS)

    def __repr__(self):
        msg = '\n-----------------------------'
        msg += '\nMANALESS COMBINATIONS'

        msg += self.instance().__repr__()

        return msg


if __name__ == '__main__':

    print(NormalCombinations())
    print(ManalessCombinations())