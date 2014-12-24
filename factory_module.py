import re
import time
import urllib.request
import champion_ids
import json
import pprint as pp

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

"""
# Independent of effect type
MANDATORY_ATTR_EFFECT = ('target_type',)
OPTIONAL_ATTR_EFFECT = ('radius', 'aoe', 'max_targets', )
# Dmg effect tags
MANDATORY_ATTR_DMG = ('dmg_category', )
OPTIONAL_ATTR_DMG = ('lifesteal', 'spellvamp', 'dmg_source', 'dot')
# Buff effect tags
MANDATORY_ATTR_BUFF = ('duration', )
OPTIONAL_ATTR_BUFF = ('affects_stat', 'is_trigger', 'delay_cd_start', 'on_hit')
"""


# ===============================================================
# ===============================================================
API_KEY = "9e0d1a10-04dc-4915-9995-67c4d6cb7ff2"


class RequestDataFromAPI(object):

    @staticmethod
    def _request_single_page_from_api(page_url):
        """
        Requests a page from API, after a brief delay.

        Return:
            (dct)
        """

        time.sleep(2)

        page_as_bytes_type = urllib.request.urlopen(page_url).read()
        page_as_str = page_as_bytes_type.decode('utf-8')

        return json.loads(page_as_str)

    @staticmethod
    def _data_storage(targeted_module, obj_name, str_to_insert):
        """
        Reads a file, informs user of file status (empty/full),
        and asks user action

        Returns:
            (None)
        """

        # Messages
        start_msg = '\n' + '-'*40
        start_msg += '\nWARNING !!!'
        start_msg += '\nStart API requests?\n'

        abort_msg = '\nData insertion ABORTED.\n'

        completion_msg = '\nData insertion COMPLETE.\n'

        # Confirms insertion
        user_start_question = input(start_msg)
        if user_start_question.lower() in ('yes', 'y'):
            pass
        else:
            print(abort_msg)
            return

        # Checks if module is non empty.
        with open(targeted_module, 'r') as read_module:

            if read_module.read() != '':
                user_answer = input('Non empty module detected. \nReplace data?\n')
                if user_answer.lower() in ('yes', 'y'):
                    print('Replacing existing file content..')
                else:
                    print(abort_msg)
                    return
            else:
                print('Inserting data..')

        # Creates file content.
        file_as_str = obj_name + ' = ' + str_to_insert

        # Replaces module content.
        with open(targeted_module, 'w') as edited_module:
            edited_module.write(file_as_str)

        print(completion_msg)

    def _request_single_page_from_api_as_str(self, page_url):

        page_as_dct = self._request_single_page_from_api(page_url=page_url)
        page_as_str = str(page_as_dct)

        return page_as_str


class RequestAllAbilitiesFromAPI(RequestDataFromAPI):

    def request_single_champ_from_api(self, champion_id):
        """
        Requests all data for a champion from api.

        Each champion's full data is at a separate page.

        Return:
            (dct)
        """

        time.sleep(2)
        page_url = ("https://eune.api.pvp.net/api/lol/static-data/eune/v1.2/champion/"
                    + champion_id
                    + "?champData=all&api_key="
                    + API_KEY)

        page_as_dct = self._request_single_page_from_api(page_url=page_url)

        return page_as_dct

    def request_all_champions_from_api(self, max_champions=None):
        """
        Creates a dict containing champion data of all champions.

        Returns:
            (dct)
        """

        all_champs_dct = {}
        all_champs_as_str = None

        for champs_requested, champ_id in enumerate(champion_ids.CHAMPION_IDS):

            if max_champions is not None:
                if champs_requested > max_champions:
                    break

            champ_name = champion_ids.CHAMPION_IDS[champ_id]
            page_as_dct = self.request_single_champ_from_api(champion_id=champ_id)

            all_champs_dct.update({champ_name: page_as_dct})

            all_champs_as_str = str(all_champs_dct)

        return all_champs_as_str

    def store_all_champions_data(self, max_champions=None):
        """
        Stores all champions' data from API.

        Returns:
            (None)
        """

        self._data_storage(targeted_module='api_champions_database.py',
                           obj_name='ALL_CHAMPIONS_ATTR',
                           str_to_insert=self.request_all_champions_from_api(max_champions=max_champions))


