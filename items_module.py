import items_folder.items_data as items_data_module
import palette

import collections


CHOSEN_ITEMS_AND_MASTERIES_BUFF_BASE = palette.buff_dct_base_deepcopy()
CHOSEN_ITEMS_AND_MASTERIES_BUFF_BASE['duration'] = 'permanent'
CHOSEN_ITEMS_AND_MASTERIES_BUFF_BASE['max_stacks'] = 1
CHOSEN_ITEMS_AND_MASTERIES_BUFF_BASE['on_hit'] = None
CHOSEN_ITEMS_AND_MASTERIES_BUFF_BASE['prohibit_cd_start'] = None
CHOSEN_ITEMS_AND_MASTERIES_BUFF_BASE['dot'] = None
# (deleted so that a dict can be created later on that will have this dict updated in it as a reference)
del CHOSEN_ITEMS_AND_MASTERIES_BUFF_BASE['stats']
del CHOSEN_ITEMS_AND_MASTERIES_BUFF_BASE['target_type']
del CHOSEN_ITEMS_AND_MASTERIES_BUFF_BASE['buff_source']


class ItemsProperties(object):

    ITEMS_BUFFS_NAMES = items_data_module.ITEMS_BUFFS_NAMES
    ITEMS_DMGS_NAMES = items_data_module.ITEMS_DMGS_NAMES
    ITEMS_ATTRIBUTES = items_data_module.ITEMS_ATTRIBUTES
    ITEMS_EFFECTS = items_data_module.ITEMS_EFFECTS
    ITEMS_CONDITIONALS = items_data_module.ITEMS_CONDITIONALS

    _CHOSEN_ITEMS_BUFF_BASE = CHOSEN_ITEMS_AND_MASTERIES_BUFF_BASE

    def __init__(self, chosen_items_lst):
        self.chosen_items_lst = chosen_items_lst

        self.items_static_stats_buff_dct = {}

        self._create_items_properties_dcts()

    def leafs_of_item(self, item_name):
        """
        Returns items' names that are build from given item and are part of the chosen build.

        :param item_name: (str)
        :return: (set)
        """

        return self.ITEMS_ATTRIBUTES[item_name]['secondary_data']['leafs'] & set(self.chosen_items_lst)

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
            leaf_dct = self.ITEMS_ATTRIBUTES[leaf]
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

        all_roots = set()
        for item in self.chosen_items_lst:
            all_roots |= items_data_module.ITEMS_ATTRIBUTES[item]['secondary_data']['roots']

        return set(self.chosen_items_lst) - all_roots

    @staticmethod
    def check_effects_empty(effects_dct):
        """
        Checks the effects of an item or ability, determining if they are completely empty.

        :param effects_dct:
        :return: (bool)
        """

        for key_1 in effects_dct:
            for key_2 in effects_dct[key_1]:
                for key_3 in effects_dct[key_1][key_2]:
                    if effects_dct[key_1][key_2][key_3]:
                        # (A single non empty ends method).
                        return True

        else:
            return False

    @staticmethod
    def _total_items_stats(non_unique_stats_dct, used_items_unique_stats_dct):
        """
        Creates a dict with all unique and non-unique stats from chosen items.

        :return: (dict)
        """

        # COMBINES UNIQUE AND NON-UNIQUE STATS
        additive_stats_dct = collections.Counter()
        percent_stats_dct = collections.Counter()

        for dct in (non_unique_stats_dct, used_items_unique_stats_dct):

            additive_stats_dct += dct['additive']
            percent_stats_dct += dct['percent']

        combined_stats_dct = {'additive': additive_stats_dct, 'percent': percent_stats_dct}

        # CONVERTS THEM TO DIFFERENT FORMAT
        # (type-name-val to name-type-val)
        final_dct = {}

        for stat_type in combined_stats_dct:

            stats_of_given_type_dct = combined_stats_dct[stat_type]
            for stat_name in stats_of_given_type_dct:

                stat_val = stats_of_given_type_dct[stat_name]

                # If stat name doesn't exist in final dict, it creates it.
                final_dct.setdefault(stat_name, {})

                # If type doesnt exist, it creates it.
                stat_final_dct = final_dct[stat_name]
                stat_final_dct.setdefault(stat_type, 0)

                stat_final_dct[stat_type] += stat_val

        return final_dct

    def _set_chosen_items_static_stats_buff(self, non_unique_stats_dct, used_items_unique_stats_dct):
        """
        Creates a buff containing all passive stats of chosen items.

        :return: (None)
        """

        stats_dct = self._total_items_stats(non_unique_stats_dct=non_unique_stats_dct,
                                            used_items_unique_stats_dct=used_items_unique_stats_dct)

        returned_dct = {'stats': stats_dct, 'buff_source': 'items', 'target_type': 'player'}
        returned_dct.update(self._CHOSEN_ITEMS_BUFF_BASE)

        self.items_static_stats_buff_dct = returned_dct

    def _create_items_properties_dcts(self):
        """
        Creates final dicts (non unique stats, unique stats, stats buff, effects, conditions) for current item build.

        :return: (None)
        """

        non_unique_stats_dct = {'additive': collections.Counter(), 'percent': collections.Counter()}
        used_items_unique_stats_dct = {'additive': collections.Counter(), 'percent': collections.Counter()}
        unique_names_used_so_far = []

        # Counter of an item's occurrence, e.g. {'item_1': 2, ..}.
        items_counter = collections.Counter(self.chosen_items_lst)

        # Each item name is applied once.
        for item_name in items_counter:

            item_count = items_counter[item_name]

            item_attrs = self.ITEMS_ATTRIBUTES[item_name]

            # NON UNIQUE STATS
            item_non_unique_stats = item_attrs['non_unique_stats']
            for stat_type in item_non_unique_stats:
                for stat_name in item_non_unique_stats[stat_type]:
                    # (multiplies stat by item's count before adding it to existing stats)
                    stat_val = item_non_unique_stats[stat_type][stat_name] * item_count
                    non_unique_stats_dct[stat_type] += collections.Counter({stat_name: stat_val})

            # UNIQUE STATS
            # If item A (leaf) builds from item B, then unique stats from B that are included in A are ignored.
            item_unique_stats_dct = item_attrs['unique_stats']

            for unique_name in item_unique_stats_dct:
                unique_dct = item_unique_stats_dct[unique_name]

                # (Unnamed uniques have 'unnamed' as a name.)
                # (It is converted to the item's name before marked as used.)
                if unique_name == 'unnamed':
                    unique_name = item_name

                if unique_name in unique_names_used_so_far:
                    continue

                else:
                    unique_names_used_so_far.append(unique_name)

                    for stat_type in unique_dct:
                        stat_type_dct = unique_dct[stat_type]
                        for stat_name in stat_type_dct:

                            used_items_unique_stats_dct[stat_type].setdefault(stat_name, 0)
                            used_items_unique_stats_dct[stat_type][stat_name] += stat_type_dct[stat_name]

            # ITEMS BUFF
            self._set_chosen_items_static_stats_buff(non_unique_stats_dct=non_unique_stats_dct,
                                                     used_items_unique_stats_dct=used_items_unique_stats_dct)

    def build_price(self):
        """
        Calculates cost of all items in given item build.

        :return: (int)
        """

        cost = 0

        for item_name in self.chosen_items_lst:
            cost += items_data_module.ITEMS_ATTRIBUTES[item_name]['secondary_data']['total_price']

        return cost

    def items_stats_dependencies(self):

        all_i_stats_deps = set()

        for i in self.chosen_items_lst:
            item_stats_deps = self.ITEMS_ATTRIBUTES[i]['stats_dependencies']

            if item_stats_deps:
                all_i_stats_deps |= item_stats_deps

        return all_i_stats_deps

if __name__ == '__main__':

    if 0:
        g = ItemsProperties(['hextech_gunblade', 'dorans_blade']).build_price()
        print(g)

    if 0:
        g = ItemsProperties(['hextech_gunblade', 'dorans_blade']).unique_stats_in_leafs_of_item(item_name='dorans_blade')
        print(g)
