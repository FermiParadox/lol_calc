import re
import time
import urllib.request
import json
import pprint as pp
import copy
import importlib
import abc
import ast
import collections

import api_champions_database
import api_masteries_database
import champion_ids
import api_key
import palette
from palette import delimiter, fat_delimiter, ON_HIT_EFFECTS
import stats
import api_items_database
import items_folder.items_data


# Info regarding API structure at https://developer.riotgames.com/docs/data-dragon


# ===============================================================
# ===============================================================
# Objects in champion module (exact strings are re.matched inside module) (???)
CHAMPION_MODULES_FOLDER_NAME = 'champions'
ITEMS_MODULES_FOLDER_NAME = 'items_folder'
ITEMS_DATA_MODULE_NAME = 'items_data'
ITEMS_DATA_MODULE_PATH = '.'.join((ITEMS_MODULES_FOLDER_NAME, ITEMS_DATA_MODULE_NAME))
ITEMS_ATTRS_DCT_NAME = 'ITEMS_ATTRIBUTES'
ITEMS_EFFECTS_DCT_NAME = 'ITEMS_EFFECTS'
ITEMS_CONDITIONS_DCT_NAME = 'ITEMS_CONDITIONALS'
ABILITIES_ATTRS_DCT_NAME = 'ABILITIES_ATTRIBUTES'
ABILITIES_EFFECT_DCT_NAME = 'ABILITIES_EFFECTS'
ABILITIES_CONDITIONALS_DCT_NAME = 'ABILITIES_CONDITIONALS'
CHAMPION_EXTERNAL_VAR_DCT_NAME = 'CHAMPION_EXTERNAL_VARIABLES'
CHAMP_CLASS_NAME = 'class ChampionAttributes'
DEFAULT_ACTIONS_PRIORITY_NAME = 'DEFAULT_ACTIONS_PRIORITY'
CHAMPION_STATS_DEPENDENCIES_NAME = 'CHAMPION_STATS_DEPENDENCIES'
RESOURCE_USED_NAME = 'RESOURCE_USED'
SPELL_LVL_UP_PRIORITIES_NAME = 'SPELL_LVL_UP_PRIORITIES'
CHAMPION_RANGE_TYPE_NAME = 'CHAMPION_RANGE_TYPE'
CHAMPION_MODULE_OBJECT_NAMES = (ABILITIES_ATTRS_DCT_NAME, ABILITIES_EFFECT_DCT_NAME,
                                ABILITIES_CONDITIONALS_DCT_NAME, CHAMPION_EXTERNAL_VAR_DCT_NAME,
                                DEFAULT_ACTIONS_PRIORITY_NAME, SPELL_LVL_UP_PRIORITIES_NAME,
                                CHAMPION_STATS_DEPENDENCIES_NAME, CHAMPION_RANGE_TYPE_NAME, CHAMP_CLASS_NAME,)

CHAMPION_BASE_STATS_DCT_NAME = 'CHAMPION_BASE_STATS'
CHAMPION_BASE_STATS_MODULE = 'app_champions_base_stats.py'


API_STORED_MASTERIES_MODULE = 'api_masteries_database.py'
MASTERIES_MODULES_FOLDER_NAME = 'masteries_dir'
MASTERIES_DATA_MODULE_NAME = 'masteries_data'
MASTERIES_ATTRS_DCT_NAME = 'MASTERIES_ATTRIBUTES'
MASTERIES_MODULE_PATH = '.'.join((MASTERIES_MODULES_FOLDER_NAME, MASTERIES_DATA_MODULE_NAME))


child_class_as_str = """class ChampionAttributes(abilities.VisualRepresentation):
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
            setattr(ChampionAttributes, i, external_vars_dct[i])"""


ALL_POSSIBLE_ACTIONS = (
    ('AA', ) +
    palette.ALL_POSSIBLE_SPELL_SHORTCUTS +
    tuple(items_folder.items_data.CASTABLE_ITEMS) +
    ('summoner_spell', )
)

STAT_TYPES = ('additive', 'percent', 'multiplicative')


# ===============================================================
class Fetch(object):
    """
    Used for retrieving stored data in a champion module, items module, or masteries module.
    """

    @staticmethod
    def imported_module(path_str):
        """
        Returns module, ensuring it is reloaded.
        :return: (module)
        """

        module = importlib.import_module(path_str)
        importlib.reload(module)

        return module

    @staticmethod
    def champion_module_path(champ_name):
        return CHAMPION_MODULES_FOLDER_NAME + '.' + champ_name

    def imported_champ_module(self, champ_name):
        """
        Returns champion module, ensuring it is reloaded.
        :return: (module)
        """

        return self.imported_module(path_str=self.champion_module_path(champ_name=champ_name))

    def imported_items_module(self):
        """
        Returns items' data module, ensuring it is reloaded.
        :return: (module)
        """

        return self.imported_module(path_str=ITEMS_DATA_MODULE_PATH)

    def imported_masteries_module(self):
        return self.imported_module(path_str=MASTERIES_MODULE_PATH)

    def champ_abilities_attrs_dct(self, champ_name):
        """
        Returns champion's abilities' attributes dict.

        Returns:
            (dct)
        """

        champ_mod = self.imported_champ_module(champ_name)
        return getattr(champ_mod, ABILITIES_ATTRS_DCT_NAME)

    def champ_effects_dct(self, champ_name):
        """
        Returns champion's abilities' effects dict.

        Returns:
            (dct)
        """

        champ_mod = self.imported_champ_module(champ_name)
        return getattr(champ_mod, ABILITIES_EFFECT_DCT_NAME)

    def items_attrs_dct(self):
        return getattr(self.imported_items_module(), ITEMS_ATTRS_DCT_NAME)

    def items_effects_dct(self):
        return getattr(self.imported_items_module(), ITEMS_EFFECTS_DCT_NAME)

    def _dmgs_or_buffs_names(self, obj_name, champ_or_item, attr_type):
        """
        Returns list of dmg names for champion or item selected.

        Because of ITEM_ATTRIBUTES and ABILITIES_ATTRIBUTES structure,
        only champion name or item name are required to define which inner dict is needed.

        :param obj_name: (str) champion name or item name
        :param champ_or_item: (str) 'champion' or 'item'
        :param attr_type: (str) 'dmgs' or 'buffs'
        :returns: (list)
        """

        if champ_or_item == 'champion':
            return sorted(self.champ_abilities_attrs_dct(champ_name=obj_name)[attr_type])

        elif champ_or_item == 'item':
            return sorted(self.items_attrs_dct()[obj_name][attr_type])

        else:
            raise palette.UnexpectedValueError

    def dmgs_names(self, obj_name, champ_or_item):
        """
        Returns a list of all dmg names in champion or item attributes dict.

        :param obj_name: (str) champion name or item name
        :param champ_or_item: (str) 'champion' or 'item'
        :returns: (list)
        """
        return self._dmgs_or_buffs_names(obj_name=obj_name, champ_or_item=champ_or_item, attr_type='dmgs')

    def buffs_names(self, obj_name, champ_or_item):
        """
        Returns a list of all buffs names in champion or item attributes dict.

        :param obj_name: (str) champion name or item name
        :param champ_or_item: (str) 'champion' or 'item'
        :returns: (list)
        """
        return self._dmgs_or_buffs_names(obj_name=obj_name, champ_or_item=champ_or_item, attr_type='buffs')

    def _obj_effects(self, obj_name, champ_or_item):
        """
        Returns dict containing ability or item effects.

        :param obj_name:
        :param champ_or_item:
        :return:
        """

        if champ_or_item == 'champion':
            mod = self.imported_champ_module(champ_name=obj_name)
            return getattr(mod, ABILITIES_EFFECT_DCT_NAME)
        else:
            return self.imported_items_module().ITEMS_EFFECTS[obj_name]

    def castable(self, spell_or_item_name, champ_or_item, champ_name=None):
        """
        Checks if given champion ability or item is castable.

        :param spell_or_item_name: (str) champion or item name
        :param champ_or_item: (str)
        :returns: (bool)
        """

        if champ_or_item == 'champion':
            spell_name = spell_or_item_name

            return self.champ_abilities_attrs_dct(champ_name=champ_name)['general_attributes'][spell_name]['castable']

        else:
            item_name = spell_or_item_name
            return self.items_attrs_dct()[item_name]['general_attributes']['castable']


# ---------------------------------------------------------------
def full_or_partial_match_in_iterable(searched_name, iterable):
    """
    Searches for given name, looking for an exact match, or a partial otherwise.

    Raises:
        (KeyValue) if more than one matches found, or no matches
    Returns:
        (str) String matching searched name.
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
        error_msg = '{} partial matches found instead of one: {}'.format(tot_partial_matches, partial_matches_lst)
        raise KeyError(error_msg)
    else:
        raise KeyError('No full or partial match.')


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
    # Handles formulas and empty strings.
    except (ValueError, SyntaxError):
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


def _dct_body_to_pretty_formatted_str(given_dct, width):
    """
    Converts given dct (body) to a pretty formatted string.
    Used for file writing.

    Args:
        width: 1 or (false value) used for depth 1 dicts
    Returns:
        (str)
    """

    if width:
        string = pp.pformat(given_dct, width=width)[1:]
    # (else width gets default value)
    else:
        string = pp.pformat(given_dct)[1:]

    new_str = ''
    for num, line in enumerate(string.split('\n')):
        if num == 0:
            # (pprint module always inserts one less whitespace for first line)
            # (indent=1 is default, giving everything one extra whitespace)
            new_str += ' '*4 + line + '\n'
        else:
            new_str += ' '*3 + line + '\n'

    return '{\n' + new_str


def dct_to_pretty_formatted_str(obj_name, obj_body_as_dct, width):
    """
    Creates pretty formatted full string of a dct to be inserted in a file.
    """

    body = _dct_body_to_pretty_formatted_str(given_dct=obj_body_as_dct, width=width)
    name_and_equal_sign = obj_name + ' = '

    return name_and_equal_sign + body


def _file_after_replacing_module_var(file_as_lines_lst, object_name, obj_as_dct_or_str, width):
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
        inserted_str = dct_to_pretty_formatted_str(obj_name=object_name, obj_body_as_dct=obj_as_dct_or_str, width=width)
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

                    old_end = num_2
                    break

            # Creates new file as string.
            new_str = ''
            for i in file_as_lines_lst[:old_start]:
                new_str += i
            new_str += inserted_str
            for i in file_as_lines_lst[old_end:]:
                new_str += i

            return new_str


# ---------------------------------------------------------------
def _return_or_pprint_complex_obj(print_mode, given_dct):
    """
    Used for pretty printing a dict or returning it.

    Args:
        print_mode: (bool)
    Returns:
        (None)
        (dct)
    """

    if print_mode is True:
        pp.pprint(given_dct)

    else:
        return given_dct


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
class OuterLoopExitError(Exception):
    pass


class InnerLoopExitError(Exception):
    pass


class RepeatChoiceErrorError(Exception):
    pass


# Loop exit keys.
INNER_LOOP_KEY = '!'
OUTER_LOOP_KEY = '!!'
REPEAT_CHOICE_KEY = '^'


def _check_loop_exit(key):
    if key == OUTER_LOOP_KEY:
        print('#### OUTER LOOP EXITED ####')
        raise OuterLoopExitError
    elif key == INNER_LOOP_KEY:
        print('#### INNER LOOP EXITED ####')
        raise InnerLoopExitError


def _check_for_repeat_choice_error(key):
    if key == REPEAT_CHOICE_KEY:
        print('### Repeating previous choice ###')
        raise RepeatChoiceErrorError


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


def inner_loop_exit_handler(func, _exception_class=InnerLoopExitError):

    return _loop_exit_handler(func=func, _exception_class=_exception_class)


def outer_loop_exit_handler(func, _exception_class=OuterLoopExitError):

    return _loop_exit_handler(func=func, _exception_class=_exception_class)


# ---------------------------------------------------------------
def _y_n_question(question_str, disallow_enter=True):
    """
    Checks user input on given question_str.
    Raises factory custom exceptions if needed.

    Returns:
        (True)
        (False)
    """

    msg = '\n{} '.format(question_str)

    if disallow_enter is False:
        msg += '(press enter to skip)'
    else:
        msg += '(y, n)'

    while True:
        answer = input(msg+'\n')

        # Check exceptions.
        _check_factory_custom_exception(given_str=answer, exclude_repeat_key=True)

        if answer == 'y':
            return True
        elif answer == 'n':
            return False
        elif (disallow_enter is False) and (answer == ''):
            return False
        else:
            print_invalid_answer()


def _enumerated_question_msg(choices_couples, max_rows=20, max_columns=4):

    choices_couples_lst = list(choices_couples)
    total_choices = len(choices_couples_lst)

    # CREATES EACH CHOICE STRING
    choices_strings_lst = []

    for couple in choices_couples_lst:
        num = couple[0]
        val = couple[1]
        choice_str = '{}: {}'.format(num, val)

        # Fills with spaces
        missing_spaces = 40 - len(choice_str)
        choice_str += ' ' * missing_spaces

        choices_strings_lst.append(choice_str)

    for _ in range(200):
        choices_strings_lst.append('')

    # FINAL MERGED STRING
    msg = ''

    # (fills with empty strings so that fix list size is reached)
    lst = [i for i in choices_strings_lst] + ['']*200

    for i in range(max_rows+1):
        # (adds 1st, 31st, 61st etc in one line)
        for k in range(max_columns):
            msg += '{}'.format(lst[i + max_rows * k])

        msg += '\n'

        if i == total_choices:
            break

    return msg


def enumerated_question(question_str, choices_seq, restrict_choices=False):
    """
    Asks dev to choose one of the enumerated choices.

    Returns:
        (anything) Selected choice can be any element of given sequence.
    """

    try:
        choices = sorted(choices_seq)
    except TypeError:
        choices = choices_seq

    enum_choices = enumerate(choices, 1)

    print(delimiter(10))
    msg = '\n' + question_str + '\n'

    msg += _enumerated_question_msg(choices_couples=enum_choices)

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


def restricted_input(question_msg, input_type, characteristic=None, disallow_enter=False):
    """
    Repeats question until valid type answer is given.

    WARNING: Plain "enter" precedes any type requirements.

    :param question_msg: (str)
    :param input_type: (str) 'str', 'bool', 'num', 'int', 'float', 'tuple', 'list'
    :param characteristic: (str) 'non_negative', 'non_zero', 'non_positive'
    :param disallow_enter: (bool) Allows or disallows giving an empty string as input for question.
    :returns: (literal)
    """

    type_name_to_func_map = {'str': str,
                             'num': 'num',
                             'int': int,
                             'bool': bool,
                             'tuple': tuple,
                             'list': list,
                             'dict': dict}

    # Raises error if unexpected type name is requested.
    if input_type not in type_name_to_func_map:
        raise palette.UnexpectedValueError

    while 1:
        answer = input('\n' + question_msg + '\n')

        # ENTER
        if answer == '':
            if disallow_enter is True:
                print_invalid_answer('\nPlain "enter" not accepted.')
                continue
            else:
                return ''

        # Expected type (string)
        if input_type == 'str':
            if re.match(r'^\w+$', answer):
                return answer
            else:
                print_invalid_answer('\nString required.')
                continue

        # NON ENTER
        try:
            answer_as_literal = ast.literal_eval(answer)
        except (ValueError, SyntaxError):
            print_invalid_answer('\n{} required.'.format(input_type.capitalize()))
            continue

        # TYPE CHECK
        # Expected type (non string)
        if type(answer_as_literal) is type_name_to_func_map[input_type]:
            # (allows next checks)
            pass
        elif input_type == 'num' and (type(answer_as_literal) is int) or (type(answer_as_literal) is float):
            # (input '2' would be "int" after 'literal_eval', so it has to be specially included in floats)
            pass

        # Wrong types
        else:
            print_invalid_answer('\nWrong type; expected {}.'.format(input_type))
            continue

        # EXTRA CHARACTERISTICS CHECK
        if characteristic is not None:

            if characteristic == 'non_zero':
                if answer_as_literal == 0:
                    print_invalid_answer('\nZero not allowed.')
                    continue
                else:
                    return answer_as_literal

            elif characteristic == 'non_negative':
                if answer_as_literal < 0:
                    print_invalid_answer('\nNon negative answers not allowed.')
                    continue
                else:
                    return answer_as_literal

            elif characteristic == 'non_positive':
                if answer_as_literal > 0:
                    print_invalid_answer('\nNon positive answers not allowed.')
                    continue
                else:
                    return answer_as_literal

            else:
                raise palette.UnexpectedValueError

        else:
            return answer_as_literal


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
                if (_input_in_len_range(given_str=input_given, choices_length=shortcut_len) is False) \
                        and (input_given not in _exception_keys().values()):

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


def suggest_attr_values(suggested_values_dct, modified_dct, restrict_choices=False, mute_exit_key_msgs=False,
                        extra_start_msg='', attrs_with_lst_val=None):
    """
    READ: single suggestion method for more details.

    Stores each chosen attribute value or repeats a choice.

    :param attrs_with_lst_val: (None), (list) When given, attr names in this list will get a list-value selection.
    """

    start_msg = '\n' + delimiter(40)
    if mute_exit_key_msgs is False:
        start_msg += '\n(type "%s" to exit inner loops)' % _exception_keys()['stop_key']
        start_msg += '\n(type "%s" to exit outer loops)' % _exception_keys()['error_key']
        start_msg += '\n(type "%s" to repeat previous choices)\n\n' % _exception_keys()['repeat_key']
    start_msg += extra_start_msg
    print(start_msg)

    num_name_couples = {num: name for num, name in enumerate(sorted(suggested_values_dct))}
    for attr_num in sorted(num_name_couples):

        while True:
            curr_attr_name = num_name_couples[attr_num]

            try:
                # List-value.
                if attrs_with_lst_val and (curr_attr_name in attrs_with_lst_val):
                    suggested_values_lst = suggested_values_dct[curr_attr_name]

                    # Sets attr equal to a list so that it can be modified.
                    modified_dct[curr_attr_name] = []
                    modified_lst = modified_dct[curr_attr_name]

                    suggest_lst_of_attr_values(suggested_values_lst=suggested_values_lst,
                                               modified_lst=modified_lst,
                                               sort_suggested_lst=False)

                else:
                    # Single value.
                    _suggest_single_attr_value(attr_name=curr_attr_name,
                                               suggested_values_dct=suggested_values_dct,
                                               modified_dct=modified_dct,
                                               restrict_choices=restrict_choices)
                break

            except RepeatChoiceErrorError:
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


def _ask_new_group_name(group_type_name, existing_names=None, disallow_enter=False):
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
        if disallow_enter is False:
            question_msg += '(enter to skip)'
        new_name = input(question_msg + '\n')
        _check_factory_custom_exception(given_str=new_name, exclude_repeat_key=True)

        if new_name in existing_names:
            print_invalid_answer('Name exists.')
            continue

        elif (disallow_enter is True) and (new_name == ''):
            print_invalid_answer('(Enter not acceptable.)')
            continue

        elif new_name == '':
            break

        else:
            break

    return new_name


def _auto_new_name_or_ask_name(existing_names, first_synthetic, second_synthetic='', disallow_enter=False):
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
                                          disallow_enter=disallow_enter)

    if new_manual_name:
        return new_manual_name
    else:
        return new_automatic_name


# ---------------------------------------------------------------
def suggest_lst_of_attr_values(suggested_values_lst, modified_lst, extra_start_msg='', stop_key=INNER_LOOP_KEY,
                               error_key=OUTER_LOOP_KEY, sort_suggested_lst=True):
    """
    Suggests values from a list to dev. Dev has to pick all valid values in his single answer.

    Modifies a list by appending suggested values.

    Returns:
        (None)
    """

    # MSG
    start_msg = '\n' + delimiter(40)
    start_msg += '\n(type "%s" to exit inner loops)\n' % stop_key
    start_msg += '\n(type "%s" to exit outer loops)\n\n' % error_key
    start_msg += extra_start_msg
    print(start_msg)

    # SORT DISPLAYED LIST
    if sort_suggested_lst is True:
        suggested_lst = sorted(suggested_values_lst)
    else:
        suggested_lst = suggested_values_lst

    enum_choices = enumerate(suggested_lst, 1)

    print(_enumerated_question_msg(enum_choices))

    # Asks dev.
    while True:
        dev_choice = input('\nSelect ALL valid names. (press only enter for empty)\n')

        # Exits loop if requested.
        _check_loop_exit(dev_choice)

        # (only comma, whitespace and digits are valid characters, or empty string)
        if re.search(r'[^\d,\s]', dev_choice) is not None:
            print_invalid_answer(extra_msg='Answer may contain only digits, whitespaces and comma. (or enter)')

        else:
            # Checks if given values correspond to actual indexes.
            # If not, message is repeated.
            try:
                # (e.g. '2, 74,5 ,1')
                pattern = re.compile(r'\d+')
                matches = re.findall(pattern, dev_choice)

                corresponding_vals_lst = []
                for match in matches:
                    index_num = int(match)

                    corresponding_value = suggested_lst[index_num - 1]

                    corresponding_vals_lst.append(corresponding_value)
                    modified_lst.append(corresponding_value)

                print(', '.join(corresponding_vals_lst))
                break

            except IndexError:
                print_invalid_answer(extra_msg='Indexes out of range.')

    print()


def enumerated_lst_creation(suggested_values_lst, extra_start_msg='', sort_suggested_lst=True):
    """
    Creates and returns a list containing all selections from an enumerated question.

    :return: (list)
    """

    lst = []
    suggest_lst_of_attr_values(suggested_values_lst=suggested_values_lst, modified_lst=lst,
                               extra_start_msg=extra_start_msg, sort_suggested_lst=sort_suggested_lst)

    return lst


# ---------------------------------------------------------------
def repeat_cluster_decorator(cluster_name):
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
ALLOWED_ABILITY_LVLS = ('1', '2', '3', '4', '5', '0')


def spell_num(spell_name):
    return palette.SPELL_SHORTCUTS.index(spell_name)


def ability_num(ability_name):
    if ability_name == 'inn':
        return 0
    else:
        return spell_num(spell_name=ability_name) + 1


# ---------------------------------------------------------------
ALLOWED_STATS_NAMES = stats.ALL_POSSIBLE_STAT_NAMES


def check_stat_name_validity(stat_name):
    """
    Checks if given name exists in app allowed stats' names.

    :param stat_name: (str)
    :return: (None)
    """

    if stat_name not in ALLOWED_STATS_NAMES:
        raise palette.UnexpectedValueError


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
class RequestAbortedError(Exception):
    pass


class RequestDataFromAPI(object):
    """
    Base class of RequestClasses(?).

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
            except RequestAbortedError as exception_msg:
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
        start_msg = '\n' + fat_delimiter(num_of_lines=40)
        start_msg += '\nWARNING !!!'
        start_msg += fat_delimiter(num_of_lines=40)
        start_msg += '\n\nAPI KEY USED: %s\n' % api_key.KEY
        start_msg += '\nStart API requests (%s)?\n' % requested_item

        abort_msg = '\nData request ABORTED.\n'

        dev_start_question = input(start_msg)
        if dev_start_question == 'y':
            pass
        else:
            raise RequestAbortedError(abort_msg)

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
        therefor (?)..

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
            champ_name = champ_name.lower()
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
    RUNES_PAGE_URL = ("https://eune.api.pvp.net/api/lol/static-data/eune/v1.2/rune?runeListData=all&api_key="
                      + api_key.KEY)

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
    def store_all_masteries_from_api(self):
        page_as_str = self.request_single_page_from_api_as_str(page_url=self.MASTERIES_PAGE_URL,
                                                               requested_item='MASTERIES')

        data_storage(targeted_module=API_STORED_MASTERIES_MODULE,
                     obj_name='ALL_MASTERIES',
                     str_to_insert=page_as_str)


