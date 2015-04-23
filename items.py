import items.items_data as items_data_module


class ItemsProperties(object):

    def __init__(self, chosen_items_lst):
        self.chosen_items_lst = chosen_items_lst

    def _create_items_properties_dcts(self):
        pass

    def leafs_used(self, items_lst):
        pass

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

    cost = ItemsProperties(['hextech_gunblade', 'dorans_blade']).build_price()
    print(cost)