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
import stats
import importlib
import ast
import collections
import api_items_database

# Info regarding API structure at https://developer.riotgames.com/docs/data-dragon


# ===============================================================
# ===============================================================
# Objects in champion module (exact strings are re.matched inside module)
CHAMPION_MODULES_FOLDER_NAME = 'champions'
ITEM_MODULES_FOLDER_NAME = 'items'
ABILITIES_ATTRS_DCT_NAME = 'ABILITIES_ATTRIBUTES'
ABILITIES_EFFECT_DCT_NAME = 'ABILITIES_EFFECTS'
ABILITIES_CONDITIONS_DCT_NAME = 'ABILITIES_CONDITIONS'
CHAMPION_EXTERNAL_VAR_DCT_NAME = 'CHAMPION_EXTERNAL_VARIABLES'
CHAMP_CLASS_NAME = 'class ChampionAttributes'
DEFAULT_ACTIONS_PRIORITY_NAME = 'DEFAULT_ACTIONS_PRIORITY'
CHAMPION_MODULE_OBJECT_NAMES = (ABILITIES_ATTRS_DCT_NAME, ABILITIES_EFFECT_DCT_NAME,
                                ABILITIES_CONDITIONS_DCT_NAME, CHAMPION_EXTERNAL_VAR_DCT_NAME, CHAMP_CLASS_NAME,
                                DEFAULT_ACTIONS_PRIORITY_NAME)

child_class_as_str = """class ChampionAttributes(object):
    DEFAULT_ACTIONS_PRIORITY = DEFAULT_ACTIONS_PRIORITY
    ABILITIES_ATTRIBUTES = ABILITIES_ATTRIBUTES
    ABILITIES_EFFECTS = ABILITIES_EFFECTS
    ABILITIES_CONDITIONS = ABILITIES_CONDITIONS
    def __init__(self, external_vars_dct=CHAMPION_EXTERNAL_VARIABLES):
        for i in external_vars_dct:
            setattr(ChampionAttributes, i, external_vars_dct[i])"""


# ===============================================================
def imported_champ_module(champ_name):
    """
    Returns champion's module.
    """
    return importlib.import_module(CHAMPION_MODULES_FOLDER_NAME + '.' + champ_name)


def champ_abilities_attrs_dct(champ_name):
    """
    Returns champion's abilities effects dict.

    Returns:
        (dct)
    """

    champ_mod = imported_champ_module(champ_name)

    return getattr(champ_mod, ABILITIES_ATTRS_DCT_NAME)


def _dmgs_names(champ_name):
    return sorted(champ_abilities_attrs_dct(champ_name)['dmgs'])


def _buffs_names(champ_name):
    return sorted(champ_abilities_attrs_dct(champ_name)['buffs'])


# ---------------------------------------------------------------
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
def chosen_val_to_literal(given_val):
    """
    Tries to convert a string to int or float,
    based on what is more suitable.

    Args:
        given_val: (str)
    Returns:
        (str)
        (int)
        (float)
    """

    try:
        return ast.literal_eval(given_val)
    except ValueError:
        # (if conversion was not successful..)
        return given_val


# ---------------------------------------------------------------
def print_invalid_answer(extra_msg=''):
    """
    Prints to notify user of invalid answer given.

    Returns:
        (None)
    """

    print('\nInvalid answer. ' + extra_msg)


def _dct_body_to_pretty_formatted_str(given_dct):
    """
    Converts given dct (body) to a pretty formatted string.
    Used for file writing.

    Returns:
        (str)
    """

    return '{\n' + pp.pformat(given_dct, indent=0)[1:-1] + '}'


def dct_to_pretty_formatted_str(obj_name, obj_body_as_dct):
    """
    Creates pretty formatted full string of a dct to be inserted in a file.
    """

    body = _dct_body_to_pretty_formatted_str(given_dct=obj_body_as_dct)
    name_and_equal_sign = obj_name + ' = '

    return name_and_equal_sign + body + '\n'


def _file_after_replacing_module_var(file_as_lines_lst, object_name, obj_as_dct_or_str):
    """
    Slices off old object from string, then creates the new string.
    Used for replacing module dicts.

    Returns:
        (str)
    """

    if type(obj_as_dct_or_str) is str:
        # (newline is required here; already exists when obj as dict)
        inserted_str = obj_as_dct_or_str + '\n'
    elif type(obj_as_dct_or_str) is dict:
        inserted_str = dct_to_pretty_formatted_str(obj_name=object_name, obj_body_as_dct=obj_as_dct_or_str)
    else:
        raise TypeError('Unexpected argument type.')

    for num_1, line_1 in enumerate(file_as_lines_lst):
        # Finds object start.
        if re.match(object_name, line_1):
            old_start = num_1

            # Finds object end.
            # (if no empty line is found, last line is marked as end.
            old_end = len(file_as_lines_lst)
            for num_2, line_2 in enumerate(file_as_lines_lst[old_start:], old_start):
                if line_2 == '\n':

                    old_end = num_2 - 1
                    break

            # Creates new file as string.
            new_str = ''
            for i in file_as_lines_lst[:old_start]:
                new_str += i
            new_str += inserted_str
            for i in file_as_lines_lst[old_end+1:]:
                new_str += i

            return new_str


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
class OuterLoopExit(Exception):
    pass


class InnerLoopExit(Exception):
    pass


class RepeatChoiceError(Exception):
    pass


# Loop exit keys.
INNER_LOOP_KEY = '!'
OUTER_LOOP_KEY = '!!'
REPEAT_CHOICE_KEY = '^'


def _check_loop_exit(key):
    if key == OUTER_LOOP_KEY:
        print('#### OUTER LOOP EXITED ####')
        raise OuterLoopExit
    elif key == INNER_LOOP_KEY:
        print('#### INNER LOOP EXITED ####')
        raise InnerLoopExit


def _check_for_repeat_choice_error(key):
    if key == REPEAT_CHOICE_KEY:
        print('# Repeating previous choice #')
        raise RepeatChoiceError


def _check_factory_custom_exception(given_str, exclude_repeat_key=False):
    """
    Raises exception if given string is an exception triggering key.

    Returns:
        (None)
    """

    _check_loop_exit(given_str)

    if exclude_repeat_key is False:
        _check_for_repeat_choice_error(given_str)


def _input_in_len_range(given_str, choices_length):
    """
    Checks if given_str is a number from 0 to max allowed.

    Returns:
        (bool)
    """

    try:
        if 0 < int(given_str) <= choices_length:
            return True
    except ValueError:
        pass

    return False


def _exception_keys():
    return dict(stop_key=INNER_LOOP_KEY, error_key=OUTER_LOOP_KEY, repeat_key=REPEAT_CHOICE_KEY)


def _loop_exit_handler(func, _exception_class=None):
    """
    Decorator used for handling Abortion exceptions raised during Requests.
    """

    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except _exception_class:
            pass

    return wrapped


def inner_loop_exit_handler(func, _exception_class=InnerLoopExit):

    return _loop_exit_handler(func=func, _exception_class=_exception_class)


def outer_loop_exit_handler(func, _exception_class=OuterLoopExit):

    return _loop_exit_handler(func=func, _exception_class=_exception_class)


# ---------------------------------------------------------------
def _y_n_question(question_str):
    """
    Checks user input on given question_str.
    Raises factory custom exceptions if needed.

    Returns:
        (True)
        (False)
    """

    while True:
        answer = input('\n{} (y, n)\n'.format(question_str))

        # Check exceptions.
        _check_factory_custom_exception(given_str=answer, exclude_repeat_key=True)

        if answer == 'y':
            return True
        elif answer == 'n':
            return False
        else:
            print_invalid_answer()


