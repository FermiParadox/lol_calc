import palette


MASTERIES_ATTRIBUTES = {
    'alchemist': {},
    'arcane_blade': {},
    'arcane_mastery': {'buffs': {},
                       'dmgs': {},
                       'stats': {'ap': {'additive': {'stat_values': (6.0,)}}}},
    'archmage': {'buffs': {},
                 'dmgs': {},
                 'stats': {'ap': {'multiplicative': {'stat_values': (0.02,
                                                                     0.035,
                                                                     0.05)}}}},
    'bandit': {},
    'blade_weaving': {'buffs': {'blade_weaving_initiator': {'buff_source': 'blade_weaving',
                                                            'dot': False,
                                                            'duration': 'permanent',
                                                            'max_stacks': 1,
                                                            'on_hit': {'apply_buff': ['blade_weaving_stack'],
                                                                       'cause_dmg': [],
                                                                       'reduce_cd': {},
                                                                       'remove_buff': []},
                                                            'stats': None,
                                                            'target_type': 'player'},
                                'blade_weaving_stack': {'buff_source': 'blade_weaving',
                                                        'dot': False,
                                                        'duration': 3,
                                                        'max_stacks': 3,
                                                        'on_hit': None,
                                                        'stats': {'spell_dmg_dealt': {'multiplicative': {'stat_mods': {},
                                                                                                         'stat_values': (0.01,)}}},
                                                        'target_type': 'player'}},
                      'dmgs': {},
                      'stats': {}},
    'bladed_armor': {},
    'block': {'buffs': {'block_buff_0': {'buff_source': 'block',
                                         'dot': False,
                                         'duration': 'permanent',
                                         'max_stacks': 1,
                                         'on_hit': {'apply_buff': ['placeholder'],
                                                    'cause_dmg': ['placeholder'],
                                                    'reduce_cd': {},
                                                    'remove_buff': ['placeholder']},
                                         'stats': {'flat_AA_reduction': {'additive': {'stat_mods': {},
                                                                                      'stat_values': (1.0,
                                                                                                      2.0)}}},
                                         'target_type': 'player'}},
              'dmgs': {},
              'stats': {}},
    'brute_force': {'buffs': {},
                    'dmgs': {},
                    'stats': {'ad_per_lvl': {'additive': {'stat_values': (0.22,
                                                                          0.39,
                                                                          0.55)}}}},
    'butcher': {},
    'culinary_master': {},
    'dangerous_game': {'buffs': {'dangerous_game_buff_0': {'buff_source': 'dangerous_game',
                                                           'dot': False,
                                                           'duration': 'permanent',
                                                           'max_stacks': 1,
                                                           'on_hit': {'apply_buff': ['placeholder'],
                                                                      'cause_dmg': ['placeholder'],
                                                                      'reduce_cd': {},
                                                                      'remove_buff': ['placeholder']},
                                                           'stats': {'placeholder_stat_1': 'placeholder'},
                                                           'target_type': 'player'}},
                       'dmgs': {},
                       'stats': {}}}


MASTERIES_BUFFS_NAMES = palette.items_or_masteries_buffs_or_dmgs_names_dct(str_buffs_or_dmgs='buffs', attrs_dct=MASTERIES_ATTRIBUTES)
MASTERIES_DMGS_NAMES = palette.items_or_masteries_buffs_or_dmgs_names_dct(str_buffs_or_dmgs='dmgs', attrs_dct=MASTERIES_ATTRIBUTES)


if __name__ == '__main__':

    # All buffs and dmgs names of all items.
    print("Item buffs' names: {}".format(MASTERIES_BUFFS_NAMES))
    print("Item buffs' names: {}".format(MASTERIES_DMGS_NAMES))