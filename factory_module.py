import re

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


class _ObsoleteClass(object):

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


# ===============================================================
def check_all_same(lst):
    """
    Iterates through a list and checks if all its elements are the same.
    
    Returns:
        (bool)
    """
    
    all_same = True

    for i in range(len(lst)-1):
        
        if lst[i] != lst[i+1]:
            all_same = False
            break
            
    return all_same


class GeneralAbilityAttributes(object):

    @staticmethod
    def general_attributes():
        return dict(
            cast_time='placeholder',
            range='placeholder',
            travel_time='placeholder',
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

    def __init__(self, api_ability_dct):
        self.api_ability_dct = api_ability_dct
        self.general_attr_dct = self.general_attributes()

    AUTOMATICALLY_FILLED_GEN_ATTR = ('range', 'cost', )

    SUGGESTED_VALUES_GEN_ATTR = dict(
        cast_time=(0.25, 0.5),
        travel_time=(0, 0.25, 0.5),
        move_while_casting=(False, True),
        dashed_distance=(None,),
        channel_time=(None,),
        reset_aa=(False, True),
    )

    def resource_cost_type(self):
        """
        Detects cost type and returns its name.

        Raises:
            (BaseException)
        Returns:
            (str)
            None
        """
        
        res_name = self.api_ability_dct['resource']

        # NO COST
        if 'No Cost' == res_name:
            return None

        # MP
        elif 'Mana Per Second' in res_name:
            return 'mp_per_sec'
        elif '}} Mana' in res_name:
            return 'mp'

        # ENERGY
        elif '}} Energy' in res_name:
            return 'energy'

        # HP
        elif '}}% of Current Health' in res_name:
            return 'current_hp'
        elif '}} Health Per Sec' in res_name:
            return 'hp_per_sec'
        elif '}} Health' in res_name:
            return 'hp'

        # RUMBLE
        elif '}} Heat' in res_name:
            return 'heat'

        # RENEKTON
        elif 'No Cost or 50 Fury' == res_name:
            return 'no_cost_or_50_fury'

        else:
            raise BaseException('Unknown cost type detected.')

    def resource_cost_values(self):
        """
        Detects cost value tuple.

        All resource costs are in a list named "cost", except health related costs.

        Returns:
            (tpl)
        """

        # HEALTH VALUES
        if 'Health' in self.api_ability_dct['resource']:
            e_num = re.findall(r'e\d', self.api_ability_dct['resource'])[0]
            effect_number = int(e_num[:][-1])

            return tuple(self.api_ability_dct['effect'][effect_number])

        else:
            return tuple(self.api_ability_dct['effect']['cost'])

    def insert_resource(self):
        """
        Inserts resource cost type and values in general attr dict.

        Does NOT insert secondary resources used (e.g. teemo R stack cost).

        Returns:
            None
        """

        self.general_attr_dct['cost'].update({self.resource_cost_type(): self.resource_cost_values()})

    def insert_range(self):
        """
        Detects and inserts an ability's range after naming it appropriately,
        based on whether it's fixed or scales per lvl.

        Returns:
            None
        """

        # Clears range and uses a different name.
        del self.general_attr_dct['range']

        range_val = self.api_ability_dct['range']

        # (if 'range' is 'self)
        if type(range_val) is str:
            range_val = 0
            range_category = 'fixed_range'

        else:
            if check_all_same(range_val):
                range_category = 'fixed_range'
                range_val = range_val[0]
            else:
                range_category = 'scaling_range'

        self.general_attr_dct.update({range_category: range_val})


class DmgAbilityAttributes(object):

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


class BuffAbilityAttributes(object):

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
    

if __name__ == '__main__':

    import api_mundo

    all_abilities = api_mundo.ABILITIES['spells']

    for ability_dct in all_abilities:
        mundo = GeneralAbilityAttributes(api_ability_dct=ability_dct)
        mundo.insert_resource()
        mundo.insert_range()

        print(mundo.general_attr_dct)