def _ask_tpl_question(question_str, choices_seq, restrict_choices=False):
    """
    Presents enumerated choices to dev.

    Returns:
        (anything) Selected choice
    """

    try:
        choices = sorted(choices_seq)
    except TypeError:
        choices = choices_seq

    enum_choices = enumerate(choices, 1)

    print(delimiter(10))
    msg = '\n' + question_str
    for num, val in enum_choices:
        msg += '\n{}: {}'.format(num, val)

    answer = None
    while True:
        answer = input(msg+'\n')

        _check_factory_custom_exception(given_str=answer, exclude_repeat_key=True)

        # Repeats loop if choices are restricted, until valid int is given.
        if restrict_choices is True:
            try:
                if int(answer) <= len(choices):
                    break
            except ValueError:
                continue

        else:
            break

    # Checks if enumerated answer was chosen.
    try:
        if 0 < int(answer) <= len(choices):
            return choices[int(answer)-1]

    except ValueError:
        pass

    # If not, returns answer as is.
    return chosen_val_to_literal(answer)


# ---------------------------------------------------------------
def _suggest_single_attr_value(attr_name, suggested_values_dct, modified_dct, restrict_choices):
    """
    Suggests a value and stores the choice.

    Value can be either picked from suggested values,
    or created by dev.

    Args:
        suggested_values_dct: (dct) e.g. {ability_attr: (val_1, val_2,), }
    Returns:
        (None)
    """

    suggested_val_tpl = tuple(suggested_values_dct[attr_name])

    # Ensures lists to be zipped have same length.
    shortcut_len = len(suggested_val_tpl)

    # INITIAL CHOICE MESSAGE
    msg = delimiter(num_of_lines=20)
    msg += '\nATTRIBUTE: %s:\n' % attr_name
    for display_val, suggested_val in enumerate(suggested_val_tpl, 1):
        msg += '\n%s: %s' % (display_val, suggested_val)

    # CHOICE PROCESSING

    # Repeats until accepted answer is given.
    input_given = None
    while True:
        input_given = input(msg + '\n')
        # (enter is not accepted)
        if input_given != '':
            # (if input given is not corresponding to a shortcut num)
            if restrict_choices is True:
                if (_input_in_len_range(given_str=input_given,
                                        choices_length=shortcut_len) is False) and (input_given not in _exception_keys().values()):

                    print_invalid_answer('Choose from the menu.')
                    continue

            break
        else:
            print_invalid_answer('Enter not accepted.')

    # (breaks loop prematurely if asked)
    _check_loop_exit(key=input_given)
    _check_for_repeat_choice_error(key=input_given)

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
    chosen_value = chosen_val_to_literal(given_val=chosen_value)
    modified_dct[attr_name] = chosen_value

    print(choice_msg)


def _suggest_attr_values(suggested_values_dct, modified_dct, restrict_choices=False, mute_exit_key_msgs=False,
                         extra_start_msg='',):
    """
    CHECK: single suggestion method for more details.

    Stores each chosen attribute value or repeats a choice.

        stop_key: (str) When given as answer, exits this loop.
        error_key: (str) When given as answer, raises error to exit outer loop.
    Returns:
        (None)
    """

    start_msg = '\n' + delimiter(40)
    if mute_exit_key_msgs is False:
        start_msg += '\n(type "%s" to exit inner loops)' % _exception_keys()['stop_key']
        start_msg += '\n(type "%s" to exit outer loops)' % _exception_keys()['error_key']
        start_msg += '\n(type "%s" to repeat previous choices)\n' % _exception_keys()['repeat_key']
    start_msg += extra_start_msg
    print(start_msg)

    num_name_couples = {num: name for num, name in enumerate(sorted(suggested_values_dct))}
    for attr_num in sorted(num_name_couples):

        while True:
            curr_attr_name = num_name_couples[attr_num]

            try:
                # (current)
                _suggest_single_attr_value(attr_name=curr_attr_name,
                                           suggested_values_dct=suggested_values_dct,
                                           modified_dct=modified_dct,
                                           restrict_choices=restrict_choices)
                break

            except RepeatChoiceError:
                # (reduces attr_num, and ensures it doesn't reach negative values)
                attr_num -= 1
                attr_num = max(attr_num, 0)


def _new_automatic_attr_dct_name(existing_names, first_synthetic, second_synthetic=''):
    """
    Creates a new name for an attr dct, ensuring no existing names are overwritten.

    Returns:
        (str) e.g.: 'q_dmg', 'q_dmg_1', ..
    """

    if second_synthetic != '':
        new_attr_name = '{}_{}_0'.format(first_synthetic, second_synthetic)
    else:
        new_attr_name = '{}_0'.format(first_synthetic)

    if existing_names:

        for num in range(1, 100, 1):

            if new_attr_name not in existing_names:
                # If a suitable name has been found, exits method.
                return new_attr_name

            else:
                if second_synthetic != '':
                    new_attr_name = '{}_{}_{}'.format(first_synthetic, second_synthetic, num)
                else:
                    new_attr_name = '{}_{}'.format(first_synthetic, num)

    # If there was no existing attr dict, returns preset name value.
    else:
        return new_attr_name


def _ask_new_group_name(group_type_name, existing_names=None, disable_enter=False):
    """
    Asks dev for new non existing name.
    'Enter' skips creation (unless disabled).

    Args:
        group_type_name: (str) Describes group (e.g. buff, dmg, condition effect)
        existing_names: (None) or (sequence)
    Returns:
        (None)
        (str)
    """

    new_name = None
    while True:
        question_msg = '\nNew {} name: '.format(group_type_name.upper())
        if disable_enter is False:
            question_msg += '(enter to skip)'
        new_name = input(question_msg + '\n')
        _check_factory_custom_exception(given_str=new_name, exclude_repeat_key=True)

        if new_name in existing_names:
            print_invalid_answer('Name exists.')
            continue

        elif (disable_enter is True) and (new_name == ''):
            print_invalid_answer('(Enter not acceptable.)')
            continue

        elif new_name == '':
            break

        else:
            break

    return new_name


def _auto_new_name_or_ask_name(existing_names, first_synthetic, second_synthetic='', disable_enter=False):
    """
    Creates automatically a new name, that doesn't overwriting existing names.
    Then asks dev for name change.

    Returns:
        (str)
    """

    # Auto name
    new_automatic_name = _new_automatic_attr_dct_name(existing_names=existing_names, first_synthetic=first_synthetic,
                                                      second_synthetic=second_synthetic)

    group_type_name = first_synthetic
    if second_synthetic != '':
        group_type_name += '_' + second_synthetic

    # Manual change if requested.
    new_manual_name = _ask_new_group_name(group_type_name=group_type_name,
                                          existing_names=list(existing_names),
                                          disable_enter=disable_enter)

    if new_manual_name:
        return new_manual_name
    else:
        return new_automatic_name


# ---------------------------------------------------------------
def _suggest_lst_of_attr_values(suggested_values_lst, modified_lst, extra_start_msg='', stop_key=INNER_LOOP_KEY,
                                error_key=OUTER_LOOP_KEY, sort_suggested_lst=True):
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

    if sort_suggested_lst is True:
        suggested_lst = sorted(suggested_values_lst)
    else:
        suggested_lst = suggested_values_lst

    for num, val in enumerate(suggested_lst, 1):
        print('%s: %s' % (num, val))

    # Asks dev.
    while True:
        dev_choice = input('\nSelect all valid names. (press only enter for empty)\n')

        # Exits loop if requested.
        _check_loop_exit(dev_choice)

        # (only comma, whitespace and digits are valid characters, or empty string)
        if re.search(r'[^\d,\s]', dev_choice) is not None:
            print_invalid_answer(extra_msg='Answer may contain only digits, whitespaces and comma. (or enter)')

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
                print_invalid_answer(extra_msg='Indexes out of range.')


# ---------------------------------------------------------------
def repeat_cluster(cluster_name):
    """
    Decorator used for repeating cluster of suggestions.
    When appropriate exception is raised, re-calls the decorated function.

    Args:
        cluster_name: (str)
    """
    def dec(func):

        def wrapped(*args, **kwargs):

            # Suggestion repetition
            while True:
                func(*args, **kwargs)

                # Question repetition
                answer = None
                while True:
                    answer = input('\nRepeat previous cluster? (press enter to skip)\n')
                    if answer == 'y':
                        print('\n############ Repeating %s. ############' % cluster_name)
                        break
                    elif answer == '':
                        break
                    else:
                        print_invalid_answer()

                if answer != 'y':
                    break

        return wrapped
    return dec

