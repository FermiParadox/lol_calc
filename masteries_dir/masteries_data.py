import palette


MASTERIES_ATTRIBUTES = {
    'alchemist': {'buffs': {},
                  'dmgs': {},
                  'stats': {}},
    'arcane_blade': {'buffs': {},
                     'dmgs': {},
                     'stats': {}},
    'arcane_mastery': {'buffs': {},
                       'dmgs': {},
                       'stats': {'ap': (6.0,)}},
    'expanded_mind': {'buffs': {},
                      'dmgs': {},
                      'stats': {'mp': (25.0,
                                       50.0,
                                       75.0)}}}


MASTERIES_BUFFS_NAMES = palette.items_or_masteries_buffs_or_dmgs_names_dct(str_buffs_or_dmgs='buffs', attrs_dct=MASTERIES_ATTRIBUTES)
MASTERIES_DMGS_NAMES = palette.items_or_masteries_buffs_or_dmgs_names_dct(str_buffs_or_dmgs='dmgs', attrs_dct=MASTERIES_ATTRIBUTES)


if __name__ == '__main__':

    # All buffs and dmgs names of all items.
    print("Item buffs' names: {}".format(MASTERIES_BUFFS_NAMES))
    print("Item buffs' names: {}".format(MASTERIES_DMGS_NAMES))