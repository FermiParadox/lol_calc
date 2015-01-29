import api_champions_database
import re
import time
import urllib.request
import champion_ids
import json
import pprint as pp
import copy
import api_key
import palette
import ast


# Info regarding API structure at https://developer.riotgames.com/docs/data-dragon


# ===============================================================
# ===============================================================
def delimiter(num_of_lines, line_type='-'):
    """
    Creates a newline and then a long line string.

    Args:
        line_type: (str) Smallest element used for the creation of the line.
    Returns:
        (str)
    """

    string = '\n'
    string += line_type * num_of_lines

    return string


def fat_delimiter(num_of_lines):
    return delimiter(num_of_lines=num_of_lines, line_type='=')


# ---------------------------------------------------------------
def _return_or_pprint_complex_obj(print_mode, dct):
    """
    Used for pretty printing a dict or returning it.

    Args:
        print_mode: (bool)
    Returns:
        (None)
        (dct)
    """

    if print_mode is True:
        pp.pprint(dct)

    else:
        return dct


def _return_or_pprint_lst(print_mode, lst):
    """
    Used for pretty printing a list with separators between elements, or returning it.

    Args:
        print_mode: (bool)
    Returns:
        (None)
        (lst)
    """

    if print_mode is True:
        for elem in lst:
            pp.pprint(elem)
            print(delimiter(num_of_lines=5))
    else:
        return lst


# ---------------------------------------------------------------
class OuterLoopExit(BaseException):
    pass


class InnerLoopExit(BaseException):
    pass


# Loop exit keys.
INNER_LOOP_KEY = '!'
OUTER_LOOP_KEY = '!!'


def check_for_loop_exit(key):
    if key == OUTER_LOOP_KEY:
        print('#### OUTER LOOP EXITED ####')
        raise OuterLoopExit
    elif key == INNER_LOOP_KEY:
        print('#### INNER LOOP EXITED ####')
        raise InnerLoopExit


def _suggest_attr_values(suggested_values_dct, modified_dct, extra_start_msg='', stop_key=INNER_LOOP_KEY,
                         error_key=OUTER_LOOP_KEY):
    """
    Suggests a value and stores the choice.

    Value can be either picked from suggested values,
    or created by dev.

    Args:
        suggested_values_dct: (dct) e.g. {ability_attr: (val_1, val_2,), }
        stop_key: (str) When given as answer, exits this loop.
        error_key: (str) When given as answer, raises error to exit outer loop.
    Returns:
        (None)
    """

    start_msg = '\n' + delimiter(40)
    start_msg += '\n(type "%s" to exit inner loops)\n' % stop_key
    start_msg += '\n(type "%s" to exit outer loops)\n' % error_key
    start_msg += extra_start_msg
    print(start_msg)

    for attr_name in sorted(suggested_values_dct):

        suggested_val_tpl = suggested_values_dct[attr_name]

        # Ensures lists to be zipped have same length.
        shortcut_len = len(suggested_val_tpl)

        # INITIAL CHOICE MESSAGE
        msg = delimiter(num_of_lines=20)
        msg += '\nATTRIBUTE: %s\n' % attr_name
        for display_val, suggested_val in enumerate(suggested_val_tpl, 1):
            msg += '\n%s: %s' % (display_val, suggested_val)

        # CHOICE PROCESSING

        # (only "enter" as input is not accepted)
        while True:
            input_given = input(msg + '\n')
            if input_given != '':
                break
            else:
                print('No value given. Try again.')

        # (breaks loop prematurely if asked)
        check_for_loop_exit(key=input_given)

        choice_num = None
        # (checks if input is an int corresponding to a suggested value shortcut)
        try:
            int_form_input = int(input_given)
            if int_form_input >= 1:
                if int_form_input <= shortcut_len:
                    choice_num = int_form_input - 1
        except ValueError:
            pass

        if choice_num is not None:
            chosen_value = suggested_val_tpl[choice_num]
        else:
            chosen_value = input_given

        # Stores the choice and notifies dev.
        choice_msg = '%s: %s\n' % (attr_name, chosen_value)
        modified_dct[attr_name] = chosen_value
        print(choice_msg)


def loop_exit_handler(func):
    """
    Used for handling Abortion exceptions raised during Requests.
    """

    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except OuterLoopExit:
            pass
        except InnerLoopExit:
            pass

    return wrapped


def _new_automatic_attr_dct_name(targeted_dct, attr_type):
    """
    Creates a new name for an attr dct, ensuring no existing names are overwritten.

    Returns:
        (str)
    """

    new_attr_name = attr_type + '_1'

    if targeted_dct:

        for num in range(1, 100, 1):
            new_attr_name = attr_type + '_' + str(num)

            if new_attr_name not in targeted_dct:
                # If a suitable name has been found, exits method.
                return new_attr_name

    # If there was no existing attr dict, returns preset name value.
    else:
        return new_attr_name


# ---------------------------------------------------------------
def _suggest_lst_of_attr_values(suggested_values_lst, modified_lst, extra_start_msg='', stop_key=INNER_LOOP_KEY,
                                error_key=OUTER_LOOP_KEY):
    """
    Suggests values from a list to dev.

    Dev has to pick all valid values in his single answer.

    Returns:
        (None)
    """
    start_msg = '\n' + delimiter(40)
    start_msg += '\n(type "%s" to exit inner loops)\n' % stop_key
    start_msg += '\n(type "%s" to exit outer loops)\n' % error_key
    start_msg += extra_start_msg
    print(start_msg)

    for num, val in enumerate(suggested_values_lst, 1):
        print('%s: %s' % (num, val))

    # Asks dev.
    while True:
        dev_choice = input('\nSelect all valid names. (press only enter for empty)\n')

        # Exits loop if requested.
        check_for_loop_exit(dev_choice)

        # (only comma, whitespace and digits are valid characters, or empty string)
        if re.search(r'[^\d,\s]', dev_choice) is not None:
            print("\nInvalid answer. Answer may contain only digits, whitespaces and comma. (or enter)")

        else:
            # Checks if given values correspond to actual indexes.
            # If not, message is repeated.
            try:
                # (e.g. '2, 7,5, 1')
                pattern = re.compile(r'(\d{1,2})+')
                matches = re.findall(pattern, dev_choice)

                for match in matches:
                    index_num = int(match)
                    modified_lst.append(suggested_values_lst[index_num - 1])
                break

            except IndexError:
                print("\nInvalid answer. Indexes out of range.")


# ---------------------------------------------------------------
SPELL_SHORTCUTS = ('q', 'w', 'e', 'r')
ABILITY_SHORTCUTS = ('inn', ) + SPELL_SHORTCUTS
EXTRA_SPELL_SHORTCUTS = ('q2', 'w2', 'e2', 'r2')
ALL_POSSIBLE_ABILITIES_SHORTCUTS = ABILITY_SHORTCUTS + EXTRA_SPELL_SHORTCUTS


def spell_num(spell_name):
    return SPELL_SHORTCUTS.index(spell_name)


def ability_num(ability_name):
    if ability_name == 'inn':
        return 0
    else:
        return spell_num(spell_name=ability_name) + 1


# ---------------------------------------------------------------
def data_storage(targeted_module, obj_name, str_to_insert):
    """
    Reads a file, informs dev of file status (empty/full),
    and asks dev action.

    Returns:
        (None)
    """

    # Messages
    abort_msg = '\nData insertion ABORTED.\n'
    completion_msg = '\nData insertion COMPLETE.\n'

    # Checks if module is non empty.
    with open(targeted_module, 'r') as read_module:

        if read_module.read() != '':
            replace_msg = 'Non empty module detected (%s). \nReplace data?\n' % targeted_module
            dev_answer = input(replace_msg)
            if dev_answer.lower() == 'y':
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


# ===============================================================
# API REQUESTS
# ===============================================================
class RequestAborted(BaseException):
    pass