# ===============================================================
#       API EXPLORATION
# ===============================================================
class _ExploreBase(object):

    @staticmethod
    def champion_id(searched_name):
        """
        Finds a champion's id number.

        Returns:
            (int)
        """

        champ_ids_dct = champion_ids.CHAMPION_IDS
        # Dict with champ names as keys and ids as values.
        inverted_ids_dct = {val.lower(): key for key, val in champ_ids_dct.items()}

        match_found = full_or_partial_match_in_iterable(searched_name=searched_name, iterable=inverted_ids_dct)

        return int(inverted_ids_dct[match_found])

    @staticmethod
    def _append_all_or_matching_str(examined_str, modified_lst, raw_str=None):
        """
        Modifies a list by inserting a string only if it matches given pattern.
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

    @staticmethod
    def modify_api_names_to_callable_string(name):
        """
        Converts to lowercase everything and
        removes or replaces characters that would not be allowed in a python object name (e.g. -'" whitespace).

        :param name: (str)
        :return: (str)
        """

        name = name.strip()

        replacement_dct = {
            ' ': '_',
            "'": '',
            '-': '_'
        }

        for character in replacement_dct:
            name = name.replace(character, replacement_dct[character])

        name = name.lower()
        name = name.strip('_')

        return name


class _ExploreApiAbilitiesAndRecommendedItemsBase(_ExploreBase):
    def __init__(self):
        self.data_module = __import__('api_champions_database')
        self.all_champions_data_dct = self.data_module.ALL_CHAMPIONS_ATTR
        self.champions_lst = sorted(self.all_champions_data_dct)


class ExploreApiAbilities(_ExploreApiAbilitiesAndRecommendedItemsBase):

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

        return _return_or_pprint_complex_obj(print_mode=print_mode, given_dct=final_dct)

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

        return _return_or_pprint_complex_obj(print_mode=print_mode, given_dct=champ_stats)

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

        return _return_or_pprint_complex_obj(print_mode=print_mode, given_dct=result)

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
            for ability_name in palette.SPELL_SHORTCUTS:
                category_name = self.single_cost_category(champ_name=champ, ability_name=ability_name)['costType']
                category_name.lower().strip()

                self._store_and_note_frequency(string=category_name,
                                               modified_dct=cost_categories_dct,
                                               name=champ)

        return _return_or_pprint_complex_obj(print_mode=print_mode, given_dct=cost_categories_dct)

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

        return _return_or_pprint_complex_obj(print_mode=print_mode, given_dct=cost_categories_dct)


class ExploreApiItems(_ExploreBase):

    def __init__(self):
        self.item_related_api_data = api_items_database.ALL_ITEMS
        # All items, INCLUDING items not usable in summoners rift (they are excluded below, so might cause bugs if used)
        self.all_items_dct_by_id = self.item_related_api_data['data']
        # (there is a method below more suitable for returning item dict, that does not require exact name match)
        self.usable_items_by_name_dct = self._usable_items_dct_by_name()
        self.total_usable_items = len(self.usable_items_by_name_dct)

    MANDATORY_MAP_ID = 1
    DISALLOWED_ITEM_TAGS = ('trinket', 'consumable', )

    def _usable_items_dct_by_name(self):
        """
        Creates a dict containing only items that can be used.

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

        for item_id in self.all_items_dct_by_id:

            # MAP
            allowed_on_map = True
            # (if there is no map exclusion, then it is usable on required map)
            try:
                if self.all_items_dct_by_id[item_id]['maps']['11'] is False:
                    allowed_on_map = False
            except KeyError:
                pass

            # PURCHASABLE
            purchasable = True
            if 'inStore' in self.all_items_dct_by_id[item_id]:
                if self.all_items_dct_by_id[item_id]['inStore'] is False:
                    purchasable = False
            # TODO: update with victor's item, since it's filtered out because of not being purchasable at tier 1.

            # NON DISALLOWED TAG
            allowed_tags = True
            if 'tags' in self.all_items_dct_by_id[item_id]:
                for tag in self.all_items_dct_by_id[item_id]['tags']:
                    if tag.lower() in self.DISALLOWED_ITEM_TAGS:
                        allowed_tags = False

            # Checks if all conditions are met.
            if allowed_on_map and allowed_tags and purchasable:
                item_name = self.all_items_dct_by_id[item_id]['name'].lower()

                # (order below matters for correct naming)
                item_name = item_name.replace('(ranged only)', '')
                item_name = item_name.replace('(melee only)', '')
                item_name = item_name.rstrip()
                item_name = item_name.replace(' ', '_')

                item_name = item_name.replace("'", '')
                item_name = item_name.replace('-', '_')
                item_name = item_name.replace(':', '_')
                item_name = item_name.replace('__', '_')
                item_name = item_name.replace('.', '')
                item_name = item_name.lower()

                dct.update({item_name: self.all_items_dct_by_id[item_id]})

        return dct

    def item_name_from_id(self, id_num):
        """
        Searches through items, and retrieves name corresponding to given id.

        :param id_num: (str), (int) id number of item
        :return: (str) or (None) if item does not belong to the usable items.
        """

        id_num = int(id_num)

        for item_name in self.usable_items_by_name_dct:
            if self.usable_items_by_name_dct[item_name]['id'] == id_num:
                return item_name

    def total_usable_items(self):
        """
        Number of usable items.

        Returns:
            (int)
        """
        return len(self.usable_items_by_name_dct)

    def actual_item_name(self, item_name):
        """
        Returns the actual item name that matches given item name.

        :param item_name: (str) Incomplete (or complete) item name.
        :return: (str)
        """
        return full_or_partial_match_in_iterable(searched_name=item_name,
                                                 iterable=self.usable_items_by_name_dct)

    def item_dct(self, given_name, print_mode=False):
        """
        Checks for an exact match of given name,
        or a partial match otherwise.

        Raises:
            (KeyValue) if more than one matches found, or no matches
        Returns:
            (dct)
        """

        matched_name = full_or_partial_match_in_iterable(searched_name=given_name,
                                                         iterable=self.usable_items_by_name_dct)

        return _return_or_pprint_complex_obj(print_mode=print_mode, given_dct=self.usable_items_by_name_dct[matched_name])

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
            item_lst = self.usable_items_by_name_dct
        else:
            # (need a list so it inserts selection into a list)
            matched_name = full_or_partial_match_in_iterable(searched_name=item, iterable=self.usable_items_by_name_dct)
            item_lst = [matched_name, ]

        descriptions_lst = []

        for item_name in sorted(item_lst):

            try:
                self._append_all_or_matching_str(examined_str=self.usable_items_by_name_dct[item_name][element_name],
                                                 modified_lst=descriptions_lst,
                                                 raw_str=raw_str)
            except KeyError:
                print("\n'%s' has no element '%s'" % (item_name, element_name))

        # Checks if print mode is selected.
        return _return_or_pprint_lst(print_mode=print_mode, lst=descriptions_lst)

    def unfiltered_descriptions(self, item=None, raw_str=None, print_mode=False):
        """
        Filters and then returns or prints "description" for given item (or for all items).

        Note: Check parent method for more details.
        """

        return self._item_elements(element_name='description', item=item,
                                   raw_str=raw_str, print_mode=print_mode)

    def item_description_xml_tag_names(self):
        """
        Finds existing xml tag names in item description.

        :return: (set)
        """
        names = set()

        for item_name in self.usable_items_by_name_dct:
            item_description = self.unfiltered_descriptions(item=item_name)[0].lower()
            matches_lst = re.findall(r'<[a-z]+>', item_description)

            names |= set(matches_lst)

        return names

    def descriptions(self, item=None, raw_str=None, print_mode=False):
        """
        Filters and then returns or prints "description" for given item (or for all items).

        Note: Check parent method for more details.
        """

        raw_lst = self.unfiltered_descriptions(item=item, raw_str=raw_str, print_mode=False)

        lst_with_filtered_strings = []
        for unfiltered_str in raw_lst:
            # FILTERS OUT:
            # <i> content </i>
            filtered_str = re.sub(r'<i>.+?</i>', '', unfiltered_str)
            # empty tags
            for xml_tag in self.item_description_xml_tag_names():
                filtered_str = re.sub(r'<{xml_tag}></{xml_tag}>'.format(xml_tag=xml_tag), '', filtered_str)

            # <font color=.... > .. </font>
            filtered_str = re.sub(r'<font.+?</font>', '', filtered_str)

            lst_with_filtered_strings.append(filtered_str)

        return _return_or_pprint_lst(lst=lst_with_filtered_strings, print_mode=print_mode)

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

        return _return_or_pprint_complex_obj(print_mode=print_mode, given_dct=counter)

    def item_tags(self, only_freq=False, print_mode=False):
        """
        Returns or pretty prints all item tags.
        """
        item_occurrence_dct = {}

        for item_name in self.usable_items_by_name_dct:

            try:
                tags_lst = self.usable_items_by_name_dct[item_name]['tags']

                for tag_str in tags_lst:
                    self._store_and_note_frequency(string=tag_str, modified_dct=item_occurrence_dct,
                                                   champions_or_items='items', name=item_name, only_freq=only_freq)

            except KeyError:
                print("\n'%s' has no element '%s'" % (item_name, 'tags'))

        return _return_or_pprint_complex_obj(print_mode=print_mode, given_dct=item_occurrence_dct)

    def item_uniques_passives_names(self, item_name):
        """
        Searches the item description and finds possible unique names.

        Empty string is caused by uniques having no name in the API (or ingame).

        :param item_name: (str)
        :returns: (list)
        """

        item_description = self.descriptions(item=item_name)[0]

        matches_lst = re.findall(r'unique passive(?: - )?(.*?):</unique>', item_description, re.I)
        return matches_lst

    def all_items_uniques_passives_names(self, print_mode=False):

        counter = collections.Counter()

        for item_name in self.usable_items_by_name_dct:
            counter += collections.Counter(self.item_uniques_passives_names(item_name=item_name))

        return _return_or_pprint_complex_obj(print_mode=print_mode, given_dct=counter)

    def _item_cost_base(self, item_name, cost_name):

        costs_dct = self.item_dct(given_name=item_name)['gold']

        try:
            return costs_dct[cost_name]
        except KeyError:
            return None

    def pprint_usable_items_by_name_dct(self):
        pp.pprint(self.usable_items_by_name_dct)

    def item_total_price(self, item_name):
        return self._item_cost_base(item_name=item_name, cost_name='total')

    def item_recipe_price(self, item_name):
        return self._item_cost_base(item_name=item_name, cost_name='base')

    def item_sell_price(self, item_name):
        return self._item_cost_base(item_name=item_name, cost_name='sell')


class ExploreRecommendedItems(_ExploreApiAbilitiesAndRecommendedItemsBase):

    def __init__(self, champion_name):
        _ExploreApiAbilitiesAndRecommendedItemsBase.__init__(self)
        self.champion_name = champion_name

    @staticmethod
    def item_name_from_id(id_num):
        return ExploreApiItems().item_name_from_id(id_num)

    def _recommended_items_data(self):
        """
        Returns a list of dicts. Each dict is for specific maps and game modes (e.g. 'ASCENSION')

        :return: (list)
        """
        return self.all_champions_data_dct[self.champion_name]['recommended']

    def _summoner_rift_items_data_dct(self):
        """
        Returns recommended items' data for 'SR' map and 'CLASSIC' mode.

        :return: (list)
        """

        all_data_lst = self._recommended_items_data()

        match = None
        matches_detected = 0
        for dct_block in all_data_lst:
            if dct_block['map'] in ('SR', '1', '11'):
                if dct_block['mode'] == 'CLASSIC':
                    matches_detected += 1
                    match = dct_block

        if matches_detected != 1:
            print('{} matches detected. Expected 1.'.format(matches_detected))
            return []
        else:
            return match['blocks']

    def type_to_item_names_map(self):
        """
        Returns items' names for each item group "type".

        :return: (dict)
        """

        dct = {}

        for data_block in self._summoner_rift_items_data_dct():
            items_type = data_block['type']
            items_block = data_block['items']

            items_names = []
            for single_item_block in items_block:
                item_id = single_item_block['id']
                items_names.append(self.item_name_from_id(id_num=item_id))

            # Ensures nothing is overwritten.
            _temp_type_name = items_type
            counter = 1
            while 1:
                if _temp_type_name in dct:
                    # (If name already exists, creates a name with a number appended to it.)
                    _temp_type_name = '{}_{}'.format(items_type, counter)
                    counter += 1
                else:
                    items_type = _temp_type_name
                    break

            dct.update({items_type: items_names})

        return dct


class ExploreApiMasteries(_ExploreBase):

    STAT_NAMES_IN_MASTERIES_MAP = {
        'cooldown reduction': {'app_name': 'cdr', 'stat_type': 'percent'},
        'armor': {'app_name': 'armor', 'stat_type': 'undefined'},
        'magic resist': {'app_name': 'mr', 'stat_type': 'undefined'},
        '% maximum health': {'app_name': 'hp', 'stat_type': 'percent'},
        'attack speed': {'app_name': 'att_speed', 'stat_type': 'percent'},
        'ability power': {'app_name': 'ap', 'stat_type': 'undefined'},
        'bonus attack damage': {'app_name': 'bonus_ad', 'stat_type': 'undefined'},
        'attack damage': {'app_name': 'ad', 'stat_type': 'undefined'},
        'attack damage per level': {'app_name': 'ad_per_lvl', 'stat_type': 'undefined'},
        'movement speed': {'app_name': 'move_speed', 'stat_type': 'undefined'},
        'lifesteal': {'app_name': 'lifesteal', 'stat_type': 'percent'},
        'spellvamp': {'app_name': 'spellvamp', 'stat_type': 'percent'},
    }

    def __init__(self):
        # Contains all masteries dict, along with version and tree.
        self.all_api_masteries_data_dct = api_masteries_database.ALL_MASTERIES
        # Dict of dicts containing each mastery's attributes.
        self.api_masteries_dcts = self.all_api_masteries_data_dct['data']
        self.masteries_dct = {}
        self.__create_masteries_dct()

        # Checks if stats names correspond to allowed app stats names.
        for i in self.STAT_NAMES_IN_MASTERIES_MAP:
            check_stat_name_validity(stat_name=self.STAT_NAMES_IN_MASTERIES_MAP[i]['app_name'])

    def mastery_name_from_id(self, id_num):
        """
        Returns name corresponding to given item id.

        :param id_num: (str) or (num)
        :return: (str) mastery name
        """

        id_num = str(id_num)

        return self.api_masteries_dcts[id_num]['name']

    def refined_mastery_name_from_id(self, id_num):
        mastery_name = self.mastery_name_from_id(id_num=id_num)

        return self.modify_api_names_to_callable_string(name=mastery_name)

    def masteries_names(self):
        """
        Returns all mastery names.

        :return: (list)
        """
        lst_returned = []

        for id_num in self.api_masteries_dcts:
            mastery_name = self.refined_mastery_name_from_id(id_num=id_num)
            lst_returned.append(mastery_name)

        return sorted(lst_returned)

    def __create_masteries_dct(self):

        for id_num in self.api_masteries_dcts:
            mastery_name = self.refined_mastery_name_from_id(id_num=id_num)
            mastery_dct = self.api_masteries_dcts[id_num]

            self.masteries_dct.update({mastery_name: mastery_dct})

    def mastery_tree(self, mastery_name):
        return self.masteries_dct[mastery_name]['masteryTree']

    def prereq_mastery(self, mastery_name):
        """
        Returns prerequisite for given mastery name if it has any.

        :param mastery_name: (str)
        :return: (str) or (None)
        """
        prereq_id = self.masteries_dct[mastery_name]['prereq']
        if prereq_id != '0':
            return self.refined_mastery_name_from_id(id_num=prereq_id)

    def max_points(self, mastery_name):
        return self.masteries_dct[mastery_name]['ranks']

    def mastery_description(self, mastery_name, print_mode=False):
        """
        Returns list of description strings for given mastery name.

        :param mastery_name: (str)
        :return: (list)
        """

        return _return_or_pprint_complex_obj(given_dct=self.masteries_dct[mastery_name]['description'], print_mode=print_mode)

    @staticmethod
    def _extracted_numbers_from_single_description_str(single_description_str):
        """
        Returns a tuple of values that are detected in given description string.

        :param single_description_str: (str) A single string of the description list.
        :return: (tuple)
        """

        single_description_str = single_description_str.lower()

        # Detects and stores values (ints and decimals along with '%').
        pattern = re.compile(r'\d+(?:\.\d+)?%?')
        matched_lst = re.findall(pattern, single_description_str)

        new_lst = []

        if matched_lst:
            for matched_str in matched_lst:
                # Converts percent values to decimals
                if '%' in matched_str:
                    matched_str = float(matched_str.strip('%')) / 100

                new_lst.append(float(matched_str))

        return tuple(new_lst)

    def stats_values_detected(self, mastery_name):
        """
        Returns a list of tuples of values that are detected in given mastery's description.

        After finding matches for each description string,
        it creates a tuple of values from first element, second, etc.

        :param mastery_name:
        :return: (list)
        """

        # List containing matches from each description string.
        lst_of_lists = []

        description_lst = self.mastery_description(mastery_name=mastery_name)

        for string in description_lst:
            single_tpl = self._extracted_numbers_from_single_description_str(single_description_str=string)
            lst_of_lists.append(single_tpl)

        # If no matches are detect ends method.
        if not any(lst_of_lists):
            return []

        # FINAL LIST
        lst_returned = []

        num_of_tuples = len(lst_of_lists[0])
        for num in range(num_of_tuples):
            # Nth lst contains n-th element from detected elements.
            lst = [i[num] for i in lst_of_lists]

            lst_returned.append(tuple(lst))

        return lst_returned

    def stats_names_detected(self, mastery_name):
        """
        Detects all stats' names in given mastery's description.

        :param mastery_name:
        :return: (list)
        """

        description_lst = self.mastery_description(mastery_name=mastery_name)
        # (first element should be enough to extract stats' names since they don't change with points)
        description_str = description_lst[0].lower()

        lst_returned = []

        for description_stat_name in self.STAT_NAMES_IN_MASTERIES_MAP:

            if description_stat_name in description_str:
                app_stat_name = self.STAT_NAMES_IN_MASTERIES_MAP[description_stat_name]['app_name']
                lst_returned.append(app_stat_name)

        return lst_returned


class ExploreChampionsBaseStats(_ExploreBase):

    @staticmethod
    def champion_base_stats(champ_name):
        """
        Returns dict containing a champion's base stats.

        :param champ_name: (str) Partial or full champion name.
        :return:
        """
        data_dct = api_champions_database.ALL_CHAMPIONS_ATTR

        name = full_or_partial_match_in_iterable(searched_name=champ_name, iterable=data_dct)
        base_stats_dct = data_dct[name]['stats']

        return base_stats_dct


# ===============================================================
#       ATTRIBUTE CREATION
# ===============================================================
# STATS DEPENDENCIES
class StatsDependencies(object):

    @staticmethod
    def _stats_dependencies(obj_name, str_champion_or_item_or_mastery):
        """
        Creates and returns dependencies list.

        :return: (set)
        """

        deps_set = set()

        print(fat_delimiter(80))
        print('STATS DEPENDENCIES, CHAMPION: {}'.format(obj_name, str_champion_or_item_or_mastery.upper()))

        while _y_n_question('\nNew dependency?'):
            if deps_set:
                print('Current dependencies:')
                for i in deps_set:
                    print(i)

            controller_stat = enumerated_question(question_str='Select CONTROLLER stat:',
                                                  choices_seq=stats.NON_PER_LVL_STAT_NAMES,
                                                  restrict_choices=True)

            affected_stat = enumerated_question(question_str='Select AFFECTED stat:',
                                                choices_seq=stats.NON_PER_LVL_STAT_NAMES,
                                                restrict_choices=True)

            deps_set.add((controller_stat, affected_stat))

        return deps_set

    def champion_stats_dependencies(self, champion_name):
        return self._stats_dependencies(obj_name=champion_name, str_champion_or_item_or_mastery='champion')

    def item_stats_dependencies(self, item_name):
        return self._stats_dependencies(obj_name=item_name, str_champion_or_item_or_mastery='item')

    def mastery_stats_dependencies(self, mastery_name):
        return self._stats_dependencies(obj_name=mastery_name, str_champion_or_item_or_mastery='mastery')


class BuffsBase(object):

    @staticmethod
    def buff_attributes():
        """
        Buff attrs include optional keys when suggested for creation, in order not to forget considering them as well.

        :return: (dict)
        """
        dct = palette.buff_dct_base_deepcopy()
        dct.update({i: palette.Placeholder() for i in palette.OPTIONAL_BUFF_KEYS})

        return dct

    USUAL_BUFF_ATTR_VALUES = dict(
        target_type=('player', 'enemy'),
        max_stacks=(1,),
        duration=(1, 2, 3, 4, 5, 'permanent'),
        prohibit_cd_start=(None, ),
        buff_source=palette.ALL_POSSIBLE_ABILITIES_SHORTCUTS,
        dot=(False, True),
        max_targets=(1, 2, 3, 4, 5, 'infinite'),
        usual_max_targets=(1, 2, 3, 4, 5),
        shield=(False, True)
    )

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
                                         'armor penetration': 'armor_penetration',
                                         'bonus attack damage': 'ad'}

    NTH_TUPLE = ('second', 'third', 'forth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth')

    def _ask_amount_of_buffs(self, modified_dct, obj_name):
        """
        Asks dev for amount of buffs for given ability or item, and creates necessary dicts based on answer.

        Args:
            obj_name: (str) ability or item name

        Returns:
            (None)
        """

        start_msg = '\n'
        start_msg += delimiter(num_of_lines=10)
        start_msg += '\nHow many buffs in %s?' % obj_name.upper()

        # Repeat until valid answer is given.
        while True:
            num_of_buffs = input(start_msg + '\n')

            _check_loop_exit(key=num_of_buffs)

            try:
                num_iter = range(int(num_of_buffs))

                for _ in num_iter:
                    new_buff_name = _new_automatic_attr_dct_name(existing_names=modified_dct, second_synthetic='buff',
                                                                 first_synthetic=obj_name)
                    modified_dct.update({new_buff_name: self.buff_attributes()})

                end_msg = '\n%s buffs selected.' % num_of_buffs
                print(end_msg)
                break

            except ValueError:
                print_invalid_answer()
                pass

    @staticmethod
    def _change_buff_names(modified_dct):
        """
        Asks if buff name change is needed,
        and if so goes through every buff name.

        Returns:
            (None)
        """

        # Does nothing if no buffs exist.
        if modified_dct:

            msg = delimiter(40)
            msg += '\nChange buff names?'

            change_buffs_answer = _y_n_question(question_str=msg)

            if change_buffs_answer:
                for previous_buff_name in sorted(modified_dct):
                    new_name_msg = delimiter(10)
                    new_name_msg += '\nInsert new name for: %s. (press enter to skip)\n' % previous_buff_name

                    new_name = input(new_name_msg)

                    if new_name == '':
                        print('\nNot changed.')
                    # If new name is selected, creates new buff with previous value,
                    # .. then removes previous buff.
                    else:
                        modified_dct.update({new_name: modified_dct[previous_buff_name]})
                        del modified_dct[previous_buff_name]

    def _ask_amount_of_buffs_and_change_names(self, modified_dct, obj_name):
        self._ask_amount_of_buffs(modified_dct=modified_dct, obj_name=obj_name)
        self._change_buff_names(modified_dct=modified_dct)