# ---------------------------------------------------------------
SPELL_SHORTCUTS = ('q', 'w', 'e', 'r')
ABILITY_SHORTCUTS = ('inn', ) + SPELL_SHORTCUTS
EXTRA_SPELL_SHORTCUTS = ('q2', 'w2', 'e2', 'r2')
ALL_POSSIBLE_SPELL_SHORTCUTS = SPELL_SHORTCUTS + EXTRA_SPELL_SHORTCUTS
ALL_POSSIBLE_ABILITIES_SHORTCUTS = ABILITY_SHORTCUTS + EXTRA_SPELL_SHORTCUTS

ALLOWED_ABILITY_LVLS = ('1', '2', '3', '4', '5')


def spell_num(spell_name):
    return SPELL_SHORTCUTS.index(spell_name)


def ability_num(ability_name):
    if ability_name == 'inn':
        return 0
    else:
        return spell_num(spell_name=ability_name) + 1


# ---------------------------------------------------------------
def data_storage(targeted_module, obj_name, str_to_insert, write_mode='w', force_write=False):
    """
    Reads and writes a file, after informing dev of file status (empty/full).

    Returns:
        (None)
    """

    # Messages
    abort_msg = '\nData insertion ABORTED.\n'
    completion_msg = '\nData insertion COMPLETE.\n'
    if write_mode == 'w':
        insertion_question = 'Replace data?'
    elif write_mode == 'a':
        insertion_question = 'Append data?'
    else:
        raise TypeError('Unexpected file open mode.')

    # Checks if module is non empty.
    with open(targeted_module, 'r') as checked_module:

        # FORCE WRITE
        if force_write is True:
            print('\nForce writing.')

        # NON EMPTY FILE
        elif checked_module.read() != '':
            replace_msg = 'Non empty module detected (%s). \n%s\n' % (targeted_module, insertion_question)
            # Repeats question.
            while True:
                dev_answer = input(replace_msg)
                if dev_answer == 'y':
                    print('Replacing existing file content..')
                    break

                # EXIT METHOD
                elif dev_answer == 'n':
                    print(abort_msg)
                    return
                else:
                    print_invalid_answer()
        # EMPTY FILE
        else:
            print('Inserting data..')

    # Creates file content.
    file_as_str = '\n' + obj_name + ' = ' + str_to_insert

    # Replaces module content.
    with open(targeted_module, write_mode) as edited_module:
        edited_module.write(file_as_str)

    print(completion_msg)