class RequestDataFromAPI(object):
    """
    Base class of RequestClasses.

    Champion data do not derive from the final method of this class,
    since multiple individual page requests must be combined.
    """

    @staticmethod
    def request_abortion_handler(func):
        """
        Used for handling Abortion exceptions raised during Requests.
        """

        def wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except RequestAborted as exception_msg:
                print(exception_msg)

        return wrapped

    @staticmethod
    def _request_confirmation(requested_item):
        """
        Asks dev if he wants to proceed with data requests from API with given API key.

        Args:
            requested_item: (str) Name of requested item from API, e.g. RUNES, ITEMS, ABILITIES.
        """

        # Messages
        start_msg = '\n' + delimiter(num_of_lines=40)
        start_msg += '\nWARNING !!!\n'
        start_msg += '\nAPI KEY USED: %s\n' % api_key.KEY
        start_msg += '\nStart API requests (%s)?\n' % requested_item

        abort_msg = '\nData request ABORTED.\n'

        dev_start_question = input(start_msg)
        if dev_start_question.lower() == 'y':
            pass
        else:
            raise RequestAborted(abort_msg)

    @staticmethod
    def request_single_page_from_api(page_url):
        """
        Requests a page from API, after a brief delay.

        Return:
            (dct)
        """

        time.sleep(2)
        print('\nRequest time: \n%s' % time.asctime())

        page_as_bytes_type = urllib.request.urlopen(page_url).read()
        page_as_str = page_as_bytes_type.decode('utf-8')

        return json.loads(page_as_str)

    def request_single_page_from_api_as_str(self, page_url, requested_item):
        """
        Requests a page after confirmation of the dev.

        Champion data requests are not derivatives of this method.

        Returns:
            (str)
        """

        self._request_confirmation(requested_item=requested_item)

        page_as_dct = self.request_single_page_from_api(page_url=page_url)
        page_as_str = str(page_as_dct)

        return page_as_str


class RequestAllAbilitiesFromAPI(RequestDataFromAPI):
    def _request_single_champ_from_api(self, champion_id):
        """
        Requests all data for a champion from api.

        Each champion's full data is a page request of its own,
        therefor

        Return:
            (dct)
        """

        page_url = ("https://eune.api.pvp.net/api/lol/static-data/eune/v1.2/champion/"
                    + champion_id
                    + "?champData=all&api_key="
                    + api_key.KEY)

        page_as_dct = self.request_single_page_from_api(page_url=page_url)

        return page_as_dct

    def _request_all_champions_from_api(self, max_champions=None):
        """
        Creates a dict containing champion data of all champions.

        Returns:
            (dct)
        """

        self._request_confirmation(requested_item='CHAMPION DATA')

        all_champs_dct = {}
        all_champs_as_str = None

        for champs_requested, champ_id in enumerate(champion_ids.CHAMPION_IDS):

            if max_champions is not None:
                if champs_requested > max_champions:
                    break

            champ_name = champion_ids.CHAMPION_IDS[champ_id]
            page_as_dct = self._request_single_champ_from_api(champion_id=champ_id)

            all_champs_dct.update({champ_name: page_as_dct})

            all_champs_as_str = str(all_champs_dct)

        return all_champs_as_str

    @RequestDataFromAPI.request_abortion_handler
    def store_all_champions_data(self, max_champions=None):
        """
        Stores all champions' data from API.

        Data stored is a dict with champion names as keywords,
        and champion ability content as value.

        Returns:
            (None)
        """

        data_storage(targeted_module='api_champions_database.py',
                     obj_name='ALL_CHAMPIONS_ATTR',
                     str_to_insert=self._request_all_champions_from_api(max_champions=max_champions))


class RequestAllRunesFromAPI(RequestDataFromAPI):
    RUNES_PAGE_URL = "https://eune.api.pvp.net/api/lol/static-data/eune/v1.2/rune?runeListData=all&api_key=" + api_key.KEY

    @RequestDataFromAPI.request_abortion_handler
    def store_all_runes_from_api(self):
        page_as_str = self.request_single_page_from_api_as_str(page_url=self.RUNES_PAGE_URL,
                                                               requested_item='RUNES')

        data_storage(targeted_module='api_runes_database.py',
                     obj_name='ALL_RUNES',
                     str_to_insert=page_as_str)


class RequestAllItemsFromAPI(RequestDataFromAPI):
    ITEMS_PAGE_URL = "https://eune.api.pvp.net/api/lol/static-data/eune/v1.2/item?itemListData=all&api_key=" + api_key.KEY

    @RequestDataFromAPI.request_abortion_handler
    def store_all_items_from_api(self):
        page_as_str = self.request_single_page_from_api_as_str(page_url=self.ITEMS_PAGE_URL,
                                                               requested_item='ITEMS')

        data_storage(targeted_module='api_items_database.py',
                     obj_name='ALL_ITEMS',
                     str_to_insert=page_as_str)


class RequestAllMasteriesFromAPI(RequestDataFromAPI):
    MASTERIES_PAGE_URL = ('https://eune.api.pvp.net/api/lol/static-data/eune/v1.2/mastery?masteryListData=all&api_key='
                          + api_key.KEY)

    @RequestDataFromAPI.request_abortion_handler
    def store_all_items_from_api(self):
        page_as_str = self.request_single_page_from_api_as_str(page_url=self.MASTERIES_PAGE_URL,
                                                               requested_item='MASTERIES')

        data_storage(targeted_module='api_masteries_database.py',
                     obj_name='ALL_MASTERIES',
                     str_to_insert=page_as_str)


# ===============================================================
#       API EXPLORATION
# ===============================================================
class ExploreBase(object):
    @staticmethod
    def _full_or_partial_match(searched_name, iterable):
        """
        Searches for given name, looking for an exact match, or a partial otherwise.

        Raises:
            (KeyValue) if more than one matches found, or no matches
        Returns:
            (str)
        """

        # EXACT MATCH
        try:
            for elem in iterable:
                if elem == searched_name:
                    return searched_name
        except KeyError:
            pass

        # PARTIAL MATCH
        partial_matches_lst = []

        for existing_name in iterable:
            existing_name = existing_name.lower()

            if searched_name.lower() in existing_name:
                partial_matches_lst.append(existing_name)

        tot_partial_matches = len(partial_matches_lst)
        if tot_partial_matches == 1:
            return partial_matches_lst[0]
        elif tot_partial_matches > 1:
            raise KeyError('More than one partial matches found.')
        else:
            raise KeyError('No full or partial match.')

    def champion_id(self, searched_name):
        """
        Finds a champion's id number.

        Returns:
            (int)
        """

        champ_ids_dct = champion_ids.CHAMPION_IDS
        # Dict with champ names as keys and ids as values.
        inverted_ids_dct = {val.lower(): key for key, val in champ_ids_dct.items()}

        match_found = self._full_or_partial_match(searched_name=searched_name, iterable=inverted_ids_dct)

        return int(inverted_ids_dct[match_found])

    @staticmethod
    def _append_all_or_matching_str(examined_str, modified_lst, raw_str=None):
        """
        Modifies a list by inserting a string that match given pattern.
        If no required pattern is given, simply appends string to list.

        Args:
            raw_str: (str) pattern of string in raw form or None
        Returns:
            (None)
        """

        # If a key phrase is selected and present, stores value.
        if raw_str is not None:
            pattern_1 = re.compile(raw_str, re.IGNORECASE | re.VERBOSE)
            if re.search(pattern_1, examined_str) is not None:
                modified_lst.append(examined_str)

        # If no required pattern, simply stores value.
        else:
            modified_lst.append(examined_str)

    @staticmethod
    def _store_and_note_frequency(string, modified_dct, name, only_freq=False, champions_or_items='champions'):
        """
        Modifies a dict by noting a string's frequency.

        Args:
            only_freq: (bool)
            champions_or_items: (str) 'champions' or 'items'. Used as dict keyword.
        Returns:
            (None)
        """
        if string not in modified_dct:
            modified_dct.update(
                {string: dict(
                    frequency=1, )})
        else:
            modified_dct[string]['frequency'] += 1

        if only_freq is False:
            if champions_or_items not in modified_dct[string]:
                modified_dct[string].update({champions_or_items: []})

            # Notes champion (or item) name.
            if name not in modified_dct[string][champions_or_items]:
                modified_dct[string][champions_or_items].append(name)


