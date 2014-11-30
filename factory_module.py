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
OPTIONAL_ATTR_GENERAL = ('no_cost', 'resets_aa', 'channel_time')

# Independent of effect type
MANDATORY_ATTR_EFFECT = ('target_name',)
OPTIONAL_ATTR_EFFECT = ('radius', 'aoe', 'max_targets', )
# Dmg effect tags
MANDATORY_ATTR_DMG = ('dmg_category', )
OPTIONAL_ATTR_DMG = ('not_scaling', 'scaling', 'lifesteal', 'spellvamp', 'dmg_source', 'dot')
# Buff effect tags
MANDATORY_ATTR_BUFF = ('duration', )
OPTIONAL_ATTR_BUFF = ('affects_stat', 'is_trigger', 'delay_cd_start' 'on_hit')


class ApiElementDetector(object):

    EXPECTED_PUBLIC_OBJECTS = 1
    ABILITY_ORDER_IN_STORE = ('inn', 'q', 'w', 'e', 'r')

    def __init__(self,
                 champ_name):
        self.champ_name = champ_name

    def abilities_dct(self):
        """
        Returns the dict containing all abilities in the champion's stored api data.

        Raises:
            (BaseException) If more or less than one public objects are found in api module.
        Returns:
            (dict)
        """

        objects_found = 0
        dct_name = None

        champ_module = __import__('api_'+self.champ_name)

        for obj_name in dir(champ_module):
            if '_' != obj_name[0]:
                objects_found += 1
                dct_name = obj_name

        # Checks if it contains exact amount of public objects in API_DATA module.
        if objects_found != self.EXPECTED_PUBLIC_OBJECTS:
            raise BaseException('Expected exactly %s objects in API data module, got %s instead.' %
                                (self.EXPECTED_PUBLIC_OBJECTS, objects_found))

        dct = getattr(champ_module, dct_name)

        return dct['spells']

    def ability_dct(self, ability_name):
        ability_num = self.ABILITY_ORDER_IN_STORE.index(ability_name)

        return self.abilities_dct()[ability_num]

    def inn(self):
        return self.ability_dct(ability_name='inn')

    def q(self):
        return self.ability_dct(ability_name='q')

    def w(self):
        return self.ability_dct(ability_name='w')

    def e(self):
        return self.ability_dct(ability_name='e')

    def r(self):
        return self.ability_dct(ability_name='r')


class ChampionAttributeSetter(object):

    pass


class ChampionModuleCreator(ChampionAttributeSetter):

    pass

if __name__ == '__main__':

    garen = ApiElementDetector('garen')
    print(garen.q())