# ===============================================================
#       API REQUESTS
# ===============================================================
class RequestAborted(Exception):
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
        if dev_start_question == 'y':
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
    ITEMS_PAGE_URL = ("https://eune.api.pvp.net/api/lol/static-data/eune/v1.2/item?itemListData=all&api_key=" +
                      api_key.KEY)

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

        WARNING: VERBOSE and IGNORECASE flags chosen.

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
        self.item_related_api_data = api_items_database.ALL_ITEMS
        self._all_items_by_id = self.item_related_api_data['data']
        self.used_items_by_name = self._used_items()

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

        for item_id in self._all_items_by_id:

            # MAP
            allowed_on_map = True
            # (if there is no map exclusion, then it is usable on required map)
            try:
                if self._all_items_by_id[item_id]['maps']['1'] is False:
                    allowed_on_map = False
            except KeyError:
                pass

            # PURCHASABLE
            purchasable = True
            if 'inStore' in self._all_items_by_id[item_id]:
                if self._all_items_by_id[item_id]['inStore'] is False:
                    purchasable = False

            # NON DISALLOWED TAG
            allowed_tags = True
            if 'tags' in self._all_items_by_id[item_id]:
                for tag in self._all_items_by_id[item_id]['tags']:
                    if tag.lower() in self.DISALLOWED_ITEM_TAGS:
                        allowed_tags = False

            # Checks if all conditions are met.
            if allowed_on_map and allowed_tags and purchasable:
                item_name = self._all_items_by_id[item_id]['name'].lower()

                # (order below matters for correct naming)
                item_name = item_name.replace('(ranged only)', '')
                item_name = item_name.replace('(melee only)', '')
                item_name = item_name.rstrip()
                item_name = item_name.replace(' ', '_')

                item_name = item_name.replace("'", '')
                item_name = item_name.replace('-', '_')
                item_name = item_name.replace(':', '_')

                dct.update({item_name: self._all_items_by_id[item_id]})

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

        matched_name = self._full_or_partial_match(searched_name=given_name, iterable=self.used_items_by_name)

        return _return_or_pprint_complex_obj(print_mode=print_mode, dct=self.used_items_by_name[matched_name])

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
            item_lst = self.used_items_by_name
        else:
            # (need a list so it inserts selection into a list)
            matched_name = self._full_or_partial_match(searched_name=item, iterable=self.used_items_by_name)
            item_lst = [matched_name, ]

        descriptions_lst = []

        for item_name in item_lst:

            try:
                self._append_all_or_matching_str(examined_str=self.used_items_by_name[item_name][element_name],
                                                 modified_lst=descriptions_lst,
                                                 raw_str=raw_str)
            except KeyError:
                print("\n'%s' has no element '%s'" % (item_name, element_name))

        # Checks if print mode is selected.
        return _return_or_pprint_lst(print_mode=print_mode, lst=descriptions_lst)

    def descriptions(self, item=None, raw_str=None, print_mode=False):
        """
        Returns "descriptions" for given item (or for all items),
        or prints it.

        Note: Check parent method for more details.
        """

        return self._item_elements(element_name='description', item=item,
                                   raw_str=raw_str, print_mode=print_mode)

    def stat_names_counter(self, print_mode=False):
        """
        Searches all item "descriptions" and recovers all item names.

        Returns:
            (counter)
        """

        counter = collections.Counter()

        for i in self.descriptions():
            match = re.findall(r'\+?\d+\s([a-z\s]+)', i.lower())

            if match:
                counter += collections.Counter(match)

        return _return_or_pprint_complex_obj(print_mode=print_mode, dct=counter)

    def item_tags(self, only_freq=False, print_mode=False):
        """
        Returns or pretty prints all item tags.
        """
        item_occurrence_dct = {}

        for item_name in self.used_items_by_name:

            try:
                tags_lst = self.used_items_by_name[item_name]['tags']

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

    def _obsolete_return_tpl_or_element(self, lst):
        """
        OBSOLETE: Efficiency should be minimal if using this method to create data,
        since each user would call the same dict in reality.

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

        return mod_val

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
        toggled=(False, True),
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

    def _suggest_cost_category(self):
        """
        Suggests cost categories to dev.

        Returns:
            (None)
        """

        modified_dct = self.general_attr_dct['cost']['standard_cost']

        _suggest_attr_values(suggested_values_dct={'COST CATEGORY': self.COST_CATEGORIES},
                             modified_dct=modified_dct, restrict_choices=True)

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
            self.general_attr_dct['base_cd'] = tuple(self.api_spell_dct['cooldown'])

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
            self.general_attr_dct['cost'] = {'standard_cost': None, 'stack_cost': None}

            # Standard cost.
            standard_cost_question = _y_n_question(question_str='Contains STANDARD COST?')
            if standard_cost_question is True:

                self.general_attr_dct['cost']['standard_cost'] = {}
                self._suggest_cost_category()
                self.general_attr_dct['cost']['standard_cost'].update({'resource_type': self.resource_cost_type()})
                self.general_attr_dct['cost']['standard_cost'].update({'values': self.resource_cost_values()})

            # Stacks cost.
            stack_cost_question = _y_n_question(question_str='Contains STACK COST?')
            if stack_cost_question is True:

                self.general_attr_dct['cost']['stack_cost'] = {}
                self.general_attr_dct['cost']['stack_cost'].update({'buff_name': 'placeholder'})
                self.general_attr_dct['cost']['stack_cost'].update({'values': 'placeholder'})

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
            self.general_attr_dct['range'] = tuple(range_val)

    def auto_fill_attributes(self):
        """
        Groups all auto inserted attributes.

        Returns:
            (None)
        """
        self.fill_range()
        self.fill_cost_attrs()
        self.fill_base_cd_values()

    @inner_loop_exit_handler
    def suggest_gen_attr_values(self):

        extra_msg = '\nGENERAL ATTRIBUTE CREATION\n'
        extra_msg += self._champion_and_ability_msg()

        _suggest_attr_values(suggested_values_dct=self.USUAL_VALUES_GEN_ATTR,
                             modified_dct=self.general_attr_dct,
                             extra_start_msg=extra_msg)

    @repeat_cluster(cluster_name='GENERAL ATTRIBUTES')
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

        _suggest_attr_values(suggested_values_dct=dict(castable=(True, False)),
                             modified_dct=self.general_attr_dct, restrict_choices=True)

        if self.general_attr_dct['castable'] is True:
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

    # Category names and required extra variables.
    AVAILABLE_DMG_CATEGORIES = dict(
        standard_dmg=None,
        chain_decay=dict(
            decay_coef='placeholder',
            min_percent_dmg='placeholder',
        ),
        aa_dmg=None)

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
            delay='placeholder',
            )

    def usual_values_dmg_attr(self):

        return dict(
            target_type=('enemy', 'player'),
            # TODO insert more categories in class and then here.
            dmg_category=sorted(self.AVAILABLE_DMG_CATEGORIES),
            dmg_source=ALL_POSSIBLE_ABILITIES_SHORTCUTS,
            life_conversion_type=('spellvamp', None, 'lifesteal'),
            radius=(None, ),
            dot=(False, True),
            max_targets=(1, 2, 3, 4, 5, 'infinite'),
            usual_max_targets=(1, 2, 3, 4, 5),
            delay=(None,)
            )

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
        Finds mod value and the stat linked to the mod.

        Returns:
            (dct)
        """

        for mod_dct in self.api_spell_dct['vars']:
            if mod_dct['key'] == mod_shortcut:
                link_name = mod_dct['link']
                stat_name = self.mod_stat_name_map()[link_name]
                mod_coeff = mod_dct['coeff']

                return {stat_name: mod_coeff[0]}

    def _obsolete_check_if_dot(self):
        """
        OBSOLETE.

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

    def _obsolete_dot_duration(self):
        """
        OBSOLETE

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

    def _suggest_dmg_mod_attrs(self, tooltip_fragment, curr_dmg_dct):
        """
        Asks mod type and mod owner, for each mod,
        and stores it in given dmg dct.

        Returns:
            (None)
        """

        curr_dmg_dct.update(
            dict(
                mods=dict(
                    player={},
                    enemy={}
                )))

        # Dmg mods in api 'effects'
        mod_val_abbrev_lst = re.findall(r'\+\{\{\s(\w\d{1,2})\s\}\}', tooltip_fragment)
        for mod_abbrev in mod_val_abbrev_lst:
            # Mod values and stats
            mod_stat_and_val_dct = self.mod_value_and_stat(mod_shortcut=mod_abbrev)

            # ASKS DEV
            mod_and_val_as_str = '\nDmg mod: %s, value: %s' % tuple(mod_stat_and_val_dct.items())[0]
            # (creates appropriate arg form for method below)
            mod_attr_template = {'mod_stat_owner': ('player', 'enemy')}
            temp_mod_dct = {}
            _suggest_attr_values(suggested_values_dct=mod_attr_template, modified_dct=temp_mod_dct,
                                 mute_exit_key_msgs=True, extra_start_msg=mod_and_val_as_str)

            # Stores mod in dmg dct.
            owner_type = temp_mod_dct['mod_stat_owner']
            curr_dmg_dct['mods'][owner_type].update(mod_stat_and_val_dct)

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
            new_dmg_name = _new_automatic_attr_dct_name(existing_names=self.dmgs_dct, second_synthetic='dmg',
                                                        first_synthetic=self.ability_name)
            self.dmgs_dct.update({new_dmg_name: self.dmg_attributes()})

            curr_dmg_dct = self.dmgs_dct[new_dmg_name]

            # INSERTS DMG VALUES
            dmg_val_abbrev = re.findall(r'\s\{\{\s(\w\d{1,2})\s\}\}', tooltip_fragment)[0]
            curr_dmg_dct['dmg_values'] = self.effect_values_by_abbr(abbr=dmg_val_abbrev)

            # INSERTS DMG TYPE
            dmg_type = re.search(r'true|magic|physical', tooltip_fragment, re.IGNORECASE).group()
            curr_dmg_dct['dmg_type'] = dmg_type.lower()

            # INSERTS MODS IN DMG
            self._suggest_dmg_mod_attrs(tooltip_fragment=tooltip_fragment, curr_dmg_dct=curr_dmg_dct)

            # INSERTS DMGS
            self.dmgs_dct.update({new_dmg_name: curr_dmg_dct})

    @staticmethod
    def _stabilized_tar_num(dmg_dct):
        """
        Calculates number of targets hit until a chain decaying dmg stabilizes.

        Then deletes not needed value from dmg dct.

        Returns:
            (float)
        """
        min_dmg_percentage = dmg_dct['min_percent_dmg']
        decay_constant = dmg_dct['decay_coef']

        del dmg_dct['min_percent_dmg']

        # Formula is: min = 1 - c(n-1)
        return (1-min_dmg_percentage)/decay_constant + 1

    def suggest_dmg_attr_values(self):

        for dmg_temp_name in sorted(self.dmgs_dct):
            msg = '\ndmg_values: %s' % self.dmgs_dct[dmg_temp_name]['dmg_values']
            msg += '\nmods: %s' % self.dmgs_dct[dmg_temp_name]['mods']

            print(msg)

            _suggest_attr_values(suggested_values_dct=self.usual_values_dmg_attr(),
                                 modified_dct=self.dmgs_dct[dmg_temp_name])

            # Decay stabilization tar num.
            if self.dmgs_dct[dmg_temp_name]['dmg_category'] == 'chain_decay':
                stabilized_num = self._stabilized_tar_num(dmg_dct=self.dmgs_dct[dmg_temp_name])

                self.dmgs_dct[dmg_temp_name].update(dict(
                    stabilized_tar_num=stabilized_num))

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
                new_dmg_name = input('\nNew name for %s: (press enter to skip)\n' % dmg)
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

            if extra_dmg == 'y':
                new_dmg_name = _new_automatic_attr_dct_name(existing_names=self.dmgs_dct, second_synthetic='dmg',
                                                            first_synthetic=self.ability_name)
                self.dmgs_dct.update({new_dmg_name: self.dmg_attributes()})
                self._suggest_dmg_values(dmg_name=new_dmg_name)
                _suggest_attr_values(suggested_values_dct=self.usual_values_dmg_attr(),
                                     modified_dct=self.dmgs_dct[new_dmg_name],
                                     extra_start_msg='\nManually inserted dmg.')
                self.modify_dmg_names()

            elif extra_dmg == 'n':
                break

            else:
                print_invalid_answer()

    def insert_dmg_category_related_attrs(self):

        if not self.dmgs_dct:
            return

        for dmg_name, dmg_dct in self.dmgs_dct.items():

            # Filters out categories that don't require extra arguments,
            # and checks if given dmg is in those categories.
            dmg_cat = dmg_dct['dmg_category']
            if dmg_cat in [key for key, val in self.AVAILABLE_DMG_CATEGORIES.items() if val is not None]:

                for extra_attr_name in self.AVAILABLE_DMG_CATEGORIES[dmg_cat]:
                    extra_msg = 'Dmg name: %s, Attribute: %s' % (dmg_name, extra_attr_name)

                    while True:
                        print(delimiter(20))
                        print(extra_msg)

                        answer = input('\n')
                        _check_loop_exit(key=answer)

                        try:
                            answer = float(answer)
                            self.dmgs_dct[dmg_name].update({extra_attr_name: answer})
                            break
                        except (ValueError, TypeError):
                            print_invalid_answer(extra_msg='Float needed.')

    @inner_loop_exit_handler
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
        self.insert_dmg_category_related_attrs()

    @repeat_cluster(cluster_name='DMG ATTRIBUTES')
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
        duration=(1, 2, 3, 4, 5, 'permanent'),
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

            _check_loop_exit(key=num_of_buffs)

            try:
                num_iter = range(int(num_of_buffs))

                for _ in num_iter:
                    new_buff_name = _new_automatic_attr_dct_name(existing_names=self.buffs_dct, second_synthetic='buff',
                                                                 first_synthetic=self.ability_name)
                    self.buffs_dct.update({new_buff_name: self.buff_attributes()})

                end_msg = '\n%s buffs selected.' % num_of_buffs
                print(end_msg)
                break

            except ValueError:
                print_invalid_answer()
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
                    print_invalid_answer()

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
                    if stat_mods_answer == 'y':

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
                    elif stat_mods_answer == 'n':
                        self.buffs_dct[buff_name]['affected_stats'][affected_stat_app_form]['stat_mods'] = None
                        break
                    else:
                        print_invalid_answer()

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
                if buff_affects_stat == 'y':

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
                elif buff_affects_stat == 'n':
                    break
                else:
                    print_invalid_answer()

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

            if changes_stats == 'n':
                print("\nDoesn't modify stats.")
                self.buffs_dct[buff_name]['affected_stats'] = None
                break

            elif changes_stats == 'y':
                if self._stat_names_in_tooltip():
                    # (clears placeholder)
                    del self.buffs_dct[buff_name]['affected_stats']['placeholder_stat_1']

                    # Inserts each affected stat.
                    self.suggest_affected_stats_and_their_attrs(buff_name=buff_name)

                break

            else:
                print_invalid_answer()

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
        NOT USED

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

    @inner_loop_exit_handler
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

    @repeat_cluster(cluster_name='BUFFS')
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
        self.initial_abilities_attrs = {shortcut: self.single_spell_attrs() for shortcut in ABILITY_SHORTCUTS}
        # e.g. {'general': {'q':{},}, 'buffs':{}, 'dmgs':{} }
        self.final_abilities_attrs = {'general': {}, 'dmgs': {}, 'buffs': {}}

    @staticmethod
    def single_spell_attrs():
        return dict(general={}, dmgs={}, buffs={})

    @inner_loop_exit_handler
    def _gen_attr(self, attrs_dct, spell_name):
        """
        Modifies given dict by inserting 'general' attributes.

        Returns:
            (None)
        """

        gen_instance = GeneralAbilityAttributes(ability_name=spell_name, champion_name=self.champion_name)
        gen_instance.run_gen_attr_creation()

        attrs_dct['general'] = gen_instance.general_attr_dct

        print(delimiter(10))
        print('\nGeneral attributes')
        pp.pprint(attrs_dct['general'])

    @inner_loop_exit_handler
    def _dmg_attrs(self, attrs_dct, spell_name):
        """
        Modifies given dict by inserting 'general' attributes.

        Returns:
            (None)
        """

        dmgs_instance = DmgAbilityAttributes(ability_name=spell_name, champion_name=self.champion_name)
        dmgs_instance.run_dmg_attr_creation()

        attrs_dct['dmgs'] = dmgs_instance.dmgs_dct

    @inner_loop_exit_handler
    def _buff_attrs(self, attrs_dct, spell_name):
        """
        Modifies given dict by inserting 'general' attributes.

        Returns:
            (None)
        """

        buffs_inst = BuffAbilityAttributes(ability_name=spell_name, champion_name=self.champion_name)
        buffs_inst.run_buff_attr_creation()

        attrs_dct['buffs'] = buffs_inst.buffs_dct

    @inner_loop_exit_handler
    def _single_spell_attrs(self, spell_name):
        """
        Creates all attributes of an ability.

        Returns:
            (dct)
        """

        print(fat_delimiter(100))

        attrs_dct = self.single_spell_attrs()

        # GENERAL ATTRIBUTES
        self._gen_attr(attrs_dct=attrs_dct, spell_name=spell_name)

        # DMG ATTRIBUTES
        self._dmg_attrs(attrs_dct=attrs_dct, spell_name=spell_name)

        # BUFF ATTRIBUTES
        self._buff_attrs(attrs_dct=attrs_dct, spell_name=spell_name)

        print(fat_delimiter(40))
        pp.pprint(attrs_dct)

        return attrs_dct

    def _create_or_redo_spells_attrs(self):
        """
        Creates attributes of every spell.
        Allows redoing creation for each spell, if needed.

        Returns:
            (None)
        """

        for spell_name in SPELL_SHORTCUTS:

            # Creates spell att
            self.initial_abilities_attrs[spell_name] = self._single_spell_attrs(spell_name=spell_name)

            # Redo spell attributes if needed.
            while True:
                redo_all_attr_of_spell = input('\nRedo all attributes of %s?\n' % spell_name.upper())

                if redo_all_attr_of_spell == 'y':
                    # (not breaking after this allows redoing multiple times)
                    self.initial_abilities_attrs[spell_name] = self._single_spell_attrs(spell_name=spell_name)

                # (exit keys added for convenience when debugging)
                elif redo_all_attr_of_spell in ('n', INNER_LOOP_KEY, OUTER_LOOP_KEY):
                    break
                else:
                    print_invalid_answer()

    def _join_spells_buffs_and_dmgs(self):
        """
        Creates final attribute dict.

        Renames duplicate buff or dmg names and stores them in two groups,
        and merges general attributes.

        Returns:
            (None)
        """

        print(fat_delimiter(80))
        print('\nFINAL ATTRIBUTE DICT')

        self.final_abilities_attrs = {'general_attributes': {}, 'dmgs': {}, 'buffs': {}}

        # GENERAL ATTRIBUTES
        for ability_name in ABILITY_SHORTCUTS:
            self.final_abilities_attrs['general_attributes'].update(
                {ability_name: self.initial_abilities_attrs[ability_name]['general']})

        # DMGS AND BUFFS
        for shortcut in ABILITY_SHORTCUTS:
            for attr_type in ('dmgs', 'buffs'):
                for existing_name in self.initial_abilities_attrs[shortcut][attr_type]:

                    # Checks for common elements.
                    if existing_name not in self.final_abilities_attrs[attr_type]:
                        # Inserts new name and assigns the corresponding dict content to it.
                        old_attr_dct = self.initial_abilities_attrs[shortcut][attr_type][existing_name]

                        self.final_abilities_attrs[attr_type].update({existing_name: old_attr_dct})

                    # If duplicate found, asks user until valid answer.
                    else:
                        print(delimiter(10))
                        print('\nDuplicate found in %s %s.' % (attr_type, existing_name))
                        while True:
                            new_name = input('\nGive new name for %s:\n' % existing_name)

                            # Invalid answer (enter).
                            if new_name == '':
                                print_invalid_answer('No name given.')

                            # Invalid answer (existing name).
                            elif new_name in self.final_abilities_attrs[attr_type]:
                                print_invalid_answer('Name already exists.')

                            # Valid answer.
                            else:
                                # Inserts new name and assigns the corresponding dict content to it.
                                old_attr_dct = self.initial_abilities_attrs[shortcut][attr_type][existing_name]

                                self.final_abilities_attrs[attr_type].update({new_name: old_attr_dct})
                                break

    @outer_loop_exit_handler
    @repeat_cluster(cluster_name='SPELL ATTRS')
    def run_spell_attrs_creation(self):
        """
        Creates all attributes for all spells of given champion,
        including spell effects.

        Returns
            (None)
        """

        self._create_or_redo_spells_attrs()

        # Creates final attribute dict.
        self._join_spells_buffs_and_dmgs()

    def create_innate_attrs(self):
        # TODO
        None


