import palette
from palette import Placeholder


ALL_SUMMONER_SPELL_NAMES = ('smite', 'exhaust', 'ignite', 'heal', 'flash', 'ghost', 'teleport', 'clairvoyance',
                            'cleanse')


IGNITE_TICKS = 5
IGNITE_DURATION = 5

_BASE_SUMMONERS_SPELLS_ATTRIBUTES = {
    'ignite': {'general_attributes': {'base_cd': 210,
                                      'cast_time': 0,
                                      'castable': True,
                                      'channel_time': None,
                                      'dashed_distance': None,
                                      'independent_cast': True,
                                      'move_while_casting': True,
                                      'range': 500,
                                      'resets_aa': False,
                                      'toggled': False,
                                      'travel_time': None},
               'buffs': {'ignite_dot_buff': {'buff_source': 'ignite',
                                             'dot': {'always_on_x_targets': 0,
                                                     'dmg_names': ['ignite_dmg'],
                                                     'period': IGNITE_DURATION/IGNITE_TICKS},
                                             'duration': IGNITE_DURATION,
                                             'max_stacks': 1,
                                             'max_targets': 1,
                                             'usual_max_targets': 1,
                                             'on_hit': {},
                                             'stats': {},
                                             'target_type': 'enemy'},
                         'ignite_grievous_wounds_buff': 'expressed_by_method'},
               'dmgs': {'ignite_dmg': {'crit_type': None,
                                       'delay': None,
                                       'dmg_category': 'standard_dmg',
                                       'dmg_source': 'ignite',
                                       'dmg_type': 'true',
                                       'dmg_values': Placeholder(),
                                       'dot': {'buff_name': 'ignite_dot_buff'},
                                       'heal_for_dmg_amount': False,
                                       'life_conversion_type': None,
                                       'max_targets': 1,
                                       'mods': {},
                                       'radius': None,
                                       'resource_type': 'hp',
                                       'target_type': 'enemy',
                                       'usual_max_targets': 1}}}
}

_BASE_SUMMONERS_SPELLS_EFFECTS = {'ignite': {'actives': {'buffs': ['ignite_dot_buff', 'grievous_wounds'],
                                                         'dmg': [],
                                                         'remove_buff': []},
                                             'passives': {'buffs': [],
                                                          'dmg': [],
                                                          'remove_buff': []}}}

# Duration is set independently for each usage of it, since multiple effects can cause this buff.
_GRIEVOUS_WOUNDS_BUFF_BASE = palette.SafeBuff({'buff_source': Placeholder(),
                                               'dot': False,
                                               'duration': Placeholder(),
                                               'max_stacks': 1,
                                               'max_targets': 1,
                                               'usual_max_targets': 1,
                                               'on_hit': {},
                                               'stats': {'percent_healing_reduction': {'additive': {'stat_mods': {},
                                                                                                    'stat_values': 0.5}}},
                                               'target_type': 'enemy',
                                               'prohibit_cd_start': {}})
_GRIEVOUS_WOUNDS_BUFF_BASE.delete_keys(['buff_source', 'duration'])

IGNITE_GRIEVOUS_WOUNDS_BUFF = {}
IGNITE_GRIEVOUS_WOUNDS_BUFF.update(_GRIEVOUS_WOUNDS_BUFF_BASE)
IGNITE_GRIEVOUS_WOUNDS_BUFF.update({'buff_source': 'ignite'})
IGNITE_GRIEVOUS_WOUNDS_BUFF.update({'duration': IGNITE_DURATION})