class ExploreApiAbilities(ExploreBase):
    def __init__(self):
        self.data_module = __import__('api_champions_database')
        self.all_champions_data_dct = self.data_module.ALL_CHAMPIONS_ATTR
        self.champions_lst = sorted(self.all_champions_data_dct)

    @staticmethod
    def _label_in_tooltip(label, ability_dct):
        """
        Checks if given label is inside the ability description.

        Strips label of any leading or trailing whitespaces,
        to avoid API accidental naming inconsistency,
        and ignores case.

        Returns:
            (str)
        """

        label = label.strip()

        # (upper or lower case is irrelevant)
        label = label.lower()

        if label in ability_dct['sanitizedTooltip'].lower():
            return True
        else:
            return False

    def label_occurrences(self, champions_lst=None, print_mode=False):
        """
        Finds all possible effect labels,
        how many times they occur and their existence in ability description.

        Returns:
            (dct)
            (None)
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

                    label = label.lower()

                    # Label frequency.
                    if label not in final_dct:
                        final_dct.update({label: {'frequency': 1, 'in_tooltip': 0}})
                    else:
                        final_dct[label]['frequency'] += 1

                    # Label in description.
                    in_tooltip = self._label_in_tooltip(label=label,
                                                        ability_dct=spell_dct)
                    if in_tooltip:
                        final_dct[label]['in_tooltip'] += 1

        return _return_or_pprint_complex_obj(print_mode=print_mode, dct=final_dct)

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

    def champion_base_stats(self, champion_name, print_mode=False):
        """
        Finds selected champion's base stats.

        Returns:
            (dct)
            (None)
        """

        champ_stats = self.all_champions_data_dct[champion_name]['stats']

        return _return_or_pprint_complex_obj(print_mode=print_mode, dct=champ_stats)

    def champion_abilities(self, champion_name, ability_name=None, print_mode=False):
        """
        Finds selected champion's abilities.

        Returns:
            (None)
        """

        champ_dct = self.all_champions_data_dct[champion_name]
        if ability_name is None:
            result = [champ_dct['passive'], ]
            result += champ_dct['spells']

        else:
            if ability_name == 'inn':
                result = champ_dct['passive']
            else:
                result = champ_dct['spells']['qwer'.index(ability_name)]

        return _return_or_pprint_complex_obj(print_mode=print_mode, dct=result)

    def champion_innates(self, champion_name=None, print_mode=False):
        """
        Returns a champion's (or all champions') innate dict,
        or prints it.

        Returns:
            (lst)
            (None)
        """
        if champion_name is not None:
            champ_lst = [champion_name, ]
        else:
            champ_lst = self.champions_lst

        for champ in champ_lst:
            if print_mode is True:
                self.champion_abilities(champion_name=champ, ability_name='inn', print_mode=True)
            else:
                return self.champion_abilities(champion_name=champ, ability_name='inn', print_mode=False)

    def sanitized_tooltips(self, champ=None, raw_str=None, print_mode=False):
        """
        Returns all tooltips for given champion (or for all champions),
        or prints it.

        If raw_str is provided, searches for its pattern.

        WARNING: VERBOSE flag chosen.

        Args:
            champ: (str) or (None)
            raw_str: (str) Normal str or raw str
        Returns:
            (lst)
            (None)
        """

        # All champions, or selected champion.
        if champ is None:
            champ_lst = self.all_champions_data_dct
        else:
            # (need a list so it inserts selection into a list)
            champ_lst = [champ, ]

        tooltips_lst = []

        for champ_name in champ_lst:
            for spell_dct in self.all_champions_data_dct[champ_name]['spells']:
                self._append_all_or_matching_str(examined_str=spell_dct['sanitizedTooltip'],
                                                 modified_lst=tooltips_lst,
                                                 raw_str=raw_str)

        # Checks if print mode is selected.
        return _return_or_pprint_lst(print_mode=print_mode, lst=tooltips_lst)

    def single_cost_category(self, champ_name, ability_name):
        """
        Finds a 'costType' in API for given champion and ability.

        Returns:
            (str)
        """

        return self.champion_abilities(champion_name=champ_name, ability_name=ability_name)['costType']

    def cost_categories(self, print_mode=False):
        """
        Finds all costType categories and their frequency of occurrence.

        Returns:
            (dct)
            (None) Prints results instead.
        """

        cost_categories_dct = {}

        for champ in self.champions_lst:
            for ability_name in SPELL_SHORTCUTS:
                category_name = self.single_cost_category(champ_name=champ, ability_name=ability_name)['costType']
                category_name.lower().strip()

                self._store_and_note_frequency(string=category_name,
                                               modified_dct=cost_categories_dct,
                                               name=champ)

        return _return_or_pprint_complex_obj(print_mode=print_mode, dct=cost_categories_dct)

    def resource_names(self, print_mode=False):
        """
        Finds all resources in API and their frequency of occurrence.

        Returns:
            (dct)
            (None) Prints results instead.
        """

        cost_categories_dct = {}

        for champ in self.champions_lst:
            champ_spells = self.champion_abilities(champion_name=champ)[1:]
            for spell_dct in champ_spells:

                try:
                    resource_name = spell_dct['resource'].rstrip().lower().lstrip()

                    self._store_and_note_frequency(string=resource_name,
                                                   modified_dct=cost_categories_dct,
                                                   name=champ)
                except KeyError:
                    pass

        return _return_or_pprint_complex_obj(print_mode=print_mode, dct=cost_categories_dct)


class ExploreApiItems(ExploreBase):
    def __init__(self):
        self.data_module = __import__('api_items_database')
        self.item_related_api_data = self.data_module.ALL_ITEMS
        self.all_items_by_id = self.item_related_api_data['data']
        self.used_items = self._used_items()

    MANDATORY_MAP_ID = 1
    DISALLOWED_ITEM_TAGS = ('trinket', 'consumable', )

    def _used_items(self):
        """
        Creates a dict containing only items that will be used.

        Excluded items:
            -not usable in required map
            -wards
            -trinkets
            -potions
            -elixirs
            -not in store

        Returns:
            (dct)
        """

        dct = {}

        for item_id in self.all_items_by_id:

            # MAP
            allowed_on_map = True
            # (if there is no map exclusion, then it is usable on required map)
            try:
                if self.all_items_by_id[item_id]['maps']['1'] is False:
                    allowed_on_map = False
            except KeyError:
                pass

            # PURCHASABLE
            purchasable = True
            if 'inStore' in self.all_items_by_id[item_id]:
                if self.all_items_by_id[item_id]['inStore'] is False:
                    purchasable = False

            # NON DISALLOWED TAG
            allowed_tags = True
            if 'tags' in self.all_items_by_id[item_id]:
                for tag in self.all_items_by_id[item_id]['tags']:
                    if tag.lower() in self.DISALLOWED_ITEM_TAGS:
                        allowed_tags = False

            # Checks if all conditions are met.
            if allowed_on_map and allowed_tags and purchasable:
                item_name = self.all_items_by_id[item_id]['name'].lower()

                # (order below matters for correct naming)
                item_name = item_name.replace('(ranged only)', '')
                item_name = item_name.replace('(melee only)', '')
                item_name = item_name.rstrip()
                item_name = item_name.replace(' ', '_')

                item_name = item_name.replace("'", '')
                item_name = item_name.replace('-', '_')
                item_name = item_name.replace(':', '_')

                dct.update({item_name: self.all_items_by_id[item_id]})

        return dct

    def item_dct(self, given_name, print_mode=False):
        """
        Checks for an exact match of given name,
        or a partial match otherwise.

        Raises:
            (KeyValue) if more than one matches found, or no matches
        Returns:
            (dct)
        """

        matched_name = self._full_or_partial_match(searched_name=given_name, iterable=self.used_items)

        return _return_or_pprint_complex_obj(print_mode=print_mode, dct=self.used_items[matched_name])

    def _item_elements(self, element_name, item=None, raw_str=None, print_mode=False):
        """
        Returns element for given item (or for all items),
        or prints it.

        If raw_str is provided, searches for its pattern.

        WARNING: VERBOSE flag chosen.

        Args:
            item: (str) or (None)
            raw_str: (str) Normal str or raw str
        Returns:
            (lst)
            (None)
        """

        # All items, or selected item.
        if item is None:
            item_lst = self.used_items
        else:
            # (need a list so it inserts selection into a list)
            item_lst = [item, ]

        descriptions_lst = []

        for item_name in item_lst:

            try:
                self._append_all_or_matching_str(examined_str=self.used_items[item_name][element_name],
                                                 modified_lst=descriptions_lst,
                                                 raw_str=raw_str)
            except KeyError:
                print("\n'%s' has no element '%s'" % (item_name, element_name))

        # Checks if print mode is selected.
        return _return_or_pprint_lst(print_mode=print_mode, lst=descriptions_lst)

    def sanitized_descriptions(self, item=None, raw_str=None, print_mode=False):
        """
        Returns "descriptions" for given item (or for all items),
        or prints it.

        Check parent method for more details.
        """

        return self._item_elements(element_name='sanitizedDescription', item=item,
                                   raw_str=raw_str, print_mode=print_mode)

    def item_tags(self, only_freq=False, print_mode=False):
        """
        Returns or pretty prints all item tags.
        """
        item_occurrence_dct = {}

        for item_name in self.used_items:

            try:
                tags_lst = self.used_items[item_name]['tags']

                for tag_str in tags_lst:
                    self._store_and_note_frequency(string=tag_str, modified_dct=item_occurrence_dct,
                                                   champions_or_items='items', name=item_name, only_freq=only_freq)

            except KeyError:
                print("\n'%s' has no element '%s'" % (item_name, 'tags'))

        return _return_or_pprint_complex_obj(print_mode=print_mode, dct=item_occurrence_dct)


# ===============================================================
#       ATTRIBUTE CREATION
# ===============================================================
class AttributesBase(object):
    def __init__(self, ability_name, champion_name):
        self.champion_name = champion_name
        self.ability_name = ability_name
        self.api_spell_dct = api_champions_database.ALL_CHAMPIONS_ATTR[champion_name]['spells'][
            spell_num(spell_name=ability_name)]
        self.api_innate_dct = api_champions_database.ALL_CHAMPIONS_ATTR[champion_name]['passive']
        self.sanitized_tooltip = self.api_spell_dct['sanitizedTooltip']
        # (removes None from API effect list)
        self.ability_effect_lst = copy.copy(self.api_spell_dct['effect'])[1:]
        # (some spells don't contain 'vars')
        try:
            self.ability_vars_dct = self.api_spell_dct['vars']
        except KeyError:
            self.ability_vars_dct = []

    @staticmethod
    def check_all_same(lst):
        """
        Iterates through a list and checks if all its elements are the same.

        Returns:
            (bool)
        """

        all_same = True

        for item_num in range(len(lst) - 1):

            if lst[item_num] != lst[item_num + 1]:
                all_same = False
                break

        return all_same

    def return_tpl_or_element(self, lst):
        """
        Returns whole list if its elements are the same,
        otherwise returns the first element.

        Args:
            tags: (str)
        Returns:
            (lst)
            (float) or (int) or (str)
        """
        if self.check_all_same(lst=lst):
            return lst[0]
        else:
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

        return self.return_tpl_or_element(lst=mod_val)

    def _champion_and_ability_msg(self):

        return '\nCHAMPION: %s, ABILITY: %s' % (self.champion_name, self.ability_name.upper())


class GeneralAbilityAttributes(AttributesBase):
    def __init__(self, ability_name, champion_name):
        AttributesBase.__init__(self,
                                ability_name=ability_name,
                                champion_name=champion_name)

        self.general_attr_dct = self.general_attributes()

    @staticmethod
    def general_attributes():
        return dict(
            cast_time='placeholder',
            range='placeholder',
            travel_time='placeholder',
            dmg_effect_names=['placeholder', ],
            buff_effect_names=['placeholder', ],
            base_cd='placeholder',
            cost=[
                # Main type auto inserted. Secondary manually.
                dict(
                    resource_type='placeholder',
                    values='values_tpl_placeholder',
                    cost_category='placeholder'
                ), ],
            move_while_casting='placeholder',
            dashed_distance='placeholder',
            channel_time='placeholder',
            resets_aa='placeholder',
            reduce_ability_cd=dict(
                name_placeholder='duration_placeholder'
            )
        )

    COST_CATEGORIES = ('normal', 'per_hit', 'per_second')

    USUAL_VALUES_GEN_ATTR = dict(
        cast_time=(0.25, 0.5, 0),
        travel_time=(0, 0.25, 0.5),
        move_while_casting=(False, True),
        dashed_distance=(None,),
        channel_time=(None,),
        resets_aa=(False, True),
    )

    def resource_cost_type(self):
        """
        Detects cost type and returns its name.

        Raises:
            (ValueError)
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
            raise ValueError('Unknown cost type detected.')

    def resource_cost_values(self):
        """
        Detects cost values tuple.

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
            return tuple(self.api_spell_dct['cost'])

    def cost_category(self):

        return ExploreApiAbilities().champion_abilities(champion_name=self.champion_name,
                                                        ability_name=self.ability_name)['costType'].lower()

    def fill_base_cd_values(self):
        """
        Detects base_cd tuple and inserts values in dct,
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
            self.general_attr_dct['base_cd'] = self.return_tpl_or_element(lst=self.api_spell_dct['cooldown'])

    def fill_cost_attrs(self):
        """
        Inserts cost attributes in general attr dict.

        Does NOT insert secondary resources used (e.g. teemo R stack cost).

        Returns:
            (None)
        """

        if self.resource_cost_type() is None:
            self.general_attr_dct['cost'] = None
        else:
            # Clears contents of 'cost' keyword,
            # and replaces them.
            self.general_attr_dct['cost'] = {}
            self.general_attr_dct['cost'].update({'resource_type': self.resource_cost_type()})
            self.general_attr_dct['cost'].update({'values': self.resource_cost_values()})
            self.general_attr_dct['cost'].update({'cost_category': self.cost_category()})

    def fill_range(self):
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
            self.general_attr_dct['range'] = self.return_tpl_or_element(lst=range_val)

    def auto_fill_attributes(self):
        """
        Groups all auto inserted attributes.

        Returns:
            (None)
        """
        self.fill_range()
        self.fill_cost_attrs()
        self.fill_base_cd_values()

    @loop_exit_handler
    def suggest_gen_attr_values(self):

        extra_msg = '\nGENERAL ATTRIBUTE CREATION\n'
        extra_msg += self._champion_and_ability_msg()

        _suggest_attr_values(suggested_values_dct=self.USUAL_VALUES_GEN_ATTR,
                             modified_dct=self.general_attr_dct,
                             extra_start_msg=extra_msg)

    def run_gen_attr_creation(self):
        """
        Inserts automatically some attributes and asks the dev for the rest.

        Returns:
            (None)
        """

        # Reset dict content
        self.general_attr_dct = {}

        msg = fat_delimiter(40)
        msg += "\nABILITY'S GENERAL ATTRIBUTES:" + self._champion_and_ability_msg() + '\n'

        print(msg)

        self.auto_fill_attributes()
        self.suggest_gen_attr_values()

        print(msg)
        pp.pprint(self.general_attr_dct)