class AbilitiesEffects(object):

    def __init__(self, champion_name):
        self.champion_name = champion_name
        self.spells_effects = {}

    def _set_spells_effects(self):

        for spell_name in SPELL_SHORTCUTS:
            self.spells_effects.update({spell_name: palette.ChampionsStats.spell_effects()})

    @inner_loop_exit_handler
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

        self._set_spells_effects()

        effects_dct = self.spells_effects[spell_name]

        for tar_type in ('enemy', 'player'):
            for application_type in ('passives', 'actives'):
                # DMGS

                dmg_msg = '%s\n' % univ_msg
                dmg_msg += '%s -- %s -- DMG APPLIED\n' % (tar_type, application_type)
                dmg_msg = dmg_msg.upper()

                _suggest_lst_of_attr_values(suggested_values_lst=_dmgs_names(champ_name=self.champion_name),
                                            modified_lst=effects_dct[tar_type][application_type]['dmg'],
                                            extra_start_msg=dmg_msg)

                pp.pprint(effects_dct[tar_type][application_type]['dmg'])

                # BUFFS APPLICATION
                buffs_applied_msg = '%s\n' % univ_msg
                buffs_applied_msg += '%s -- %s -- BUFFS APPLIED' % (tar_type, application_type)
                buffs_applied_msg = buffs_applied_msg.upper()

                _suggest_lst_of_attr_values(suggested_values_lst=_buffs_names(champ_name=self.champion_name),
                                            modified_lst=effects_dct[tar_type][application_type]['buffs'],
                                            extra_start_msg=buffs_applied_msg)

                pp.pprint(effects_dct[tar_type][application_type]['buffs'])

                # BUFF REMOVAL
                buff_removal_msg = '%s\n' % univ_msg
                buff_removal_msg += '%s -- %s -- BUFFS REMOVED' % (tar_type, application_type)
                buff_removal_msg = buff_removal_msg.upper()

                _suggest_lst_of_attr_values(suggested_values_lst=_buffs_names(champ_name=self.champion_name),
                                            modified_lst=effects_dct[tar_type][application_type]['remove_buff'],
                                            extra_start_msg=buff_removal_msg)

                pp.pprint(effects_dct[tar_type][application_type]['remove_buff'])

        # CD MODIFICATION
        lst_of_modified = []
        cd_mod_msg = '\nCDs MODIFIED ON CAST'
        _suggest_lst_of_attr_values(suggested_values_lst=SPELL_SHORTCUTS,
                                    modified_lst=lst_of_modified,
                                    extra_start_msg=cd_mod_msg)

        for cd_modified_name in lst_of_modified:

            mod_value = None
            while True:
                mod_value = input('\nHow much is %s modified for?\n' % cd_modified_name)

                try:
                    if float(mod_value) > 0:
                        break
                    else:
                        print('\nValue has to be higher than 0. Try again.')
                except ValueError:
                    print('\nValue has to be num. Try again.')

            effects_dct['player']['actives']['cds_modified'].update({cd_modified_name: mod_value})

        pp.pprint(self.spells_effects)

    @outer_loop_exit_handler
    @repeat_cluster(cluster_name='SPELL EFFECTS')
    def run_spell_effects_creation(self):
        """
        Creates effects of every spell.
        Allows redoing creation for each spell, if needed.

        Note: has to follow all buff and dmg creation so that all names are available.

        Returns:
            (None)
        """

        for spell_name in SPELL_SHORTCUTS:

            # Creates a spell's effects.
            self._create_single_spell_effects_dct(spell_name=spell_name)

            # Redo
            while True:
                redo_all_eff_of_spell = input('\nRedo all effects of %s?\n' % spell_name.upper())

                # Redo spell effects if needed.
                # (exit keys added for convenience when debugging)
                if redo_all_eff_of_spell in ('y', INNER_LOOP_KEY, OUTER_LOOP_KEY):
                    # (not breaking after this allows redoing multiple times)
                    self._create_single_spell_effects_dct(spell_name=spell_name)

                elif redo_all_eff_of_spell == 'n':
                    break
                else:
                    print_invalid_answer()


