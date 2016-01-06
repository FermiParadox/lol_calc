import palette


MASTERIES_ATTRIBUTES = {
    'assassin': {'buffs': {},
                 'dmgs': {},
                 'stats': {'percent_dmg_dealt_increase': {'additive': {'stat_values': (0.015,)}}},
                 'stats_dependencies': set()},
    'bandit': {},
    'battering_blows': {'buffs': {},
                        'dmgs': {},
                        'stats': {'percent_armor_penetration': {'additive': {'stat_values': (0.013999999999999999,
                                                                                             0.027999999999999997,
                                                                                             0.042,
                                                                                             0.055999999999999994,
                                                                                             0.07)}}},
                        'stats_dependencies': set()},
    'bond_of_stone': {'buffs': {},
                      'dmgs': {},
                      'stats': {'percent_dmg_reduction': {'additive': {'stat_values': (0.03,)}}},
                      'stats_dependencies': set()},
    'bounty_hunter': {'buffs': {'bounty_hunter_buff_0': {'aura': False,
                                                         'buff_source': 'masteries',
                                                         'dot': False,
                                                         'duration': 'permanent',
                                                         'max_stacks': 1,
                                                         'max_targets': 1,
                                                         'on_being_hit': {},
                                                         'on_hit': {},
                                                         'shield': False,
                                                         'stats': {'percent_dmg_dealt_increase': {'additive': {'stat_mods': {'unique_enemies_killed': (0.01,)},
                                                                                                               'stat_values': 0}}},
                                                         'target_type': 'player',
                                                         'usual_max_targets': 1}},
                      'dmgs': {},
                      'stats': {},
                      'stats_dependencies': set()}}


MASTERIES_BUFFS_NAMES = palette.items_or_masteries_buffs_or_dmgs_names_dct(str_buffs_or_dmgs='buffs', attrs_dct=MASTERIES_ATTRIBUTES)
MASTERIES_DMGS_NAMES = palette.items_or_masteries_buffs_or_dmgs_names_dct(str_buffs_or_dmgs='dmgs', attrs_dct=MASTERIES_ATTRIBUTES)


if __name__ == '__main__':

    # All buffs and dmgs names of all items.
    print("Item buffs' names: {}".format(MASTERIES_BUFFS_NAMES))
    print("Item buffs' names: {}".format(MASTERIES_DMGS_NAMES))
