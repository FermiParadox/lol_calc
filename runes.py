import app_runes_database as api_module
import palette
import copy

# Matched rune names.
API_TO_APP_STAT_NAME_MAP = dict(
    FlatMagicDamageMod=dict(additive='ap'),
    FlatSpellBlockMod=dict(additive='mr'),
    rFlatSpellBlockModPerLevel=dict(additive='mr_per_lvl'),
    rFlatArmorModPerLevel=dict(additive='armor_per_lvl'),
    FlatCritChanceMod=dict(additive='crit_chance'),
    rFlatMagicDamageModPerLevel=dict(additive='ap_per_lvl'),
    rFlatHPModPerLevel=dict(additive='hp_per_lvl'),
    FlatMPRegenMod=dict(additive='mp5'),
    rFlatHPRegenModPerLevel=dict(additive='hp5_per_lvl'),
    PercentEXPBonus=dict(percent='xp'),
    FlatEnergyPoolMod=dict(additive='energy'),
    rFlatEnergyRegenModPerLevel=dict(additive='ep5_per_lvl'),
    rFlatGoldPer10Mod=dict(additive='gp5'),
    FlatHPPoolMod=dict(additive='hp'),
    PercentAttackSpeedMod=dict(percent='att_speed'),
    rFlatMPRegenModPerLevel=dict(additive='mp5_per_lvl'),
    rPercentTimeDeadMod=dict(additive='death_time_reduction'),
    FlatEnergyRegenMod=dict(additive='ep5'),
    PercentSpellVampMod=dict(additive='spellvamp'),
    FlatCritDamageMod=dict(additive='crit_modifier'),
    rFlatMPModPerLevel=dict(additive='mp_per_lvl'),
    rFlatArmorPenetrationMod=dict(additive='flat_armor_penetration'),
    FlatMPPoolMod=dict(additive='mp'),
    FlatPhysicalDamageMod=dict(additive='ad'),
    rFlatPhysicalDamageModPerLevel=dict(additive='ad_per_lvl'),
    FlatHPRegenMod=dict(additive='hp5'),
    PercentLifeStealMod=dict(additive='lifesteal'),
    PercentMovementSpeedMod=dict(percent='move_speed'),
    FlatArmorMod=dict(additive='armor'),
    rFlatEnergyModPerLevel=dict(additive='energy_per_lvl'),
    rFlatMagicPenetrationMod=dict(additive='flat_magic_penetration'),
    PercentHPPoolMod=dict(percent='hp'),
    rPercentCooldownModPerLevel=dict(additive='cdr_per_lvl'),
    rPercentCooldownMod=dict(additive='cdr')
)


# ----------------------------------------------------------------------------------------------------------------------
_RUNE_BUFF_DCT_BASE = copy.deepcopy(palette.BUFF_DCT_BASE)
_RUNE_BUFF_DCT_BASE['duration'] = 'permanent'
_RUNE_BUFF_DCT_BASE['target_type'] = 'player'
_RUNE_BUFF_DCT_BASE['max_stacks'] = 1
_RUNE_BUFF_DCT_BASE['on_hit'] = None
_RUNE_BUFF_DCT_BASE['prohibit_cd_start'] = False
_RUNE_BUFF_DCT_BASE['dot'] = False