class Conditionals(object):
    def __init__(self, champion_name):
        self.champion_name = champion_name
        self.champ_module = imported_champ_module(champ_name=champion_name)
        self.abilities_dct = self.champ_module.ABILITIES_ATTRIBUTES
        self.abilities_effects = champ_abilities_attrs_dct(champ_name=champion_name)
        self.conditions = {}

    TARGET_TYPES = ('player', 'enemy')
    # (Used to determine what to insert next.)
    FORMULA_TYPE = ('constant_value', 'x_function')
    OPERATOR_TYPES = ('>', '<', '==', '<=', '>=')
    NON_PER_LVL_STAT_NAMES = sorted(i for i in stats.StatCalculation.ALL_POSSIBLE_STAT_NAMES if 'per_lvl' not in i)

    def available_buff_names(self):
        return sorted(self.abilities_dct['buffs'])

    def available_dmg_names(self):
        return sorted(self.abilities_dct['dmgs'])

    def available_buff_attr_names(self):

        s = {}
        for buff_name in self.available_buff_names():
            s |= self.abilities_dct['buffs'][buff_name].keys()

        return s

    def available_dmg_attr_names(self):

        s = {}
        for dmg_name in self.available_dmg_names():
            s |= self.abilities_dct['dmgs'][dmg_name].keys()

        return s

    def available_ability_attr_names(self):

        s = {}
        for ability_name in self.abilities_dct['general_attributes']:
            s |= self.abilities_dct['general_attributes'][ability_name].keys()

        return s

    def trigger_setup_dct(self,):

        return dict(
            buff=dict(
                buff_name=self.available_buff_names(),
                owner_type=self.TARGET_TYPES,
                operator=self.OPERATOR_TYPES,
                stacks=[str(i) for i in range(1, 10)],
                ),
            stat=dict(
                stat_name=self.NON_PER_LVL_STAT_NAMES,
                owner_type=self.TARGET_TYPES,
                operator=self.OPERATOR_TYPES,
                value=()
            ),
            spell_lvl=dict(
                spell_name=ALL_POSSIBLE_SPELL_SHORTCUTS,
                operator=self.OPERATOR_TYPES,
                lvl=ALLOWED_ABILITY_LVLS
            ),
            on_cd=dict(
                spell_name=ALL_POSSIBLE_SPELL_SHORTCUTS
            ))

    def effect_setup_dct(self):

        dct = dict(
            ability_effect=dict(
                ability_name=ALL_POSSIBLE_SPELL_SHORTCUTS,
                tar_type=('enemy', 'player'),
                # Contains spell effect categories
                lst_category=palette.ChampionsStats.spell_effects()['player']['actives'],
                mod_operation=('append', 'replace'),
            ),

            ability_attr=dict(
                ability_name=ALL_POSSIBLE_SPELL_SHORTCUTS,
                attr_name=self.available_ability_attr_names(),
                mod_operation=('multiply', 'add', 'replace'),
                formula_type=self.FORMULA_TYPE,
                ),

            buff_attr=dict(
                buff_name=self.available_buff_names(),
                buff_attr_name=self.available_buff_attr_names(),
                mod_operation=('multiply', 'add', 'replace'),
                formula_type=self.FORMULA_TYPE
                ),

            buff_on_hit=dict(
                buff_name=self.available_buff_names(),
                lst_category=palette.ChampionsStats.on_hit_effects(),
                mod_operation=('append', 'replace'),
                ),

            dmg_attr=dict(
                dmg_name=self.available_dmg_names(),
                attr_name=self.available_dmg_attr_names(),
                mod_operation=('multiply', 'add', 'replace'),
                formula_type=self.FORMULA_TYPE,
                ),
            )

        return dct

    @staticmethod
    def constant_values_dct():
        return dict(
            values_tpl=()
        )

    @staticmethod
    def formula_contents_dct():
        return dict(
            x_formula=(),
            x_type=('buff', 'stat'),
            x_name=(),
            x_owner=('player', 'enemy', None),
        )

    def _remove_prev_formula_keys(self, con_name, eff_name):
        """
        NOT USED.

        Removes previous formula keys from condition effect.
        """
        for k in self.formula_contents_dct():
            if k in self.conditions[con_name]['effects'][eff_name]:
                del self.conditions[con_name]['effects'][eff_name][k]

    def _create_and_insert_new_trigger(self, con_name):
        """
        Creates new trigger, and inserts it in given condition's dict.

        Returns:
            (None)
        """

        # Creates trig name.
        trig_name = _auto_new_name_or_ask_name(first_synthetic='trigger',
                                               existing_names=self.conditions[con_name]['triggers'],
                                               disable_enter=True)

        # Inserts trig name.
        self.conditions[con_name]['triggers'].update({trig_name: {}})

        # Inserts trig types.
        trig_type = _ask_tpl_question(question_str='Trigger TYPE?', choices_seq=self.trigger_setup_dct(),
                                      restrict_choices=True)

        self.conditions[con_name]['triggers'][trig_name].update({'trigger_type': trig_type})

        # Inserts trig contents.
        _suggest_attr_values(suggested_values_dct=self.trigger_setup_dct()[trig_type],
                             modified_dct=self.conditions[con_name]['triggers'][trig_name],
                             restrict_choices=True)

        print(delimiter(40))
        print('\nTRIGGER: {}'.format(trig_name))
        pp.pprint(self.conditions[con_name]['triggers'][trig_name])

    @repeat_cluster(cluster_name='CONDITION TRIGGERS')
    def _add_triggers(self, con_name):
        """
        Adds all triggers for given condition name.

        Returns:
            (None)
        """

        self.conditions[con_name].update({'triggers': {}})

        print(delimiter(20))
        # ADDS TRIGGER OR EXITS
        while True:
            end_trig_answer = _y_n_question(question_str='\nAdd trigger?')
            if not end_trig_answer:
                return
            else:
                self._create_and_insert_new_trigger(con_name)

        print(fat_delimiter(40))
        print('\nCONDITION: {}'.format(con_name))
        pp.pprint(self.conditions[con_name]['triggers'])

    def _create_and_insert_new_effect(self, con_name):
        """
        Creates new effect, and inserts it in given condition's dict.

        Returns:
            (None)
        """

        # Creates effect name.
        eff_name = _auto_new_name_or_ask_name(first_synthetic='effect',
                                              existing_names=self.conditions[con_name]['effects'],
                                              disable_enter=False)

        # Inserts effect name.
        self.conditions[con_name]['effects'].update({eff_name: {}})

        # Inserts effect types.
        eff_type = _ask_tpl_question(question_str='Effect TYPE?', choices_seq=self.effect_setup_dct(),
                                     restrict_choices=True)

        self.conditions[con_name]['effects'][eff_name].update({'effect_type': eff_type})

        # Inserts effect contents.
        _suggest_attr_values(suggested_values_dct=self.effect_setup_dct()[eff_type],
                             modified_dct=self.conditions[con_name]['effects'][eff_name],
                             restrict_choices=True)

        # Inserts effect formula.
        # (formula type is used for non buffs/dmgs)
        if 'formula_type' in self.conditions[con_name]['effects'][eff_name]:
            if self.conditions[con_name]['effects'][eff_name]['formula_type'] == 'x_formula':
                suggested_dct = self.formula_contents_dct()

            else:
                suggested_dct = self.constant_values_dct()

            _suggest_attr_values(suggested_values_dct=suggested_dct,
                                 modified_dct=self.conditions[con_name]['effects'][eff_name],)

        # Buffs/dmgs (names)
        else:
            self.conditions[con_name]['effects'][eff_name].update({'names_lst': []})
            cat = self.conditions[con_name]['effects'][eff_name]['category']
            if cat in ('buffs', 'remove_buff'):
                _suggest_lst_of_attr_values(suggested_values_lst=self.available_buff_names(),
                                            modified_lst=self.conditions[con_name]['effects'][eff_name]['names_lst'])
            # ('modifies_cd')
            elif 'cd' in cat:
                self.conditions[con_name]['effects'][eff_name].update({'names_dct': {}})

                _suggest_lst_of_attr_values(suggested_values_lst=ALL_POSSIBLE_ABILITIES_SHORTCUTS,
                                            modified_lst=self.conditions[con_name]['effects'][eff_name]['names_lst'])
                # ( {'q': (1,2..), }
                cd_mod_suggested_dct = {i: (1, 2, 3) for i in self.conditions[con_name]['effects'][eff_name]['names_lst']}
                _suggest_attr_values(suggested_values_dct=cd_mod_suggested_dct,
                                     modified_dct=self.conditions[con_name]['effects'][eff_name]['names_dct'])
                # (deletes list since it was used only temporarily to create the cd modification dct)
                del self.conditions[con_name]['effects'][eff_name]['names_lst']
            else:
                _suggest_lst_of_attr_values(suggested_values_lst=self.available_dmg_names(),
                                            modified_lst=self.conditions[con_name]['effects'][eff_name]['names_lst'])

        print(delimiter(40))
        print('\nEFFECT: {}'.format(eff_name))
        pp.pprint(self.conditions[con_name]['effects'][eff_name])

    @repeat_cluster(cluster_name='CONDITION EFFECTS')
    def _add_effects(self, con_name):
        """
        Adds all triggers for given condition name.

        Returns:
            (None)
        """

        self.conditions[con_name].update({'effects': {}})

        print(fat_delimiter(20))
        print('\nCONDITION: {}'.format(con_name))

        while True:
            end_eff_answer = _y_n_question(question_str='\nAdd effect?')

            if not end_eff_answer:
                return
            else:
                self._create_and_insert_new_effect(con_name=con_name)

        print(fat_delimiter(40))
        print('\nCONDITION: {}'.format(con_name))
        pp.pprint(self.conditions[con_name]['effects'])

    def _create_single_condition(self, con_name):

        # TRIGGERS
        self._add_effects(con_name=con_name)
        # EFFECTS
        self._add_triggers(con_name=con_name)

    @outer_loop_exit_handler
    @repeat_cluster(cluster_name='ALL CONDITIONS')
    def run_conditions_creation(self):
        print(fat_delimiter(100))
        msg = '\nCONDITIONALS CREATION:'
        msg += ('\n(triggers in a condition are checked with AND, never with OR. '
                'When OR needed, a new condition has to be created.)')
        print(msg)

        while True:
            print(fat_delimiter(40))

            # Ends method if no name is provided.
            if not _y_n_question('New condition?'):
                break
            else:
                # CONDITION NAME
                new_con_name = _auto_new_name_or_ask_name(first_synthetic='conditional', existing_names=self.conditions)
                self.conditions.update({new_con_name: {}})

                self._create_single_condition(con_name=new_con_name)

        print(fat_delimiter(40))
        print('\nCONDITIONALS')
        print('\nCHAMPION: {}'.format(self.champion_name))
        pp.pprint(self.conditions)