class RequestAllRunesFromAPI(RequestDataFromAPI):

    RUNES_PAGE_URL = "https://eune.api.pvp.net/api/lol/static-data/eune/v1.2/rune?runeListData=all&api_key=" + API_KEY

    def request_all_runes_from_api(self):
        """
        Requests all runes from API.

        Returns:
            (str)
        """

        return self._request_single_page_from_api_as_str(page_url=self.RUNES_PAGE_URL)

    def store_all_runes_from_api(self):

        self._data_storage(targeted_module='api_runes_database.py',
                           obj_name='ALL_RUNES',
                           str_to_insert=self.request_all_runes_from_api())


class RequestAllItemsFromAPI(RequestDataFromAPI):

    ITEMS_PAGE_URL = "https://eune.api.pvp.net/api/lol/static-data/eune/v1.2/item?itemListData=all&api_key=" + API_KEY

    def request_all_items_from_api(self):
        """
        Requests all items from API.

        Returns:
            (str)
        """

        return self._request_single_page_from_api_as_str(page_url=self.ITEMS_PAGE_URL)

    def store_all_items_from_api(self):

        self._data_storage(targeted_module='api_items_database.py',
                           obj_name='ALL_ITEMS',
                           str_to_insert=self.request_all_items_from_api())


class ExploreApiAbilities(object):

    def __init__(self):
        self.data_module = __import__('api_champions_database')
        self.all_champions_data_dct = self.data_module.ALL_CHAMPIONS_ATTR

    @staticmethod
    def label_in_tooltip(label, ability_dct):
        """
        Checks if given label is inside the ability description.

        Strips label of any leading or trailing whitespaces,
        to avoid API accidental naming inconsistency,
        and ignores case.

        Returns:
            (str)
        """

        label = label.lstrip()
        label = label.rstrip()

        # (upper or lower case is irrelevant)
        label = label.lower()
        if label in ability_dct['sanitizedTooltip']:
            return True
        else:
            return False

    def label_occurrences(self, champions_lst=None):
        """
        Returns dict containing all possible effect labels,
        how many times they occur and their existence in ability description.

        Returns:
            (dct)
        """

        # All champions, or a list of champions.
        if champions_lst is None:
            champ_lst = self.all_champions_data_dct
        else:
            champ_lst = champions_lst

        final_dct = {}

        for champ_name in champ_lst:
            for spell_dct in self.all_champions_data_dct[champ_name]['spells']:
                for label in spell_dct['leveltip']['label']:

                    # Label frequency.
                    if label not in final_dct:
                        final_dct.update({label: {'frequency': 1, 'in_tooltip': 0}})
                    else:
                        final_dct[label]['frequency'] += 1

                    # Label in description.
                    in_tooltip = self.label_in_tooltip(label=label,
                                                       ability_dct=spell_dct)
                    if in_tooltip:
                        final_dct[label]['in_tooltip'] += 1

        return final_dct

    def mod_link_names(self):
        """
        Checks frequency of all stat names of mods and which champions have them.

        Returns:
            (dct)
        """
        dct = {}

        for champ_name in self.all_champions_data_dct:
            for spell_dct in self.all_champions_data_dct[champ_name]['spells']:

                if 'vars' in spell_dct:
                    for coeff_dct in spell_dct['vars']:
                        link_name = coeff_dct['link']

                        if link_name in dct:
                            dct[link_name]['frequency'] += 1
                        else:
                            dct.update({link_name: {}})
                            dct[link_name].update({'frequency': 1, 'champions': [champ_name]})

                        if champ_name not in dct[link_name]['champions']:
                            dct[link_name]['champions'].append(champ_name)

        return dct

    def champion_base_stats(self, champion_name):
        """
        Prints selected champion's base stats.

        Returns:
            (None)
        """
        champ_stats = self.all_champions_data_dct[champion_name]['stats']

        pp.pprint(champ_stats)

    def champion_abilities(self, champion_name, ability_name=None):
        """
        Prints selected champion's abilities.

        Returns:
            (None)
        """
        champ_dct = self.all_champions_data_dct[champion_name]
        if ability_name is None:
            result = champ_dct['spells']

        else:
            if ability_name == 'inn':
                result = champ_dct['passive']
            else:
                result = champ_dct['spells']['qwer'.index(ability_name)]

        pp.pprint(result)


