import numpy
import items_folder.items_data as unique_items_data


_GOLD_AT_LVL_1 = 470

_X_VALUES = [1, 18]

# (Supports get less gold usually)
_NON_SUPPORT_Y_VALUES = [_GOLD_AT_LVL_1, 17000]
_SUPPORT_Y_VALUES = [_GOLD_AT_LVL_1, 12000]


def _linear_fit_coefs(lvl_vals, gold_vals):
    """
    Fits linearly given gold vs lvl values.

    :param lvl_vals: (sequence)
    :param gold_vals: (sequence)
    :return: (tuple) Coefficients a1 and a0.
    """

    a_1, a_0 = numpy.polyfit(lvl_vals, gold_vals, 1)

    return a_1, a_0


def __gold_at_lvl(champ_lvl, a_1, a_0):
    """
    Calculates gold at given lvl.

    Note: Not to be merged with _linear_fit_coefs to avoid unnecessary calls to polyfit.

    :param champ_lvl:
    :param a_1: (float)
    :param a_0: (float)
    :return: (int) Rounded gold.
    """

    gold_val = a_1 * champ_lvl + a_0

    # Anything but the first lvl can be rounded.
    if champ_lvl == 1:
        return int(gold_val)
    else:
        return int(round(gold_val, -2))


def _non_support_gold_at_lvl(champ_lvl):
    a_1, a_0 = _linear_fit_coefs(lvl_vals=_X_VALUES, gold_vals=_NON_SUPPORT_Y_VALUES)
    return __gold_at_lvl(champ_lvl=champ_lvl, a_1=a_1, a_0=a_0)


def _support_gold_at_lvl(champ_lvl):
    a_1, a_0 = _linear_fit_coefs(lvl_vals=_X_VALUES, gold_vals=_SUPPORT_Y_VALUES)
    return __gold_at_lvl(champ_lvl=champ_lvl, a_1=a_1, a_0=a_0)


_NON_SUPPORT_GOLD_VS_LVL_MAP = {lvl: _non_support_gold_at_lvl(champ_lvl=lvl) for lvl in range(1, 19)}
_SUPPORT_GOLD_VS_LVL_MAP = {lvl: _support_gold_at_lvl(champ_lvl=lvl) for lvl in range(1, 19)}


# Lists of (complete) items in buying order.
# 7 items are included since doran's is sold.
__SHEN_ITEMS_QUEUE = ('dorans_shield',)
_ITEMS_QUEUES_DCT = {'shen': __SHEN_ITEMS_QUEUE}
# TODO: Insert the rest of item queues.

_SUPPORTS_SET = {'thresh'}


