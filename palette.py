import copy
import importlib
import pprint
import os
import re

import champion_ids


# WARNING: Do not import dev mods (to avoid circular imports).
# If they are to be imported, note in imported module that it should not import this module.


# ----------------------------------------------------------------------------------------------------------------------
class UnexpectedValueError(Exception):
    """
    NOT TO BE HANDLED!
    Exception indicating that an unexpected value has been given to a variable.
    """
    pass


# ----------------------------------------------------------------------------------------------------------------------
class NotAllowedOperationError(Exception):
    """
    NOT TO BE HANDLED!
    Exception indicating that an operation that is not allowed was performed.
    """
    pass


def _not_allowed_operation_error_func(*args, **kwargs):
    raise NotAllowedOperationError()


# ----------------------------------------------------------------------------------------------------------------------
# NON-ITERABLE STR
class NonIterableStr(str):
    def __iter__(self):
        raise NotAllowedOperationError('Iteration attempted on non iterable string.')


# ----------------------------------------------------------------------------------------------------------------------
# PLACEHOLDER

class PlaceholderUsedError(Exception):
    """
    NOT TO BE HANDLED!
    Raised when placeholder is accidentally used.
    """
    pass


def _placeholder_error_func(*args, **kwargs):
    raise PlaceholderUsedError


class PlaceholderClass(object):
    """
    Used for adding an extra layer of bug preventions when accidentally placeholders have not been removed.

    WARNING: Some accidental uses of a placeholder will not raise an exception as they should.
        Only most common usage is covered.
    """

    def __init__(self, allowed_values=None, data_type=None, non_restricted_choice=False):
        self.__allowed_values = allowed_values
        self.__data_type = data_type
        self.__non_restricted_choice = non_restricted_choice

    @property
    def allowed_values(self):
        return self.__allowed_values

    @property
    def allowed_type(self):
        return self.__data_type

    @property
    def non_restricted_choice(self):
        return self.__non_restricted_choice


SUPPRESSED_MAGIC_METHODS = ('__bool__', '__eq__', '__ge__', '__gt__', '__le__', '__lt__', '__ne__')
for magic_method in SUPPRESSED_MAGIC_METHODS:
    setattr(PlaceholderClass, magic_method, _placeholder_error_func)

placeholder = PlaceholderClass()
placeholder_list = PlaceholderClass(data_type=list)
placeholder_dict = PlaceholderClass(data_type=dict)
placeholder_int = PlaceholderClass(data_type=int)
placeholder_float = PlaceholderClass(data_type=float)
placeholder_bool = PlaceholderClass(data_type=bool)
placeholder_set = PlaceholderClass(data_type=set)
placeholder_str = PlaceholderClass(data_type=str)


# ----------------------------------------------------------------------------------------------------------------------
def all_modules_in_project():
    """
    Finds all modules imported in the current working directory tree.

    :return: (None)
    """

    project_directories = set()
    project_files = set()

    modules_imported = set()

    for path, dirs_names, files_names_in_dir in os.walk(os.getcwd()):
        project_directories |= set(dirs_names)

        for file_name in files_names_in_dir:
            if file_name.endswith('.py'):

                project_files.add(file_name[:-3])

                with open(path + '/' + file_name, 'r') as opened_file:
                    file_lines = opened_file.readlines()

                    for line in file_lines:

                        # import XXX
                        match = re.match(r'import\s([\w\.]+)', line)
                        if match:
                            modules_imported.add(match.groups()[0])

                        # from XXX
                        match = re.match(r'from\s([\w\.]+)', line)
                        if match:
                            modules_imported.add(match.groups()[0])

    # Removes XXX that were matched as follows `import proj_dir. .. .XXX`
    for module in modules_imported.copy():
        matched = re.match(r'(\w+)\.', module)
        if matched:
            pre_dot = matched.groups()[0]

            if pre_dot in project_directories:
                modules_imported.remove(module)

            else:
                # Replaces `xxx.yyy` with `xxx`
                modules_imported.remove(module)
                modules_imported.add(pre_dot)

    return modules_imported - project_files - project_directories