class DmgAbilityAttributes(AttributesBase):
    """
    Each instance of this class is used for creation of all dmgs of a single ability.

    An ability can contain 0 or more "dmg attributes" in its _STATS.

    (Each "dmg" must have a single responsibility.)
    """

    def __init__(self, ability_name, champion_name):
        AttributesBase.__init__(self,
                                ability_name=ability_name,
                                champion_name=champion_name)

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
    def usual_values_dmg_attr():

        return dict(
            target_type=('enemy', 'player'),
            # TODO insert more categories in class and then here.
            dmg_category=('standard_dmg', 'innate_dmg', 'chain_decay', 'chain_limited_decay', 'aa_dmg_value'),
            dmg_source=ALL_POSSIBLE_ABILITIES_SHORTCUTS,
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
                    mana='mp', )

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

        api_string = self.sanitized_tooltip

        # (e.g. ' {{ e1}} true damage' )
        p = re.compile(
            r"""
            \s\{\{\s\w\d{1,2}\s\}\}             # ' {{ e1 }}'
            [^,.]*?                             # any characters in between excluding , and .
            (?:true|magic|magical|physical)     # 'true', 'magic' (sometimes referred as 'magical') or 'physical'
            \sdamage                            # ' damage'

            """, re.IGNORECASE | re.VERBOSE)
        lst = p.findall(api_string)

        return lst

    def mod_value_and_stat(self, mod_shortcut):
        """
        Finds mod's value and the stat linked to the mod.

        Returns:
            (dct)
        """

        for mod_dct in self.api_spell_dct['vars']:
            if mod_dct['key'] == mod_shortcut:
                link_name = mod_dct['link']
                stat_name = self.mod_stat_name_map()[link_name]
                mod_coeff = mod_dct['coeff']

                return {stat_name: mod_coeff}

    def _check_if_dot(self):
        """
        Check if given ability contains hints of a dot.

        Returns:
            (bool)
        """

        string = self.sanitized_tooltip

        # 'damage over 2.5 seconds' or 'damage over {{ d1 }} seconds'
        pattern_1 = re.compile(
            r"""
            damage
            \s
            (?: over | for )
            \s
            ( \d+\.?\d* | \{\{\s \w\d{1,2} \s\}\} )          # ('4' or '2.3') or '{{ e1 }}'
            \s
            seconds

            """, re.IGNORECASE | re.VERBOSE)

        result_1 = re.search(pattern_1, string)

        if result_1:
            return True
        else:
            return False

    def fill_dot(self, dmg_dct):

        dmg_dct['dot'] = self._check_if_dot()

    def _Dot_duration(self):
        """
        Not complete (or needed at all probably).
        """

        string = self.sanitized_tooltip

        p = re.compile(
            r"""
            damage
            \s
            over
            \s
            ( \d+\.?\d* | \{\{\s \w\d{1,2} \s\}\} )          # ('4' or '2.3') or '{{ e1 }}'
            \s
            seconds

            """, re.IGNORECASE | re.VERBOSE)

        results_found = re.findall(p, string)

        # If no matches are found returns message.
        if results_found:
            duration_str = results_found[0]
        else:
            return 'No dots detected.'

        # Else converts string to float (or list of floats) and returns it.
        if '{' in duration_str:
            abbr = re.search(r'\w\d{1,2}', duration_str)
            return self.api_spell_dct['effects'][abbr]

        else:
            return float(duration_str)

    def _suggest_dmg_values(self, dmg_name):
        """
        Allows dev to choose between possible values from ability's 'effect' list.

        Returns:
            (None)
        """

        ability_dct = ExploreApiAbilities().champion_abilities(champion_name=self.champion_name,
                                                               ability_name=self.ability_name)

        effect_lst = ability_dct['effect']

        # Groups all possible lists in a list.
        lst_of_values = []
        for lst in effect_lst:
            if lst is not None:
                lst_of_values.append(lst)

        while True:
            msg = '\n' + delimiter(num_of_lines=10)
            msg += '\nSelect dmg values.'

            for couple in enumerate(lst_of_values, 1):
                msg += '\n%s: %s' % couple

            chosen_lst_num = input(msg + '\n')

            try:
                selected_lst = lst_of_values[int(chosen_lst_num) - 1]
                self.dmgs_dct[dmg_name]['dmg_values'] = selected_lst
                return

            except ValueError:
                print('Invalid selection. Try again.')

    def fill_dmg_type_and_mods_and_dot(self):
        """
        Detects dmg type, its abbreviation,
        and list of dmg modifier abbreviations and their values.

        Returns:
            (None)
        """

        dmgs_lst = self.raw_dmg_strings()

        for tooltip_fragment in dmgs_lst:

            # INSERTS DMG NAME AND ATTRS
            # New temporary dmg name.
            new_dmg_name = _new_automatic_attr_dct_name(targeted_dct=self.dmgs_dct, attr_type='dmg')
            self.dmgs_dct.update({new_dmg_name: self.dmg_attributes()})

            curr_dmg_dct = self.dmgs_dct[new_dmg_name]

            # INSERTS DMG VALUES
            dmg_val_abbrev = re.findall(r'\s\{\{\s(\w\d{1,2})\s\}\}', tooltip_fragment)[0]
            curr_dmg_dct['dmg_values'] = self.effect_values_by_abbr(abbr=dmg_val_abbrev)

            # INSERTS DMG TYPE
            dmg_type = re.search(r'true|magic|physical', tooltip_fragment, re.IGNORECASE).group()
            curr_dmg_dct['dmg_type'] = dmg_type.lower()

            # INSERTS MODS IN DMG
            curr_dmg_dct.update({'mods': {}})
            # Dmg mods in api 'effects'
            mod_val_abbrev_lst = re.findall(r'\+\{\{\s(\w\d{1,2})\s\}\}', tooltip_fragment)
            for mod_abbrev in mod_val_abbrev_lst:
                # Mod values and stats
                curr_dmg_dct['mods'].update(self.mod_value_and_stat(mod_shortcut=mod_abbrev))

            # INSERTS DMGS
            self.dmgs_dct.update({new_dmg_name: curr_dmg_dct})

            # INSERTS DOT
            self.fill_dot(self.dmgs_dct[new_dmg_name])

    def suggest_dmg_attr_values(self):

        for dmg_temp_name in sorted(self.dmgs_dct):
            msg = '\ndmg_values: %s' % self.dmgs_dct[dmg_temp_name]['dmg_values']
            msg += '\nmods: %s' % self.dmgs_dct[dmg_temp_name]['mods']

            print(msg)

            _suggest_attr_values(suggested_values_dct=self.usual_values_dmg_attr(),
                                 modified_dct=self.dmgs_dct[dmg_temp_name])

    def modify_dmg_names(self):
        """
        Asks dev to provide new names for each dmg of given ability.

        Returns:
            (None)
        """

        # Checks if there is anything to rename.
        if not self.dmgs_dct:
            return

        modification_start_msg = '\n\n' + delimiter(num_of_lines=40)

        print(modification_start_msg)

        for dmg in sorted(self.dmgs_dct):
            pp.pprint(self.dmgs_dct)

            while True:
                new_dmg_name = input('\nInsert new dmg name for %s. (press enter to skip)\n' % dmg)
                if new_dmg_name == '':
                    print('\nName will not change.\n')
                    break

                elif new_dmg_name in self.dmgs_dct:
                    print('\nName already exists.')

                else:
                    # (stores temporarily previous content of dmg_x)
                    dct_content = self.dmgs_dct[dmg]
                    del self.dmgs_dct[dmg]
                    # (and assigns it to new name)
                    self.dmgs_dct.update({new_dmg_name: dct_content})
                    print('\nNew name: %s' % new_dmg_name)
                    break

        print('\nDmg name modification ENDED. \n%s' % delimiter(num_of_lines=10))

    def insert_extra_dmg(self):
        """
        Allows dev to insert extra dmg dicts that have been missed by automatic inspection.

        Returns:
            (None)
        """

        while True:
            print('\n' + delimiter(num_of_lines=10))
            extra_dmg = input('\nInsert extra dmg?\n')

            if extra_dmg.lower() == 'y':
                new_dmg_name = _new_automatic_attr_dct_name(targeted_dct=self.dmgs_dct, attr_type='dmg')
                self.dmgs_dct.update({new_dmg_name: self.dmg_attributes()})
                self._suggest_dmg_values(dmg_name=new_dmg_name)
                _suggest_attr_values(suggested_values_dct=self.usual_values_dmg_attr(),
                                     modified_dct=self.dmgs_dct[new_dmg_name],
                                     extra_start_msg='\nManually inserted dmg.')
                self.modify_dmg_names()

            # "enter", 'n' and 'no'
            elif extra_dmg.lower() == 'n':
                break

            else:
                print('Invalid answer.')

    @loop_exit_handler
    def _run_dmg_attr_creation_without_result_msg(self):
        """
        Runs all relevant methods for each dmg attribute detected.

        Returns:
            (None)
        """

        self.fill_dmg_type_and_mods_and_dot()
        self.suggest_dmg_attr_values()
        self.insert_extra_dmg()
        self.modify_dmg_names()

    def run_dmg_attr_creation(self):
        """
        Runs all relevant methods for each dmg attribute detected.

        Returns:
            (None)
        """

        msg = fat_delimiter(40)
        msg += '\nDMG ATTRIBUTES:'
        msg += self._champion_and_ability_msg()
        print(msg)

        # Resets dict contents.
        self.dmgs_dct = {}

        self._run_dmg_attr_creation_without_result_msg()

        print(msg)
        print('\nRESULT\n')
        pp.pprint(self.dmgs_dct)