class StatsCreation(object):

    @staticmethod
    def _suggest_stats(stats_dct, stat_name, suggested_values_lst, suggest_mods_func):
        chosen_types_lst = []
        suggest_lst_of_attr_values(suggested_values_lst=('additive', 'percent', 'multiplicative'),
                                   modified_lst=chosen_types_lst)

        for type_name in chosen_types_lst:
            stats_dct[stat_name].update({type_name: {}})

            # (dict form effects for parameter below)
            eff_values_dct = {'stat_values': suggested_values_lst}

            suggest_attr_values(suggested_values_dct=eff_values_dct,
                                modified_dct=stats_dct[stat_name][type_name],
                                extra_start_msg='AFFECTED STAT: {}'.format(stat_name))

            # STAT MODS
            suggest_mods_func(stats_dct=stats_dct, affected_stat=stat_name)

    def _suggest_single_affected_stats_and_its_attrs(self, buff_name, stat_name, stats_dct, suggest_mods_func,
                                                     suggested_values_lst):
        """
        Suggests stats that may be affected by a buff,
        and each stat's mods.

        Returns:
            (None)
        """
        msg = delimiter(40)
        msg += '\nDoes %s affect %s?\n' % (buff_name, stat_name.upper())

        while 1:
            buff_affects_stat = input(msg)
            if buff_affects_stat == 'y':

                stats_dct.update({stat_name: {}})

                self._suggest_stats(stats_dct=stats_dct, stat_name=stat_name,
                                    suggest_mods_func=suggest_mods_func,
                                    suggested_values_lst=suggested_values_lst)

                break
            elif buff_affects_stat == 'n':
                break
            else:
                print_invalid_answer()


class GenAttrsBase(object):
    COST_CATEGORIES = ('normal', 'per_hit', 'per_second', 'per_hit_or_single_tar_spell')

    USUAL_VALUES_GEN_ATTR = dict(
        cast_time=(0.25, 0.5, 0),
        travel_time=(0, 0.25, 0.5),
        move_while_casting=(False, True),
        dashed_distance=(None,),
        channel_time=(None,),
        resets_aa=(False, True),
        toggled=(False, True),
        independent_cast=(False, True),
        base_cd=(),
        range=()
    )

    @staticmethod
    def general_attributes():
        return palette.GENERAL_ATTRIBUTES


class DmgsBase(object):

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
        """
        Dmg attrs include optional keys when suggested for creation, in order not to forget considering them as well.

        :return: (dict)
        """
        dct = palette.dmg_dct_base_deepcopy()
        dct.update({i: palette.Placeholder() for i in palette.OPTIONAL_DMG_KEYS})

        return dct

    def usual_values_dmg_attrs(self):

        return dict(
            target_type=('enemy', 'player'),
            dmg_category=sorted(self.AVAILABLE_DMG_CATEGORIES),
            resource_type=('hp', 'mp', 'energy'),
            dmg_source=palette.ALL_POSSIBLE_ABILITIES_SHORTCUTS,
            life_conversion_type=('spellvamp', None, 'lifesteal'),
            radius=(None, ),
            dot=(False, True),
            max_targets=(1, 2, 3, 4, 5, 'infinite'),
            usual_max_targets=(1, 2, 3, 4, 5),
            delay=(None,),
            crit_type=palette.CRIT_TYPES,
            heal_for_dmg_amount=(False, True)
        )

    @staticmethod
    def mod_stat_name_map():
        """
        Returns dict mapping modifying stat name in API champion ability dict, with APP stat name.

        Checks if APP stat names suggested match existing stat names.

        :return: (dict)
        """

        dct = dict(attackdamage='ad',
                   bonusattackdamage='bonus_ad',
                   spelldamage='ap',
                   armor='armor',
                   bonusarmor='bonus_armor',
                   bonushealth='bonus_hp',
                   bonusspellblock='bonus_mr',
                   health='hp',
                   mana='mp', )

        if set(dct.values()) - ALLOWED_STATS_NAMES:
            raise palette.UnexpectedValueError('Some APP stat names suggested here are not registered.')

        return dct

    @staticmethod
    def dmg_mod_contents():

        return dict(
            player={},      # (e.g. 'player': {'stat1': value,} )
            enemy={}
        )

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

    def _create_shield_or_dmg_mods(self, mods_dct):

        if _y_n_question(question_str='Dmg has mods?'):
            mods_dct.update(self.dmg_mod_contents())

            # OWNER
            for owner_type in mods_dct:

                # NAMES
                mods_names = []
                suggest_lst_of_attr_values(suggested_values_lst=stats.NON_PER_LVL_STAT_NAMES, modified_lst=mods_names,
                                           extra_start_msg='Mods belonging to {}\n'.format(owner_type.upper()))

                if mods_names:
                    for mod_name in mods_names:
                        mods_dct[owner_type].update({mod_name: {}})

                        # APPLICATION TYPE
                        for mod_type in ('additive', 'multiplicative'):
                            if _y_n_question("{}'s mod: {}, is {}".format(owner_type, mod_name.upper(), mod_type.upper())):

                                # VALUE
                                mod_value = restricted_input('{} mod value?'.format(mod_name.upper()), input_type='num')

                                mods_dct[owner_type][mod_name].update({mod_type: mod_value})

        pp.pprint(mods_dct)

    def _create_shield(self, shield_dct, description_to_print):
        if shield_dct:
            shield_dct = {}

            # Type
            shield_type = enumerated_question(question_str='Shield type?',
                                              choices_seq=palette.SHIELD_TYPES,
                                              restrict_choices=True)

            shield_dct.update({'shield_type': shield_type})

            # Values
            shield_val = restricted_input('Shield value?', input_type='num', characteristic='non_negative')
            shield_dct.update({'shield_values': shield_val})

            # Mods
            shield_dct.update({'shield_mods': {}})
            shield_mods_dct = shield_dct['shield_mods']

            pp.pprint(description_to_print)
            self._create_shield_or_dmg_mods(mods_dct=shield_mods_dct)


