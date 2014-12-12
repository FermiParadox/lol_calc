import copy

# Info regarding API structure at https://developer.riotgames.com/docs/data-dragon

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


# Independent of effect type
MANDATORY_ATTR_EFFECT = ('target_type',)
OPTIONAL_ATTR_EFFECT = ('radius', 'aoe', 'max_targets', )
# Dmg effect tags
MANDATORY_ATTR_DMG = ('dmg_category', )
OPTIONAL_ATTR_DMG = ('not_scaling', 'scaling', 'lifesteal', 'spellvamp', 'dmg_source', 'dot')
# Buff effect tags
MANDATORY_ATTR_BUFF = ('duration', )
OPTIONAL_ATTR_BUFF = ('affects_stat', 'is_trigger', 'delay_cd_start', 'on_hit')


class ApiElementDetector(object):

    EXPECTED_PUBLIC_OBJECTS = 1
    ABILITY_ORDER_IN_STORE = ('inn', 'q', 'w', 'e', 'r')

    def __init__(self,
                 champ_name):
        
        self.champ_name = champ_name
        
        self.suggested_tags = {}
        self.set_suggested_tags()

        self.attr_types = {}
        self.set_attr_type()
    
    def set_suggested_tags(self):
        
        for ability_name in self.ABILITY_ORDER_IN_STORE:
            self.suggested_tags.update({ability_name: []})
    
    def set_attr_type(self):

        for ability_name in self.ABILITY_ORDER_IN_STORE:
            self.attr_types.update({ability_name: ['general', ]})

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
        """
        Returns a dict from API for given ability.

        There are 4 dicts in API data (one for each ability) and 1 stored manually for innate.

        Returns:
            (dict)
        """
        ability_num = self.ABILITY_ORDER_IN_STORE.index(ability_name)

        return self.abilities_dct()[ability_num]

    def create_attr_tags(self):

        for ability_name in self.ABILITY_ORDER_IN_STORE:

            tags = []
            if 'dealing' in self.ability_dct(ability_name):

                tags.append('scaling')

    
class ChampionAttributeSetter(ApiElementDetector):

    pass


class ChampionModuleCreator(ChampionAttributeSetter):

    pass


class AbilityAttributes(object):

    GENERAL_ATTRIBUTES = dict(
        cast_time='placeholder',
        range='placeholder',
        dmg_effect_names=['placeholder', ],
        buff_effect_names=['placeholder', ],
        cost=dict(
            type_1_placeholder='value_tpl_1_placeholder',
            ),
        move_while_casting='placeholder',
        dashed_distance='placeholder',
        channel_time='placeholder',
        reset_aa='placeholder',
        reduce_ability_cd=dict(
            name_placeholder='duration_placeholder'
        )
    )

    # (each ability can contain 0 or more 'dmg' attributes in its _STATS)
    DMG_ATTRIBUTES = dict(
        target_type='placeholder',
        dmg_category='placeholder',
        dmg_type='placeholder',
        values='placeholder',
        dmg_source='placeholder',
        # (e.g. None, 'normal': {stat1: coef1,}, 'by_ability_lvl': {stat1: (coef_lvl1,),})
        bonus_by_stats='placeholder',
        # (e.g. None, lifesteal, spellvamp)
        life_conversion_type='placeholder',
        radius='placeholder',
        dot='placeholder',
        max_targets='placeholder',
        aoe='placeholder',
    )

    # (each ability can contain 0 or more 'buff' attributes in its _STATS)
    BUFF_ATTRIBUTES = dict(
        target_type='placeholder',
        duration='placeholder',
        max_stacks='placeholder',
        affected_stat=dict(
            names=dict(
                stat_1=dict(
                    percent='placeholder',
                    additive='placeholder',),),
            affected_by=dict(
                stat_1='placeholder',)
        ),
        on_hit=dict(
            apply_buff=['placeholder', ],
            add_dmg=['placeholder', ],
            remove_buff=['placeholder', ]
        ),
        prohibit_cd_start='placeholder',
    )
    
    def __init__(self):
        # (each ability must contain 'general' attribute in its _STATS)
        self.x_STATS = dict(
            general=copy.deepcopy(self.GENERAL_ATTRIBUTES),
            )


if __name__ == '__main__':

    garen = ApiElementDetector('garen')
    print(garen.ability_dct('q').keys())
