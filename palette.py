import copy
import importlib


TARGET_TYPES = ('player', 'enemy')

COMPARISON_OPERATOR_STRINGS = ('>', '<', '==', '<=', '>=')

ALLOWED_ABILITY_LVLS = ('1', '2', '3', '4', '5', '0')

SPELL_SHORTCUTS = ('q', 'w', 'e', 'r')
ABILITY_SHORTCUTS = ('inn', ) + SPELL_SHORTCUTS
EXTRA_SPELL_SHORTCUTS = ('q2', 'w2', 'e2', 'r2')
ALL_POSSIBLE_SPELL_SHORTCUTS = SPELL_SHORTCUTS + EXTRA_SPELL_SHORTCUTS
ALL_POSSIBLE_ABILITIES_SHORTCUTS = ABILITY_SHORTCUTS + EXTRA_SPELL_SHORTCUTS


BUFF_DCT_BASE = dict(
    target_type='placeholder',
    duration='placeholder',
    max_stacks='placeholder',
    stats=dict(
        placeholder_stat_1='placeholder'
    ),
    on_hit=dict(
        apply_buff=['placeholder', ],
        cause_dmg=['placeholder', ],
        cds_modified={},
        remove_buff=['placeholder', ]
    ),
    prohibit_cd_start='placeholder',
    buff_source='placeholder',
    dot=False,
)


def buff_dct_base_deepcopy():
    return copy.deepcopy(BUFF_DCT_BASE)


DMG_DCT_BASE = dict(
    target_type='placeholder',
    dmg_category='placeholder',
    resource_type='placeholder',
    dmg_type='placeholder',
    dmg_values='placeholder',
    dmg_source='placeholder',
    # (None or 'normal': {stat1: coeff1,} or 'by_ability_lvl': {stat1: (coeff_lvl1,),})
    mods='placeholder',
    # (None or lifesteal or spellvamp)
    life_conversion_type='placeholder',
    radius='placeholder',
    dot={'dot_buff': 'placeholder'},
    max_targets='placeholder',
    delay='placeholder',
    crit_type='placeholder'
)


CRIT_TYPES = (None, 'normal', 'always')


SHIELDS_DATA = {'shield_type': 'placeholder',
                'mods': {},
                'shield_value': 'placeholder'}


ON_HIT_EFFECTS = dict(
    cause_dmg=[],
    apply_buff=[],
    remove_buff=[],
    cds_modified={},
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