class AbilitiesAttributesBase(GenAttrsBase):

    def __init__(self, ability_name, champion_name):
        self.champion_name = champion_name
        self.ability_name = ability_name
        self.api_spell_dct = api_champions_database.ALL_CHAMPIONS_ATTR[champion_name]['spells'][
            spell_num(spell_name=ability_name)]
        self.api_innate_dct = api_champions_database.ALL_CHAMPIONS_ATTR[champion_name]['passive']
        self.sanitized_tooltip = self.api_spell_dct['sanitizedTooltip']
        # (removes None from API effect list)
        self.ability_effects_lst = copy.copy(self.api_spell_dct['effect'])[1:]
        # (some spells don't contain 'vars')
        try:
            self.ability_vars_dct = self.api_spell_dct['vars']
        except KeyError:
            self.ability_vars_dct = []
        self.mod_vals_lst = [var_dct['coeff'] for var_dct in self.ability_vars_dct]

    def _champion_and_ability_msg(self):

        return '\nCHAMPION: %s, ABILITY: %s' % (self.champion_name, self.ability_name.upper())

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


class ItemAndMasteriesBase(object):

    @staticmethod
    def pprint_item_or_mastery_description(obj_name, obj_description_str, str_item_or_mastery):
        """
        Pretty prints mastery or item description.

        :param obj_name: (str) Item or mastery name.
        :param obj_description_str:
        :param str_item_or_mastery: 'item' or 'mastery'
        :return: (None)
        """
        print('\n:{} {}\n'.format(str_item_or_mastery.upper(), obj_name))
        pp.pprint(obj_description_str)

    @staticmethod
    def item_or_buff_attributes():
        return {k: v for k, v in BuffsBase.buff_attributes().items() if k != 'prohibit_cd_start'}

    @staticmethod
    def _suggest_buff_affected_stats_of_item_or_mastery(buff_name, str_item_or_mastery, pprint_description_func,
                                                        mastery_or_item_name, buffs_dct, available_stat_names,
                                                        lst_of_values_tuples):
        """
        Modifies item buffs dict for given buff,
        by inserting buff affected stats suggested by dev.

        :param buff_name: (str)
        :param mastery_or_item_name: (str)
        :param buffs_dct: (dict) Dict of all masteries' or all items' buffs.
        :return: (None)
        """

        available_stat_names = available_stat_names + ['']

        print(delimiter(40))
        pprint_description_func()
        # Asks if buff affects stats.
        if _y_n_question(question_str='Buff {} affects stats?'.format(buff_name.upper())) is True:

            # Resets affected_stats dict.
            buffs_dct[buff_name]['stats'] = {}

            while 1:
                print(delimiter(40))
                pprint_description_func()

                # STAT NAME
                stat_name_msg = '{}: {}, '.format(str_item_or_mastery.upper(), mastery_or_item_name)
                stat_name_msg += 'BUFF: {}.'.format(buff_name)
                stat_name_msg += '\nStat name? ("1" to exit)\n'

                stat_name = enumerated_question(question_str=stat_name_msg,
                                                # (enter added as a choice by '')
                                                choices_seq=available_stat_names,
                                                restrict_choices=True)

                if stat_name == '':
                    break

                # STAT TYPE
                stat_type_msg = '{}: {}, '.format(str_item_or_mastery.upper(), mastery_or_item_name)
                stat_type_msg += 'BUFF: {}, '.format(buff_name)
                stat_type_msg += 'STAT NAME: {}.'.format(stat_name)
                stat_type_msg += '\nStat type?\n'

                stat_type = enumerated_question(question_str=stat_type_msg,
                                                choices_seq=STAT_TYPES,
                                                restrict_choices=True)

                # STAT VALUE
                stat_val_msg = '{}: {}, '.format(str_item_or_mastery.upper(), mastery_or_item_name)
                stat_val_msg += 'BUFF: {}, '.format(buff_name)
                stat_val_msg += 'TYPE: {}, '.format(stat_type)
                stat_val_msg += 'STAT NAME: {}.'.format(stat_name)
                stat_val_msg += '\nStat value?\n'

                stat_vals = enumerated_question(question_str=stat_val_msg, choices_seq=lst_of_values_tuples)

                # STATS DICT INSERTION
                buff_stats_dct = buffs_dct[buff_name]['stats']

                if stat_name not in buff_stats_dct:
                    buff_stats_dct.update({stat_name: {}})

                if stat_type not in buff_stats_dct[stat_name]:
                    buff_stats_dct[stat_name].update(
                        {stat_type: {'stat_mods': {}, 'stat_values': None}})

                buff_stats_dct[stat_name][stat_type]['stat_values'] = stat_vals

                # MODS
                while 1:

                    # MOD NAME
                    mod_name_msg = '{}: {}, '.format(str_item_or_mastery.upper(), mastery_or_item_name)
                    mod_name_msg += 'BUFF: {}, '.format(buff_name)
                    mod_name_msg += 'STAT NAME: {}, '.format(stat_name)
                    mod_name_msg += 'TYPE: {}.'.format(stat_type)
                    mod_name_msg += '\nMod names?\n'

                    mod_name = enumerated_question(question_str=mod_name_msg,
                                                   # (enter added as a choice by '')
                                                   choices_seq=available_stat_names,
                                                   restrict_choices=True)

                    if mod_name == '':
                        break

                    buff_stats_dct[stat_name][stat_type]['stat_mods'].update({mod_name: None})

                    # MOD VALUE
                    mod_val_msg = '{}: {}, '.format(str_item_or_mastery.upper(), mastery_or_item_name)
                    mod_val_msg += 'BUFF: {}, '.format(buff_name)
                    mod_val_msg += 'STAT NAME: {}, '.format(stat_name)
                    mod_val_msg += 'TYPE: {}, '.format(stat_type)
                    mod_val_msg += 'MOD NAME: {}.'.format(mod_name)
                    mod_val_msg += '\nMod values? \n'
                    mod_vals = enumerated_question(question_str=mod_val_msg, choices_seq=lst_of_values_tuples)

                    buff_stats_dct[stat_name][stat_type]['stat_mods'][mod_name] = mod_vals

        pp.pprint(buffs_dct[buff_name]['stats'])

    @staticmethod
    def usual_item_or_mastery_buff_attrs_values():
        # (buff_source of item buffs is always the item)
        disallowed = ('prohibit_cd_start', 'buff_source')
        return {k: v for k, v in BuffsBase().USUAL_BUFF_ATTR_VALUES.items() if k not in disallowed}


class _ConditionalsBase(metaclass=abc.ABCMeta):

    def __init__(self):
        self.conditions_dct = None

    @abc.abstractproperty
    def trigger_setup_dct(self):
        pass

    @abc.abstractproperty
    def effect_setup_dct(self):
        pass

    @abc.abstractproperty
    def attrs_with_lst_val(self):
        pass

    def _create_and_insert_new_trigger(self, con_name):
        """
        Creates new trigger, and inserts it in given condition's dict.

        Returns:
            (None)
        """

        # Creates trig name.
        trig_name = _auto_new_name_or_ask_name(first_synthetic='trigger',
                                               existing_names=self.conditions_dct[con_name]['triggers'])

        # Inserts trig name.
        self.conditions_dct[con_name]['triggers'].update({trig_name: {}})

        # Inserts trig types.
        trig_type = enumerated_question(question_str='Trigger TYPE?', choices_seq=self.trigger_setup_dct,
                                        restrict_choices=True)

        self.conditions_dct[con_name]['triggers'][trig_name].update({'trigger_type': trig_type})

        # Inserts trig contents.
        suggest_attr_values(suggested_values_dct=self.trigger_setup_dct[trig_type],
                            modified_dct=self.conditions_dct[con_name]['triggers'][trig_name],
                            restrict_choices=True,
                            attrs_with_lst_val=self.attrs_with_lst_val)

        print(delimiter(40))
        print('\nTRIGGER: {}'.format(trig_name))
        pp.pprint(self.conditions_dct[con_name]['triggers'][trig_name])

    def _create_and_insert_new_effect_base(self, con_name):
        """
        Creates new effect, and inserts it in given condition's dict.

        Returns:
            (str) Mostly not used; needed in only few classes.
        """

        # Creates effect name.
        eff_name = _auto_new_name_or_ask_name(first_synthetic='effect',
                                              existing_names=self.conditions_dct[con_name]['effects'],)

        # Inserts effect name.
        self.conditions_dct[con_name]['effects'].update({eff_name: {}})

        # Inserts effect types.
        eff_type = enumerated_question(question_str='Effect TYPE?', choices_seq=self.effect_setup_dct,
                                       restrict_choices=True)

        self.conditions_dct[con_name]['effects'][eff_name].update({'effect_type': eff_type})

        # Inserts effect contents.
        suggest_attr_values(suggested_values_dct=self.effect_setup_dct[eff_type],
                            modified_dct=self.conditions_dct[con_name]['effects'][eff_name],
                            restrict_choices=True,
                            attrs_with_lst_val=self.attrs_with_lst_val)

        print(delimiter(40))
        print('\nEFFECT: {}'.format(eff_name))
        pp.pprint(self.conditions_dct[con_name]['effects'][eff_name])

        return eff_name

    def __add_triggers_or_effects(self, con_name, trig_or_eff_creation_func, trig_or_eff_str):
        """
        Adds all triggers or effects for given condition name.

        :param con_name:
        :param trig_or_eff_creation_func: (function)
        :param trig_or_eff_str: (str) 'trigger', 'effect'
        :return:
        """

        # (e.g. 'effect'->'effects')
        plural_str = trig_or_eff_str + 's'

        self.conditions_dct[con_name].update({plural_str: {}})

        print(fat_delimiter(20))
        print('\nCONDITION: {}'.format(con_name))

        while True:
            end_eff_answer = _y_n_question(question_str='\nAdd {}?'.format(plural_str))

            if not end_eff_answer:
                return
            else:
                trig_or_eff_creation_func(con_name=con_name)

        print(fat_delimiter(40))
        print('\nCONDITION: {}'.format(con_name))
        pp.pprint(self.conditions_dct[con_name][plural_str])

    @repeat_cluster_decorator(cluster_name='CONDITION TRIGGERS')
    def _add_triggers(self, con_name):
        return self.__add_triggers_or_effects(con_name=con_name,
                                              trig_or_eff_creation_func=self._create_and_insert_new_trigger,
                                              trig_or_eff_str='trigger')

    @repeat_cluster_decorator(cluster_name='CONDITION EFFECTS')
    def _add_effects(self, con_name):
        return self.__add_triggers_or_effects(con_name=con_name,
                                              trig_or_eff_creation_func=self._create_and_insert_new_effect_base,
                                              trig_or_eff_str='effect')

    def _create_single_condition(self, con_name):

        # TRIGGERS
        self._add_effects(con_name=con_name)
        # EFFECTS
        self._add_triggers(con_name=con_name)

    @outer_loop_exit_handler
    @repeat_cluster_decorator(cluster_name='ALL CONDITIONS')
    def run_conditions_creation(self, extra_msg=''):
        """

        :return: (None)
        """
        self.conditions_dct = {}
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
                new_con_name = _auto_new_name_or_ask_name(first_synthetic='conditional',
                                                          existing_names=self.conditions_dct)
                self.conditions_dct.update({new_con_name: {}})

                self._create_single_condition(con_name=new_con_name)

        print(fat_delimiter(40))
        print('\nCONDITIONALS')
        if extra_msg:
            print(extra_msg)
        pp.pprint(self.conditions_dct)


# ---------------------------------------------------------------
# ABILITIES