# ----------------------------------------------------------------------------------------------------------------------
# COMPARATOR

def __print_extra_elements_msg(depth_and_path_str_msg, both_full_objects_msg, extra_elements_1, extra_elements_2,
                               str_elements_or_keys):
    msg = depth_and_path_str_msg + both_full_objects_msg
    msg += 'Extra {}: \n'.format(str_elements_or_keys.upper())
    msg += '1:    {}\n'.format(sorted(extra_elements_1))
    msg += '2:    {}\n\n'.format(sorted(extra_elements_2))

    print(msg)


def almost_equal(num_1, num_2, relative_delta=10**-6):
    """
    Checks if given numbers are almost equal to one another.

    :return: (bool)
    """

    if relative_delta > 1:
        raise ValueError('Relative delta too large.')

    diff = abs(num_1 - num_2)

    given_relative_delta = diff / num_1

    if given_relative_delta <= relative_delta:
        return True
    else:
        return False


def __compare_complex_object(obj_1, obj_2, _depth=0, _path_str='', _difference_detected=False):
    """
    Prints differences of 2 given dicts.

    Avoid using when given objects contain a list of dicts.
    """

    if obj_1 == obj_2:
        return _difference_detected

    pformated_1 = pprint.pformat(obj_1, width=10**6)
    pformated_2 = pprint.pformat(obj_2, width=10**6)
    depth_and_path_str_msg = 'DEPTH: {}, PATH: {}\n'.format(_depth, _path_str)
    both_full_objects_msg = 'Full objects: \n1:    {}\n2:    {}\n'.format(pformated_1, pformated_2)

    # Different types.
    if type(obj_1) != type(obj_2):
        _difference_detected = True
        different_types_msg = depth_and_path_str_msg + both_full_objects_msg
        different_types_msg += 'Different TYPES\n\n'

        print(different_types_msg)
        return _difference_detected

    # SETS
    if isinstance(obj_1, set):
        extra_elements_1 = obj_1-obj_2
        extra_elements_2 = obj_2-obj_1

        if extra_elements_1 or extra_elements_2:
            _difference_detected = True

            __print_extra_elements_msg(depth_and_path_str_msg=depth_and_path_str_msg,
                                       both_full_objects_msg=both_full_objects_msg,
                                       extra_elements_1=extra_elements_1,
                                       extra_elements_2=extra_elements_2,
                                       str_elements_or_keys='elements')

    # DICTS
    elif isinstance(obj_1, dict):
        # Dict keys
        keys_1 = obj_1.keys()
        keys_2 = obj_2.keys()

        extra_keys_1 = keys_1 - keys_2
        extra_keys_2 = keys_2 - keys_1
        if extra_keys_1 or extra_keys_2:
            _difference_detected = True

            __print_extra_elements_msg(depth_and_path_str_msg=depth_and_path_str_msg,
                                       both_full_objects_msg=both_full_objects_msg,
                                       extra_elements_1=extra_keys_1,
                                       extra_elements_2=extra_keys_2,
                                       str_elements_or_keys='keys')

        # Dict values
        for k in sorted(obj_1):
            # (key must exist in both dicts to compare its values)
            if k not in obj_2:
                continue

            dict_val_1 = obj_1[k]
            dict_val_2 = obj_2[k]

            # (same values are skipped)
            if dict_val_1 == dict_val_2:
                continue
            else:
                new_path = _path_str + '[' + str(k) + ']'
                new_depth = _depth + 1
                _difference_detected = __compare_complex_object(obj_1=dict_val_1, obj_2=dict_val_2,
                                                                _depth=new_depth, _path_str=new_path,
                                                                _difference_detected=_difference_detected)

    # LIST, TUPLE
    elif type(obj_1) in (list, tuple):
        # Same size
        if len(obj_1) == len(obj_2):
            for i, j in zip(obj_1, obj_2):
                new_path = _path_str + '[' + 'SEQUENCE' + ']'
                new_depth = _depth + 1
                _difference_detected = __compare_complex_object(obj_1=i, obj_2=j,
                                                                _depth=new_depth,
                                                                _path_str=new_path,
                                                                _difference_detected=_difference_detected)

        # Different size
        else:
            _difference_detected = True

            obj_1_as_set = {tuple(i) for i in obj_1}
            obj_2_as_set = {tuple(i) for i in obj_2}

            extra_elements_1 = obj_1_as_set - obj_2_as_set
            extra_elements_2 = obj_2_as_set - obj_1_as_set
            __print_extra_elements_msg(depth_and_path_str_msg=depth_and_path_str_msg,
                                       both_full_objects_msg=both_full_objects_msg,
                                       extra_elements_1=extra_elements_1,
                                       extra_elements_2=extra_elements_2,
                                       str_elements_or_keys='elements')

    # NUMBER
    elif type(obj_1) in (int, float):
        if not almost_equal(obj_1, obj_2):
            diff_objects_msg = depth_and_path_str_msg + both_full_objects_msg
            diff_objects_msg += 'DIFFERENT objects \n\n'

            print(diff_objects_msg)

    elif isinstance(obj_1, str):
        if obj_1 != obj_2:
            diff_objects_msg = depth_and_path_str_msg + both_full_objects_msg
            diff_objects_msg += 'DIFFERENT strings \n\n'

            print(diff_objects_msg)

    else:
        raise UnexpectedValueError

    return _difference_detected


