"""
Module used for setting attributes for a champion's abilities.
There is always one 'general' keyword in _STATS, and 0 or more secondary effects.

Approach: Interactive.

Run as main and set attributes interactively.

Automatic functionality:
    -suggests ability attributes
    -suggests data source (that is, which tuple in api data to be used for given situation)
    -checks missing attributes
    -asks choice confirmation
    -creates source code (that is, champion module)

e.g.
garen=ChampionClassFactory(module_name='garen')
garen.q().gen_attr('reset_aa', 'no_cost')

"""

# (each ability contains 'general' attribute in its _STATS)
MANDATORY_ATTR_GENERAL = ('cast_time', 'delay', 'range', 'effect_names',)
SUGGESTED_ATTR_GENERAL = ('no_cost', 'resets_aa', )

# Probable tags independent of effect type
SUGGESTED_ATTR_EFFECT = ('radius', 'aoe', 'max_targets', )
# Dmg effect tags
SUGGESTED_ATTR_DMG = ('not_scaling', 'scaling', 'lifesteal', 'spellvamp', )
# Buff effect tags
SUGGESTED_ATTR_BUFF = ('affects_stat', 'is_trigger')


class ChampionAttributeSetter(object):

    pass


class ChampionModuleCreator(ChampionAttributeSetter):

    pass