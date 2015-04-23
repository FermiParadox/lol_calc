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

    def leafs_of_item(self, item_name):
        """
        Returns items' names that are build from given item and are part of the chosen build.

        :param item_name: (str)
        :return: (set)
        """

        return self.items_attrs_dct[item_name]['secondary_data']['leafs'] & set(self.chosen_items_lst)

    def unique_stats_in_leafs_of_item(self, item_name):
        """
        Returns a dict of all additive and all percent unique stats' names of an item's leafs.

        :param item_name: (str)
        :return: (dict)
        """
        used_leafs = self.leafs_of_item(item_name)
        returned_dct = {'additive': [], 'percent': []}

        # For each leaf-item..
        for leaf in used_leafs:
            leaf_dct = self.items_attrs_dct[leaf]
            # ..for each stat type..
            for stat_type in leaf_dct:
                # ..creates a list of the stat names and adds it in existing results.
                returned_dct[stat_type] += list(leaf_dct['unique_stats'][stat_type].keys())

        return returned_dct

    def non_roots_in_build(self):
        """
        Returns items that are not the base for any of items in current build.

        :return: (list)
        """

        all_roots = {}
        for item in self.chosen_items_lst:
            all_roots |= items_data_module.ITEMS_ATTRIBUTES[item]['secondary_stats']

        return set(self.chosen_items_lst) - all_roots

    def _create_items_properties_dcts(self):
        """
        Creates final dicts (effects, attributes, dmgs, buffs, conditions) for current item build.

        :return: (None)
        """

        for item_name in self.chosen_items_lst:
            item_attrs = self.items_attrs_dct[item_name]
            item_effects = self.items_effects_dct[item_name]
            item_conditions = self.items_conditions_dct[item_name]

            # NON UNIQUE STATS
            item_non_unique_stats = item_attrs['non_unique_stats']
            for stat_type in item_non_unique_stats:
                self.non_unique_stats_dct[stat_type] += collections.Counter(item_non_unique_stats[stat_type])

            # UNIQUE STATS
            # If item A (leaf) builds from item B, then unique stats from B that are included in A are ignored.
            unique_stats_dct = item_attrs['unique_stats']
            leafs_stats = self.unique_stats_in_leafs_of_item(item_name=item_name)

            for stat_type in unique_stats_dct:
                for stat_name in unique_stats_dct[stat_type]:
                    # If stat is no inside leafs' stats.
                    if stat_name not in leafs_stats[stat_type]:
                        self.unique_stats_dct[stat_type].update({stat_name: unique_stats_dct[stat_type][stat_name]})

            # EFFECTS
            # Root effects are ignored, since leaf is (assumed to) override them.




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

    testUniqueLeafsUniqueStats = True
    if testUniqueLeafsUniqueStats:
        g = ItemsProperties(['hextech_gunblade', 'dorans_blade']).unique_stats_in_leafs_of_item(item_name='dorans_blade')
        print(g)