class GeneralAbilityAttributes(AbilitiesAttributesBase):

    def __init__(self, ability_name, champion_name):
        AbilitiesAttributesBase.__init__(self,
                                         ability_name=ability_name,
                                         champion_name=champion_name)

        self.general_attr_dct = self.general_attributes()

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

        suggest_attr_values(suggested_values_dct={'cost_category': self.COST_CATEGORIES},
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

        suggest_attr_values(suggested_values_dct=self.USUAL_VALUES_GEN_ATTR,
                            modified_dct=self.general_attr_dct,
                            extra_start_msg=extra_msg)

    def _suggest_cd_reductions(self):
        """
        Suggests ability names and the value their cd is reduced by on this ability's cast.

        :return: (None)
        """
        reduced_ability_names = []
        suggest_lst_of_attr_values(modified_lst=reduced_ability_names,
                                   suggested_values_lst=palette.ALL_POSSIBLE_SPELL_SHORTCUTS,
                                   extra_start_msg='\nOn cast modifies cd of following abilities:',
                                   sort_suggested_lst=False)

        # (removes placeholders to prepare for data insertion)
        self.general_attr_dct['cds_modified'] = {}
        # For each reduced ability, creates dict key and suggests values.
        for ability_name in reduced_ability_names:

            suggest_attr_values(suggested_values_dct={ability_name: (1, )},
                                modified_dct=self.general_attr_dct['cds_modified'])

    @repeat_cluster_decorator(cluster_name='GENERAL ATTRIBUTES')
    def run_gen_attr_creation(self):
        """
        Inserts automatically some attributes and asks the dev for the rest.

        Returns:
            (None)
        """

        # Reset dict contents
        self.general_attr_dct = {}

        msg = fat_delimiter(40)
        msg += "\nABILITY'S GENERAL ATTRIBUTES:" + self._champion_and_ability_msg() + '\n'

        print(msg)

        suggest_attr_values(suggested_values_dct=dict(castable=(True, False)),
                            modified_dct=self.general_attr_dct, restrict_choices=True)

        if self.general_attr_dct['castable'] is True:
            self.general_attr_dct.update({k: v for k, v in self.general_attributes().items()})

            self.auto_fill_attributes()
            self.suggest_gen_attr_values()
            self._suggest_cd_reductions()

        print(msg)
        pp.pprint(self.general_attr_dct)


class DmgAbilityAttributes(AbilitiesAttributesBase, DmgsBase):
    """
    Each instance of this class is used for creation of all dmgs of a single ability.

    An ability can contain 0 or more "dmg attributes" in its _STATS.

    (Each "dmg" must have a single responsibility.)
    """

    def __init__(self, ability_name, champion_name):
        AbilitiesAttributesBase.__init__(self,
                                         ability_name=ability_name,
                                         champion_name=champion_name)

        self.dmgs_dct = {}

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
            (dict)
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

        curr_dmg_dct.update({'mods': self.dmg_mod_contents()})

        # Dmg mods in api 'effects'
        mod_val_abbrev_lst = re.findall(r'\+\{\{\s(\w\d{1,2})\s\}\}', tooltip_fragment)
        for mod_abbrev in mod_val_abbrev_lst:
            # Mod values and stats
            mod_stat_and_val_dct = self.mod_value_and_stat(mod_shortcut=mod_abbrev)
            mod_name, mod_val = tuple(mod_stat_and_val_dct.items())[0]

            # ASKS DEV
            mod_and_val_as_str = '\nDmg mod: %s, value: %s' % (mod_name, mod_val)
            # (creates appropriate arg form for method below)
            mod_attr_template = {'mod_stat_owner': ('player', 'enemy')}
            temp_mod_dct = {}
            suggest_attr_values(suggested_values_dct=mod_attr_template, modified_dct=temp_mod_dct,
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

            suggest_attr_values(suggested_values_dct=self.usual_values_dmg_attrs(),
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

        print('\n' + delimiter(num_of_lines=10))
        extra_dmg = _y_n_question('\nInsert extra dmg?\n')

        if extra_dmg:
            new_dmg_name = _new_automatic_attr_dct_name(existing_names=self.dmgs_dct, second_synthetic='dmg',
                                                        first_synthetic=self.ability_name)
            self.dmgs_dct.update({new_dmg_name: self.dmg_attributes()})
            self._suggest_dmg_values(dmg_name=new_dmg_name)
            suggest_attr_values(suggested_values_dct=self.usual_values_dmg_attrs(),
                                modified_dct=self.dmgs_dct[new_dmg_name],
                                extra_start_msg='\nManually inserted dmg.')
            self.modify_dmg_names()

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

    @repeat_cluster_decorator(cluster_name='DMG ATTRIBUTES')
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


@inner_loop_exit_handler
def suggest_affected_stats_attributes(obj_name, modified_stats_dct, possible_stat_values_lst,
                                      possible_mod_values_lst, question_msg=''):
    """
    Suggests stats that the buff modifies and
    mods of the stats (if any of the stats are scaling).

    :return: (None)
    """

    msg = '\nBuff: {}\n'.format(obj_name)
    if question_msg:
        msg += question_msg
    else:
        msg += 'Does it modify stats'

    if _y_n_question(msg):
        modified_stats_names = []
        suggest_lst_of_attr_values(suggested_values_lst=stats.NON_PER_LVL_STAT_NAMES,
                                   modified_lst=modified_stats_names)

        # Stat name
        for stat_modified in modified_stats_names:
            modified_stats_dct.update({stat_modified: {}})

            buff_name_stat_name_msg = '\nBuff: {}, STAT: {}'.format(obj_name, stat_modified)

            # Stat type
            for stat_type in STAT_TYPES:
                if _y_n_question(buff_name_stat_name_msg+'\nIs there a {} bonus to the stat?'.format(stat_type.upper())):
                    modified_stats_dct[stat_modified].update(
                        {stat_type: {'stat_mods': {}, }})
                else:
                    continue

                # Stat values
                stat_vals = enumerated_question(question_str=buff_name_stat_name_msg+'\nStat values?',
                                                choices_seq=possible_stat_values_lst)
                modified_stats_dct[stat_modified][stat_type].update(
                    {'stat_values': stat_vals})

                # MODS
                modifier_name_question = buff_name_stat_name_msg + '\nDoes the stat have modifiers?'
                if _y_n_question(modifier_name_question):

                    stat_modifiers_lst = []
                    suggest_lst_of_attr_values(suggested_values_lst=stats.NON_PER_LVL_STAT_NAMES,
                                               modified_lst=stat_modifiers_lst)

                    for modifier in stat_modifiers_lst:

                        # Suggests mod values.
                        modifier_vals_question = '\nBUFF: {}, STAT: {}, MOD: {}'.format(obj_name, stat_modified, modifier)
                        modifier_vals_question += '\nChoose mod values.'

                        # (must be a tuple, even if only a single value is selected)
                        mod_vals = enumerated_lst_creation(suggested_values_lst=possible_mod_values_lst,
                                                           extra_start_msg=modifier_vals_question,
                                                           sort_suggested_lst=False)

                        mod_vals = tuple(mod_vals)

                        # Inserts mod values.
                        modified_stats_dct[stat_modified][stat_type]['stat_mods'].update(
                            {modifier: mod_vals})

    else:
        print("\nDoesn't modify stats.")
        modified_stats_dct.clear()


class BuffAbilityAttributes(AbilitiesAttributesBase, BuffsBase, StatsCreation, DmgsBase):
    """
    Each instance of this class is used for a single ability.

    An ability can contain 0 or more 'buff' attributes in its _STATS.
    """

    def __init__(self, ability_name, champion_name):
        AbilitiesAttributesBase.__init__(self,
                                         ability_name=ability_name,
                                         champion_name=champion_name)

        self.buffs_dct = {}

    # ---------------------------------------------------------------
    # Stats
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

    # ---------------------------------------------------------------

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
                        result_str = self.ability_effects_lst[int(effect_abbr[0])]
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

        self._ask_amount_of_buffs_and_change_names(modified_dct=self.buffs_dct, obj_name=self.ability_name)
        print(delimiter(40))

        for buff_name in sorted(self.buffs_dct):
            print(delimiter(10))
            self.buffs_dct[buff_name]['stats'] = {}

            stats_dct = self.buffs_dct[buff_name]['stats']
            suggest_affected_stats_attributes(obj_name=buff_name,
                                              modified_stats_dct=stats_dct,
                                              possible_stat_values_lst=self.ability_effects_lst,
                                              possible_mod_values_lst=self.mod_vals_lst)

            usual_attrs_msg = 'USUAL BUFF ATTRIBUTES\n'
            usual_attrs_msg += '\nBUFF: %s' % buff_name
            suggest_attr_values(suggested_values_dct=self.USUAL_BUFF_ATTR_VALUES,
                                modified_dct=self.buffs_dct[buff_name],
                                extra_start_msg=usual_attrs_msg)

            shield_dct = self.buffs_dct[buff_name]['shield']
            if shield_dct:
                self._create_shield(shield_dct=shield_dct, description_to_print=self.sanitized_tooltip)

    @repeat_cluster_decorator(cluster_name='BUFFS')
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

    """
    'ABILITIES_ATTRIBUTES' is the name of the dict containing all ability related general attributes, buffs and dmgs.
    """

    def __init__(self, champion_name):
        self.champion_name = champion_name
        self.initial_abilities_attrs = {shortcut: self.single_spell_attrs() for shortcut in palette.ABILITY_SHORTCUTS}
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
        if _y_n_question(question_str='{} contains dmgs?'.format(spell_name.upper())):
            self._dmg_attrs(attrs_dct=attrs_dct, spell_name=spell_name)

        # BUFF ATTRIBUTES
        if _y_n_question(question_str='{} contains buffs?'.format(spell_name.upper())):
            self._buff_attrs(attrs_dct=attrs_dct, spell_name=spell_name)

        print(fat_delimiter(40))
        pp.pprint(attrs_dct)

        return attrs_dct

    @outer_loop_exit_handler
    def _create_or_redo_spells_attrs(self):
        """
        Creates attributes of every spell.
        Allows redoing creation for each spell, if needed.

        Returns:
            (None)
        """

        for spell_name in palette.SPELL_SHORTCUTS:

            # Creates spell att
            self.initial_abilities_attrs[spell_name] = self._single_spell_attrs(spell_name=spell_name)

            # Redo spell attributes if needed.
            redo_all_attr_of_spell = _y_n_question(question_str='\nRedo all attributes of {}?'.format(spell_name.upper()))

            if redo_all_attr_of_spell:
                # (not breaking after this allows redoing multiple times)
                self.initial_abilities_attrs[spell_name] = self._single_spell_attrs(spell_name=spell_name)

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
        for ability_name in palette.ABILITY_SHORTCUTS:
            self.final_abilities_attrs['general_attributes'].update(
                {ability_name: self.initial_abilities_attrs[ability_name]['general']})

        # DMGS AND BUFFS
        for shortcut in palette.ABILITY_SHORTCUTS:
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

    @repeat_cluster_decorator(cluster_name='SPELL ATTRS')
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
        pass


class EffectsBase(object):

    @staticmethod
    @inner_loop_exit_handler
    def _create_single_obj_effects_dct(obj_name, champ_or_item, univ_msg, modified_eff_dct, champ_name=None):
        """
        Creates effects dict of a single spell or item.

        Dev is asked about possible dmg and buff names,
        and cd modifiers.

        :param obj_name: (str) spell or item name
        :param champ_or_item: (str) 'champion' or 'item'
        :param univ_msg: (str)
        :param modified_eff_dct: (dict) Exact dict that gets all effects for given object.
        :return: (None)
        """

        if not _y_n_question('Does {} have any effects?'.format(obj_name)):
            modified_eff_dct.clear()
            return

        print(fat_delimiter(100))
        print('\nEFFECTS DICT')

        app_types_tpl = ('passives', 'actives')

        for application_type in app_types_tpl:
            # DMGS

            dmg_msg = '%s\n' % univ_msg
            dmg_msg += '%s -- DMG APPLIED\n' % application_type
            dmg_msg = dmg_msg.upper()

            if champ_or_item == 'champion':
                dmg_names = Fetch().dmgs_names(obj_name=champ_name, champ_or_item=champ_or_item)
                buffs_names = Fetch().buffs_names(obj_name=champ_name, champ_or_item=champ_or_item)
            else:
                dmg_names = Fetch().dmgs_names(obj_name=obj_name, champ_or_item=champ_or_item)
                buffs_names = Fetch().buffs_names(obj_name=obj_name, champ_or_item=champ_or_item)

            suggest_lst_of_attr_values(suggested_values_lst=dmg_names,
                                       modified_lst=modified_eff_dct[application_type]['dmg'],
                                       extra_start_msg=dmg_msg)

            pp.pprint(modified_eff_dct[application_type]['dmg'])

            # BUFFS APPLICATION
            buffs_applied_msg = '%s\n' % univ_msg
            buffs_applied_msg += '%s -- BUFFS APPLIED' % application_type
            buffs_applied_msg = buffs_applied_msg.upper()

            suggest_lst_of_attr_values(suggested_values_lst=buffs_names,
                                       modified_lst=modified_eff_dct[application_type]['buffs'],
                                       extra_start_msg=buffs_applied_msg)

            pp.pprint(modified_eff_dct[application_type]['buffs'])

            # BUFF REMOVAL
            buff_removal_msg = '%s\n' % univ_msg
            buff_removal_msg += '%s -- BUFFS REMOVED' % application_type
            buff_removal_msg = buff_removal_msg.upper()

            suggest_lst_of_attr_values(suggested_values_lst=buffs_names,
                                       modified_lst=modified_eff_dct[application_type]['remove_buff'],
                                       extra_start_msg=buff_removal_msg)

            pp.pprint(modified_eff_dct[application_type]['remove_buff'])

        # CD MODIFICATION
        lst_of_modified = []
        cd_mod_msg = '\nCDs MODIFIED ON CAST'
        suggest_lst_of_attr_values(suggested_values_lst=palette.SPELL_SHORTCUTS,
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

            modified_eff_dct['player']['actives']['cds_modified'].update({cd_modified_name: mod_value})

        pp.pprint(modified_eff_dct)


class AbilitiesEffects(EffectsBase):

    def __init__(self, champion_name):
        self.champion_name = champion_name
        self.spells_effects = None

    @staticmethod
    def _spells_effects_dct():

        dct = {}

        for spell_name in palette.SPELL_SHORTCUTS:
            dct.update({spell_name: palette.spell_effects()})

        return dct

    def _single_spell_effects_creation(self, spell_name):

        msg = 'Champion: {}, Ability: {}'.format(self.champion_name, spell_name)
        # Creates a spell's effects.
        self._create_single_obj_effects_dct(obj_name=spell_name, champ_or_item='champion', univ_msg=msg,
                                            modified_eff_dct=self.spells_effects[spell_name],
                                            champ_name=self.champion_name)

    @outer_loop_exit_handler
    @repeat_cluster_decorator(cluster_name='SPELL EFFECTS')
    def run_spells_effects_creation(self):
        """
        Creates effects of every spell.
        Allows redoing creation for each spell, if needed.

        Note: has to follow all buff and dmg creation so that all names are available.

        Returns:
            (None)
        """

        # Resets dict
        self.spells_effects = self._spells_effects_dct()

        for spell_name in palette.SPELL_SHORTCUTS:
            self._single_spell_effects_creation(spell_name=spell_name)


class _ItemsAndAbilitiesConditionalsBase(_ConditionalsBase):

    def __init__(self, obj_name, obj_type, attributes_dct, effects_dct):
        _ConditionalsBase.__init__(self)
        self.obj_name = obj_name
        # 'champion' or 'item'
        self.obj_type = obj_type
        self.attributes_dct = attributes_dct
        self.abilities_effects_dct = effects_dct
        self.available_dmg_attr_names = DmgsBase.dmg_attributes()
        self.available_buff_attr_names = BuffsBase.buff_attributes()

    @property
    def attrs_with_lst_val(self):
        return []

    TARGET_TYPES = palette.TARGET_TYPES
    # (Used to determine what to insert next.)
    FORMULA_TYPE = ('constant_value', 'x_function')
    COMPARISON_OPERATOR_STRINGS = palette.COMPARISON_OPERATOR_STRINGS
    NON_PER_LVL_STAT_NAMES = stats.NON_PER_LVL_STAT_NAMES
    SPECIAL_ATTRS_NAMES = ('stats', 'on_hit')

    def available_buff_names(self):
        return sorted(self.attributes_dct['buffs'])

    def available_dmg_names(self):
        return sorted(self.attributes_dct['dmgs'])

    def available_attr_names(self):
        return sorted(i for i in GenAttrsBase.general_attributes() if i not in self.SPECIAL_ATTRS_NAMES)

    @property
    def trigger_setup_dct(self,):

        return dict(
            buff=dict(
                buff_name=self.available_buff_names(),
                owner_type=self.TARGET_TYPES,
                operator=self.COMPARISON_OPERATOR_STRINGS,
                stacks=[str(i) for i in range(1, 10)],
            ),
            stat=dict(
                stat_name=self.NON_PER_LVL_STAT_NAMES,
                owner_type=self.TARGET_TYPES,
                operator=self.COMPARISON_OPERATOR_STRINGS,
                value=()
            ),
            spell_lvl=dict(
                spell_name=palette.ALL_POSSIBLE_SPELL_SHORTCUTS,
                operator=self.COMPARISON_OPERATOR_STRINGS,
                lvl=ALLOWED_ABILITY_LVLS
            ),
            on_cd=dict(
                spell_name=palette.ALL_POSSIBLE_SPELL_SHORTCUTS
            ))

    @property
    def effect_setup_dct(self):

        dct = dict(
            ability_effect=dict(
                obj_name=palette.ALL_POSSIBLE_SPELL_SHORTCUTS,
                # Contains spell effect categories
                lst_category=palette.spell_effects()['player']['actives'],
                mod_operation=('append', 'remove'),
            ),

            ability_attr=dict(
                obj_name=palette.ALL_POSSIBLE_SPELL_SHORTCUTS,
                attr_name=self.available_attr_names,
                mod_operation=('multiply', 'add', 'remove'),
                formula_type=self.FORMULA_TYPE,
            ),

            buff_attr=dict(
                obj_name=self.available_buff_names(),
                buff_attr_name=self.available_buff_attr_names,
                mod_operation=('multiply', 'add', 'remove'),
                formula_type=self.FORMULA_TYPE
            ),

            buff_on_hit=dict(
                buff_name=self.available_buff_names(),
                lst_category=ON_HIT_EFFECTS,
                mod_operation=('append', 'remove'),
            ),

            dmg_attr=dict(
                dmg_name=self.available_dmg_names(),
                attr_name=self.available_dmg_attr_names,
                mod_operation=('multiply', 'add', 'remove'),
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
            if k in self.conditions_dct[con_name]['effects'][eff_name]:
                del self.conditions_dct[con_name]['effects'][eff_name][k]

    def _create_and_insert_new_effect(self, con_name):

        eff_name = self._create_and_insert_new_effect_base(con_name=con_name)

        # EFFECT FORMULA
        # (formula type is used for non buffs/dmgs)
        if 'formula_type' in self.conditions_dct[con_name]['effects'][eff_name]:
            if self.conditions_dct[con_name]['effects'][eff_name]['formula_type'] == 'x_formula':
                suggested_dct = self.formula_contents_dct()

            else:
                suggested_dct = self.constant_values_dct()

            suggest_attr_values(suggested_values_dct=suggested_dct,
                                modified_dct=self.conditions_dct[con_name]['effects'][eff_name],)

        # Buffs/dmgs (names)
        else:
            self.conditions_dct[con_name]['effects'][eff_name].update({'names_lst': []})
            cat = self.conditions_dct[con_name]['effects'][eff_name]['category']
            if cat in ('buffs', 'remove_buff'):
                suggest_lst_of_attr_values(suggested_values_lst=self.available_buff_names(),
                                           modified_lst=self.conditions_dct[con_name]['effects'][eff_name]['names_lst'])
            # ('modifies_cd')
            elif 'cd' in cat:
                self.conditions_dct[con_name]['effects'][eff_name].update({'names_dct': {}})

                suggest_lst_of_attr_values(suggested_values_lst=palette.ALL_POSSIBLE_ABILITIES_SHORTCUTS,
                                           modified_lst=self.conditions_dct[con_name]['effects'][eff_name]['names_lst'])
                # ( {'q': (1,2..), }
                cd_mod_suggested_dct = {i: (1, 2, 3) for i in
                                        self.conditions_dct[con_name]['effects'][eff_name]['names_lst']}

                suggest_attr_values(suggested_values_dct=cd_mod_suggested_dct,
                                    modified_dct=self.conditions_dct[con_name]['effects'][eff_name]['names_dct'])
                # (deletes list since it was used only temporarily to create the cd modification dct)
                del self.conditions_dct[con_name]['effects'][eff_name]['names_lst']
            else:
                suggest_lst_of_attr_values(suggested_values_lst=self.available_dmg_names(),
                                           modified_lst=self.conditions_dct[con_name]['effects'][eff_name]['names_lst'])

        print(delimiter(40))
        print('\nEFFECT: {}'.format(eff_name))
        pp.pprint(self.conditions_dct[con_name]['effects'][eff_name])

    def _extra_msg_during_condition_run(self):
        return '\n{}: {}'.format(self.obj_type.upper(), self.obj_name)

    def run_conditions_creation(self, extra_msg=None):
        """
        Creates all conditions.

        :param extra_msg: (None) No actual need for it; used to match signature of overridden method.
        :return: (None)
        """
        return super().run_conditions_creation(extra_msg=self._extra_msg_during_condition_run())


class AbilitiesConditionals(_ItemsAndAbilitiesConditionalsBase):

    def __init__(self, champion_name):
        super().__init__(obj_name=champion_name,
                         obj_type='champion',
                         attributes_dct=Fetch().champ_abilities_attrs_dct(champ_name=champion_name),
                         effects_dct=Fetch().champ_effects_dct(champ_name=champion_name))


# ---------------------------------------------------------------
# ITEMS

class ItemAttrCreation(GenAttrsBase, DmgsBase, BuffsBase, EffectsBase, ItemAndMasteriesBase):

    """
    Responsible for creating a SINGLE item's attributes: unique and stacking item stats, item buffs, item effects.
    """

    ITEM_STAT_NAMES_MAP = {'Ability Power': {'app_name': 'ap',
                                             'application_type': 'additive'},
                           'Ability Power per level': {'app_name': 'ap_per_lvl',
                                                       'application_type': 'additive'},
                           'Armor': {'app_name': 'armor',
                                     'application_type': 'additive'},
                           'Attack Damage': {'app_name': 'ad',
                                             'application_type': 'additive'},
                           'Attack Speed': {'app_name': 'att_speed',
                                            'application_type': 'percent'},
                           'Base Health Regen': {'app_name': 'hp5',
                                                 'application_type': 'percent'},
                           'Base Mana Regen': {'app_name': 'mp5',
                                               'application_type': 'percent'},
                           'Cooldown Reduction': {'app_name': 'cdr',
                                                  'application_type': 'percent'},
                           'Critical Strike Chance': {'app_name': 'crit_chance',
                                                      'application_type': 'additive'},
                           'Health': {'app_name': 'hp',
                                      'application_type': 'additive'},
                           'Life Steal': {'app_name': 'lifesteal',
                                          'application_type': 'additive'},
                           'Magic Penetration': {'app_name': 'flat_magic_penetration',
                                                 'application_type': 'additive'},
                           'Magic Resist': {'app_name': 'mr',
                                            'application_type': 'additive'},
                           'Mana': {'app_name': 'mp',
                                    'application_type': 'additive'},
                           'Mana per level': {'app_name': 'mp_per_lvl',
                                              'application_type': 'additive'},
                           'Movement Speed': {'app_name': 'move_speed',
                                              'application_type': 'undefined'},
                           'Spell Vamp': {'app_name': 'spellvamp',
                                          'application_type': 'additive'},}

    _STATS_APP_NAMES = {i['app_name'] for i in ITEM_STAT_NAMES_MAP.values()}
    stats.ensure_allowed_stats_names(_STATS_APP_NAMES)

    BUFF_DOT_ATTRS = {i: () for i in palette.BUFF_DOT_ATTRS}

    def items_stat_names(self):
        """
        Returns a list of names of item stats.

        Includes both APP named stats and stats that have to be translated.

        :returns: (list)
        """
        lst = list(self._STATS_APP_NAMES)+['tar_current_hp', 'tar_max_hp', 'move_speed_reduction', 'flat_non_aoe_reduction']
        return lst

    def __init__(self, item_name):
        # Converts given item name to actual name.
        self.item_name = ExploreApiItems().actual_item_name(item_name=item_name)
        self.explore_items_module_inst = ExploreApiItems()
        self.item_id = self.explore_items_module_inst.item_dct(self.item_name)['id']
        self.item_simple_stats_dct = {}     # (stats between <stats> and </stats>)
        self.item_gen_attrs = {}
        self.non_unique_item_stats = {}
        self.unique_item_stats = {}
        self.item_dmgs = {}
        self.item_buffs = {}
        self.item_effects = {}
        self.item_tree = {}
        self.item_api_data_dct = self.explore_items_module_inst.item_dct(given_name=self.item_name)
        self._item_description_str = self.explore_items_module_inst.descriptions(item=self.item_name)[0]

    @staticmethod
    def general_attributes():

        # Not needed list.
        lst = ['dashed_distance', 'cost', 'resets_aa', 'channel_time', 'dashed_distance', 'cds_modified', ]

        # Removes not needed.
        dct = {k: v for k, v in GenAttrsBase.general_attributes().items() if k not in lst}
        return dct

    def item_dmg_attrs(self):
        dct = {k: v for k, v in self.dmg_attributes().items() if k != 'dmg_source'}
        dct.update({'dmg_source': self.item_name})

        return dct

    def usual_item_values_dmg_attrs(self):
        """
        Creates usual values for item dmg attributes.

        :return: (dict)
        """

        dct = {k: v for k, v in self.usual_values_dmg_attrs().items() if k != 'dmg_source'}

        dct.update({'dmg_type': ('magic', 'physical', 'true', 'AA')})

        return dct

    def item_buff_attributes(self):
        dct = {k: v for k, v in self.item_or_buff_attributes().items() if k != 'buff_source'}
        dct.update({'buff_source': self.item_name})

        return dct

    # ------------------------------------------------------------
    def pprint_item_description(self):
        self.pprint_item_or_mastery_description(obj_name=self.item_name,
                                                obj_description_str=self._item_description_str,
                                                str_item_or_mastery='item')

    def arithmetic_values_in_description(self):
        """
        Finds all numbers in item description. Percent values are changed to decimal.

        :return: (list)
        """

        arithmetic_vals = set()

        pattern = re.compile(r'''
        \d+                     # Starts with digits
        (?:\.\d+)?              # ..may continue with dot and digits
        \s?
        %?                      # .. may end with %.
        ''', re.VERBOSE)

        matches = re.findall(pattern, self._item_description_str)

        # Strings to floats.
        for value in matches:
            # Converts percent to decimal.
            if '%' in value:
                value = value.strip('% ')
                value = float(value) / 100.
                arithmetic_vals.add(value)

            else:
                arithmetic_vals.add(float(value))

        # Converts floats to ints when needed (e.g. 1.0 -> 1)
        final_values_set = set()
        for value in arithmetic_vals:
            val_as_int = int(value)
            if val_as_int == value:
                final_values_set.add(val_as_int)

            else:
                final_values_set.add(value)

        return final_values_set

    @staticmethod
    def _all_matches_between_given_tag(item_description, tag_str):
        return re.findall(r'<{tag_str}>(.+)</{tag_str}>'.format(tag_str=tag_str), item_description)

    def _content_between_non_dup_tags_in_description(self, item_description, tag_str):
        """
        Cuts off and returns stats string in an item description by the xml tags (<stats> </stats>).

        Not to be used for tags that exist more than once in a single description.

        :return: (str)
        """

        between_tags_matches = self._all_matches_between_given_tag(item_description=item_description, tag_str=tag_str)

        total_found = len(between_tags_matches)
        if total_found > 1:
            raise palette.UnexpectedValueError('Description contains several matches with given tag.')
        elif total_found == 0:
            return ''
        else:
            return between_tags_matches[0]

    def _automatic_non_unique_stats_names_and_values(self, given_description_str):
        """
        Creates a dict with stat names as values and stat value as key.

        Assumes stats' bonuses are of a single type. Raises exception if multiple values for same stat are detected.

        :return: (dict)
        """

        dct = {}

        # Non unique stats are between: <stats> </stats>
        non_unique_stats_str = self._content_between_non_dup_tags_in_description(item_description=given_description_str,
                                                                                 tag_str='stats')

        # Takes everything between a ">" and a "<".
        stat_strings_lst = re.split(r'<[^<^>]+>', non_unique_stats_str)
        stat_strings_lst = [i for i in stat_strings_lst if i != '']

        for str_fragment in stat_strings_lst:
            val_str = re.search(r'\d+(?:\.\d+)?%?', str_fragment).group()

            # VALUE
            val = ast.literal_eval(val_str.rstrip('%'))

            # Percent is converted to float.
            if '%' in val_str:
                val /= 100

            # NAME
            # (starts searching in longest names first in order to avoid mismatching 'ap' instead of 'ap per lvl')
            for api_name in sorted(self.ITEM_STAT_NAMES_MAP, key=lambda x: len(x), reverse=True):

                if api_name.lower() in str_fragment.lower():
                    stat_app_name = self.ITEM_STAT_NAMES_MAP[api_name]['app_name']

                    if '%' in val_str:
                        stat_type = 'percent'
                    else:
                        stat_type = 'additive'

                    dct.setdefault(stat_type, {})

                    if stat_app_name in dct[stat_type]:
                        raise KeyError('{} already exists.'.format(stat_app_name))

                    dct[stat_type].update({stat_app_name: val})
                    break
            else:
                # No match found.
                print('WARNING: No matching stat found in string: {}\nNon-unique stats set to empty dict'.format(str_fragment))

        return dct

    def create_non_unique_stats_names_and_values(self):
        """
        Creates a dict with stat names as values and stat value as key.

        :return: (None)
        """

        auto_created_stats = self._automatic_non_unique_stats_names_and_values(
            given_description_str=self._item_description_str)

        print(delimiter(20))
        print('\nAutocreated NON UNIQUE stats:')
        pp.pprint(auto_created_stats)
        print()

        self.non_unique_item_stats = auto_created_stats

    def _detected_uniques_names(self):

        names_lst = []

        between_tags_matches = self._all_matches_between_given_tag(item_description=self._item_description_str,
                                                                   tag_str='unique')

        between_tags_matches += self._all_matches_between_given_tag(item_description=self._item_description_str,
                                                                    tag_str='aura')

        # Extracts unique name.
        for between_tag_str in between_tags_matches:
            match_found = re.findall(r'UNIQUE [a-z]*\s?-\s*([^:]+):', between_tag_str, re.I)
            if match_found:
                raw_name_detected = match_found[0]

                name = _ExploreBase.modify_api_names_to_callable_string(name=raw_name_detected)
                names_lst.append(name)

        return names_lst

    def _possible_unique_names(self):
        lst = ['unnamed']
        lst += sorted(self._detected_uniques_names())
        return lst

    @staticmethod
    def _create_unique_or_non_unique_stats(obj_name, modified_stats_dct, possible_stat_values_lst):
        modified_stats_names = []
        suggest_lst_of_attr_values(suggested_values_lst=stats.NON_PER_LVL_STAT_NAMES,
                                   modified_lst=modified_stats_names)

        # Stat name
        for stat_modified in modified_stats_names:

            stat_name_msg = '\nITEM: {}, STAT: {}'.format(obj_name, stat_modified)

            # Stat type
            for stat_type in STAT_TYPES:
                if _y_n_question(stat_name_msg+'\nIs there a {} bonus to the stat?'.format(stat_type.upper())):
                    # (created here, instead of outside the loop, since some types aren't needed)
                    modified_stats_dct.setdefault(stat_type, {})

                    # Stat values
                    stat_vals = enumerated_question(question_str=stat_name_msg+'\nStat values?',
                                                    choices_seq=possible_stat_values_lst)

                    modified_stats_dct[stat_type].update({stat_modified: stat_vals})

    def create_unique_stats_values(self):
        """
        Detects unique stats and their values in an item description, and stores them.

        :return: (None)
        """

        pp.pprint(self._item_description_str)

        possible_unique_names = self._possible_unique_names()

        print(fat_delimiter(40))
        print('\nUNIQUE item stats:')
        selected_unique_names_lst = enumerated_lst_creation(suggested_values_lst=possible_unique_names,
                                                            sort_suggested_lst=False)

        for name_of_unique in selected_unique_names_lst:
            self.unique_item_stats.update({name_of_unique: {}})

            print('unique name: {}\n'.format(name_of_unique.upper()))

            self._create_unique_or_non_unique_stats(obj_name=self.item_name,
                                                    modified_stats_dct=self.unique_item_stats[name_of_unique],
                                                    possible_stat_values_lst=self.arithmetic_values_in_description())

        print(delimiter(40))
        print('UNIQUE stats:')
        pp.pprint(self.unique_item_stats)

    @repeat_cluster_decorator(cluster_name='ITEM GEN ATTRS')
    def create_item_gen_attrs(self):
        self.item_gen_attrs = {}

        # Castable
        suggest_attr_values(suggested_values_dct=dict(castable=(True, False)),
                            modified_dct=self.item_gen_attrs, restrict_choices=True)

        # (if castable continues inserting the rest of the keys)
        if self.item_gen_attrs['castable'] is True:
            self.item_gen_attrs.update({k: v for k, v in self.general_attributes().items()})

            suggest_attr_values(suggested_values_dct=self.USUAL_VALUES_GEN_ATTR, modified_dct=self.item_gen_attrs)

        pp.pprint(self.item_gen_attrs)

    @repeat_cluster_decorator(cluster_name='ITEM DMG MODS')
    def _create_dmg_mods(self, dmg_name):
        self.pprint_item_description()

        mods_dct = self.item_dmgs[dmg_name]['mods']
        self._create_shield_or_dmg_mods(mods_dct=mods_dct)

    @inner_loop_exit_handler
    def _create_item_single_dmg(self):
        # Dmg name
        new_dmg_name = _auto_new_name_or_ask_name(existing_names=self.item_dmgs,
                                                  first_synthetic='{}_dmg'.format(self.item_name))

        # (msg)
        print(fat_delimiter(40))
        print('\nDMG NAME: {}'.format(new_dmg_name))

        expression_way = enumerated_question("Expressed by: (if expressed by another item, insert item name)",
                                             choices_seq=('normally', 'by_method'))

        if expression_way == 'by_method':
            self.item_dmgs.update({new_dmg_name: 'expressed_by_method'})

        elif expression_way == 'normally':
            # (creates new_dmg_name dct)
            self.item_dmgs.update({new_dmg_name: self.item_dmg_attrs()})
            # Dmg value
            dmg_val = restricted_input(question_msg='Dmg value?\n', input_type='num', characteristic='non_negative',
                                       disallow_enter=True)

            self.item_dmgs[new_dmg_name]['dmg_values'] = dmg_val
            # Rest of dmg attributes
            suggest_attr_values(suggested_values_dct=self.usual_item_values_dmg_attrs(),
                                modified_dct=self.item_dmgs[new_dmg_name],)

            # Dot.
            if self.item_dmgs[new_dmg_name]['dot']:
                dot_buff = restricted_input('Name of dot-buff?', input_type='str', disallow_enter=True)

                self.item_dmgs[new_dmg_name]['dot'] = {'buff_name': dot_buff}

            # Inserts dmg mods.
            self._create_dmg_mods(dmg_name=new_dmg_name)

        # Expressed by item.
        else:
            self.item_dmgs.update({new_dmg_name: expression_way})

        print(delimiter(40))
        pp.pprint(self.item_dmgs[new_dmg_name])

    @repeat_cluster_decorator(cluster_name='ITEM DMGS')
    @inner_loop_exit_handler
    def create_item_dmgs(self):

        # Prints item description.
        print(fat_delimiter(40))
        self.pprint_item_description()

        # Number of dmgs
        num_of_dmgs = restricted_input(question_msg='Number of dmgs?\n', input_type='int',
                                       characteristic='non_negative', disallow_enter=True)

        # Resets item_dmgs dct.
        self.item_dmgs = {}
        for _ in range(num_of_dmgs):
            self._create_item_single_dmg()

        # Prints all dmgs
        print('DMGS:')
        pp.pprint(self.item_dmgs)

    def _suggest_buff_affected_stats_of_item(self, buff_name):
        self._suggest_buff_affected_stats_of_item_or_mastery(buff_name=buff_name, str_item_or_mastery='item',
                                                             pprint_description_func=self.pprint_item_description,
                                                             mastery_or_item_name=self.item_name,
                                                             buffs_dct=self.item_buffs,
                                                             available_stat_names=self.items_stat_names(),
                                                             lst_of_values_tuples=())

    @repeat_cluster_decorator(cluster_name='ITEM BUFFS')
    @inner_loop_exit_handler
    def create_item_buffs(self):

        print(fat_delimiter(80))
        self.pprint_item_description()

        self.item_buffs = {}
        self._ask_amount_of_buffs_and_change_names(modified_dct=self.item_buffs, obj_name=self.item_name)

        for buff_name in self.item_buffs:
            # Expressed by method.
            print(fat_delimiter(40))
            print('BUFF: {}'.format(buff_name))
            expression_way = enumerated_question("Expressed by: (if expressed by another item, insert item name)",
                                                 choices_seq=('normally', 'by_method'))

            if expression_way == 'by_method':
                self.item_buffs.update({buff_name: 'expressed_by_method'})

            elif expression_way == 'normally':
                # Expressed normally.
                self.item_buffs.update({buff_name: self.item_buff_attributes()})

                # Buff attrs (excluding stats)
                buff_msg = '\nITEM: {}, BUFF: {}'.format(self.item_name, buff_name)
                suggest_attr_values(suggested_values_dct=self.usual_item_or_mastery_buff_attrs_values(),
                                    modified_dct=self.item_buffs[buff_name], extra_start_msg=buff_msg)

                # DOT
                if self.item_buffs[buff_name]['dot']:
                    self.item_buffs[buff_name]['dot'] = {'dmg_names': []}
                    suggest_attr_values(suggested_values_dct={k: v for k, v in self.BUFF_DOT_ATTRS.items() if k != 'dmg_names'},
                                        modified_dct=self.item_buffs[buff_name]['dot'],
                                        extra_start_msg='Dot attrs: ')

                    suggest_lst_of_attr_values(suggested_values_lst=list(self.item_dmgs),
                                               modified_lst=self.item_buffs[buff_name]['dot']['dmg_names'],
                                               extra_start_msg='Dmgs names?')

                # SHIELD
                shield_dct = self.item_buffs[buff_name]['shield']
                self._create_shield(shield_dct=shield_dct, description_to_print=self._item_description_str)

                # Stats affected by buff.
                self.item_buffs[buff_name]['stats'] = {}
                suggest_affected_stats_attributes(obj_name=buff_name,
                                                  modified_stats_dct=self.item_buffs[buff_name]['stats'],
                                                  possible_stat_values_lst=self.arithmetic_values_in_description(),
                                                  possible_mod_values_lst=self.arithmetic_values_in_description())

            else:
                self.item_buffs.update({buff_name: expression_way})

        buff_names = sorted(self.item_buffs)
        dmgs_names = sorted(self.item_dmgs)

        # On hit
        # (done later so that buffs' and dmgs' names are available)
        for buff_name in self.item_buffs:

            if isinstance(self.item_buffs[buff_name], str):
                # (skips if expressed by method)
                continue

            self.item_buffs[buff_name].update(on_hit=palette.ON_HIT_EFFECTS)
            buff_on_hit_dct = self.item_buffs[buff_name]['on_hit']
            if _y_n_question('Does {} have ON HIT?'.format(buff_name.upper())):

                # ('reduce_cd' should be set manually since too few items have it)

                suggest_lst_of_attr_values(modified_lst=buff_on_hit_dct['apply_buff'], suggested_values_lst=buff_names,
                                           extra_start_msg='APPLIED BUFFS on hit.')

                suggest_lst_of_attr_values(modified_lst=buff_on_hit_dct['cause_dmg'], suggested_values_lst=dmgs_names,
                                           extra_start_msg='CAUSED DMGS on hit.')

                suggest_lst_of_attr_values(modified_lst=buff_on_hit_dct['remove_buff'], suggested_values_lst=buff_names,
                                           extra_start_msg='REMOVED BUFFS on hit.')

            else:
                self.item_buffs[buff_name]['on_hit'] = {}

        print('BUFFS:')
        pp.pprint(self.item_buffs)

    @repeat_cluster_decorator(cluster_name='ITEM EFFECTS')
    def create_item_effects(self):

        self.item_effects = palette.item_effects()
        msg = 'ITEM: {}'.format(self.item_name)

        self._create_single_obj_effects_dct(obj_name=self.item_name,
                                            champ_or_item='item',
                                            univ_msg=msg,
                                            modified_eff_dct=self.item_effects,
                                            champ_name=None)

    # -----------------------------------------------------------
    # Tree
    def _item_tree_piece_base_function(self, key_name):
        """
        :param key_name: (str) 'into', 'from'
        :return: (tuple)
        """

        lst = []

        if key_name in self.item_api_data_dct:
            for id_num_as_str in self.item_api_data_dct[key_name]:
                # Appends all names corresponding to the id_nums.
                item_name = self.explore_items_module_inst.item_name_from_id(id_num=id_num_as_str)
                if item_name:
                    lst.append(item_name)

        return tuple(lst)

    def item_builds_into(self):
        """

        :return: (set)
        """

        return set(self._item_tree_piece_base_function(key_name='into'))

    def item_builds_from(self):
        """

        :return: (dict)
        """

        built_from_tpl = self._item_tree_piece_base_function(key_name='from')

        return dict(collections.Counter(built_from_tpl))

    def _item_roots_leafs_base(self, from_or_into, _given_id_num_as_str=None, _set_of_ids=None):
        """
        Base method for finding all items that this item is build from or into.

        :param from_or_into: (str) 'from' or 'into'. Key in the item dict of examined list
        :param _given_id_num_as_str: (str) Initially automatically set to self.item_id,
            then set through recursion to leaf or root item ids.
        :param _set_of_ids: (set) Used in recursion to pass previous items found.
        :return: (set) names of items
        """

        # (has to be none unless called through recursion)
        if _given_id_num_as_str is None:
            _given_id_num_as_str = str(self.item_id)

        if _set_of_ids is None:
            set_of_ids = set()
        else:
            set_of_ids = _set_of_ids

        # (Item with current id_num, not self.item_name)
        examined_item_dct = self.explore_items_module_inst.all_items_dct_by_id[_given_id_num_as_str]
        try:
            added_lst = examined_item_dct[from_or_into]
        except KeyError:
            added_lst = []

        for id_num_as_str in added_lst:
            set_of_ids.update({id_num_as_str})
            self._item_roots_leafs_base(from_or_into=from_or_into, _given_id_num_as_str=id_num_as_str,
                                        _set_of_ids=set_of_ids)

        final_set_with_item_names = {
            self.explore_items_module_inst.item_name_from_id(id_num=i) for i in set_of_ids}

        return final_set_with_item_names

    def item_roots(self):
        """
        Finds all items that this item is build from.

        :return: (set) Names of items.
        """
        return self._item_roots_leafs_base(from_or_into='from')

    def item_leafs(self):
        """
        Finds all items that are built from this item.

        :return: (set) Names of items.
        """
        return self._item_roots_leafs_base(from_or_into='into')

    # -----------------------------------------------------------
    # Secondary data dict
    def item_secondary_data_dct(self):
        """
        Creates and returns a dict containing secondary item data.

        "Secondary" refers to non-stats, item id, build tree, gold, recipe cost, etc.

        :returns: (dict)
        """

        explore_inst = self.explore_items_module_inst

        dct = {}

        dct.update({'id': int(self.item_id)})
        dct.update({'build_from': self.item_builds_from()})
        dct.update({'builds_into': self.item_builds_into()})
        dct.update({'roots': self.item_roots()})
        dct.update({'leafs': self.item_leafs()})

        dct.update({'total_price': explore_inst.item_total_price(item_name=self.item_name)})
        dct.update({'recipe_price': explore_inst.item_recipe_price(item_name=self.item_name)})
        dct.update({'sell_price': explore_inst.item_sell_price(item_name=self.item_name)})

        return dct


class ItemsConditionals(_ItemsAndAbilitiesConditionalsBase):

    def __init__(self, item_name):
        super().__init__(obj_name=item_name,
                         obj_type='item',
                         attributes_dct=Fetch().items_attrs_dct()[item_name],
                         effects_dct=Fetch().items_effects_dct())


# ---------------------------------------------------------------
# MASTERIES
class MasteryCreation(BuffsBase, DmgsBase, ItemAndMasteriesBase):

    """
    Responsible for creation of a mastery's stats, buffs and dmgs.

    Dmgs and on-hit effects are to be created manually, since there is only a single dmg in masteries.
    """

    BASE_MASTERY_DCT = dict(
        stats=None,
        buffs={},
        dmgs={},
        stats_dependencies={})

    def __init__(self, mastery_name):
        self.mastery_name = mastery_name
        self.inst = ExploreApiMasteries()
        self.raw_masteries_dct = self.inst.masteries_dct
        self.mastery_buffs = {}

    def print_mastery_description(self):
        return self.inst.mastery_description(mastery_name=self.mastery_name, print_mode=True)

    def mastery_buff_attributes(self):
        return self.item_or_buff_attributes()

    def possible_stats_names(self,):
        """
        Returns a list with possible stat names.
        On the top of the list are stats detected since they are most probably the ones to use.

        :return: (list)
        """

        detected_names_set = set(self.inst.stats_names_detected(mastery_name=self.mastery_name))
        allowed_names_set = set(ALLOWED_STATS_NAMES)

        allowed_names_set -= detected_names_set

        names_lst = sorted(detected_names_set) + sorted(allowed_names_set)

        return names_lst

    def possible_stat_values(self):
        return self.inst.stats_values_detected(mastery_name=self.mastery_name)

    def create_and_return_mastery_stats(self):

        self.print_mastery_description()

        print('Select empty string if mastery doesnt modify stats.')

        possible_stat_names = [''] + self.possible_stats_names()
        possible_stat_values = self.possible_stat_values()

        selected_names_lst = []
        suggest_lst_of_attr_values(suggested_values_lst=possible_stat_names,
                                   modified_lst=selected_names_lst,
                                   sort_suggested_lst=False)
        stats_dct = {}

        if selected_names_lst == ['']:
            print('Mastery modifies 0 stats.')
            return stats_dct

        self.print_mastery_description()

        stats_dct = {k: {} for k in selected_names_lst}

        for stat_name in stats_dct:
            msg = '\nSTAT NAME: {}\n'.format(stat_name)
            chosen_types_lst = []
            suggest_lst_of_attr_values(suggested_values_lst=('additive', 'percent', 'multiplicative'),
                                       modified_lst=chosen_types_lst,
                                       extra_start_msg=msg)

            for type_name in chosen_types_lst:
                stats_dct[stat_name].update({type_name: {}})

                # (dict form effects for parameter below)
                eff_values_dct = {'stat_values': possible_stat_values}

                suggest_attr_values(suggested_values_dct=eff_values_dct,
                                    modified_dct=stats_dct[stat_name][type_name],
                                    extra_start_msg=msg)

        return stats_dct

    def suggest_buff_affected_stats_of_mastery(self, buff_name):
        self._suggest_buff_affected_stats_of_item_or_mastery(buff_name=buff_name, str_item_or_mastery='mastery',
                                                             pprint_description_func=self.print_mastery_description,
                                                             mastery_or_item_name=self.mastery_name,
                                                             buffs_dct=self.mastery_buffs,
                                                             available_stat_names=self.possible_stats_names(),
                                                             lst_of_values_tuples=self.possible_stat_values())

    def create_mastery_buffs(self):

        print(fat_delimiter(40))
        print('MASTERY: {}\n'.format(self.mastery_name))
        self.print_mastery_description()

        self.mastery_buffs = {}
        self._ask_amount_of_buffs_and_change_names(modified_dct=self.mastery_buffs, obj_name=self.mastery_name)

        for buff_name in sorted(self.mastery_buffs):
            self.mastery_buffs.update({buff_name: self.mastery_buff_attributes()})

            buff_msg = '\nMASTERY: {}, BUFF: {}'.format(self.mastery_name, buff_name)
            # Stats affected by buff.
            self.suggest_buff_affected_stats_of_mastery(buff_name=buff_name)
            # Rest of buff attrs.
            suggest_attr_values(suggested_values_dct=self.usual_item_or_mastery_buff_attrs_values(),
                                modified_dct=self.mastery_buffs[buff_name], extra_start_msg=buff_msg)
            # Buff source
            self.mastery_buffs[buff_name]['buff_source'] = 'masteries'

        pp.pprint(self.mastery_buffs)
        print(delimiter(80))

    def create_and_return_mastery(self, print_mode=False):
        dct = copy.deepcopy(self.BASE_MASTERY_DCT)

        print(fat_delimiter(80))
        print('MASTERY: {}\n'.format(self.mastery_name))

        dct['stats'] = self.create_and_return_mastery_stats()
        pp.pprint(dct['stats'])
        print(delimiter(80))

        self.create_mastery_buffs()
        dct['buffs'] = self.mastery_buffs

        dct['stats_dependencies'] = StatsDependencies().mastery_stats_dependencies(mastery_name=self.mastery_name)

        return _return_or_pprint_complex_obj(given_dct=dct, print_mode=print_mode)


# ---------------------------------------------------------------
# ROTATIONS CONDITIONALS
class RotationPriorityConditional(_ConditionalsBase):

    TARGET_TYPES = palette.TARGET_TYPES
    COMPARISON_OPERATOR_STRINGS = palette.COMPARISON_OPERATOR_STRINGS
    EFFECTS_SETUP_TYPES = ('prioritized', 'priority_fragment')

    def __init__(self, champion_name):
        _ConditionalsBase.__init__(self)

        self.champion_name = champion_name

    def _priority_trigger_buffs(self):
        items_buffs = list(items_folder.items_data.ITEMS_BUFFS_NAMES)
        champions_buffs = palette.champion_buffs_or_dmgs_names_lst(champion_name=self.champion_name, str_buffs_or_dmgs='buffs')

        lst = items_buffs + champions_buffs
        return sorted(lst)

    @property
    def trigger_setup_dct(self):

        return dict(
            active_buffs=dict(
                buff_names=self._priority_trigger_buffs(),
                owner_type=self.TARGET_TYPES,
                stacks_at_least=(1, 2, 3, 4, 5,),
            ),

            previous_action=dict(
                obj_name=ALL_POSSIBLE_ACTIONS,
            ),
        )

    @property
    def effect_setup_dct(self):
        return dict(
            top_priority=dict(
                obj_name=ALL_POSSIBLE_ACTIONS
            ),
            priority_fragment=dict(
                priority_fragment_lst=ALL_POSSIBLE_ACTIONS
            ),
            consecutive_action=dict(
                preceding_action=ALL_POSSIBLE_ACTIONS,
                succeeding_action=ALL_POSSIBLE_ACTIONS
            )
        )

    @property
    def attrs_with_lst_val(self):
        return ['priority_fragment_lst', 'buff_names']


# SKILLS LVLS
class SkillsLvlUps(object):

    @staticmethod
    def lvl_priorities_dct_base():
        return dict(
            spells_lvl_up_queue='list_placeholder',
            at_least_one_lvl_in_each=(True, False),
            max_spells_lvl_ups='varying_placeholder',
            automatically_lvled_up='varying_placeholder'
        )

    @staticmethod
    def _automatically_lvled_up_value():
        """
        Returns a dict with spells and champion lvls at which these spells get automatically a lvl up.

        :return: (dict)
        """

        dct = {}

        auto_lvled_up_spells_exist = _y_n_question(question_str='Does any spell get automatically lvled up?')

        if auto_lvled_up_spells_exist:
            spell_names_lst = []
            suggest_lst_of_attr_values(suggested_values_lst=palette.SPELL_SHORTCUTS, modified_lst=spell_names_lst)

            for spell_name in spell_names_lst:
                q_msg = 'Give champ lvls (tuple) at which {} is auto lvled up.'.format(spell_name.upper())
                lvls_lst = restricted_input(question_msg=q_msg, input_type='tuple', disallow_enter=True)

                dct.update({spell_name: lvls_lst})

        return dct

    @staticmethod
    def _max_spells_lvls():
        """
        If spells have the usual max lvl returns string,
        otherwise returns a dict with each spell's max lvl.

        :return: (dict) (str)
        """

        all_spells_usual_max_lvl = _y_n_question(question_str='All spells have the usual max lvl?')

        if all_spells_usual_max_lvl:
            return 'standard'

        else:
            suggested_values_dct = {i: () for i in palette.SPELL_SHORTCUTS}
            dct = {}

            suggest_attr_values(suggested_values_dct=suggested_values_dct, modified_dct=dct)

            return dct

    def lvl_up_priorities(self):
        """

        :return: (dict)
        """
        dct = self.lvl_priorities_dct_base()

        msg = 'Highest to lowest priority spell lvling up?'
        spells_lvl_up_queue_lst = []
        suggest_lst_of_attr_values(suggested_values_lst=palette.SPELL_SHORTCUTS,
                                   modified_lst=spells_lvl_up_queue_lst, extra_start_msg=msg)

        dct['spells_lvl_up_queue'] = spells_lvl_up_queue_lst

        dct['at_least_one_lvl_in_each'] = _y_n_question('Lvl up each ability at least once?')

        dct['max_spells_lvl_ups'] = self._max_spells_lvls()

        dct['automatically_lvled_up'] = self._automatically_lvled_up_value()

        return dct

    @staticmethod
    def champion_resource_used():
        return enumerated_question(question_str='Resource used?', choices_seq=stats.ALL_RESOURCE_NAMES)


# ===============================================================
#       MODULE CREATION
# ===============================================================

class ModuleCreatorBase(object):

    @staticmethod
    def _append_obj_in_module(obj_name, new_object_as_dct_or_str, targeted_module, width):
        """
        Appends full object inside targeted_module.

        :param obj_name: (str) 'ABILITIES_EFFECTS', 'TRINITY_FORCE', etc.
        :param new_object_as_dct_or_str: (str) or (dict) object body
        :param targeted_module: (str)
        :return: (None)
        """

        if type(new_object_as_dct_or_str) is dict:
            final_str = dct_to_pretty_formatted_str(obj_name=obj_name,
                                                    obj_body_as_dct=new_object_as_dct_or_str,
                                                    width=width)
        else:
            obj_as_str = new_object_as_dct_or_str
            final_str = '\n' + obj_name + ' = ' + obj_as_str + '\n'

        with open(targeted_module, 'a') as read_file:
            read_file.write(final_str)

    @staticmethod
    def _replace_obj_in_module(obj_name, new_object_as_dct_or_str, targeted_module_path_str, width):
        """
        Replaces full object in module.

        :param obj_name: (str)
        :param new_object_as_dct_or_str: (dct) or (str) object body
        :return: (None)
        """

        with open(targeted_module_path_str, 'r') as read_file:
            read_file_as_lst = read_file.readlines()

        replacement = _file_after_replacing_module_var(file_as_lines_lst=read_file_as_lst, object_name=obj_name,
                                                       obj_as_dct_or_str=new_object_as_dct_or_str, width=width)

        with open(targeted_module_path_str, 'w') as w:
            w.write(replacement)

    @staticmethod
    def _obj_existence(obj_name, targeted_module_path_str):
        """
        Checks start of each line in a module for obj existence.

        :param obj_name: (str)
        :param targeted_module_path_str: (str)
        :return:
        """

        try:
            with open(targeted_module_path_str, 'r') as read_file:
                r_as_lst = read_file.readlines()

                for line in r_as_lst:
                    if re.match(r'{}'.format(obj_name), line):
                        return True
                # If no match has been found, returns False.
                else:
                    return False

        except FileNotFoundError:
            with open(targeted_module_path_str, 'w') as _:
                pass

    @staticmethod
    def insert_object_in_dct(obj_name, modified_dct, auto_replace, property_name, data_creation_func):
        """
        Checks if given object name has an existing data dict.
        If replacement is confirmed, creates and inserts data in given dict.

        :param obj_name:
        :param modified_dct: Contains existing data.
        :param auto_replace:
        :param property_name:
        :param data_creation_func:
        :return: (None)
        """

        if obj_name in modified_dct:
            # (if auto replace true, skips asking)
            if auto_replace or _y_n_question('{} {} exists. Replace?'.format(
                    obj_name.capitalize(), property_name.upper())):

                # Creates and inserts item dict into items dict.
                modified_dct[obj_name] = data_creation_func()

            else:
                print('\nAborting insertion.')
                return

        else:
            modified_dct[obj_name] = data_creation_func()

    def insert_object_in_module(self, obj_name, targeted_module_path_str, new_obj_as_dct_or_str_or_func, func_args=(),
                                replacement_question_msg='', width=None, verify_replacement=True):
        """
        Inserts object in module after verifying replacement if needed.
        If object doesn't exist, it is appended.

        WARNING: When used for class insertion, assumes no empty lines between class start and __init__ end.

        :return: (None)
        """

        # If object exists, replaces it.
        if self._obj_existence(obj_name=obj_name, targeted_module_path_str=targeted_module_path_str):

            replacement_question_msg += '\nObject {} exists. Replace it?'.format(obj_name)
            # (if verify_replacement is False short-circuits)
            if (not verify_replacement) or _y_n_question(question_str=replacement_question_msg):

                if type(new_obj_as_dct_or_str_or_func) in (dict, str):
                    new_obj_as_dct_or_str = new_obj_as_dct_or_str_or_func
                else:
                    new_obj_as_dct_or_str = new_obj_as_dct_or_str_or_func(*func_args)

                self._replace_obj_in_module(obj_name=obj_name,
                                            new_object_as_dct_or_str=new_obj_as_dct_or_str,
                                            targeted_module_path_str=targeted_module_path_str, width=width)
            else:
                print('\nReplacement canceled.')

        # If object doesn't exist, appends object.
        else:

            if type(new_obj_as_dct_or_str_or_func) in (dict, str):
                    new_obj_as_dct_or_str = new_obj_as_dct_or_str_or_func
            else:
                new_obj_as_dct_or_str = new_obj_as_dct_or_str_or_func(*func_args)

            self._append_obj_in_module(obj_name=obj_name,
                                       new_object_as_dct_or_str=new_obj_as_dct_or_str,
                                       targeted_module=targeted_module_path_str, width=width)

    def pformat_obj_in_champ_or_items_module(self, obj_name, items_or_a_champ_name):
        """
        Edits a module by formatting a dict inside of it.

        :param obj_name: (str) e.g. 'ITEMS_EFFECTS'
        :param items_or_a_champ_name: (str) 'items' or a champion name
        :return: (None)
        """

        try:
            # Champion.
            path = CHAMPION_MODULES_FOLDER_NAME + '/' + items_or_a_champ_name + '.py'
            module = Fetch().imported_champ_module(champ_name=items_or_a_champ_name)
        except ImportError:
            # Items.
            path = ITEMS_MODULES_FOLDER_NAME + '/' + ITEMS_DATA_MODULE_NAME + '.py'
            module = Fetch().imported_items_module()
        existing_obj = getattr(module, obj_name)

        self._replace_obj_in_module(obj_name=obj_name, new_object_as_dct_or_str=existing_obj,
                                    targeted_module_path_str=path, width=1)

        print("\n{} in '{}' pretty formatted.".format(obj_name, path))

    def pformat_obj_in_path(self, obj_name, obj_module_path):
        """
        Edits a module by formatting a dict inside of it.

        :param obj_name: (str) Dict name
        :param obj_module_path: (str) Path of module with '/' instead of '.' , e.g. 'items/items_data.py'.
        :return: (None)
        """

        path_str = obj_module_path.replace('/', '.')
        path_str = path_str.rstrip('.py')
        module = Fetch().imported_module(path_str=path_str)
        existing_obj = getattr(module, obj_name)

        self._replace_obj_in_module(obj_name=obj_name, new_object_as_dct_or_str=existing_obj,
                                    targeted_module_path_str=obj_module_path, width=1)

        print("\n{} in '{}' pretty formatted.".format(obj_name, obj_module_path))


class ChampionsBaseStats(ModuleCreatorBase):

    BASE_STATS_API_TO_APP_NAME_MAP = dict(
        hp='hp',
        hpregenperlevel='hp5',
        mpperlevel='mp_per_lvl',
        spellblock='mr',
        attackdamageperlevel='ad_per_lvl',
        critperlevel='crit_chance_per_lvl',
        crit='crit_chance',
        attackdamage='ad',
        mpregen='mp5',
        movespeed='move_speed',
        hpperlevel='hp_per_lvl',
        attackspeedoffset='att_speed_offset',
        hpregen='hp5',
        mp='mp',
        attackspeedperlevel='att_speed_per_lvl',
        mpregenperlevel='mp5_per_lvl',
        attackrange='range',
        armor='armor',
        armorperlevel='armor_per_lvl',
        spellblockperlevel='mr_per_lvl',
    )

    @staticmethod
    def att_speed_by_att_speed_offset(att_speed_offset):
        """
        Calculates attack speed from attack speed offset.

        :param att_speed_offset: (float)
        :return: (float)
        """

        att_speed = 0.625 / (1 + att_speed_offset)

        return att_speed

    def _app_compatible_champ_base_stats_dct(self, champ_name):
        """
        Returns a dict with names compatible with app expectations.

        WARNING: 'resource_used' is set to everyone as 'mp'.

        :return: (dict)
        """

        raw_dct = ExploreChampionsBaseStats().champion_base_stats(champ_name=champ_name)

        new_dct = {}

        # Converts stat names to app used names.
        for key, val in raw_dct.items():
            new_key = self.BASE_STATS_API_TO_APP_NAME_MAP[key]
            new_dct.update({new_key: val})

        # Creates and inserts base attack speed.
        att_speed_val = self.att_speed_by_att_speed_offset(att_speed_offset=new_dct['att_speed_offset'])
        new_dct.update({'base_att_speed': att_speed_val})

        return new_dct

    def _all_champions_base_stats(self):
        all_champs_base_stats_dct = {}

        for champ_name in api_champions_database.ALL_CHAMPIONS_ATTR:
            champ_dct = self._app_compatible_champ_base_stats_dct(champ_name=champ_name)

            all_champs_base_stats_dct.update({champ_name: champ_dct})

        return all_champs_base_stats_dct

    def store_champions_base_stats(self):

        dct = self._all_champions_base_stats()

        self.insert_object_in_module(obj_name=CHAMPION_BASE_STATS_DCT_NAME,
                                     targeted_module_path_str=CHAMPION_BASE_STATS_MODULE,
                                     new_obj_as_dct_or_str_or_func=dct)


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
        suggest_lst_of_attr_values(suggested_values_lst=('AA',) + palette.ALL_POSSIBLE_SPELL_SHORTCUTS,
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
            effects_inst.run_spells_effects_creation()

            return effects_inst.spells_effects

        elif obj_name == ABILITIES_CONDITIONALS_DCT_NAME:
            instance = AbilitiesConditionals(champion_name=self.champion_name)
            instance.run_conditions_creation()

            return instance.conditions_dct

        elif obj_name == CHAMPION_EXTERNAL_VAR_DCT_NAME:
            return self._external_vars()

        elif obj_name == CHAMP_CLASS_NAME:
            return child_class_as_str

        elif obj_name == DEFAULT_ACTIONS_PRIORITY_NAME:
            return self._priority_tpl_as_str()

        elif obj_name == SPELL_LVL_UP_PRIORITIES_NAME:
            return SkillsLvlUps().lvl_up_priorities()

        elif obj_name == RESOURCE_USED_NAME:
            return str(SkillsLvlUps().champion_resource_used())

        elif obj_name == CHAMPION_STATS_DEPENDENCIES_NAME:
            deps = StatsDependencies().champion_stats_dependencies(champion_name=self.champion_name)
            return str(deps)

        elif obj_name == CHAMPION_RANGE_TYPE_NAME:
            if _y_n_question('Is {} ranged?'.format(self.champion_name.upper())):
                return 'ranged'
            else:
                return 'melee'

        else:
            palette.UnexpectedValueError(obj_name)

    def run_single_element_creation(self, obj_name):
        replacement_question_msg = '\nCHAMPION: {}, OBJECT NAME: {}'.format(self.champion_name, obj_name)

        self.insert_object_in_module(obj_name=obj_name,
                                     new_obj_as_dct_or_str_or_func=self._champ_obj_as_dct_or_str,
                                     func_args=(obj_name,),
                                     replacement_question_msg=replacement_question_msg,
                                     targeted_module_path_str=self.champion_module_path_str, width=None)
        # Delay used to ensure file is "refreshed" after being writen on. (might be redundant)
        time.sleep(0.2)

    def run_champ_module_creation(self):
        """
        Creates all champion module related data (module dicts, class, etc)

        Returns:
            (None)
        """

        for obj_name in CHAMPION_MODULE_OBJECT_NAMES:
            self.run_single_element_creation(obj_name=obj_name)


class ItemsModuleCreator(ModuleCreatorBase):

    def __init__(self, item_name):
        self.item_name = ExploreApiItems().actual_item_name(item_name=item_name)
        self.items_data_path_str = '{}/items_data.py'.format(ITEMS_MODULES_FOLDER_NAME)
        self.used_items = ExploreApiItems().usable_items_by_name_dct
        # (the same instance of item creation is needed, so it's stored in a var)
        self.temporary_item_attr_creation_instance = None

    def create_and_return_item_attrs_dct(self):
        """
        Returns a dict containing item attributes.

        :return: (dict)
        """

        dct = {}

        self.temporary_item_attr_creation_instance = ItemAttrCreation(item_name=self.item_name)
        self.temporary_item_attr_creation_instance.create_non_unique_stats_names_and_values()
        self.temporary_item_attr_creation_instance.create_unique_stats_values()
        self.temporary_item_attr_creation_instance.create_item_gen_attrs()
        self.temporary_item_attr_creation_instance.create_item_dmgs()
        self.temporary_item_attr_creation_instance.create_item_buffs()

        dct.update({'secondary_data': self.temporary_item_attr_creation_instance.item_secondary_data_dct()})
        dct.update({'non_unique_stats': self.temporary_item_attr_creation_instance.non_unique_item_stats})
        dct.update({'unique_stats': self.temporary_item_attr_creation_instance.unique_item_stats})
        dct.update({'general_attributes': self.temporary_item_attr_creation_instance.item_gen_attrs})
        dct.update({'dmgs': self.temporary_item_attr_creation_instance.item_dmgs})
        dct.update({'buffs': self.temporary_item_attr_creation_instance.item_buffs})
        dct.update({'stats_dependencies': StatsDependencies().item_stats_dependencies(item_name=self.item_name)})

        return dct

    def create_and_return_current_item_effects_dct(self):
        """
        Creates and returns effects of current item creation instance.
        If no instance has been created (e.g. only effects are being set without earlier data creation)
        uses existing data in items module.

        :return: (dict)
        """

        if self.temporary_item_attr_creation_instance:
            instance = self.temporary_item_attr_creation_instance
            instance.create_item_effects()

            return instance.item_effects

        else:
            # Gets stored data.
            module = Fetch().imported_items_module()
            item_attrs_dct = getattr(module, ITEMS_ATTRS_DCT_NAME)
            # Creates instance and inserts data.
            instance = ItemAttrCreation(item_name=self.item_name)
            instance.item_buffs = item_attrs_dct[self.item_name]['buffs']
            instance.item_gen_attrs = item_attrs_dct[self.item_name]['general_attributes']
            instance.non_unique_item_stats = item_attrs_dct[self.item_name]['non_unique_stats']
            instance.item_dmgs = item_attrs_dct[self.item_name]['dmgs']
            # Uses instance to create effects.
            instance.create_item_effects()

            return instance.item_effects

    def create_and_return_current_item_conditions_dct(self):

        instance = ItemsConditionals(item_name=self.item_name)
        instance.run_conditions_creation()
        return instance.conditions_dct

    def _insert_item_created_attrs_or_effects_or_conds(self, effects_or_attrs_or_conds, auto_replace=False):
        """
        Inserts all data of given item in items' data module.

        Imports or reloads the data module, and checks if item's data is inside items' attributes (or effects) dict.

        :param effects_or_attrs_or_conds: (str) 'effects' or 'attrs'
        :param auto_replace: (bool) When False, asks user for replacement confirmation (if item already existing).
        :return: (None)
        """

        if effects_or_attrs_or_conds == 'attrs':
            property_name = ITEMS_ATTRS_DCT_NAME
            creation_func = self.create_and_return_item_attrs_dct
        elif effects_or_attrs_or_conds == 'effects':
            property_name = ITEMS_EFFECTS_DCT_NAME
            creation_func = self.create_and_return_current_item_effects_dct
        else:
            property_name = ITEMS_CONDITIONS_DCT_NAME
            creation_func = self.create_and_return_current_item_conditions_dct

        # Gets existing stored dict.
        try:
            items_module = Fetch().imported_items_module()
            existing_data_dct = getattr(items_module, property_name)
        except AttributeError:
            existing_data_dct = {}

        self.insert_object_in_dct(obj_name=self.item_name, modified_dct=existing_data_dct,
                                  auto_replace=auto_replace, property_name=property_name,
                                  data_creation_func=creation_func)

        self.insert_object_in_module(obj_name=property_name, new_obj_as_dct_or_str_or_func=existing_data_dct,
                                     replacement_question_msg='', width=1,
                                     targeted_module_path_str='/'.join((ITEMS_MODULES_FOLDER_NAME,
                                                                        ITEMS_DATA_MODULE_NAME)) + '.py',
                                     verify_replacement=False)

    def create_and_insert_item_attrs(self, auto_replace=False):
        self._insert_item_created_attrs_or_effects_or_conds(effects_or_attrs_or_conds='attrs',
                                                            auto_replace=auto_replace)

    def create_and_insert_item_effects(self, auto_replace=False):
        self._insert_item_created_attrs_or_effects_or_conds(effects_or_attrs_or_conds='effects',
                                                            auto_replace=auto_replace)

    def create_and_insert_item_conditionals(self, auto_replace=False):
        """
        Creates and inserts item conditionals.

        :param auto_replace: (bool)
        :return: (None)
        """
        self._insert_item_created_attrs_or_effects_or_conds(effects_or_attrs_or_conds='conds',
                                                            auto_replace=auto_replace)

    def create_item(self):
        self.create_and_insert_item_attrs()
        self.create_and_insert_item_effects()
        self.create_and_insert_item_conditionals()

    @staticmethod
    def create_all_items():
        for item_name in sorted(ExploreApiItems().usable_items_by_name_dct):
            creation_instance = ItemsModuleCreator(item_name=item_name)
            creation_instance.create_item()

    @staticmethod
    def create_not_created_items(excluded_str=None):
        for item_name in sorted(ExploreApiItems().usable_items_by_name_dct):

            if excluded_str:
                if excluded_str.lower() in item_name.lower():
                    print('Auto skipping {}. (contains string: {})'.format(item_name, excluded_str))
                    continue

            if item_name not in Fetch().items_attrs_dct():
                print(fat_delimiter(80))
                if _y_n_question('Create {}?'.format(item_name.upper())):
                    creation_instance = ItemsModuleCreator(item_name=item_name)
                    creation_instance.create_item()


class MasteryModuleCreator(ModuleCreatorBase):

    def create_all_mastery_dcts(self, skip_existing=True):

        all_masteries_names = ExploreApiMasteries().masteries_names()

        # START MSG
        print(fat_delimiter(80))
        print('\nMASTERIES CREATION')
        if skip_existing:
            print('(auto skipping existing)\n')
        else:
            print('(existing will be replaced)\n')

        # CREATION
        for mastery_name in all_masteries_names:

            property_name = MASTERIES_ATTRS_DCT_NAME
            existing_data_dct = Fetch().imported_masteries_module().MASTERIES_ATTRIBUTES

            # Skips existing if required.
            if skip_existing and (mastery_name in existing_data_dct):
                continue

            print(fat_delimiter(80))
            print('\nMASTERY: {}'.format(mastery_name))
            ExploreApiMasteries().mastery_description(mastery_name=mastery_name, print_mode=True)

            if _y_n_question(question_str='Mastery contains data?'):
                mastery_creation_func = MasteryCreation(mastery_name).create_and_return_mastery
            else:
                mastery_creation_func = lambda: {}

            self.insert_object_in_dct(obj_name=mastery_name, modified_dct=existing_data_dct,
                                      auto_replace=False, property_name=property_name,
                                      data_creation_func=mastery_creation_func)

            self.insert_object_in_module(obj_name=property_name, new_obj_as_dct_or_str_or_func=existing_data_dct,
                                         replacement_question_msg='', width=1,
                                         targeted_module_path_str='/'.join((MASTERIES_MODULES_FOLDER_NAME,
                                                                            MASTERIES_DATA_MODULE_NAME)) + '.py',
                                         verify_replacement=False)


# ===============================================================
# ===============================================================
if __name__ == '__main__':

    # ABILITY GEN ATTR CREATION
    if 0:
        for ability_shortcut in palette.SPELL_SHORTCUTS:
            GeneralAbilityAttributes(ability_name=ability_shortcut, champion_name='drmundo').run_gen_attr_creation()
            break

    # DMG ATTR CREATION
    if 0:
        for ability_shortcut in ('q',):
            dmgAttrInstance = DmgAbilityAttributes(ability_name=ability_shortcut, champion_name='teemo')
            dmgAttrInstance.run_dmg_attr_creation()

    # NTH ATTACK
    if 0:
        for champName in ExploreApiAbilities().all_champions_data_dct:
            for abilityName in palette.SPELL_SHORTCUTS:
                res = BuffAbilityAttributes(abilityName, champName).refined_nth_attack()
                if res:
                    print((champName, res))

    # STORING ALL CHAMPIONS DATA
    if 0:
        RequestAllAbilitiesFromAPI().store_all_champions_data()
    # REQUEST ITEMS API
    if 0:
        RequestAllItemsFromAPI().store_all_items_from_api()

    # EXPLORING CHAMPION ABILITIES AND TOOLTIPS
    if 0:
        champName = 'annie'
        ExploreApiAbilities().champion_abilities(champion_name=champName, print_mode=True)
        ExploreApiAbilities().sanitized_tooltips(champ=champName, raw_str=None, print_mode=True)

    # ABILITY ATTRIBUTES
    if 0:
        inst = AbilitiesAttributes(champion_name='jax')
        inst._single_spell_attrs('q')

    # CHAMPION ID
    if 0:
        print(ExploreApiAbilities().champion_id('dariu'))

    # CHAMPION MODULE CREATION
    if 0:
        ChampionModuleCreator(champion_name='vayne').run_champ_module_creation()

    # FETCHING CASTABLE ABILITIES
    if 0:
        castable = Fetch().castable(spell_or_item_name='q', champ_or_item='champion', champ_name='jax')
        print(castable)

    # ITEM ATTR CREATION
    if 0:
        inst = ItemAttrCreation(item_name='gun')
        inst.create_non_unique_stats_names_and_values()
        print(inst.non_unique_item_stats)

    # ITEM ATTRS, EFFECTS AND CONDITIONALS CREATION AND INSERTION
    if 1:
        inst = ItemsModuleCreator(item_name='skirmishers_sabre')
        inst.create_item()
    # Create all items.
    if 1:
        ItemsModuleCreator.create_not_created_items('enchantment')

    # PRETTY FORMAT OBJECT IN MODULE
    if 0:
        inst = ModuleCreatorBase()
        inst.pformat_obj_in_path('APP_RUNES_DCT', 'app_runes_database.py')

    # MASTERIES EXPLORATION
    # Tuple of values detection.
    if 0:
        inst = ExploreApiMasteries()
        l = inst.stats_values_detected('sorcery')
        print(l)
    # Stats names detection.
    if 0:
        inst = ExploreApiMasteries()
        l = inst.stats_names_detected('warlord')
        print(l)

    # MASTERIES CREATION
    if 0:
        inst = MasteryCreation(mastery_name='enchanted_armor')
        inst.create_and_return_mastery(print_mode=True)

    if 0:
        inst = MasteryModuleCreator()
        inst.create_all_mastery_dcts()

    # CHAMPION BASE STATS CALCULATION
    if 0:
        d = ChampionsBaseStats()._app_compatible_champ_base_stats_dct(champ_name='alistar')
        pp.pprint(d)
    # Creates and stores base stats.
    if 0:
        ChampionsBaseStats().store_champions_base_stats()

    # PRIORITY CONDITIONALS (creation, not insertion)
    if 0:
        RotationPriorityConditional('jax').run_conditions_creation()

    # SKILL LVL UP PRIORITIES.
    if 0:
        ChampionModuleCreator('jax').run_single_element_creation(SPELL_LVL_UP_PRIORITIES_NAME)