class BuffAbilityAttributes(AttributesBase):
    """
    Each instance of this class is used for a single ability.

    An ability can contain 0 or more 'buff' attributes in its _STATS.
    """

    def __init__(self, ability_name, champion_name):
        AttributesBase.__init__(self,
                                ability_name=ability_name,
                                champion_name=champion_name)

        self.buffs_dct = {}

    @staticmethod
    def buff_attributes():
        return dict(
            target_type='placeholder',
            duration='placeholder',
            max_stacks='placeholder',
            affected_stats=dict(
                placeholder_stat_1='placeholder'
            ),
            on_hit=dict(
                apply_buff=['placeholder', ],
                add_dmg=['placeholder', ],
                reduce_cd={},
                remove_buff=['placeholder', ]
            ),
            prohibit_cd_start='placeholder',
        )

    @staticmethod
    def affected_stat_attributes():
        return dict(
            bonus_type='placeholder',
            stat_values='placeholder',
            stat_mods={})

    @staticmethod
    def stat_mod_attributes():
        return dict(
            placeholder_stat_1='placeholder')

    STAT_NAMES_IN_TOOLTIPS_TO_APP_MAP = {'attack damage': 'ad',
                                         'ability power': 'ap',
                                         'attack speed': 'att_speed',
                                         'movement speed': 'move_speed',
                                         'armor': 'armor',
                                         'magic resist': 'mr',
                                         'critical strike chance': 'crit_chance',
                                         'armor penetration': 'armor_penetration'}

    NTH_TUPLE = ('second', 'third', 'forth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth')

    USUAL_BUFF_ATTR_VALUES = dict(
        target_type=('player', 'enemy'),
        max_stacks=(1,),
        duration=(1,),
        prohibit_cd_start=(None, )
    )

    def _stat_names_in_tooltip(self):
        """
        Checks if ability contains a buff that modifies stats.

        Returns:
            (lst)
        """

        stats_lst = []

        for stat_name in self.STAT_NAMES_IN_TOOLTIPS_TO_APP_MAP:
            if stat_name in self.sanitized_tooltip.lower():
                stats_lst.append(stat_name)

        return stats_lst

    def ask_amount_of_buffs(self):
        """
        Asks dev for amount of buffs for given ability.

        Returns:
            (None)
        """

        start_msg = '\n'
        start_msg += delimiter(num_of_lines=10)
        start_msg += '\nHow many buffs in ability %s?' % self.ability_name

        # Repeat until valid answer is given.
        while True:
            num_of_buffs = input(start_msg + '\n')

            check_for_loop_exit(key=num_of_buffs)

            try:
                num_iter = range(int(num_of_buffs))

                for _ in num_iter:
                    new_buff_name = _new_automatic_attr_dct_name(targeted_dct=self.buffs_dct, attr_type='buff')
                    self.buffs_dct.update({new_buff_name: self.buff_attributes()})

                end_msg = '\n%s buffs selected.' % num_of_buffs
                print(end_msg)
                break

            except ValueError:
                print('Invalid answer. Try again.')
                pass

    def change_buff_names(self):
        """
        Asks if buff name change is needed,
        and if so goes through every buff name.

        Returns:
            (None)
        """

        # Does nothing if no buffs exist.
        if self.buffs_dct:

            msg = delimiter(40)
            msg += '\nChange buff names?\n'

            while True:
                change_buffs_answer = input(msg)

                if change_buffs_answer == 'y':
                    for previous_buff_name in sorted(self.buffs_dct):
                        new_name_msg = delimiter(10)
                        new_name_msg += '\nInsert new name for: %s. (press enter to skip)\n' % previous_buff_name

                        new_name = input(new_name_msg)

                        if new_name == '':
                            print('\nNot changed.')
                        # If new name is selected, creates new buff with previous value,
                        # .. then removes previous buff.
                        else:
                            self.buffs_dct.update({new_name: self.buffs_dct[previous_buff_name]})
                            del self.buffs_dct[previous_buff_name]
                    break
                elif change_buffs_answer == 'n':
                    break
                else:
                    print('Invalid answer. Try again.')

    def suggest_stat_mods(self, buff_name, affected_stat):
        """
        Checks if affected stat has any possible mod-stats,
        and suggests them.

        Returns:
            (None)
        """

        # Removes affected stat name from possible mods.
        possible_mods = self._stat_names_in_tooltip()
        possible_mods.remove(affected_stat)

        # Checks if there are any stats left in ability tooltip.
        if possible_mods:

            affected_stat_app_form = self.STAT_NAMES_IN_TOOLTIPS_TO_APP_MAP[affected_stat]

            start_msg = delimiter(40)
            start_msg += '\nCHAMPION: %s, ABILITY: %s' % (self.champion_name, self.ability_name)
            start_msg += '\nSTAT: %s' % affected_stat_app_form

            for stat_mod in possible_mods:

                stat_mod_msg = delimiter(10)
                stat_mod_msg += '\nIs %s modified by %s?' % (affected_stat, stat_mod)

                stat_mod_app_form = self.STAT_NAMES_IN_TOOLTIPS_TO_APP_MAP[stat_mod]

                while True:
                    stat_mods_answer = input(stat_mod_msg + '\n')
                    if stat_mods_answer.lower() == 'y':

                        # Creates new mod dict for affected stat.
                        self.buffs_dct[buff_name]['affected_stats'][affected_stat_app_form].update({'stat_mods': {}})
                        # Inserts new mod name.
                        self.buffs_dct[buff_name]['affected_stats'][affected_stat_app_form]['stat_mods'].update(
                            {stat_mod_app_form: None})

                        pp.pprint(self.ability_vars_dct)

                        # (params for method below)
                        mod_vals_lst = [var_dct['coeff'] for var_dct in self.ability_vars_dct]
                        suggested_vals_dct = {stat_mod_app_form: mod_vals_lst}
                        modified_dct = self.buffs_dct[buff_name]['affected_stats'][affected_stat_app_form]['stat_mods']
                        extra_msg = '\nmod value:'

                        _suggest_attr_values(suggested_values_dct=suggested_vals_dct,
                                             modified_dct=modified_dct,
                                             extra_start_msg=extra_msg)
                        break
                    elif stat_mods_answer.lower() in ('n', 'no'):
                        self.buffs_dct[buff_name]['affected_stats'][affected_stat_app_form]['stat_mods'] = None
                        break
                    else:
                        print('\nInvalid answer. Try again.')

    def suggest_affected_stats_and_their_attrs(self, buff_name):
        """
        Suggests stats that may be affected by a buff,
        and each stat's mods.

        Returns:
            (None)
        """

        for affected_stat in self._stat_names_in_tooltip():
            # Asks if buff affects given stat.
            msg = delimiter(40)
            msg += '\nDoes %s affect %s?\n' % (buff_name, affected_stat.upper())

            while True:
                buff_affects_stat = input(msg)
                if buff_affects_stat.lower() == 'y':

                    stat_name = self.STAT_NAMES_IN_TOOLTIPS_TO_APP_MAP[affected_stat]

                    msg = 'AFFECTED STAT: %s' % stat_name

                    self.buffs_dct[buff_name]['affected_stats'].update({stat_name: self.affected_stat_attributes()})

                    # (dict form effects for parameter below)
                    eff_values_dct = {'stat_values': self.ability_effect_lst,
                                      'bonus_type': ('additive', 'multiplicative')}

                    _suggest_attr_values(suggested_values_dct=eff_values_dct,
                                         modified_dct=self.buffs_dct[buff_name]['affected_stats'][stat_name],
                                         extra_start_msg=msg)

                    # STAT MODS
                    self.suggest_stat_mods(buff_name=buff_name, affected_stat=affected_stat)

                    break
                elif buff_affects_stat.lower() == 'n':
                    break
                else:
                    print('Invalid answer. Try again')

    def suggest_possible_stat_attributes(self, buff_name):
        """
        Suggests possible values for stats,
        mods of the stats (if they are scaling),
        and mod values.

        Returns:
            (None)
        """

        start_msg = delimiter(10)
        start_msg += '\nBUFF: %s' % buff_name
        start_msg += '\nDoes it modify stats?'

        while True:
            changes_stats = input(start_msg + '\n')

            if changes_stats.lower() == 'n':
                print("\nDoesn't modify stats.")
                self.buffs_dct[buff_name]['affected_stats'] = None
                break

            elif changes_stats.lower() == 'y':
                if self._stat_names_in_tooltip():
                    # (clears placeholder)
                    del self.buffs_dct[buff_name]['affected_stats']['placeholder_stat_1']

                    # Inserts each affected stat.
                    self.suggest_affected_stats_and_their_attrs(buff_name=buff_name)

                break

            else:
                print('\nInvalid answer. Try again.')

    def every_nth_attack(self):
        """
        Checks if ability tooltip indicates every_x_hits functionality,
        and if so returns the nth value as a string.

        NOTE: Not designed for multiple matches in tooltip.
        Should it happen, only first valid match is returned.

        Returns:
            (str)
            (None)
        """

        ability_dct = ExploreApiAbilities().champion_abilities(champion_name=self.champion_name,
                                                               ability_name=self.ability_name)

        tooltip = ability_dct['sanitizedTooltip']

        pattern_1 = re.compile(r"""

            every
            \s
            (?: \{\{\s (\w\d{1,2}) \s\}\} | (third) | (\d+)\w*)
            \s
            (?: consecutive\s | basic\s)?

            (?:  hit | strike | attack )

            """, re.IGNORECASE | re.VERBOSE)

        # (findall result is a list of tuples, usually single tuple, with multiple strings)
        findall_result = re.findall(pattern_1, tooltip)

        if not findall_result == []:

            # Finds non empty string.
            for single_str in findall_result[0]:
                if single_str != '':
                    return single_str

    def refined_nth_attack(self):
        """
        Converts to int form the "nth" hit.

        Returns:
            (int)
        """

        nth_as_str = self.every_nth_attack()

        nth_as_int = None

        # Determines to which value it corresponds.
        if nth_as_str is None:
            return

        # (e.g. 'e10')
        elif re.search(r'[a-z]\d{1,2}', nth_as_str):

            nth_as_int = self.effect_values_by_abbr(abbr=nth_as_str)
            # (ensures non static "nth" type attacks don't pass unnoticed)
            if type(nth_as_int) is list:
                raise ValueError('Non stable value handling not accounted for.')

        # (e.g. '3rd')
        elif re.search(r'\d{1,2}[a-z]{2}', nth_as_str):
            # (slices last two letters off, leaving only the number)
            nth_as_int = nth_as_str[:-2]

        # (e.g. 'third')
        elif nth_as_str in self.NTH_TUPLE:
            for num, nth_str in enumerate(self.NTH_TUPLE, start=1):
                if nth_str == nth_as_str:
                    nth_as_int = num

        return nth_as_int

    def suggest_stat_buff_attributes(self):
        """
        Not finished.
        """
        start_msg = delimiter(40)
        start_msg += '\nABILITY %s' % self.ability_name
        start_msg += '\nBuff modifies stats?'

        mods_stat_question = input(start_msg + '\n')
        if mods_stat_question.lower() == 'y':
            self.suggest_unused_stats()

    def _re_findall_result_to_lst(self, findall_results):
        """
        Converts findall result (list of tuples) into list of non empty strings.
        Then changes string to int or to abbreviation's corresponding values.

        Args:
            find_results: (str) string of a number, or string of an abbreviation e.g. 'e3'
        Returns:
            (lst)
        """

        # Converts list of tuples into list of non empty strings.
        possible_values = []
        for result_tpl in findall_results:
            for result_str in result_tpl:
                if result_str != '':

                    # (recovers effect value if it was an abbreviation)
                    effect_abbr = re.findall(r'\D(\d{1,2})', result_str)
                    if effect_abbr:
                        result_str = self.ability_effect_lst[int(effect_abbr[0])]
                    else:
                        result_str = int(result_str)

                    possible_values.append(result_str)

        return possible_values

    def possible_duration_values(self):
        """
        Checks if given ability has durations,
        and returns a list of most probable values.

        Returns:
            (lst)
        """

        string = self.api_spell_dct['sanitizedTooltip']

        # 'for {{ f10 }} seconds'
        pattern_1 = re.compile(r"""
        for
        \s
        (?: \{\{\s (\w\d{1,2}) \s\}\}  | (\d+\.?\d*) )      # ' {{ e1 }}' or '2.4'
        \s
        seconds

        """, re.IGNORECASE | re.VERBOSE)

        results = pattern_1.findall(string)

        return self._re_findall_result_to_lst(findall_results=results)

    def possible_slow_values(self):
        """
        Checks if given ability reduces movement speed,
        and returns a list of most probable values.

        Most probable values can be int or list type.

        Returns:
            (lst)
        """

        string = self.api_spell_dct['sanitizedTooltip']

        # 'slowing them by {{ e12 }}% (+{{ f1 }}%)'
        pattern_1 = re.compile(r"""
        slow\w*?  \s                                                    # 'slows', 'slowing', 'slowed' etc
        [^{.]*?                                                         # any number of words that may follow
        by \s

        (?: \{\{\s (\w\d{1,2}) \s\}\}  | (\d+\.?\d*) )  %               # ' {{ e1 }}%' or '45%'

        \s?
        (?: \( \+ \{\{\s                                                # '(+{{ f1 }})', if existing
        (\w\d{1,2})
        \s\}\}%\) )*

        """, re.IGNORECASE | re.VERBOSE)

        results = pattern_1.findall(string)

        return self._re_findall_result_to_lst(findall_results=results)

    # TODO: Allow duration link to another buff (that is, buff_3_duration = buff_1_duration

    @loop_exit_handler
    def _run_buff_attr_creation_without_result_msg(self):

        self.ask_amount_of_buffs()
        self.change_buff_names()
        print(delimiter(40))

        for buff_name in sorted(self.buffs_dct):
            self.suggest_possible_stat_attributes(buff_name=buff_name)

            usual_attrs_msg = 'USUAL BUFF ATTRIBUTES\n'
            usual_attrs_msg += '\nBUFF: %s' % buff_name
            _suggest_attr_values(suggested_values_dct=self.USUAL_BUFF_ATTR_VALUES,
                                 modified_dct=self.buffs_dct[buff_name],
                                 extra_start_msg=usual_attrs_msg)

    def run_buff_attr_creation(self):

        # Reset dict content
        self.buffs_dct = {}

        start_msg = fat_delimiter(40)
        start_msg += '\nCHAMPION: %s, ABILITY: %s' % (self.champion_name, self.ability_name)

        print(start_msg)

        self._run_buff_attr_creation_without_result_msg()
        print(delimiter(40))
        pp.pprint(self.buffs_dct)


