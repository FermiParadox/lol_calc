import abilities

ABILITIES_ATTRIBUTES = {
    'buffs': {},
    'dmgs': {},
    'general_attributes': {'e': {'castable': False},
                           'inn': {},
                           'q': {'castable': False},
                           'r': {'castable': False},
                           'w': {'castable': False}}}
ABILITIES_EFFECTS = {
    'inn': {},
    'e': {},
    'q': {},
    'r': {},
    'w': {}}

ABILITIES_CONDITIONALS = {}

CHAMPION_EXTERNAL_VARIABLES = {}

DEFAULT_ACTIONS_PRIORITY = ('AA',)

SPELL_LVL_UP_PRIORITIES = {
    'at_least_one_lvl_in_each': True,
    'automatically_lvled_up': {},
    'max_spells_lvl_ups': 'standard',
    'spells_lvl_up_queue': ['r', 'q', 'e', 'w']}

ACTION_PRIORITIES_CONDITIONALS = {}

CHAMPION_STATS_DEPENDENCIES = set()

CHAMPION_RANGE_TYPE = 'ranged'

RESOURCE_USED = 'mp'


class ChampionAttributes(abilities.VisualRepresentation):
    ABILITIES_ATTRIBUTES = ABILITIES_ATTRIBUTES
    ABILITIES_EFFECTS = ABILITIES_EFFECTS
    ABILITIES_CONDITIONALS = ABILITIES_CONDITIONALS
    RESOURCE_USED = RESOURCE_USED
    ACTION_PRIORITIES_CONDITIONALS = ACTION_PRIORITIES_CONDITIONALS
    DEFAULT_ACTIONS_PRIORITY = DEFAULT_ACTIONS_PRIORITY
    SPELL_LVL_UP_PRIORITIES = SPELL_LVL_UP_PRIORITIES
    CHAMPION_STATS_DEPENDENCIES = CHAMPION_STATS_DEPENDENCIES

    def __init__(self, kwargs, external_vars_dct=CHAMPION_EXTERNAL_VARIABLES):
        self.player_range_type = CHAMPION_RANGE_TYPE
        abilities.VisualRepresentation.__init__(self, **kwargs)
        for i in external_vars_dct:
            setattr(ChampionAttributes, i, external_vars_dct[i])
