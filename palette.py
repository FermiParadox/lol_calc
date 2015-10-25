import copy
import importlib
import pprint

# WARNING: Do not import dev mods (to avoid circular imports).


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
# PLACEHOLDER

class PlaceholderUsedError(Exception):
    """
    NOT TO BE HANDLED!
    Raised when placeholder is accidentally used.
    """
    pass


def _placeholder_error_func(*args, **kwargs):
    raise PlaceholderUsedError


class Placeholder(object):
    """
    Used to add an extra layer of bug preventions when accidentally placeholders have not been removed.

    It is not bulletproof, some accidental uses of a placeholder will not raise an exception as they should.
    Only most common usages are covered.
    """

    def __init__(self, optional_value=None):
        self.__optional_value = optional_value

    @property
    def value(self):
        return self.__optional_value


SUPPRESSED_MAGIC_METHODS = ('__bool__', '__eq__', '__ge__', '__gt__', '__le__', '__lt__', '__ne__')
for magic_method in SUPPRESSED_MAGIC_METHODS:
    setattr(Placeholder, magic_method, _placeholder_error_func)

PlaceholderList = PlaceholderDict = PlaceholderInt = PlaceholderBool = PlaceholderSet = PlaceholderStr = Placeholder


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
class SafeValueInsertionDict(dict):
    """
    Disallows creation of a non existing key through d[new_key] = val.
    """
    def __setitem__(self, key, value):
        if key not in self:
            raise KeyError('{}'.format(key))
        dict.__setitem__(self, key, value)


class SpecifiedKeysDict(SafeValueInsertionDict):
    """
    Allows creation of a dict only with specified keys.
    Keys can be removed or reinserted but only if they are within the allowed.
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
        full_dct = {i: False for i in self.OPTIONAL_KEYS}
        full_dct.update(given_dct)
        super().__init__(**full_dct)

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


# BUFF
BUFF_DCT_BASE = dict(
    buff_source=Placeholder(),
    dot=Placeholder(),
    duration=Placeholder(),
    max_stacks=Placeholder(),
    max_targets=Placeholder(),      # Refers to max number of targets that can get the effect from a single application
    on_hit=dict(
        apply_buff=[Placeholder(), ],
        cause_dmg=[Placeholder(), ],
        cds_modified={},
        remove_buff=[Placeholder(), ]
    ),
    stats=dict(
        placeholder_stat_1=Placeholder()
    ),
    target_type=Placeholder(),
    usual_max_targets=Placeholder(),
)

OPTIONAL_BUFF_KEYS = ('shield', 'aura', 'prohibit_cd_start')


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


SHIELD_ATTRS = {'shield_type': Placeholder(),
                'shield_value': Placeholder()}


BUFF_DOT_ATTRS = {'period': Placeholder(),
                  'dmg_names': PlaceholderList(),
                  'always_on_x_targets': Placeholder()}     # False or int.


# ----------------------------------------------------------------------------------------------------------------------
# DMG
DMG_DCT_BASE = dict(
    crit_type=Placeholder(),
    delay=Placeholder(),
    dmg_category=Placeholder(),
    dmg_source=Placeholder(),
    dmg_type=Placeholder(),
    dmg_values=Placeholder(),
    dot=Placeholder(),
    heal_for_dmg_amount=PlaceholderBool(),
    life_conversion_type=Placeholder(),     # (None or lifesteal or spellvamp)
    resource_type=Placeholder(),
    max_targets=Placeholder(),  # Refers to max number of targets that can get the effect from a single application
    mods=Placeholder(),     # (None or 'normal': {stat1: coeff1,} or 'by_ability_lvl': {stat1: (coeff_lvl1,),})
    radius=Placeholder(),
    target_type=Placeholder(),
    usual_max_targets=Placeholder(),
)


OPTIONAL_DMG_KEYS = ()


class SafeDmg(SpecifiedKeysDict):
    MANDATORY_KEYS = set(DMG_DCT_BASE.keys())
    OPTIONAL_KEYS = set(OPTIONAL_DMG_KEYS)
    ALLOWED_KEYS = MANDATORY_KEYS | OPTIONAL_KEYS


DMG_DOT_ATTRS = {'dot_buff': PlaceholderStr(),
                 'jumps_on_death': PlaceholderBool()}


CRIT_TYPES = (None, 'normal', 'always')


SHIELDS_DATA = {'shield_type': Placeholder(),
                'mods': {},
                'shield_value': Placeholder()}

# (currently no other types exist in-game)
SHIELD_TYPES = ('any', 'magic')


ON_HIT_EFFECTS = dict(
    cause_dmg=[],
    apply_buff=[],
    remove_buff=[],
    cds_modified={},
)


ON_ACTION_EFFECTS = {
    'increase_counter_stat':
        {'counter_stat_name': Placeholder(),
         'value_increase': Placeholder()}}
ON_ACTION_EFFECTS.update(ON_HIT_EFFECTS)


ON_ACTION_TRIGGERS = dict(
    cost_mandatory=(True, False),
    sources_names_ignored={'placeholder_source_category': 'placeholder_source_name', },
    sources_categories_ignored=('items', 'masteries', 'summoner_spells', 'champion_spells'),
)


# ----------------------------------------------------------------------------------------------------------------------
GENERAL_ATTRIBUTES = dict(
    cast_time=Placeholder(),
    range=Placeholder(),
    travel_time=Placeholder(),
    base_cd=Placeholder(),
    cost=[
        dict(
            resource_type=Placeholder(),
            values=Placeholder(),
            cost_category=Placeholder()
        ), ],
    independent_cast=Placeholder(),
    move_while_casting=Placeholder(),
    dashed_distance=Placeholder(),
    channel_time=Placeholder(),
    resets_aa=Placeholder(),
    cds_modified=dict(
        name_placeholder=Placeholder()
    )
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
    print()