class AbilitiesAttributes(object):
    def __init__(self, champion_name):
        self.champion_name = champion_name
        self.abilities_attributes = {key: self.single_spell_attrs() for key in ABILITY_SHORTCUTS}

        self.spells_effects = {}
        self._set_spells_effects()

        self.existing_attr_names = {'dmgs': [], 'buffs': []}

    def _set_spells_effects(self):

        for spell_name in SPELL_SHORTCUTS:
            self.spells_effects.update({spell_name: palette.ChampionsStats.spell_effects()})

    @staticmethod
    def single_spell_attrs():
        return dict(general={}, dmgs={}, buffs={})

    def add_name_to_existing_attr_names(self, attr_type, attr_names_lst):
        """
        Adds all dmg or buff names from selected names list.

        Returns:
            (None)
        """
        for attr_name in attr_names_lst:
            if attr_name not in self.existing_attr_names[attr_type]:
                self.existing_attr_names[attr_type].append(attr_name)

    def _create_single_spell_attrs(self, spell_name):
        """
        Creates all attributes of an ability.

        Returns:
            (dct)
        """

        print(fat_delimiter(100))

        dct = self.single_spell_attrs()

        gen_instance = GeneralAbilityAttributes(ability_name=spell_name, champion_name=self.champion_name)
        gen_instance.run_gen_attr_creation()

        dct['general'] = gen_instance.general_attr_dct

        dmgs_instance = DmgAbilityAttributes(ability_name=spell_name, champion_name=self.champion_name)
        dmgs_instance.run_dmg_attr_creation()

        dct['dmgs'] = dmgs_instance.dmgs_dct
        self.add_name_to_existing_attr_names(attr_type='dmgs', attr_names_lst=dct['dmgs'])

        buffs_inst = BuffAbilityAttributes(ability_name=spell_name, champion_name=self.champion_name)
        buffs_inst.run_buff_attr_creation()

        dct['buffs'] = buffs_inst.buffs_dct
        self.add_name_to_existing_attr_names(attr_type='buffs', attr_names_lst=dct['buffs'])

        print(fat_delimiter(40))
        pp.pprint(dct)

        return dct

    def _create_single_spell_effects_dct(self, spell_name):
        """
        Creates effects dict of a single spell, for given champion.

        Dev is asked about possible dmg and buff names,
        and cd modifiers.

        Returns:
            (None)
        """

        print(fat_delimiter(100))
        print('\nEFFECTS DICT')

        univ_msg = '\nCHAMPION: %s, ABILITY: %s' % (self.champion_name, spell_name)

        dmgs_names = self.existing_attr_names['dmgs']
        buffs_names = self.existing_attr_names['buffs']

        effects_dct = self.spells_effects[spell_name]

        for tar_type in ('enemy', 'player'):
            for application_type in ('passives', 'actives'):
                # DMGS

                dmg_msg = '%s\n' % univ_msg
                dmg_msg += '%s -- %s -- DMG APPLIED\n' % (tar_type, application_type)
                dmg_msg = dmg_msg.upper()

                _suggest_lst_of_attr_values(suggested_values_lst=dmgs_names,
                                            modified_lst=effects_dct[tar_type][application_type]['dmg'],
                                            extra_start_msg=dmg_msg)

                # BUFFS APPLICATION
                buffs_applied_msg = '%s\n' % univ_msg
                buffs_applied_msg += '%s -- %s -- BUFFS APPLIED' % (tar_type, application_type)
                buffs_applied_msg = buffs_applied_msg.upper()

                _suggest_lst_of_attr_values(suggested_values_lst=buffs_names,
                                            modified_lst=effects_dct[tar_type][application_type]['buffs'],
                                            extra_start_msg=buffs_applied_msg)

                # BUFF REMOVAL
                buff_removal_msg = '%s\n' % univ_msg
                buff_removal_msg += '%s -- %s -- BUFFS REMOVED' % (tar_type, application_type)
                buff_removal_msg = buff_removal_msg.upper()

                _suggest_lst_of_attr_values(suggested_values_lst=buffs_names,
                                            modified_lst=effects_dct[tar_type][application_type]['remove_buff'],
                                            extra_start_msg=buff_removal_msg)

        # CD MODIFICATION
        lst_of_modified = []
        cd_mod_msg = '\nCDs MODIFIED ON CAST'
        _suggest_lst_of_attr_values(suggested_values_lst=SPELL_SHORTCUTS,
                                    modified_lst=lst_of_modified,
                                    extra_start_msg=cd_mod_msg)

        for cd_modified in lst_of_modified:

            mod_value = None
            while True:
                mod_value = input('\nHow much is it modified for?\n')

                try:
                    if float(mod_value) > 0:
                        break
                    else:
                        print('\nValue has to be higher than 0. Try again.')
                except ValueError:
                    print('\nValue has to be num. Try again.')

            effects_dct['player']['actives']['cds_modified'].update({cd_modified: mod_value})

        pp.pprint(self.spells_effects)

    def create_spells_attrs_and_effects(self):
        """
        Creates all attributes for all spells of given champion,
        including spell effects.

        Returns
            (dct)
        """

        for spell_name in SPELL_SHORTCUTS:
            self.abilities_attributes[spell_name] = self._create_single_spell_attrs(spell_name=spell_name)

        # (has to follow all buff and dmg creation so that all names are available)
        for spell_name in SPELL_SHORTCUTS:
            self._create_single_spell_effects_dct(spell_name=spell_name)

    def create_passive_attrs(self):
        # TODO
        ''