class EnemyItemsAutoSelection(object):

    NON_SUPPORT_GOLD_VS_LVL_MAP = _NON_SUPPORT_GOLD_VS_LVL_MAP
    SUPPORT_GOLD_VS_LVL_MAP = _SUPPORT_GOLD_VS_LVL_MAP
    SUPPORTS_SET = _SUPPORTS_SET
    ITEMS_QUEUES_DCT = _ITEMS_QUEUES_DCT

    NON_SUPPORT_DORANS_MAINTAINED_UNTIL_LVL = 15

    UNIMPORTANT_STATS = {'mp5', 'hp5', 'gp5'}

    @staticmethod
    def _item_cost(item_name):
        return unique_items_data.ITEMS_ATTRIBUTES[item_name]['secondary_data']['total_cost']

    @staticmethod
    def _builds_from(item_name):
        return unique_items_data.ITEMS_ATTRIBUTES[item_name]['secondary_data']['builds_into']

    @staticmethod
    def _item_stats_set(item_name):
        """
        Returns all item's stats.

        :param item_name: (str)
        :return: (set)
        """

        stats_used = set()

        item_data_dct = unique_items_data.ITEMS_ATTRIBUTES[item_name]

        for stacking_type in ('non_unique_stats', 'unique_stats'):
            stats_dct = item_data_dct[stacking_type]

            for stat_type in stats_dct:
                for stat_name in stats_dct[stat_type]:
                    stats_used.add(stat_name)

        return stats_used

    @staticmethod
    def _item_sell_price(item_name):
        return unique_items_data.ITEMS_ATTRIBUTES[item_name]['secondary_data']['sell_price']

    def _prioritised_roots_queue(self, item_name):
        """
        Returns sorted list of items based on cost, while taking into account stats' "importance".

        NOTE: "Roots" refers to immediate item's roots not all its roots.

        :param item_name: (str)
        :return: (list) Item names, from most important to less important.
        """

        costs_dct = {}
        roots = self._builds_from(item_name=item_name)

        for root_item in roots:
            costs_dct.update({root_item: self._item_cost(item_name=root_item)})

        # Sorts by cost.
        items_queue = sorted(costs_dct, key=costs_dct.get)

        # UNIMPORTANT ITEMS
        # Sinks items containing only unimportant stats to the bottom of the list.
        unimportant_items = []

        for checked_item in items_queue:
            item_stats = self._item_stats_set(item_name=checked_item)

            if item_stats - self.UNIMPORTANT_STATS:
                pass

            # If item has only unimportant stats.
            else:
                unimportant_items.append(checked_item)

        # Sorts unimportant items by cost.
        unimportant_items = sorted(unimportant_items, key=costs_dct.get)

        # Places unimportant items at the bottom.
        items_queue = [i for i in items_queue if i not in unimportant_items]
        items_queue += unimportant_items

        return items_queue

    def _insert_item_and_apply_cost(self, available_items_queue, items_lst_and_available_gold_dct):
        """
        Modifies the items list and the available gold by inserting items whose costs suffices.
        Recursively adds roots.

        NOTE: "Roots" refers to immediate item's roots not all its roots.

        :param items_lst_and_available_gold_dct: (dict) Contains current-items' list and available gold.
        :return:
        """

        for item_name in available_items_queue:
            available_gold = items_lst_and_available_gold_dct['available_gold']
            item_cost = self._item_cost(item_name=item_name)

            # Insufficient gold.
            if item_cost <= available_gold:
                items_lst_and_available_gold_dct['available_gold'] -= item_cost
                items_lst_and_available_gold_dct['items'].append(item_name)

            else:
                # (Inserts as many roots as possible)
                roots_queue = self._prioritised_roots_queue(item_name=item_name)

                self._insert_item_and_apply_cost(available_items_queue=roots_queue,
                                                 items_lst_and_available_gold_dct=items_lst_and_available_gold_dct)

    def _enemy_items(self, enemy_lvl, enemy_champ_name):
        """
        Returns a list with the items an enemy is using.

        :param enemy_lvl: (int)
        :param enemy_champ_name: (str)
        :return: (list)
        """

        item_queue_iter = iter(self.ITEMS_QUEUES_DCT[enemy_champ_name])
        items_lst = []

        # AVAILABLE GOLD
        if enemy_champ_name in self.SUPPORTS_SET:
            available_gold = self.SUPPORT_GOLD_VS_LVL_MAP[enemy_lvl]
        else:
            available_gold = self.NON_SUPPORT_GOLD_VS_LVL_MAP[enemy_lvl]

        # DORAN'S INSERTION
        # (supports don't use it)
        if enemy_champ_name in self.SUPPORTS_SET:
            if enemy_lvl > self.NON_SUPPORT_DORANS_MAINTAINED_UNTIL_LVL:

                doran_name = next(item_queue_iter)
                items_lst.append(doran_name)

                available_gold -= self._item_cost(item_name=doran_name)

        # (dict needed in method below)
        items_and_available_gold_dct = {}
        items_and_available_gold_dct.update({'available_gold': available_gold})
        items_and_available_gold_dct.update({'items': items_lst})

        # NON DORAN'S INSERTION
        self._insert_item_and_apply_cost(available_items_queue=item_queue_iter,
                                         items_lst_and_available_gold_dct=items_and_available_gold_dct)

        return items_lst


if __name__ == '__main__':
    print('\nNon support gold: {}'.format(_NON_SUPPORT_GOLD_VS_LVL_MAP))
    print('Support gold: {}\n'.format(_SUPPORT_GOLD_VS_LVL_MAP))

    item = 'hextech_gunblade'
    stats_lst = EnemyItemsAutoSelection()._item_stats_set(item_name=item)
    print('\nStats in {}: {}\n'.format(item, stats_lst))