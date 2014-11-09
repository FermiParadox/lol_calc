import api_static_stored_data
import palette

# Converts item related API data to app compatible format.


class ApiItemConverter(object):

    """
    API item dict structure:

        'data': (contains item IDs)
            '3108':
                'image':
                'tags': (categories in store when purchasing in game)
                'depth':
                'plaintext':
                'into': (items that use this item in their recipe)
                'from': (items used to make this item)
                'name': (in game item name)
                'description':
                'sanitizedDescription':
                'stats':
                'id': (same as previous item id)
                'gold':
                    'base': (recipe value of item)
                    'total': (total value of item)
                    'purchasable':
                    'sell': (resell value)
        'basic': (useless)
        'version':
        'tree': (list with dictionaries as elements, containing categories in store when purchasing in game)
        'type': (useless)
        'groups': (list with dictionaries as elements, contains max stacks of items e.g. max boots->1)
    """

    @staticmethod
    def item_id_to_full_name_dct():
        """
        Returns dict containing item ids and their full names.

        Filters out trinkets.

        e.g. {3104: 'Black Cleaver',}
        """

        excluded_tags = ('Trinket',)

        dct = {}

        api_dct = api_static_stored_data.API_ITEMS_DCT['data']

        for id_num in api_dct:

            if 'tags' in api_dct[id_num]:

                exclude_item = False
                # Filters out excluded tags.
                for tag_name in excluded_tags:

                    if tag_name in api_dct[id_num]['tags']:
                        exclude_item = True
                        break

                if not exclude_item:
                    dct.update({id_num: api_dct[id_num]['name']})

        return dct

    @staticmethod
    def full_name_to_app_name(full_name):
        """
        Converts full name of an item to app format name.

        Args:
            full_name: (string) Full item name in API.
        Returns:
            string
        """

        app_name = full_name.replace(' ', '_')
        app_name = app_name.replace("'", '')
        app_name = app_name.lower()

        return app_name

    def app_name_to_id_dct(self):
        """
        Creates dict with item names (app format) and their id as value.

        Returns:
            dict
        """

        dct = {}

        for id_num in self.item_id_to_full_name_dct():

            app_name = self.full_name_to_app_name(full_name=self.item_id_to_full_name_dct()[id_num])
            dct.update({app_name: id_num})

        return dct


if __name__ == '__main__':
    print(ApiItemConverter().app_name_to_id_dct())