# ===============================================================
#       MODULE CREATION
# ===============================================================
class ModuleCreator(object):
    def __init__(self, champion_name):
        self.champion_name = champion_name
        self.external_vars_dct = {}

    def external_vars(self):
        """
        Asks dev for externally set extra variables (set optionally by user, e.g. jax's dodged hits during E).

        Returns:
            (None)
        """

        print(fat_delimiter(40))

        question_msg = '\nExternally set var name? (press enter to skip)'

        while True:

            external_val_name = input(question_msg)

            if external_val_name == '':
                print('\nNo external variable selected.')
                break
            else:
                external_val_initial_value = input('\nInitial value for %s' % external_val_name)

                self.external_vars_dct.update({external_val_name: external_val_initial_value})

    def insert_attrs(self):
        """
        Inserts abilities' attributes and effects,
        after pretty formatting them.

        Returns:
            (None)
        """

        instance = AbilitiesAttributes(champion_name=self.champion_name)
        instance.create_spells_attrs_and_effects()
        abilities_attrs = instance.abilities_attributes
        effects = instance.spells_effects

        for dct in (abilities_attrs, effects):
            dct_as_str = '{\n' + pp.pformat(dct, indent=0)[1:-1] + '\n}'

            data_storage(targeted_module='champions/jax.py',
                         obj_name='ABILITIES_EFFECTS',
                         str_to_insert=dct_as_str)