# ===============================================================
# ===============================================================
def check_all_same(lst):
    """
    Iterates through a list and checks if all its elements are the same.

    Returns:
        (bool)
    """

    all_same = True

    for item_num in range(len(lst)-1):

        if lst[item_num] != lst[item_num+1]:
            all_same = False
            break

    return all_same


def return_tpl_or_element(lst):
    """
    Returns whole list if its elements are the same,
    otherwise returns the first element.

    Args:
        tags: (str)
    Returns:
        (lst)
        (float) or (int) or (str)
    """
    if check_all_same(lst=lst):
        return lst[0]
    else:
        return lst


# ---------------------------------------------------------------
def suggest_attr_values(suggested_values_dct, modified_dct):
    """
    Suggests a value and stores the choice.

    Returns:
        (None)
    """

    print('\n'+'-'*40)
    print('\n(type "stop" at any point to exit)')

    for attr_name in suggested_values_dct:

        display = [' ', '1', '2', '3', '4', '5']
        shortcuts = ['', '1', '2', '3', '4', '5']

        suggested_val_tpl = suggested_values_dct[attr_name]

        # Ensures lists to be zipped have same length.
        shortcut_len = len(suggested_val_tpl)
        display = display[:shortcut_len]
        shortcuts = shortcuts[:shortcut_len]

        # INITIAL CHOICE MESSAGE
        msg = '-'*20
        msg += '\nATTRIBUTE: %s' % attr_name
        for shortcut_val, sugg_val, display_val in zip(shortcuts, suggested_val_tpl, display):
            msg += '\n%s: %s' % (display_val, sugg_val)
        msg += '\n'

        # CHOICE PROCESSING
        choice_num = None
        input_given = input(msg)

        # (breaks loot prematurely if asked)
        if input_given == 'stop':
            print('#### LOOP STOPPED ####')
            break

        for val_num, val in enumerate(shortcuts):
            if val == input_given:
                choice_num = val_num
                break

        # Checks if user chose a suggested value.
        if choice_num is not None:
            chosen_value = suggested_val_tpl[choice_num]
        else:
            chosen_value = input_given

        # Stores the choice and notifies user.
        choice_msg = '\n%s: %s\n' % (attr_name, chosen_value)
        modified_dct[attr_name] = chosen_value
        print(choice_msg)


# ---------------------------------------------------------------
def all_abilities_dct(champion_name):
    """
    Returns stored champion api abilities dict.

    Returns:
        (dct)
    """

    champ_module = __import__('api_'+champion_name)

    return champ_module.ABILITIES['spells']


def ability_dct_by_name(ability_name, champion_name):
    """
    Returns an ability's information contained in api data.

    Returns:
        (dct)
    """

    for ability_num, ability_letter in enumerate('qwer'[:]):
        if ability_letter == ability_name:
            return all_abilities_dct(champion_name=champion_name)[ability_num]

    raise BaseException('Invalid ability name.')


