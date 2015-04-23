import items.items_data as items_data_module
import collections


class ItemsProperties(object):

    def __init__(self, chosen_items_lst):
        self.chosen_items_lst = chosen_items_lst
        self.non_unique_stats_dct = {'additive': collections.Counter(), 'percent': collections.Counter()}
        self.unique_stats_dct = {'additive': collections.Counter(), 'percent': collections.Counter()}
        self.items_attrs_dct = items_data_module.ITEMS_ATTRIBUTES
        self.items_effects_dct = items_data_module.ITEMS_EFFECTS
        self.items_conditions_dct = items_data_module.ITEMS_CONDITIONS

    def leafs_used(self, item_name):
        """
        Returns items' names that are build from given item and are part of the chosen build.

        :param item_name: (str)
        :return: (set)
        """

        return self.items_attrs_dct[item_name]['secondary_data']['leafs'] & set(self.chosen_items_lst)

    def _create_items_properties_dcts(self):
        """
        Creates final dicts (effects, attributes, dmgs, buffs, conditions) for given item build.

        :return: (None)
        """

        for item_name in self.chosen_items_lst:
            item_attrs = self.items_attrs_dct[item_name]
            item_effects = self.items_effects_dct[item_name]
            item_conditions = self.items_conditions_dct[item_name]

            # Stacking stats.
            item_non_unique_stats = item_attrs['non_unique_stats']
            for stat_type in item_non_unique_stats:
                self.non_unique_stats_dct[stat_type] += collections.Counter(item_non_unique_stats[stat_type])

            # Unique stats.
            unique_stats_dct = item_attrs['unique_stats']
            for stat_type in item_non_unique_stats:
                self.unique_stats_dct[stat_type] += collections.Counter(unique_stats_dct[stat_type])





    def items_(self):
        pass

    def items_effects(self):
        pass

    def items_conditions(self):
        pass

    def build_price(self):
        """
        Calculates cost of all items in given item build.

        :return: (int)
        """

        cost = 0

        for item_name in self.chosen_items_lst:
            cost += items_data_module.ITEMS_ATTRIBUTES[item_name]['secondary_data']['total_price']

        return cost






if __name__ == '__main__':

    testBuildCost = True
    if testBuildCost:
        g = ItemsProperties(['hextech_gunblade', 'dorans_blade']).build_price()
        print(g)