class DuplicateNameError(Exception):
    """
    To be raised when a duplicate buff or dmg name is found.

    Duplicate buffs or dmgs can cause bugs when translated.
    """
    pass


ITEMS_ATTRIBUTES = {
    'dorans_blade': {'buffs': {},
                     'dmgs': {},
                     'general_attributes': {'castable': False},
                     'non_unique_stats': {'additive': {'ad': 7,
                                                       'hp': 70,
                                                       'lifesteal': 0.03}},
                     'secondary_data': {'build_from': {},
                                        'builds_into': set(),
                                        'id': 1055,
                                        'leafs': set(),
                                        'recipe_price': 440,
                                        'roots': set(),
                                        'sell_price': 176,
                                        'total_price': 440},
                     'unique_stats': {}},
    'hextech_gunblade': {'buffs': {'hextech_gunblade_slow': {'dot': False,
                                                             'duration': 2,
                                                             'max_stacks': 1,
                                                             'on_hit': {'add_dmg': [],
                                                                        'apply_buff': [],
                                                                        'reduce_cd': {},
                                                                        'remove_buff': []},
                                                             'stats': {'move_speed_reduction': 0.4},
                                                             'target_type': 'enemy'}},
                         'dmgs': {'hextech_gunblade_dmg_0': {'delay': None,
                                                             'dmg_category': 'standard_dmg',
                                                             'dmg_source': 'gunblade',
                                                             'dmg_type': 'magic',
                                                             'dmg_values': 150,
                                                             'dot': False,
                                                             'life_conversion_type': 'spellvamp',
                                                             'max_targets': 1,
                                                             'mods': {'enemy': {},
                                                                      'player': {'ap': {'additive': 0.4}}},
                                                             'radius': None,
                                                             'resource_type': 'hp',
                                                             'target_type': 'enemy',
                                                             'usual_max_targets': 1}},
                         'general_attributes': {'base_cd': 60,
                                                'cast_time': 0,
                                                'castable': True,
                                                'channel_time': None,
                                                'dashed_distance': None,
                                                'independent_cast': True,
                                                'move_while_casting': True,
                                                'range': 500,
                                                'resets_aa': False,
                                                'toggled': False,
                                                'travel_time': 0.25},
                         'non_unique_stats': {'additive': {'ad': 40,
                                                           'ap': 80,
                                                           'lifesteal': 0.12}},
                         'secondary_data': {'build_from': {'bilgewater_cutlass': 1,
                                                           'hextech_revolver': 1},
                                            'builds_into': set(),
                                            'id': 3146,
                                            'leafs': set(),
                                            'recipe_price': 800,
                                            'roots': {'amplifying_tome',
                                                      'bilgewater_cutlass',
                                                      'hextech_revolver',
                                                      'long_sword',
                                                      'vampiric_scepter'},
                                            'sell_price': 2380,
                                            'total_price': 3400},
                         'unique_stats': {'additive': {'spellvamp': 0.2}}}}

ITEMS_EFFECTS = {
    'dorans_blade': {'enemy': {'actives': {'buffs': [],
                                           'dmg': [],
                                           'remove_buff': []},
                               'passives': {'buffs': [],
                                            'dmg': [],
                                            'remove_buff': []}},
                     'player': {'actives': {'buffs': [],
                                            'dmg': [],
                                            'remove_buff': []},
                                'passives': {'buffs': [],
                                             'dmg': [],
                                             'remove_buff': []}}},
    'hextech_gunblade': {'enemy': {'actives': {'buffs': ['hextech_gunblade_slow'],
                                               'dmg': ['hextech_gunblade_dmg_0'],
                                               'remove_buff': []},
                                   'passives': {'buffs': [],
                                                'dmg': [],
                                                'remove_buff': []}},
                         'player': {'actives': {'buffs': [],
                                                'dmg': [],
                                                'remove_buff': []},
                                    'passives': {'buffs': [],
                                                 'dmg': [],
                                                 'remove_buff': []}}}}

ITEMS_CONDITIONALS = {
    'hextech_gunblade': {},
    'dorans_blade': {}}


def _items_buffs_or_dmgs_names_dct(buffs_or_dmgs):
    """
    Creates a dict of all items' dmgs or buffs names as keys, and corresponding item name as value.

    :param buffs_or_dmgs: (str) 'dmgs', 'buffs'
    :return: (dict) Key: buff name, value: item name
    """

    dct = {}

    for item_name in ITEMS_ATTRIBUTES:
        for buff_name in ITEMS_ATTRIBUTES[item_name][buffs_or_dmgs]:

            # Checks if obj already exists.
            if buff_name in dct:
                raise DuplicateNameError
            # Adds obj name to list
            else:
                dct.update({buff_name: item_name})

    return dct


ITEMS_BUFFS_NAMES = _items_buffs_or_dmgs_names_dct(buffs_or_dmgs='buffs')
ITEMS_DMGS_NAMES = _items_buffs_or_dmgs_names_dct(buffs_or_dmgs='dmgs')


if __name__ == '__main__':

    # Buffs and dmgs names.
    print("Item buffs' names: {}".format(ITEMS_BUFFS_NAMES))
    print("Item buffs' names: {}".format(ITEMS_DMGS_NAMES))