# ===============================================================
# ===============================================================
class GeneralAbilityAttributes(object):

    @staticmethod
    def general_attributes():
        return dict(
            cast_time='placeholder',
            range='placeholder',
            travel_time='placeholder',
            dmg_effect_names=['placeholder', ],
            buff_effect_names=['placeholder', ],
            base_cd='placeholder',
            cost=dict(
                # Main type auto inserted. Secondary manually.
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

    def __init__(self, api_spell_dct, champion_name):
        self.champion_name = champion_name
        self.api_spell_dct = api_spell_dct
        self.general_attr_dct = self.general_attributes()

    AUTOMATICALLY_FILLED_GEN_ATTR = ('range', 'cost', )

    SUGGESTED_VALUES_GEN_ATTR = dict(
        cast_time=(0.25, 0.5, 0),
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

        res_name = self.api_spell_dct['resource']

        # NO COST
        if 'No Cost' == res_name:
            return None

        # MP
        elif 'Mana Per Second' in res_name:
            return 'mp_per_sec'
        elif 'Mana Per Attack' in res_name:
            return 'mp_per_attack'
        elif '}} Mana' in res_name:
            return 'mp'

        # ENERGY
        elif '}} Energy' in res_name:
            return 'energy'

        # HP
        elif '}}% of Current Health' in res_name:
            return 'percent_hp'
        elif '}} Health Per Sec' in res_name:
            return 'hp_per_sec'
        elif '}} Health' in res_name:
            return 'hp'

        # RUMBLE
        elif '}} Heat' in res_name:
            return None

        # RENEKTON
        elif 'No Cost or 50 Fury' == res_name:
            return None

        # PASSIVES
        elif 'Passive' == res_name:
            return None

        else:
            raise BaseException('Unknown cost type detected.')

    def resource_cost_values(self):
        """
        Detects cost value tuple.

        All resource costs are in a list named "cost", except health related costs.

        Returns:
            (tpl)
        """

        # HEALTH COST
        if 'Health' in self.api_spell_dct['resource']:
            e_num = re.findall(r'e\d', self.api_spell_dct['resource'])[0]
            effect_number = int(e_num[:][-1])

            return tuple(self.api_spell_dct['effect'][effect_number])

        # ABILITIES WITHOUT A COST
        elif self.resource_cost_type is None:
            return None

        # NORMAL COST
        else:
            return tuple(self.api_spell_dct['effect']['cost'])

    def insert_base_cd_values(self):
        """
        Detects base_cd tuple and inserts value in dct,
        unless ability is passive (removes base_cd completely from dct).

        Returns:
            (None)
        """

        # NOT CASTABLE
        if self.api_spell_dct['resource'] == 'Passive':
            # Removes base_cd since its not applicable.
            del self.general_attr_dct['base_cd']

        # CASTABLE
        else:
            self.general_attr_dct['base_cd'] = return_tpl_or_element(lst=self.api_spell_dct['cooldown'])

    def insert_resource(self):
        """
        Inserts resource cost type and values in general attr dict.

        Does NOT insert secondary resources used (e.g. teemo R stack cost).

        Returns:
            (None)
        """

        if self.resource_cost_type() is None:
            self.general_attr_dct['cost'] = None
        else:
            self.general_attr_dct['cost'] = {}
            self.general_attr_dct['cost'].update({self.resource_cost_type(): self.resource_cost_values()})

    def insert_range(self):
        """
        Detects and inserts an ability's range.

        Returns:
            (None)
        """

        range_val = self.api_spell_dct['range']

        # (if 'range' is 'self)
        if type(range_val) is str:
            self.general_attr_dct['range'] = 0

        else:
            self.general_attr_dct['range'] = return_tpl_or_element(lst=range_val)

    def auto_insert_attributes(self):
        """
        Groups all auto inserted attributes.

        Returns:
            (None)
        """
        self.insert_range()
        self.insert_resource()
        self.insert_base_cd_values()

    def suggest_gen_attr_values(self):
        suggest_attr_values(suggested_values_dct=self.SUGGESTED_VALUES_GEN_ATTR,
                            modified_dct=self.general_attr_dct)

    def run_class(self):

        self.auto_insert_attributes()
        self.suggest_gen_attr_values()


class DmgAbilityAttributes(object):

    """
    An ability can contain 0 or more "dmg attributes" in its _STATS.

    Each "dmg" must have a single responsibility.
    """

    def __init__(self, ability_name, api_spell_dct):
        self.api_spell_dct = api_spell_dct
        self.ability_name = ability_name
        self.ability_num = 'qwer'.index(self.ability_name)
        self.dmgs_dct = {}

    @staticmethod
    def dmg_attributes():
        return dict(
            target_type='placeholder',
            dmg_category='placeholder',
            dmg_type='placeholder',
            dmg_values='placeholder',
            dmg_source='placeholder',
            # (None or 'normal': {stat1: coeff1,} or 'by_ability_lvl': {stat1: (coeff_lvl1,),})
            mods='placeholder',
            # (None or lifesteal or spellvamp)
            life_conversion_type='placeholder',
            radius='placeholder',
            dot='placeholder',
            max_targets='placeholder',
            )

    @staticmethod
    def suggested_values_dmg_attr():
        
        return dict(
            target_type=('enemy', 'player'),
            # TODO insert more categories in class and then here.
            dmg_category=('standard_dmg', 'innate_dmg', 'chain_decay', 'chain_limited_decay', 'aa_dmg_value'),
            dmg_source=('q', 'w', 'e', 'r', 'inn'),
            life_conversion_type=('spellvamp', None, 'lifesteal'),
            radius=(None, ),
            dot=(False, True),
            max_targets=(1, 2, 3, 4, 5, 'infinite'),
            usual_max_targets=(1, 2, 3, 4, 5),
            )

    AUTOMATICALLY_FILLED_DMG_ATTR = ()

    @staticmethod
    def mod_stat_name_map():
        return dict(attackdamage='ad',
                    bonusattackdamage='bonus_ad',
                    spelldamage='ap',
                    armor='armor',
                    bonusarmor='bonus_armor',
                    bonushealth='bonus_hp',
                    bonusspellblock='bonus_ap',
                    health='hp',
                    mana='mp',)

    @staticmethod
    def single_dmg_dct_template_in_factory():
        return dict(
            dmg_type='placeholder',
            abbr_in_effects='placeholder',
            mod_1='placeholder',

            )

    @staticmethod
    def single_mod_dct_template_in_factory():
        return dict(
            abbr_in_effects='placeholder',

            )

    def raw_dmg_strings(self):
        """
        Detects all string parts related to dmg dealing in api ability description.

        Each result in the returned list,
        contains the name of the dmg shortcut (as named in api 'effect'),
        and the name of modifiers.

        Returns:
            (list)
        """

        api_string = self.api_spell_dct['sanitizedTooltip']

        # (e.g. ' {{ e1}} true damage' )
        p = re.compile(
            r"""
            (?:\s\{\{\s)\w\d(?:\s\}\})          # ' {{ e1 }}'
            [^,.]*?                             # any characters in between excluding , and .
            (?:true|magic|physical)             # true magic or physical
            \sdamage                            # ' damage'

            """, re.IGNORECASE | re.VERBOSE)
        lst = p.findall(api_string)

        return lst

    def effect_values_by_abbr(self, abbr):
        """
        Detects the values of an effect,
        and returns a tuple or float based on whether it changes or not.

        To be used ONLY for 'effect' contents (e.g. not dmg mods).

        Returns:
            (tpl)
            (float)
        """

        # (last character of modifier)
        effect_num = int(abbr[-1:])

        mod_val = self.api_spell_dct['effect'][effect_num]

        return return_tpl_or_element(lst=mod_val)

    def mod_value_and_stat(self, mod_shortcut):
        """
        Finds mod's value and the stat linked to the mod.

        Returns:
            (dct)
        """

        for mod_dct in self.api_spell_dct['vars']:
            if mod_dct['key'] == mod_shortcut:

                link_name = mod_dct['link']
                stat_name = self.mod_stat_name_map[link_name]
                mod_coeff = mod_dct['coeff']

                return {stat_name: mod_coeff}

    def insert_dmg_type_and_mods(self):
        """
        Detects dmg type, its abbreviation,
        and list of dmg modifier abbreviations and their values.

        Returns:
            (None)
        """

        dmgs_lst = self.raw_dmg_strings()

        for dmg_num, tooltip_fragment in enumerate(dmgs_lst):

            # INSERTS DMG NAME AND ATTRS
            # New temporary dmg name.
            new_dmg_name = 'dmg_' + str(dmg_num+1)
            self.dmgs_dct.update({new_dmg_name: self.dmg_attributes()})

            curr_dmg_dct = self.dmgs_dct[new_dmg_name]

            # INSERTS DMG VALUES
            dmg_val_abbrev = re.findall(r'\s\{\{\s(\w\d)\s\}\}', tooltip_fragment)[0]
            curr_dmg_dct['dmg_values'] = self.effect_values_by_abbr(abbr=dmg_val_abbrev)

            # INSERTS DMG TYPE
            dmg_type = re.search(r'true|magic|physical', tooltip_fragment).group()
            curr_dmg_dct['dmg_type'] = dmg_type

            # INSERTS MODS IN DMG
            curr_dmg_dct.update({'mods': {}})
            # Dmg mods in api 'effects'
            mod_val_abbrev_lst = re.findall(r'\+\{\{\s(\w\d)\s\}\}', tooltip_fragment)
            for mod_abbrev in mod_val_abbrev_lst:
                # Mod values and stats
                curr_dmg_dct['mods'].update(self.mod_value_and_stat(mod_shortcut=mod_abbrev))

            # INSERTS DMGS

            self.dmgs_dct.update({new_dmg_name: curr_dmg_dct})

    def suggest_dmg_attr_values(self):

        for dmg_temp_name in sorted(self.dmgs_dct):

            msg = '\n%s\n' % ('='*40)
            msg += '\n%s' % dmg_temp_name.upper()
            msg += '\ndmg_values: %s' % self.dmgs_dct[dmg_temp_name]['dmg_values']
            msg += '\nmods: %s' % self.dmgs_dct[dmg_temp_name]['mods']

            print(msg)

            suggest_attr_values(suggested_values_dct=self.suggested_values_dmg_attr(),
                                modified_dct=self.dmgs_dct[dmg_temp_name])


class BuffAbilityAttributes(object):

    """
    An ability can contain 0 or more 'buff' attributes in its _STATS.
    """

    @staticmethod
    def buff_attributes():
        return dict(
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


# ===============================================================
# ===============================================================
if __name__ == '__main__':

    import api_champions_database

    champName = 'ashe'
    allAbilities = api_champions_database.ALL_CHAMPIONS_ATTR[champName]['spells']

    testGen = False
    if testGen is True:
        for abilityDct in allAbilities:
            GeneralAbilityAttributes(api_spell_dct=abilityDct, champion_name='Mundo').run_class()
            break

    testDmg = False
    if testDmg is True:
        for abilityDct in allAbilities:
            dmgAttrInstance = DmgAbilityAttributes(api_spell_dct=abilityDct, ability_name='q')
            dmgAttrInstance.insert_dmg_type_and_mods()
            dmgAttrInstance.suggest_dmg_attr_values()
            d = dmgAttrInstance.dmgs_dct
            pp.pprint(d)

    testApiStorage = False
    if testApiStorage is True:
        RequestAllAbilitiesFromAPI().store_all_champions_data(max_champions=None)

    testExploration = True
    if testExploration is True:
        exploreFunc = ExploreApiAbilities().mod_link_names()
        pp.pprint(exploreFunc)