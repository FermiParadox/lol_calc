import copy
import importlib
import pprint


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
# SAFE DICT
class SafeDict(dict):
    """
    Disallows creation of a non existing key through d[new_key] = val.
    """
    def __setitem__(self, key, value):
        if key not in self:
            raise KeyError('{}'.format(key))
        dict.__setitem__(self, key, value)


# ----------------------------------------------------------------------------------------------------------------------


TARGET_TYPES = ('player', 'enemy')

COMPARISON_OPERATOR_STRINGS = ('>', '<', '==', '<=', '>=')

ALLOWED_ABILITY_LVLS = ('1', '2', '3', '4', '5', '0')

SPELL_SHORTCUTS = ('q', 'w', 'e', 'r')
ABILITY_SHORTCUTS = ('inn', ) + SPELL_SHORTCUTS
EXTRA_SPELL_SHORTCUTS = ('q2', 'w2', 'e2', 'r2')
ALL_POSSIBLE_SPELL_SHORTCUTS = SPELL_SHORTCUTS + EXTRA_SPELL_SHORTCUTS
ALL_POSSIBLE_ABILITIES_SHORTCUTS = ABILITY_SHORTCUTS + EXTRA_SPELL_SHORTCUTS


BUFF_DCT_BASE = dict(
    target_type=Placeholder(),
    duration=Placeholder(),
    max_stacks=Placeholder(),
    stats=dict(
        placeholder_stat_1=Placeholder()
    ),
    on_hit=dict(
        apply_buff=[Placeholder(), ],
        cause_dmg=[Placeholder(), ],
        cds_modified={},
        remove_buff=[Placeholder(), ]
    ),
    prohibit_cd_start=Placeholder(),
    buff_source=Placeholder(),
    dot=False,
)


def buff_dct_base_deepcopy():
    return copy.deepcopy(BUFF_DCT_BASE)


DMG_DCT_BASE = dict(
    target_type=Placeholder(),
    dmg_category=Placeholder(),
    resource_type=Placeholder(),
    dmg_type=Placeholder(),
    dmg_values=Placeholder(),
    dmg_source=Placeholder(),
    # (None or 'normal': {stat1: coeff1,} or 'by_ability_lvl': {stat1: (coeff_lvl1,),})
    mods=Placeholder(),
    # (None or lifesteal or spellvamp)
    life_conversion_type=Placeholder(),
    radius=Placeholder(),
    dot={'dot_buff': Placeholder()},
    max_targets=Placeholder(),
    delay=Placeholder(),
    crit_type=Placeholder(),
    heal_for_dmg_amount=Placeholder((False, True))
)


CRIT_TYPES = (None, 'normal', 'always')


SHIELDS_DATA = {'shield_type': Placeholder(),
                'mods': {},
                'shield_value': Placeholder()}


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


def dmg_dct_base_deepcopy():
    return copy.deepcopy(DMG_DCT_BASE)


class UnexpectedValueError(Exception):
    """
    NOT TO BE HANDLED!
    Exception indicating that an unexpected value has been given to a variable.
    """
    pass


class DuplicateNameError(Exception):
    """
    To be raised when a duplicate buff or dmg name is found.

    Duplicate buffs or dmgs can cause bugs when translated.
    """
    pass


def items_or_masteries_buffs_or_dmgs_names_dct(str_buffs_or_dmgs, attrs_dct):
    """
    Creates a dict of all items' (or masteries') dmgs or buffs names as keys, and corresponding item name as value.

    Raises error if duplicate names are found.

    :param str_buffs_or_dmgs: (str) 'dmgs', 'buffs'
    :return: (dict) Key: buff name, value: item name
    """

    dct = {}

    for obj_name in attrs_dct:
        if str_buffs_or_dmgs in attrs_dct[obj_name]:
            for attr_name in attrs_dct[obj_name][str_buffs_or_dmgs]:

                # Checks if obj already exists.
                if attr_name in dct:
                    raise DuplicateNameError(attr_name)
                # Adds obj name to list
                else:
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


class ChampionsStats(object):

    @staticmethod
    def inn_effects():
        return dict(
            enemy=dict(

                # buffs and effects activated at skill lvl up
                passives=dict(buffs=[],
                              remove_buff=[])),

            player=dict(

                # buffs and effects activated at skill lvl up
                passives=dict(buffs=[],
                              remove_buff=[]))
        )

    @staticmethod
    def spell_effects():
        return dict(
            enemy=dict(

                # Buffs and effects activated at skill lvl up.
                passives=dict(buffs=[],
                              remove_buff=[],
                              dmg=[]),

                # Buffs and effects activated on cast.
                actives=dict(buffs=[],
                             remove_buff=[],
                             dmg=[])),

            player=dict(

                # Buffs and effects activated at skill lvl up.
                passives=dict(buffs=[],
                              remove_buff=[],
                              dmg=[]),

                # Buffs and effects activated on cast.
                actives=dict(buffs=[],
                             remove_buff=[],
                             dmg=[],
                             cds_modified={}))
        )

    def item_effects(self):
        dct = self.spell_effects()
        del dct['player']['actives']['cds_modified']

        return dct


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
