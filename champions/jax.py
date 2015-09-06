import abilities

ABILITIES_ATTRIBUTES = {
    'buffs': {'e_dmg_red': {'dot': False,
                            'buff_source': 'e',
                            'duration': 2,
                            'max_stacks': 1,
                            'on_hit': {},
                            'prohibit_cd_start': None,
                            'stats': {'percent_AA_reduction': {'additive': {'stat_mods': {},
                                                                            'stat_values': 1.0}},
                                      'percent_aoe_reduction': {'percent': {'stat_mods': {},
                                                                            'stat_values': 0.25}}},
                            'target_type': 'player'},
              'e_stun': {'buff_source': 'e',
                         'dot': False,
                         'duration': 1,
                         'max_stacks': 1,
                         'on_hit': {},
                         'prohibit_cd_start': None,
                         'stats': None,
                         'target_type': 'enemy'},
              'inn_att_speed_buff': {'buff_source': 'inn',
                                     'dot': False,
                                     'duration': 2.5,
                                     'max_stacks': 6,
                                     'on_hit': {},
                                     'prohibit_cd_start': None,
                                     'stats': {'att_speed': {'percent': {'stat_mods': None,
                                                                         'stat_values': (0.04,
                                                                                         0.06,
                                                                                         0.08,
                                                                                         0.1,
                                                                                         0.12,
                                                                                         0.14)}}},
                                     'target_type': 'player'},
              'inn_att_speed_initiator': {'buff_source': 'inn',
                                          'dot': False,
                                          'duration': 'permanent',
                                          'max_stacks': 1,
                                          'on_hit': {'apply_buff': ['inn_att_speed_buff'],
                                                     'cause_dmg': [],
                                                     'cds_modified': {},
                                                     'remove_buff': []},
                                          'prohibit_cd_start': None,
                                          'stats': None,
                                          'target_type': 'player'},
              'r_dmg_red': {'buff_source': 'r',
                            'dot': False,
                            'duration': 8,
                            'max_stacks': 1,
                            'on_hit': {},
                            'prohibit_cd_start': None,
                            'stats': {'armor': {'additive': {'stat_mods': {'bonus_ad': (0.5,)},
                                                             'stat_values': (20.0,
                                                                             35.0,
                                                                             50.0)}},
                                      'mr': {'additive': {'stat_mods': {'ap': (0.2,)},
                                                          'stat_values': (20.0,
                                                                          35.0,
                                                                          50.0)}}},
                            'target_type': 'player'},
              'r_hit_counter': {'buff_source': 'r',
                                'dot': False,
                                'duration': 5,
                                'max_stacks': 3,
                                'on_hit': {},
                                'prohibit_cd_start': None,
                                'stats': None,
                                'target_type': 'player'},
              'r_n_hit_initiator': {'buff_source': 'r',
                                    'dot': False,
                                    'duration': 'permanent',
                                    'max_stacks': 1,
                                    'on_hit': {'apply_buff': ['r_hit_counter'],
                                               'cause_dmg': [],
                                               'cds_modified': {},
                                               'remove_buff': []},
                                    'prohibit_cd_start': None,
                                    'stats': None,
                                    'target_type': 'player'},
              'w_buff_0': {'buff_source': 'r',
                           'dot': False,
                           'duration': 7,
                           'max_stacks': 1,
                           'on_hit': {},
                           'prohibit_cd_start': 'w',
                           'stats': None,
                           'target_type': 'player'}},
    'dmgs': {'e_dmg_0': {'delay': 1,
                         'dmg_category': 'standard_dmg',
                         'dmg_source': 'e',
                         'dmg_type': 'physical',
                         'dmg_values': (50.0,
                                        75.0,
                                        100.0,
                                        125.0,
                                        150.0),
                         'dot': False,
                         'life_conversion_type': 'spellvamp',
                         'max_targets': 5,
                         'mods': {'enemy': {},
                                  'player': {'bonus_ad': {'additive': 0.5}}},
                         'radius': 150,
                         'resource_type': 'hp',
                         'target_type': 'enemy',
                         'usual_max_targets': 2,
                         'crit_type': None},
             'q_dmg_0': {'delay': None,
                         'dmg_category': 'standard_dmg',
                         'dmg_source': 'q',
                         'dmg_type': 'physical',
                         'dmg_values': (70.0,
                                        110.0,
                                        150.0,
                                        190.0,
                                        230.0),
                         'dot': False,
                         'life_conversion_type': 'spellvamp',
                         'max_targets': 1,
                         'mods': {'enemy': {},
                                  'player': {'ap': {'additive': 0.6},
                                             'bonus_ad': {'additive': 1.0}}},
                         'radius': None,
                         'resource_type': 'hp',
                         'target_type': 'enemy',
                         'usual_max_targets': 1,
                         'crit_type': None},
             'r_dmg_0': {'delay': None,
                         'dmg_category': 'standard_dmg',
                         'dmg_source': 'r',
                         'dmg_type': 'magic',
                         'dmg_values': (100.0,
                                        160.0,
                                        220.0),
                         'dot': False,
                         'life_conversion_type': 'spellvamp',
                         'max_targets': 1,
                         'mods': {'enemy': {},
                                  'player': {'ap': {'additive': 0.7}}},
                         'radius': None,
                         'resource_type': 'hp',
                         'target_type': 'enemy',
                         'usual_max_targets': 1,
                         'crit_type': None},
             'w_dmg_0': {'delay': None,
                         'dmg_category': 'standard_dmg',
                         'dmg_source': 'w',
                         'dmg_type': 'magic',
                         'dmg_values': (40.0,
                                        75.0,
                                        110.0,
                                        145.0,
                                        180.0),
                         'dot': False,
                         'life_conversion_type': 'spellvamp',
                         'max_targets': 1,
                         'mods': {'enemy': {},
                                  'player': {'ap': {'additive': 0.6}}},
                         'radius': None,
                         'resource_type': 'hp',
                         'target_type': 'enemy',
                         'usual_max_targets': 1,
                         'crit_type': None}},
    'general_attributes': {'e': {'base_cd': (16.0,
                                             14.0,
                                             12.0,
                                             10.0,
                                             8.0),
                                 'cast_time': 0,
                                 'castable': True,
                                 'channel_time': None,
                                 'cost': {'stack_cost': None,
                                          'standard_cost': {'cost_category': 'normal',
                                                            'resource_type': 'mp',
                                                            'values': (70,
                                                                       75,
                                                                       80,
                                                                       85,
                                                                       90)}},
                                 'dashed_distance': None,
                                 'independent_cast': False,
                                 'move_while_casting': True,
                                 'range': 0,
                                 'cds_modified': None,
                                 'resets_aa': False,
                                 'toggled': False,
                                 'travel_time': 0},
                           'inn': {},
                           'q': {'base_cd': (10.0,
                                             9.0,
                                             8.0,
                                             7.0,
                                             6.0),
                                 'cast_time': 0.25,
                                 'castable': True,
                                 'channel_time': None,
                                 'cost': {'stack_cost': None,
                                          'standard_cost': {'cost_category': 'normal',
                                                            'resource_type': 'mp',
                                                            'values': (65,
                                                                       65,
                                                                       65,
                                                                       65,
                                                                       65)}},
                                 'dashed_distance': 600,
                                 'independent_cast': False,
                                 'move_while_casting': False,
                                 'range': (700,
                                           700,
                                           700,
                                           700,
                                           700),
                                 'cds_modified': None,
                                 'resets_aa': False,
                                 'toggled': False,
                                 'travel_time': 0},
                           'r': {'base_cd': (80.0,
                                             80.0,
                                             80.0),
                                 'cast_time': 0,
                                 'castable': True,
                                 'channel_time': None,
                                 'cost': {'stack_cost': None,
                                          'standard_cost': {'cost_category': 'normal',
                                                            'resource_type': 'mp',
                                                            'values': (100,
                                                                       100,
                                                                       100)}},
                                 'dashed_distance': None,
                                 'independent_cast': False,
                                 'move_while_casting': True,
                                 'range': 0,
                                 'cds_modified': None,
                                 'resets_aa': False,
                                 'toggled': False,
                                 'travel_time': 0},
                           'w': {'base_cd': (7.0,
                                             6.0,
                                             5.0,
                                             4.0,
                                             3.0),
                                 'cast_time': 0,
                                 'castable': True,
                                 'channel_time': None,
                                 'cost': {'stack_cost': None,
                                          'standard_cost': {'cost_category': 'normal',
                                                            'resource_type': 'mp',
                                                            'values': (30,
                                                                       30,
                                                                       30,
                                                                       30,
                                                                       30)}},
                                 'dashed_distance': None,
                                 'independent_cast': False,
                                 'move_while_casting': True,
                                 'range': 0,
                                 'cds_modified': None,
                                 'resets_aa': True,
                                 'toggled': False,
                                 'travel_time': 0}}}