def compare_complex_object(obj_1, obj_2):
    return __compare_complex_object(obj_1=obj_1, obj_2=obj_2)


# ----------------------------------------------------------------------------------------------------------------------
class FrozenKeysDict(dict):
    """Disallows insertion of new keys and deletion of existing keys once the dict has been created. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __delitem__(self, *args, **kwargs):
        raise NotAllowedOperationError

    def __setitem__(self, key, value):
        raise NotAllowedOperationError


# ----------------------------------------------------------------------------------------------------------------------
def x_to_x_dct(seq):
    """
    Used to ensure change to a string is forced in distant locations in code as well.

    e.g.
    Allows replacing:
        `if 'x' in some_iterable`

    with this:
        `if name.x in some_iterable`

    :return: (dict) Each value is the same as its key, that is k1==v1, k2==v2 etc.
    """

    return {i: i for i in seq}


class XToX(FrozenKeysDict):
    """
    Used to ensure object names are within allowed names.
    Makes the verification process easier by allowing different ways of using the names.

    Allows replacing:
        `if 'x' in some_iterable`

    with either of the following:
        `if allowed_vals.x in some_iterable`
        `if 'allowed_vals['x'] in some_iterable`

    """

    def __init__(self, seq):
        d = x_to_x_dct(seq=seq)
        super().__init__(**d)
        self.turn_keys_into_properties()

    def turn_keys_into_properties(self):
        """
        Converts all dict keys into properties.
        Raises exception if given property shouldn't be inserted because it conflicts with an existing property.

        :return:
        """
        for k, v in self.items():
            if k in dir(self):
                raise UnexpectedValueError('{} already exists as dict-class property.'.format(k))

            else:
                setattr(self, k, v)


# ----------------------------------------------------------------------------------------------------------------------
class SpecifiedKeysDict(dict):
    """
    Allows creation of a dict only with specified keys.
    Keys can be removed or reinserted but only if they are within the allowed.

    Allowed keys that were not explicitly given are set to a false-typed value.
    """

    MANDATORY_KEYS = set()
    OPTIONAL_KEYS = set()
    ALLOWED_KEYS = MANDATORY_KEYS | OPTIONAL_KEYS

    EXTRA_KEY_DETECTED_MSG = 'Extra keys given ({}). Keys are restricted only to "ALLOWED_KEYS".'

    def __init__(self, given_dct):
        given_dct_keys = given_dct.keys()

        # Disallows extra keys.
        extra_keys = given_dct_keys - self.ALLOWED_KEYS
        if extra_keys:
            raise UnexpectedValueError(self.EXTRA_KEY_DETECTED_MSG.format(extra_keys))

        # Disallows omitting mandatory keys.
        self.mandatory_keys_omitted = self.MANDATORY_KEYS - given_dct_keys
        if self.mandatory_keys_omitted:
            raise UnexpectedValueError('Mandatory keys omitted: {}'.format(self.mandatory_keys_omitted))

        # Auto inserts optional keys with False-type value.
        full_dct = {i: {} for i in self.OPTIONAL_KEYS}
        full_dct.update(given_dct)
        super().__init__(full_dct)

    def __setitem__(self, key, value):
        if key not in self.ALLOWED_KEYS:
            raise KeyError('Trying to insert new key ({}) in a SafeDict.'.format(key))
        dict.__setitem__(self, key, value)

    def delete_keys(self, sequence):
        """
        Deletes all keys in given sequence.

        Used to make deletion of multiple keys less verbose.

        :return: (None)
        """
        for i in sequence:
            del self[i]

    def update(self, *args, **kwargs):
        if (set(kwargs) - self.ALLOWED_KEYS) or (set(*args) - self.ALLOWED_KEYS):
            raise UnexpectedValueError(self.EXTRA_KEY_DETECTED_MSG)
        dict.update(*args, **kwargs)

# ----------------------------------------------------------------------------------------------------------------------


TARGET_TYPES = ('player', 'enemy')

COMPARISON_OPERATOR_STRINGS = ('>', '<', '==', '<=', '>=')

ALLOWED_ABILITY_LVLS = ('1', '2', '3', '4', '5', '0')

SPELL_SHORTCUTS = ('q', 'w', 'e', 'r')
ABILITY_SHORTCUTS = ('inn', ) + SPELL_SHORTCUTS
EXTRA_SPELL_SHORTCUTS = ('q2', 'w2', 'e2', 'r2')
ALL_POSSIBLE_SPELL_SHORTCUTS = SPELL_SHORTCUTS + EXTRA_SPELL_SHORTCUTS
ALL_POSSIBLE_ABILITIES_SHORTCUTS = ABILITY_SHORTCUTS + EXTRA_SPELL_SHORTCUTS

ALL_CHAMPIONS_NAMES = champion_ids.CHAMPION_IDS.values()


DMG_TYPES = ('magic', 'physical', 'true', 'AA')


# ----------------------------------------------------------------------------------------------------------------------
# BUFF
BUFF_DCT_BASE = dict(
    buff_source=placeholder,
    dot=placeholder,
    duration=placeholder,
    max_stacks=placeholder,
    max_targets=placeholder,      # Refers to max number of targets that can get the effect from a single application
    on_hit=dict(
        apply_buff=[placeholder, ],
        cause_dmg=[placeholder, ],
        cds_modified={},
        remove_buff=[placeholder, ]
    ),
    stats=dict(
        placeholder_stat_1=placeholder
    ),
    target_type=placeholder,
    usual_max_targets=placeholder,
)

OPTIONAL_BUFF_KEYS = ('shield', 'aura', 'prohibit_cd_start', 'on_being_hit')


def buff_dct_base_deepcopy():
    return copy.deepcopy(BUFF_DCT_BASE)


class SafeBuff(SpecifiedKeysDict):
    """
    Allows creation of a buff dict only with specified keys.
    Keys can be removed or reinserted but only if they are within the allowed.
    """

    MANDATORY_KEYS = set(BUFF_DCT_BASE.keys())
    OPTIONAL_KEYS = set(OPTIONAL_BUFF_KEYS)
    ALLOWED_KEYS = MANDATORY_KEYS | OPTIONAL_KEYS

BUFF_ATTRS_NAMES = x_to_x_dct(SafeBuff.ALLOWED_KEYS)

SHIELD_ATTRS = {'shield_type': placeholder,
                'shield_value': placeholder}


BUFF_DOT_ATTRS = {'period': placeholder,
                  'dmg_names': placeholder_list,
                  'always_on_x_targets': placeholder}     # False or int.


# ----------------------------------------------------------------------------------------------------------------------
# DMG
DMG_DCT_BASE = dict(
    crit_type=placeholder,
    delay=placeholder,
    dmg_category=placeholder,
    dmg_source=placeholder,
    dmg_type=placeholder,
    dmg_values=placeholder,
    dot=placeholder,
    heal_for_dmg_amount=placeholder_bool,
    life_conversion_type=placeholder,     # (None or lifesteal or spellvamp)
    resource_type=placeholder,
    max_targets=placeholder,  # Refers to max number of targets that can get the effect from a single application
    mods=placeholder,     # (None or 'normal': {stat1: coeff1,} or 'by_ability_lvl': {stat1: (coeff_lvl1,),})
    radius=placeholder,
    target_type=placeholder,
    usual_max_targets=placeholder,
)


OPTIONAL_DMG_KEYS = ('on_kill',)


class SafeDmg(SpecifiedKeysDict):
    MANDATORY_KEYS = set(DMG_DCT_BASE.keys())
    OPTIONAL_KEYS = set(OPTIONAL_DMG_KEYS)
    ALLOWED_KEYS = MANDATORY_KEYS | OPTIONAL_KEYS

DMG_ATTRS_NAMES = x_to_x_dct(SafeDmg.ALLOWED_KEYS)

DMG_DOT_ATTRS = {'dot_buff': placeholder_str,
                 'jumps_on_death': placeholder_bool}


CRIT_TYPES = (None, 'normal', 'always')


SHIELDS_DATA = {'shield_type': placeholder,
                'mods': {},
                'shield_value': placeholder}

# (currently no other types exist in-game)
SHIELD_TYPES = ('any', 'magic')


# ----------------------------------------------------------
_ON_X_EFFECTS_BASE = dict(
    cause_dmg=[],
    apply_buff=[],
    remove_buff=[],
    cds_modified={},
)


def on_x_effects_base_deepcopy():
    return copy.deepcopy(_ON_X_EFFECTS_BASE)


# ----------------------------------------------------------
EVERY_NTH_BASE = {
    'max_n': placeholder_int,       # value at which the effects occur
    'starting_n': placeholder,      # int or 'max'
    'on_hit': placeholder_dict,
    'counter_duration': placeholder_float,
    'stacks_per_hit': placeholder_int,
    'stacks_per_movement_unit': placeholder_float,
    'reset_on_aa_target_change': placeholder_bool,
}


# ----------------------------------------------------------
ON_HIT_EFFECTS = on_x_effects_base_deepcopy()
ON_BEING_HIT = on_x_effects_base_deepcopy()

ON_ENEMY_DEATH = {
    # (that is, dmgs names; NOT categories)
    'causes_of_death': PlaceholderClass(allowed_values=['any'])
}
ON_ENEMY_DEATH.update(on_x_effects_base_deepcopy())

# WARNING:
# On-dmg and on-dealing-dmg effects are used inside a dmg dict and inside a buff dict respectively.

ON_DMG_EFFECTS = on_x_effects_base_deepcopy()

ON_DEALING_DMG = {
    'dmg_types': PlaceholderClass(['any', 'physical', 'magic', 'true'], data_type=list, non_restricted_choice=True),
    'source_types_or_names': PlaceholderClass(['any', 'champion_abilities', 'champion_spells', 'summoner_spells'])
}
ON_DEALING_DMG.update(on_x_effects_base_deepcopy())

# (not used, probably never will be used since "_EFFECTS" dicts serve that purpose)
ON_ACTION_EFFECTS = {
    'increase_counter_stat':
        {'counter_stat_name': placeholder,
         'value_increase': placeholder}}
ON_ACTION_EFFECTS.update(on_x_effects_base_deepcopy())


ON_ACTION_TRIGGERS = dict(
    cost_mandatory=(True, False),
    sources_names_ignored={'placeholder_source_category': 'placeholder_source_name', },
    sources_categories_ignored=('items', 'masteries', 'summoner_spells', 'champion_spells'),
)


# ----------------------------------------------------------------------------------------------------------------------
GENERAL_ATTRIBUTES = dict(
    cast_time=placeholder_float,
    range=placeholder,
    travel_time=placeholder_float,
    base_cd=placeholder,
    cost=[
        dict(
            resource_type=placeholder,
            values=placeholder,
            cost_category=placeholder
        ), ],
    independent_cast=placeholder_bool,
    move_while_casting=placeholder_bool,
    dashed_distance=placeholder_int,
    channel_time=placeholder,
    resets_aa=placeholder_bool,
    apply_on_hit_effects=placeholder_bool,
    cds_modified=dict(
        name_placeholder=placeholder
    )
)

OPTIONAL_GENERAL_ATTRIBUTES_NAMES = (
    'apply_on_hit_effects'
)


class SafeGeneralAttributes(SpecifiedKeysDict):
    MANDATORY_KEYS = set(GENERAL_ATTRIBUTES.keys())
    OPTIONAL_KEYS = set()
    ALLOWED_KEYS = MANDATORY_KEYS | OPTIONAL_KEYS


# ----------------------------------------------------------------------------------------------------------------------
def inn_effects():
    return dict(
            # buffs and effects activated at skill lvl up
            passives=dict(buffs=[],
                          remove_buff=[])
    )


def spell_effects():
    return dict(

            # Buffs and effects activated at skill lvl up.
            passives=dict(buffs=[],
                          remove_buff=[],
                          dmg=[]),

            # Buffs and effects activated on cast.
            actives=dict(buffs=[],
                         remove_buff=[],
                         dmg=[],
                         cds_modified={})
    )


def frozen_keys_spell_effects():
    return FrozenKeysDict(

        # Buffs and effects activated at skill lvl up.
        passives=FrozenKeysDict(buffs=[],
                                remove_buff=[],
                                dmg=[]),

        # Buffs and effects activated on cast.
        actives=FrozenKeysDict(buffs=[],
                               remove_buff=[],
                               dmg=[],
                               cds_modified={})
    )


def item_effects():
    dct = spell_effects()
    del dct['actives']['cds_modified']

    return dct


def dmg_dct_base_deepcopy():
    return copy.deepcopy(DMG_DCT_BASE)


class DuplicateNameError(Exception):
    """
    To be raised when a duplicate buff or dmg name is found.

    Duplicate buffs or dmgs can cause bugs when translated.
    """
    pass


def items_or_masteries_buffs_or_dmgs_names_dct(str_buffs_or_dmgs, attrs_dct):
    """
    Creates a dict of all items' (or masteries') dmgs or buffs names as keys, and corresponding item name as value.

    :param str_buffs_or_dmgs: (str) 'dmgs', 'buffs'
    :return: (dict) Key: buff name, value: item name
    """

    dct = {}

    for obj_name in attrs_dct:
        if str_buffs_or_dmgs in attrs_dct[obj_name]:
            for attr_name in attrs_dct[obj_name][str_buffs_or_dmgs]:

                dct.update({attr_name: obj_name})

    return dct


def champion_buffs_or_dmgs_names_lst(champion_name, str_buffs_or_dmgs):
    """

    :param champion_name: (str)
    :param str_buffs_or_dmgs: (str) 'dmgs', 'buffs'
    :return: (list)
    """
    path_str = 'champions' + '.' + champion_name
    module = importlib.import_module(path_str)

    lst = sorted(module.ABILITIES_ATTRIBUTES[str_buffs_or_dmgs])

    return lst


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


if __name__ == '__main__':

    from pprint import pprint as pp
    pp(all_modules_in_project())