class ApiToAppRunesData(object):

    WHITESPACES_4 = ' '*4
    RUNES_DCT_STRUCTURE = {}
    RUNES_COLORS = ('red', 'blue', 'yellow', 'quint')

    def runes_dct(self):
        """
        Creates dict with tier 3 runes, categorized by color, stat and type.

        Structure: {quint: {ad: {percent:}}

        Return:
            dict
        """

        final_dct = {}

        # Inserts available colors in final_dct.
        for available_colors in self.RUNES_COLORS:
            final_dct.update({available_colors: {}})

        api_dct = api_module.API_RUNES_DATA['data']

        # Checks each rune.
        for rune_id in api_dct:

            # Filters out lower tier runes.
            for tier_num in api_dct[rune_id]['rune']['tier']:

                api_stat_name = list(api_dct[rune_id]['stats'].keys())[0]
                bonus_type = list(API_TO_APP_STAT_NAME_MAP[api_stat_name].keys())[0]
                stat_name = API_TO_APP_STAT_NAME_MAP[api_stat_name][bonus_type]

                # In the api some values (e.g. cdr) are negative.
                stat_value = abs(api_dct[rune_id]['stats'][api_stat_name])

                # In the api quints are refer to as 'black' .
                rune_color = api_dct[rune_id]['rune']['type']
                if rune_color == 'black':
                    rune_color = 'quint'

                if stat_name not in final_dct[rune_color]:
                    final_dct[rune_color].update({stat_name: {}})

                if bonus_type not in final_dct[rune_color][stat_name]:
                    final_dct[rune_color][stat_name].update({bonus_type: {}})

                final_dct[rune_color][stat_name][bonus_type].update({tier_num: stat_value})

        return final_dct

    def rune_dct_string(self):
        """
        Returns dict with tier 3 runes, categorized by color, stat and type.

        Return:
            dct
        """

        # Comment describing dct structure.
        dct_string = "# (eg. {'red': {}, 'quint': {}, } )"

        # Name of dict.
        dct_string += 'APP_RUNES_DCT = ' + str(self.runes_dct())

        dct_string = dct_string.replace(': {',
                                        ': \n%s{' % self.WHITESPACES_4)

        dct_string = dct_string.replace('}}, ',
                                        '}}, \n')

        return dct_string

    def insert_runes_to_module(self, module='runes'):
        """
        Inserts runes dict to module or replaces it if already existing.
        """


class RunesFinal(object):

    def __init__(self,
                 player_lvl,
                 selected_runes):

        self.player_lvl = player_lvl
        self.selected_runes = selected_runes        # e.g. {'red': {'ad': 5, 'ad_per_lvl': {'additive: 4},}, }
        self.runes_buff_store = _RUNE_BUFF_DCT_BASE     # e.g. {'stats': 'att_speed': {'percent': },}

        self.set_runes_buff_store()

    def set_runes_buff_store(self, rune_tier='3'):
        """
        Returns dict containing the stats given by all runes.

        Dict structure Color -> stat_name -> {'rune_name': '', 'stat_value': ''}
        """

        if self.selected_runes:

            for rune_color in self.selected_runes:

                # For all runes of that color..
                for stat_name in self.selected_runes[rune_color]:

                    for bonus_type in self.selected_runes[rune_color][stat_name]:

                        # Total stat from all same type runes.
                        total_stat = (self.selected_runes[rune_color][stat_name][bonus_type] *
                                      api_module.APP_RUNES_DCT[rune_color][stat_name][bonus_type][rune_tier])

                        # If it's a 'per_lvl' stat, calculates total value..
                        if 'per_lvl' in stat_name:
                            total_stat *= self.player_lvl
                            # .. and removes '_per_lvl' from the stat to be stored.
                            stat_name = stat_name.replace('_per_lvl', '')

                        # Creates keyword if stat doesnt exist
                        runes_buff_stats = self.runes_buff_store['stats']
                        if runes_buff_stats:
                            if stat_name not in runes_buff_stats:
                                runes_buff_stats.update({stat_name: {}})

                            if bonus_type not in runes_buff_stats[stat_name]:
                                runes_buff_stats[stat_name].update({bonus_type: total_stat})

                            # ..otherwise adds total stat value.
                            else:
                                runes_buff_stats[stat_name][bonus_type] += total_stat

        return

    def runes_buff(self):
        """
        Returns runes_buff_store.

        Used because of add_buff structure requiring a function instead of a dict.
        """

        return self.runes_buff_store


if __name__ == '__main__':

    ask_mod_rune_file = input('\nInsert all runes to module?')

    if ask_mod_rune_file.lower() in ('y', 'yes'):
        # Appends in api data.
        print('\nModifying stored api data...')
        ApiToAppRunesData().modify_rune_file()
        print('\nModification complete.')
    else:
        print('\nFinished without modifications.')