ABILITIES_EFFECTS = {
    'inn': {'enemy': {'passives': {'buffs': [], 'dmg': [], 'remove_buff': []}},
            'player': {'passives': {'buffs': ['inn_att_speed_initiator'], 'dmg': [], 'remove_buff': []}}},
    'e': {'enemy': {'actives': {'buffs': [], 'dmg': ['e_dmg_0'], 'remove_buff': []},
                    'passives': {'buffs': [], 'dmg': [], 'remove_buff': []}},
          'player': {'actives': {'buffs': ['e_dmg_red'],
                                 'cds_modified': {},
                                 'dmg': [],
                                 'remove_buff': []},
                     'passives': {'buffs': [], 'dmg': [], 'remove_buff': []}}},
    'q': {'enemy': {'actives': {'buffs': [], 'dmg': ['q_dmg_0'], 'remove_buff': []},
                    'passives': {'buffs': [], 'dmg': [], 'remove_buff': []}},
          'player': {'actives': {'buffs': [],
                                 'cds_modified': {},
                                 'dmg': [],
                                 'remove_buff': []},
                     'passives': {'buffs': [], 'dmg': [], 'remove_buff': []}}},
    'r': {'enemy': {'actives': {'buffs': [], 'dmg': [], 'remove_buff': []},
                    'passives': {'buffs': [], 'dmg': [], 'remove_buff': []}},
          'player': {'actives': {'buffs': ['r_dmg_red'],
                                 'cds_modified': {},
                                 'dmg': [],
                                 'remove_buff': []},
                     'passives': {'buffs': ['r_n_hit_initiator'],
                                  'dmg': [],
                                  'remove_buff': []}}},
    'w': {'enemy': {'actives': {'buffs': [], 'dmg': [], 'remove_buff': []},
                    'passives': {'buffs': [], 'dmg': [], 'remove_buff': []}},
          'player': {'actives': {'buffs': [],
                                 'cds_modified': {},
                                 'dmg': [],
                                 'remove_buff': []},
                     'passives': {'buffs': [], 'dmg': [], 'remove_buff': []}}}
}