class ItemCreation(object):

    ITEM_STAT_NAMES_MAP = {
        'Ability Power': 'ap',
        'Ability Power per level': 'ap_per_lvl',
        'Armor': 'armor',
        'Attack Damage': 'ad',
        'Attack Speed': 'att_speed',
        'Base Health Regen': 'hp5',
        'Base Mana Regen': 'mp5',
        'Critical Strike Chance': 'crit_chance',
        'Cooldown Reduction': 'cdr',
        'Health': 'hp',
        'Life Steal': 'lifesteal',
        'Magic Penetration': 'flat_magic_penetration',
        'Magic Resist': 'mr',
        'Mana': 'mp',
        'Movement Speed': 'move_speed',
        'Spell Vamp': 'spellvamp',
    }

    def __init__(self):
        self._validate_stats_names()

    def _validate_stats_names(self):
        """
        Ensures all stat names in this class are exactly the same as the main program's stat names.

        Raises:
            UnexpectedValueError
        Returns:
            (None)
        """

        diff = set(self.ITEM_STAT_NAMES_MAP.values()) - (stats.ALL_POSSIBLE_STAT_NAMES | stats.ALL_RESOURCE_NAMES)

        if diff:
            raise palette.UnexpectedValueError(diff)

    @staticmethod
    def _stats_partition_in_description(item_description):
        """
        Cuts off and returns stats string in an item description by the xml tags (<stats> </stats>).

        Returns:
            (str)
        """

        try:
            return re.search(r'<stats>(.+)</stats>', item_description).group()

        except AttributeError:
            return ''

    def _stats_values_dct(self, item_name):
        """
        Returns a dict with stat names as values and stat value as key.

        Returns:
            (dict)
        """

        dct = {}

        description_str = ExploreApiItems().descriptions(item=item_name)[0].lower()
        stats_part_str = self._stats_partition_in_description(item_description=description_str)

        partitions_lst = re.split(r'<br>', stats_part_str)

        for str_part in partitions_lst:

            # STAT NAME
            # (reverse used to ensure 'ap per lvl' is matched before 'ap',
            # otherwise it will mismatch 'ap')
            for i in reversed(list(self.ITEM_STAT_NAMES_MAP)):
                if i.lower() in str_part:
                    stat_name = self.ITEM_STAT_NAMES_MAP[i]

                    # STAT VALUE
                    # Searches for int or float.
                    stat_val_str = re.search(r'(\d+\.?\d*%?)\s', str_part).group()

                    # Converts percent to float.
                    if '%' in stat_val_str:
                        stat_val_str = stat_val_str.replace('%', '')
                        stat_val = ast.literal_eval(stat_val_str) / 100.

                    else:
                        stat_val = ast.literal_eval(stat_val_str)

                    dct.update({stat_name: stat_val})

        return dct







