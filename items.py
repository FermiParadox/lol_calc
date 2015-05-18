import items_folder.items_data as items_data_module
import palette

import collections


_CHOSEN_ITEMS_BUFF_BASE = palette.buff_dct_base()
_CHOSEN_ITEMS_BUFF_BASE['target_type'] = 'player'
_CHOSEN_ITEMS_BUFF_BASE['duration'] = 'permanent'
_CHOSEN_ITEMS_BUFF_BASE['max_stacks'] = 1
_CHOSEN_ITEMS_BUFF_BASE['on_hit'] = None
_CHOSEN_ITEMS_BUFF_BASE['prohibit_cd_start'] = None
_CHOSEN_ITEMS_BUFF_BASE['buff_source'] = 'items'
_CHOSEN_ITEMS_BUFF_BASE['dot'] = None
# (deleted so that a dict can be created later on that will have this dict updated in it as a reference)
del _CHOSEN_ITEMS_BUFF_BASE['stats']


class ItemsProperties(object):

    ITEMS_BUFFS_NAMES = items_data_module.ITEMS_BUFFS_NAMES
    ITEMS_DMGS_NAMES = items_data_module.ITEMS_DMGS_NAMES
    ITEMS_ATTRIBUTES = items_data_module.ITEMS_ATTRIBUTES
    ITEMS_EFFECTS = items_data_module.ITEMS_EFFECTS
    ITEMS_CONDITIONALS = items_data_module.ITEMS_CONDITIONALS

    CHOSEN_ITEMS_BUFF_BASE = _CHOSEN_ITEMS_BUFF_BASE

    def __init__(self, chosen_items_lst):
        self.chosen_items_lst = chosen_items_lst

        self.non_unique_stats_dct = {'additive': collections.Counter(), 'percent': collections.Counter()}
        self.unique_stats_dct = {'additive': collections.Counter(), 'percent': collections.Counter()}

        self.items_effects_dct = {}
        self.items_conditions_dct = {}

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
    def merge_item_effects_dct_to_existing(existing_dct, new_merged_dct):
        """
        OBSOLETE
        (merging effect and condition dicts was wrong, since different actives cant be merged)

        Merges an item's effects dict into an existing effects dict.

        Assumes the final values are lists,
        which is not the case when there is "cds_modified" for champions instead of items.

        :param existing_dct:
        :param new_merged_dct:
        :return: (None)
        """

        for key_1 in new_merged_dct:
            for key_2 in new_merged_dct[key_1]:
                for key_3 in new_merged_dct[key_1][key_2]:
                    existing_dct[key_1][key_2][key_3] += new_merged_dct[key_1][key_2][key_3]

    def total_items_stats(self):
        """
        Creates a dict with all unique and non-unique stats from chosen items.

        :return: (dict)
        """

        additive_stats_dct = collections.Counter()
        percent_stats_dct = collections.Counter()

        for dct in (self.non_unique_stats_dct, self.unique_stats_dct):

            additive_stats_dct += dct['additive']
            percent_stats_dct += dct['percent']

        return {'additive': additive_stats_dct, 'percent': percent_stats_dct}

    def _set_chosen_items_static_stats_buff(self):
        """
        Creates a buff containing all passive stats of chosen items.

        :return: (None)
        """
        returned_dct = {'stats': self.total_items_stats()}
        returned_dct.update(self.CHOSEN_ITEMS_BUFF_BASE)

        self.items_static_stats_buff_dct = returned_dct

    def items_static_stats_buff(self):
        return self.items_static_stats_buff_dct

    def _create_items_properties_dcts(self):
        """
        Creates final dicts (non unique stats, unique stats, stats buff, effects, conditions) for current item build.

        :return: (None)
        """

        # Counter of an item's occurrence, e.g. {'item_1': 2, ..}.
        items_counter = collections.Counter(self.chosen_items_lst)

        # Each item name is applied once.
        for item_name in items_counter:

            item_count = items_counter[item_name]

            item_attrs = self.ITEMS_ATTRIBUTES[item_name]
            item_effects = self.ITEMS_EFFECTS[item_name]
            item_conditions = self.ITEMS_CONDITIONALS[item_name]

            # NON UNIQUE STATS
            item_non_unique_stats = item_attrs['non_unique_stats']
            for stat_type in item_non_unique_stats:
                for stat_name in item_non_unique_stats[stat_type]:
                    # (multiplies stat by item's count before adding it to existing stats)
                    stat_val = item_non_unique_stats[stat_type][stat_name] * item_count
                    self.non_unique_stats_dct[stat_type] += collections.Counter({stat_name: stat_val})

            # UNIQUE STATS
            # If item A (leaf) builds from item B, then unique stats from B that are included in A are ignored.
            unique_stats_dct = item_attrs['unique_stats']
            leafs_stats = self.unique_stats_in_leafs_of_item(item_name=item_name)

            for stat_type in unique_stats_dct:
                for stat_name in unique_stats_dct[stat_type]:
                    # If stat is no inside leafs' stats.
                    if stat_name not in leafs_stats[stat_type]:
                        self.unique_stats_dct[stat_type].update({stat_name: unique_stats_dct[stat_type][stat_name]})

            # ITEMS BUFF
            self._set_chosen_items_static_stats_buff()

            # EFFECTS AND CONDITIONS
            # Root effects (and conditions) are set to an empty dict, since leaf is (assumed to) override them.
            if item_name in self.non_roots_in_build():
                self.items_effects_dct.update({item_name: item_effects})
                self.items_conditions_dct.update({item_name: item_conditions})
            else:
                self.items_effects_dct.update({item_name: {}})
                self.items_conditions_dct.update({item_name: {}})

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

    from pprint import pprint as pp

    testBuildCost = False
    if testBuildCost:
        g = ItemsProperties(['hextech_gunblade', 'dorans_blade']).build_price()
        print(g)

    testUniqueLeafsUniqueStats = False
    if testUniqueLeafsUniqueStats:
        g = ItemsProperties(['hextech_gunblade', 'dorans_blade']).unique_stats_in_leafs_of_item(item_name='dorans_blade')
        print(g)

    testAllItemPropertyCreation = True
    if testAllItemPropertyCreation:
        g = ItemsProperties(['hextech_gunblade', 'dorans_blade'])
        pp(g.items_effects_dct)
        print('-'*10)
        pp(g.items_conditions_dct)