ABILITIES_CONDITIONALS = {
    'q_apply_w_conditional': {'effects': {'apply_w_dmg': {'obj_name': 'q',
                                                          'lst_category': 'dmg',
                                                          'effect_type': 'ability_effect',
                                                          'mod_operation': 'append',
                                                          'names_lst': ['w_dmg_0'],
                                                          'tar_type': 'enemy'},
                                          'remove_w_buff': {'obj_name': 'q',
                                                            'lst_category': 'remove_buff',
                                                            'effect_type': 'ability_effect',
                                                            'mod_operation': 'append',
                                                            'names_lst': ['w_buff_0'],
                                                            'tar_type': 'player'}},
                              'triggers': {}},
    'r_nth_hit': {'effects': {'apply_r_dmg': {'obj_name': 'r_n_hit_initiator',
                                              'lst_category': 'cause_dmg',
                                              'effect_type': 'buff_on_hit',
                                              'mod_operation': 'append',
                                              'names_lst': ['r_dmg_0']},
                              'remove_r_counter_stacks': {'obj_name': 'r_n_hit_initiator',
                                                          'lst_category': 'remove_buff',
                                                          'effect_type': 'buff_on_hit',
                                                          'mod_operation': 'append',
                                                          'names_lst': ['r_hit_counter']},
                              'remove_r_counter_application': {'obj_name': 'r_n_hit_initiator',
                                                               'lst_category': 'apply_buff',
                                                               'effect_type': 'buff_on_hit',
                                                               'mod_operation': 'remove',
                                                               'names_lst': ['r_hit_counter']}},
                  'triggers': {'nth_hit_trig': {'buff_name': 'r_hit_counter',
                                                'operator': '>=',
                                                'owner_type': 'player',
                                                'stacks': 2,
                                                'trigger_type': 'buff'}}}}

CHAMPION_EXTERNAL_VARIABLES = {
    'hits_dodged_during_e': 5}

DEFAULT_ACTIONS_PRIORITY = ('r', 'e', 'q', 'AA', 'w')

ACTION_PRIORITIES_CONDITIONALS = {'w_after_AA': {'effects': {'effect_0': {'effect_type': 'top_priority',
                                                                          'obj_name': 'w'}},
                                                 'triggers': {'trigger_0': {'obj_name': 'AA',
                                                                            'trigger_type': 'previous_action'}}}}

RESOURCE_USED = 'mp'


SPELL_LVL_UP_PRIORITIES = {
    'at_least_one_lvl_in_each': True,
    'automatically_lvled_up': {},
    'max_spells_lvl_ups': 'standard',
    'spells_lvl_up_queue': ['r', 'w', 'q', 'e']}


class ChampionAttributes(abilities.VisualRepresentation):

    ABILITIES_ATTRIBUTES = ABILITIES_ATTRIBUTES
    ABILITIES_EFFECTS = ABILITIES_EFFECTS
    ABILITIES_CONDITIONALS = ABILITIES_CONDITIONALS
    RESOURCE_USED = RESOURCE_USED
    ACTION_PRIORITIES_CONDITIONALS = ACTION_PRIORITIES_CONDITIONALS
    DEFAULT_ACTIONS_PRIORITY = DEFAULT_ACTIONS_PRIORITY
    SPELL_LVL_UP_PRIORITIES = SPELL_LVL_UP_PRIORITIES

    def __init__(self, kwargs, external_vars_dct=CHAMPION_EXTERNAL_VARIABLES):
        abilities.VisualRepresentation.__init__(self, **kwargs)
        for i in external_vars_dct:
            setattr(ChampionAttributes, i, external_vars_dct[i])