# ===============================================================
# ===============================================================
if __name__ == '__main__':

    testGen = False
    if testGen is True:
        for ability_shortcut in SPELL_SHORTCUTS:
            GeneralAbilityAttributes(ability_name=ability_shortcut, champion_name='drmundo').run_gen_attr_creation()
            break

    testDmg = False
    if testDmg is True:
        for ability_shortcut in ('q',):
            dmgAttrInstance = DmgAbilityAttributes(ability_name=ability_shortcut, champion_name='teemo')
            dmgAttrInstance.run_dmg_attr_creation()

    testBuffs = False
    if testBuffs is True:
        for champName in ExploreApiAbilities().all_champions_data_dct:
            for abilityName in SPELL_SHORTCUTS:
                res = BuffAbilityAttributes(abilityName, champName).refined_nth_attack()
                if res:
                    print((champName, res))

    testApiStorage = False
    if testApiStorage is True:
        RequestAllAbilitiesFromAPI().store_all_champions_data()

    testExploration = False
    if testExploration is True:
        ExploreApiAbilities().sanitized_tooltips(champ='jax', raw_str=r'every\s\d+hit', print_mode=True)

    testCombination = False
    if testCombination is True:
        inst = AbilitiesAttributes(champion_name='jax')
        inst._create_single_spell_attrs('q')

    testChampIDs = False
    if testChampIDs is True:
        print(ExploreApiAbilities().champion_id('dariu'))

    testModuleInsertion = True
    if testModuleInsertion is True:
        ModuleCreator(champion_name='jax').insert_attrs()