# ===============================================================
#       MODULE CREATION
# ===============================================================
class ModuleCreatorBase(object):

    @staticmethod
    def _append_obj_in_module(obj_name, new_object_as_dct_or_str, targeted_module):
        """
        Appends full object inside targeted_module.

        :param obj_name: (str) 'ABILITIES_EFFECTS', 'TRINITY_FORCE', etc.
        :param new_object_as_dct_or_str: (str) or (dict) object body
        :param targeted_module: (str)
        :return: (None)
        """

        if type(new_object_as_dct_or_str) is dict:
            obj_as_str = dct_to_pretty_formatted_str(obj_name=obj_name, obj_body_as_dct=new_object_as_dct_or_str)
        else:
            obj_as_str = new_object_as_dct_or_str

        with open(targeted_module, 'a') as r:
            r.write(obj_as_str)

    @staticmethod
    def _replace_obj_in_module(obj_name, new_object_as_dct_or_str, targeted_module):
        """
        Replaces full object in module.

        :param obj_name: (str)
        :param new_object_as_dct_or_str: (dct) or (str) object body
        :return: (None)
        """

        with open(targeted_module, 'r') as r:
            r_as_lst = r.readlines()

        replacement = _file_after_replacing_module_var(file_as_lines_lst=r_as_lst, object_name=obj_name,
                                                       obj_as_dct_or_str=new_object_as_dct_or_str)

        with open(targeted_module, 'w') as w:
            w.write(replacement)

    @staticmethod
    def _obj_existence(obj_name, targeted_module):
        """
        Checks start of each line in a module for obj existence, ignoring starting preceding whitespaces.

        :param obj_name: (str)
        :param targeted_module: (str)
        :return:
        """

        with open(targeted_module, 'r') as r:
            r_as_lst = r.readlines()

        for line in r_as_lst:
            if re.match(r'\s*{}'.format(obj_name), line):
                return True
        # If no match has been found, returns False.
        else:
            return False

    def _insert_object_in_champ_module(self, obj_name, new_object_as_dct_or_str, replace_question_msg, targeted_module):
        """
        Inserts object in module after verifying replacement if needed.

        WARNING: When used for class insertion, assumes no empty lines between class start and __init__ end.

        Returns:
            (None)
        """

        # If object exists, replaces it.
        if self._obj_existence(obj_name=obj_name, targeted_module=targeted_module):
            
            if _y_n_question(question_str=replace_question_msg):
                self._replace_obj_in_module(obj_name=obj_name, new_object_as_dct_or_str=new_object_as_dct_or_str,
                                            targeted_module=targeted_module)
            else:
                print('\nReplacement canceled.')

        # If object doesn't exist, appends object.
        else:
            self._append_obj_in_module(obj_name=obj_name, new_object_as_dct_or_str=new_object_as_dct_or_str,
                                       targeted_module=targeted_module)
            

class ChampionModuleCreator(ModuleCreatorBase):

    def __init__(self, champion_name):
        self.champion_name = champion_name
        self.external_vars_dct = {}
        self.champion_module_path_str = '{}/{}.py'.format(CHAMPION_MODULES_FOLDER_NAME, self.champion_name)

    @staticmethod
    def _priority_tpl_as_str():
        """
        Creates action priority tuple.
        """

        priority_lst = []
        _suggest_lst_of_attr_values(suggested_values_lst=('AA',) + ALL_POSSIBLE_SPELL_SHORTCUTS,
                                    modified_lst=priority_lst,
                                    extra_start_msg='ACTION PRIORITY TUPLE',
                                    sort_suggested_lst=False)

        priority_tpl = tuple(priority_lst)

        return str(priority_tpl)

    @staticmethod
    def _external_vars():
        """
        Asks dev for externally set extra variables (set optionally by user, e.g. jax's dodged hits during E).

        Returns:
            (None)
        """

        print(fat_delimiter(40))

        dct = {}

        question_msg = '\nNew name for externally set var: (press enter to exit)\n'
        while True:

            external_val_name = input(question_msg)

            if external_val_name == '':
                print('\nNo external variable selected.')
                break
            else:
                external_val_initial_value = input('\nDefault value for %s:\n' % external_val_name)
                external_val_initial_value = chosen_val_to_literal(given_val=external_val_initial_value)

                dct.update({external_val_name: external_val_initial_value})

        return dct

    def _champ_obj_as_dct_or_str(self, obj_name):
        """
        Returns appropriate object body as dict or string, for given champion object name.

        Returns:
            (dict) or (str)
        """
        if obj_name == ABILITIES_ATTRS_DCT_NAME:
            attrs_inst = AbilitiesAttributes(champion_name=self.champion_name)
            attrs_inst.run_spell_attrs_creation()

            return attrs_inst.final_abilities_attrs

        elif obj_name == ABILITIES_EFFECT_DCT_NAME:
            effects_inst = AbilitiesEffects(champion_name=self.champion_name)
            effects_inst.run_spell_effects_creation()

            return effects_inst.spells_effects

        elif obj_name == ABILITIES_CONDITIONS_DCT_NAME:
            instance = Conditionals(champion_name=self.champion_name)
            instance.run_conditions_creation()

            return instance.conditions

        elif obj_name == CHAMPION_EXTERNAL_VAR_DCT_NAME:
            return self._external_vars()

        elif obj_name == CHAMP_CLASS_NAME:
            return child_class_as_str

        elif obj_name == DEFAULT_ACTIONS_PRIORITY_NAME:
            return self._priority_tpl_as_str()

        else:
            palette.UnexpectedValueError(obj_name)

    def run_champ_module_creation(self):
        """
        Creates all champion module related data (module dicts, class, etc)

        Returns:
            (None)
        """

        for obj_name in CHAMPION_MODULE_OBJECT_NAMES:
            replace_question_msg = '\nCHAMPION: {}, OBJECT NAME: {}'.format(self.champion_name, obj_name)
            replace_question_msg += '\nObject exists. Replace it?'
            
            self._insert_object_in_champ_module(obj_name=obj_name, 
                                                new_object_as_dct_or_str=self._champ_obj_as_dct_or_str(obj_name),
                                                replace_question_msg=replace_question_msg,
                                                targeted_module=self.champion_module_path_str)
            # Delay used to ensure file is "refreshed" after being writen on. (might be redundant)
            time.sleep(0.2)


class ItemModuleCreator(ModuleCreatorBase):

    def __init__(self):
        self.items_module_path_str = '{}/items_non_unique_data.py'.format(ITEM_MODULES_FOLDER_NAME)



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
        champName = 'annie'
        ExploreApiAbilities().champion_abilities(champion_name=champName, print_mode=True)
        ExploreApiAbilities().sanitized_tooltips(champ=champName, raw_str=None, print_mode=True)

    testCombination = False
    if testCombination is True:
        inst = AbilitiesAttributes(champion_name='jax')
        inst._single_spell_attrs('q')

    testChampIDs = False
    if testChampIDs is True:
        print(ExploreApiAbilities().champion_id('dariu'))

    testModuleInsertion = False
    if testModuleInsertion is True:
        ChampionModuleCreator(champion_name='jax').run_champ_module_creation()

    testItemNames = False
    if testItemNames is True:
        c = ExploreApiItems()._all_items_by_id

    testValidStatNames = False
    if testValidStatNames is True:
        inst = ItemCreation()

    testStatNamesValues = True
    if testStatNamesValues is True:
        for i in ExploreApiItems().used_items_by_name:
            print(i, ItemCreation()._stats_values_dct(i))