import copy
import palette
import functools

from champions import app_champions_base_stats


ALL_RESOURCE_NAMES = frozenset({'mp', 'energy', 'rage', None, 'flow', 'hp'})

RESOURCE_CURRENT_STAT_NAMES = frozenset({'current_'+i for i in ALL_RESOURCE_NAMES if i is not None})
RESOURCE_TO_CURRENT_RESOURCE_MAP = {i: 'current_'+i for i in ALL_RESOURCE_NAMES if i is not None}

CURRENT_TYPE_STATS = RESOURCE_CURRENT_STAT_NAMES | {'current_hp', }

DEFENSIVE_SPECIAL_STATS = frozenset({'percent_physical_reduction_by_armor',
                                     'percent_magic_reduction_by_mr',
                                     'reduced_armor',
                                     'reduced_mr',
                                     'physical_dmg_taken',
                                     'magic_dmg_taken',
                                     })


# Contains 2 stat variants of a defense reducing stat; one for armor and one for mr.
# e.g. percent_armor_reduction and percent_mr_reduction
# (used for a method, to avoid code repetition)
_DEFENSE_REDUCING_MR_AND_ARMOR_MAP = dict(
    armor=dict(
        _percent_reduction='percent_armor_reduction',
        _percent_penetration='percent_armor_penetration',
        _flat_reduction='flat_armor_reduction',
        _flat_penetration='flat_armor_penetration',
    ),
    mr=dict(
        _percent_reduction='percent_mr_reduction',
        _percent_penetration='percent_mr_penetration',
        _flat_reduction='flat_mr_reduction',
        _flat_penetration='flat_mr_penetration',
    )
)


# Defensive stats that normally exist without need of special function to create
# (contains deepest dict values from DEFENSE_REDUCING_STATS)
# Dmg reductions and extra dmg dealt modifiers are both expressed by the same stats, and are always multiplicative.
DEFENSIVE_NORMAL_STATS = {'flat_AA_reduction', 'crit_dmg_reduction',
                          'flat_dmg_reduction', 'flat_physical_dmg_reduction', 'flat_magic_dmg_reduction', 'tenacity',
                          'flat_non_aoe_reduction', 'flat_aoe_reduction', 'slow_reduction', 'flat_survivability',
                          'percent_survivability', }
# (flat and percent survivability must have ONLY additive bonuses)
for armor_or_mr in _DEFENSE_REDUCING_MR_AND_ARMOR_MAP:
    for _key in _DEFENSE_REDUCING_MR_AND_ARMOR_MAP[armor_or_mr]:
        DEFENSIVE_NORMAL_STATS.update({_DEFENSE_REDUCING_MR_AND_ARMOR_MAP[armor_or_mr][_key]})

PERCENT_SPECIAL_STATS_SET = frozenset({'percent_armor_penetration',
                                       'percent_AA_reduction',
                                       'percent_aoe_reduction',
                                       'percent_non_aoe_reduction',
                                       'percent_magic_penetration',
                                       'percent_dmg_reduction',
                                       'percent_physical_dmg_reduction',
                                       'percent_mr_penetration',
                                       'percent_magic_dmg_reduction'})

# Contains all champions' base stats names.
BASE_STATS = set()
for _champ_name in app_champions_base_stats.CHAMPION_BASE_STATS:
    for _base_stat_name in app_champions_base_stats.CHAMPION_BASE_STATS[_champ_name]:
        BASE_STATS.update({_base_stat_name})


# Stats by items or buffs that are not calculated by their own (special) method.
NORMAL_STAT_NAMES = {'percent_healing_reduction'}

# Extracted from rune_stat_names_map with: re.findall(r'\'(\w+)\'', s)
RUNE_STAT_NAMES = frozenset({'ap', 'mr', 'mr_per_lvl', 'armor_per_lvl', 'crit_chance', 'ap_per_lvl', 'hp_per_lvl',
                             'mp5', 'hp5_per_lvl', 'xp', 'energy', 'ep5_per_lvl', 'gp5', 'hp', 'att_speed',
                             'mp5_per_lvl', 'death_time_reduction', 'ep5', 'spellvamp', 'crit_modifier',
                             'mp_per_lvl', 'flat_armor_penetration', 'mp', 'ad', 'ad_per_lvl', 'hp5',
                             'lifesteal', 'move_speed', 'armor', 'energy_per_lvl', 'flat_magic_penetration',
                             'hp', 'cdr_per_lvl', 'cdr'})


ALL_STANDARD_STAT_NAMES = frozenset(
    (NORMAL_STAT_NAMES | BASE_STATS | RUNE_STAT_NAMES | RESOURCE_CURRENT_STAT_NAMES | DEFENSIVE_NORMAL_STATS | PERCENT_SPECIAL_STATS_SET) - ALL_RESOURCE_NAMES)


# All bonus_ stats can be calculated through corresponding method, but only those noted below are allowed.
ALLOWED_BONUS_STATS = frozenset({'bonus_ad',
                                 'bonus_armor',
                                 'bonus_mr',
                                 'bonus_hp'})

BONUS_STAT_NAME_TO_BASE_NAME_MAP = {
    'bonus_ad': 'ad',
    'bonus_armor': 'armor',
    'bonus_mr': 'mr',
    'bonus_hp': 'hp'
}


# Contains stats that are not included in base_stats_dct and are calculated separately by their own methods.
SPECIAL_STATS_SET = frozenset({'base_ad',
                               'att_speed',
                               'move_speed',
                               'move_speed_reduction',
                               'missing_hp',
                               'missing_mp',
                               'champion_lvl',
                               } | DEFENSIVE_SPECIAL_STATS)


ALL_POSSIBLE_STAT_NAMES = ALL_STANDARD_STAT_NAMES | SPECIAL_STATS_SET | ALLOWED_BONUS_STATS | (ALL_RESOURCE_NAMES - {None})

ALL_POSSIBLE_STAT_NAMES_EXCLUDING_CURRENT_TYPE = {i for i in ALL_POSSIBLE_STAT_NAMES if not i.startswith('current_')}
NON_PER_LVL_STAT_NAMES = sorted(i for i in ALL_POSSIBLE_STAT_NAMES if 'per_lvl' not in i)


def ensure_allowed_stats_names(iterable):
    """
    Checks if all elements are allowed stat names.

    :return:
    """
    for i in iterable:
        if i not in ALL_POSSIBLE_STAT_NAMES:
            raise palette.UnexpectedValueError(i)


# Some stats are already limited by the way they are calculated and the checks performed using dict below are redundant.
# However, they should remain in this dict to ensure bugs aren't created if their calculation changes.
# (e.g. percent_armor_reduction, percent_magic_reduction etc):
STATS_UPPER_LIMITS = {'percent_healing_reduction': 1,
                      'crit_dmg_reduction': 1,
                      'slow_reduction': 1,
                      'att_speed': 2.5,
                      'tenacity': 1,
                      'percent_armor_reduction': 1,
                      'death_time_reduction': 1,
                      'crit_chance': 1,
                      'percent_survivability': 1,
                      'percent_mr_reduction': 1,
                      'magic_dmg_taken': 1,
                      'cdr': 0.4,
                      'move_speed_reduction': 1}
STATS_UPPER_LIMITS.update({i: 1 for i in PERCENT_SPECIAL_STATS_SET})
ensure_allowed_stats_names(STATS_UPPER_LIMITS)


# Enemy base stats' names.
_ENEMY_BASE_STATS_NAMES = {'hp', 'ap', 'armor', 'mr', 'hp5'}
# (ensure they are allowed)
if _ENEMY_BASE_STATS_NAMES - ALL_POSSIBLE_STAT_NAMES:
    raise palette.UnexpectedValueError
_ENEMY_BASE_STATS_NAMES |= DEFENSIVE_NORMAL_STATS


class NonExistingNormalStatError(Exception):
    """
    Used to indicate stat was not found when searched by request stat function
    in ALL_STANDARD_STAT_NAMES and current stats.
    """
    pass


class StatCalculation(object):

    """
    Contains methods for the calculation of some stats' values.
    """

    ALL_RESOURCE_NAMES = ALL_RESOURCE_NAMES
    RESOURCE_CURRENT_STAT_NAMES = RESOURCE_CURRENT_STAT_NAMES
    DEFENSIVE_SPECIAL_STATS = DEFENSIVE_SPECIAL_STATS
    RUNE_STAT_NAMES = RUNE_STAT_NAMES
    ALL_STANDARD_STAT_NAMES = ALL_STANDARD_STAT_NAMES
    RESOURCE_TO_CURRENT_RESOURCE_MAP = RESOURCE_TO_CURRENT_RESOURCE_MAP
    ENEMY_BASE_STATS_NAMES = _ENEMY_BASE_STATS_NAMES
    CURRENT_TYPE_STATS = CURRENT_TYPE_STATS

    def __init__(self,
                 champion_lvls_dct,
                 selected_champions_dct,
                 initial_active_buffs,
                 initial_current_stats,
                 initial_enemies_total_stats,):

        self.champion_lvls_dct = champion_lvls_dct
        self.player_lvl = self.champion_lvls_dct['player']

        self.selected_champions_dct = selected_champions_dct

        self.player_current_resource_name = ''

        self.all_target_names = tuple(sorted(self.selected_champions_dct.keys()))   # e.g. ['player', 'enemy_1', ]

        self.enemy_target_names = tuple(tar for tar in sorted(self.all_target_names) if tar != 'player')

        self.total_enemies = len(self.enemy_target_names)

        self.initial_active_buffs = initial_active_buffs    # Can contain 0 to all targets and their buffs.
        self.initial_current_stats = initial_current_stats  # Can contain 0 to all targets and their stats.

        self.active_buffs = {}

        self.initial_enemies_total_stats = initial_enemies_total_stats
        # Contains player's base stats ..
        # (e.g. ad at lvl1 without per lvl bonus, ad_per_lvl, etc.)
        # .. and enemies TOTAL stats.
        # (that is, after applying enemy items, enemy masteries, runes, abilities etc).
        self.basic_stats_dct = {}
        self.set_basic_stats_dct()

        self.current_stats = {}

        self.set_active_buffs()
        self.set_player_current_resource_name()

    def set_player_current_resource_name(self):
        """
        Creates player's current resource name and stores it.

        Returns:
            (None)
        """

        self.player_current_resource_name = 'current_' + self.RESOURCE_USED

    def place_tars_and_empty_dct_in_dct(self, dct, ensure_empty_dct=True):
        """
        Inserts into a dct target names as keywords, and empty dict as value for each targets.
        To be used for empty dicts only.

        Returns:
            (None)
        Raises:
            (ValueError)
        """

        if ensure_empty_dct and dct:
            raise ValueError('Dict is not empty.')

        for tar in self.all_target_names:
            dct.update({tar: {}})

    def fill_up_tars_and_empty_obj_in_dct(self, given_dct, obj_type='dict'):
        if obj_type == 'dict':
            empty_obj = {}
        elif obj_type == 'list':
            empty_obj = []
        else:
            raise palette.UnexpectedValueError

        for tar in self.all_target_names:
            given_dct.setdefault(tar, empty_obj)

    def set_basic_stats_dct(self):
        """
        Creates base stats dict.

        :return: (None)
        """

        if self.initial_enemies_total_stats:
            self.basic_stats_dct.update(self.initial_enemies_total_stats)

        all_base_stats_dct = app_champions_base_stats.CHAMPION_BASE_STATS

        player_base_stats = all_base_stats_dct[self.selected_champions_dct['player']]
        self.basic_stats_dct.update({'player': player_base_stats})
        self.basic_stats_dct['player'].update({'crit_modifier': 2})

        for tar_name in self.enemy_target_names:
            if tar_name not in self.basic_stats_dct:
                self.basic_stats_dct.update({tar_name: {}})

                tar_champ = self.selected_champions_dct[tar_name]
                tar_hp = all_base_stats_dct[tar_champ]['hp']
                tar_hp_per_lvl = all_base_stats_dct[tar_champ]['hp_per_lvl']
                self.basic_stats_dct[tar_name].update({'hp': tar_hp, 'hp_per_lvl': tar_hp_per_lvl})
                self.basic_stats_dct[tar_name].update({'crit_modifier': 2})

    def set_active_buffs(self):
        """
        Sets active_buffs to initial_active_buffs if any.
        Then inserts target in active buffs if not already there.

        :return: (None)
        """

        # Checks if there are initial_active_buffs.
        if self.initial_active_buffs:
            self.active_buffs = copy.deepcopy(self.initial_active_buffs)

        # Fills with targets that have not been set.
        for tar in self.all_target_names:
            if tar not in self.active_buffs:
                self.active_buffs.update({tar: {}})

    # TODO: memoization (ONLY of player stat since enemy "base stats" are set by "reverse mode")
    def _base_stat(self, stat_name, tar_name):
        """
        Returns stat value resulting from base stat value and per lvl scaling,
        that is, based exclusively on champion (no items, runes, masteries etc.).

        :param stat_name: (str)
        :param tar_name: (str)
        :return: (float)
        """

        tar_base_stats_dct = self.basic_stats_dct[tar_name]

        # If the stat exists in target's base stats..
        if stat_name in tar_base_stats_dct:
            # .. its initial value is set to it.
            value = tar_base_stats_dct[stat_name]
        else:
            value = 0

        # PER_LVL BONUS
        # Iterates through all base stats.
        base_stat_per_lvl_name = stat_name + '_per_lvl'
        if base_stat_per_lvl_name in tar_base_stats_dct:
            # .. it adds it to the value.
            tar_lvl = self.champion_lvls_dct[tar_name]
            per_lvl_bonus = tar_base_stats_dct[base_stat_per_lvl_name]
            # TODO: replace copyrighted function below (use non linear fitting)
            value += per_lvl_bonus * (7/400*(tar_lvl**2-1) + 267/400*(tar_lvl-1))

        return value

    def _bonus_stat(self, stat_name, tar_name):
        """
        Returns only the bonus value of a stat,
        that is, only values related to abilities, items, masteries, runes, etc,
        without champion base (and per champion lvl) values.

        :param stat_name: (str)
        :param tar_name: (str)
        :return: (float)
        """

        # Removes 'bonus_' from stat name.
        stat_name = stat_name[6:]

        base_stat_value = self._base_stat(stat_name=stat_name, tar_name=tar_name)
        total_stat_val = self._standard_stat(requested_stat=stat_name, tar_name=tar_name)

        return total_stat_val - base_stat_value

    def _bonus_value_for_given_type(self, stat_name, bonus_type, buff_dct, tar_name, buff_name, buff_stats_dct):
        """
        Calculates and returns the value of given

        :return: (None)
        """

        buff_source = buff_dct['buff_source']
        value_num_or_dct = buff_stats_dct[stat_name][bonus_type]

        if type(value_num_or_dct) in (int, float):
            stat_val = value_num_or_dct

        else:
            values_tpl_or_num = value_num_or_dct['stat_values']

            if type(values_tpl_or_num) in (int, float):
                stat_val = values_tpl_or_num

            else:
                values_tpl = value_num_or_dct['stat_values']

                if buff_source == 'inn':
                    ability_lvl = self.innate_special_lvl(values_tpl=values_tpl)
                    lvl_index = ability_lvl - 1

                elif buff_source in palette.SPELL_SHORTCUTS:
                    ability_lvl = self.ability_lvls_dct[buff_source]
                    lvl_index = ability_lvl - 1

                else:
                    lvl_index = 0

                # STAT VALUE
                stat_val = values_tpl[lvl_index]

            # STAT MODS
            # (all stat mods are additive)
            stat_mods_dct = value_num_or_dct['stat_mods']
            if stat_mods_dct:
                _req_stat_func = self.request_stat
                for mod_name in stat_mods_dct:
                    mod_vals = stat_mods_dct[mod_name]

                    if mod_vals:
                        if len(mod_vals) == 1:
                            stat_val += mod_vals[0] * _req_stat_func(target_name='player', stat_name=mod_name)
                        else:
                            stat_val += mod_vals[lvl_index]

        # Stacks.
        stat_val *= self.active_buffs[tar_name][buff_name]['current_stacks']

        return stat_val

    def stat_bonuses(self, tar_name, stat_name, requested_type=None):
        """
        Creates bonus for given stat and target.

        :param requested_type: 'multiplicative', 'additive' or 'percent'
            Optional; used when only one of the types is needed to avoid repeatative 'ifs'.
        :return: (dict) Keys: bonus types, values: corresponding values.
        """

        bonuses_dct = {}

        # (sorted to avoid non determinism)
        for buff_name in sorted(self.active_buffs[tar_name]):

            buff_dct = self.req_buff_dct_func(buff_name=buff_name)
            # (All buff stats dict)
            buff_stats_dct = buff_dct['stats']
            # Checks if the buff has stat bonuses.
            if buff_stats_dct:

                if stat_name in sorted(buff_stats_dct):

                    stat_dct = buff_stats_dct[stat_name]

                    for bonus_type in sorted(stat_dct):
                        if not stat_dct[bonus_type]:
                            continue

                        type_val = self._bonus_value_for_given_type(stat_name=stat_name, bonus_type=bonus_type,
                                                                    buff_dct=buff_dct, tar_name=tar_name,
                                                                    buff_name=buff_name, buff_stats_dct=buff_stats_dct)

                        bonuses_dct.setdefault(bonus_type, {})
                        bonuses_dct[bonus_type].update({buff_name: type_val})

        if requested_type in bonuses_dct:
            return bonuses_dct[requested_type]
        else:
            return bonuses_dct

    def total_stat_bonus(self, tar_name, stat_name, bonus_type):
        """
        Returns total bonus of a given target's stat.

        :return: (float)
        """
        return sum(self.stat_bonuses(tar_name=tar_name, stat_name=stat_name, requested_type=bonus_type).values())

    def _standard_stat(self, requested_stat, tar_name):
        """
        Calculates the value of a stat after applying all its bonuses to its base value found in base_stats_dct.

        Not to be used for special stats like att_speed, or ad.
        Not to be used for filtered stats.

        If stat doesnt exist it returns 0 since some stats (e.g. lifesteal)
        might not always be present in base_stats_dct.

        :param requested_stat: (str)
        :param tar_name: (str)
        :return: (float) unfiltered stat value after bonuses
        """

        if requested_stat not in ALL_POSSIBLE_STAT_NAMES_EXCLUDING_CURRENT_TYPE:
            raise NotImplementedError(requested_stat)

        # BASE VALUE PLUS BASE PER LVL
        value = self._base_stat(stat_name=requested_stat, tar_name=tar_name)

        tar_bonuses_stat_dct = self.stat_bonuses(tar_name=tar_name, stat_name=requested_stat)

        # If there are any bonuses at all..
        if tar_bonuses_stat_dct:

            if 'additive' in tar_bonuses_stat_dct:
                value += sum(tar_bonuses_stat_dct['additive'].values())

            if 'percent' in tar_bonuses_stat_dct:
                multiplication_mod = 1
                multiplication_mod += sum(tar_bonuses_stat_dct['percent'].values())

                value *= multiplication_mod

            if 'multiplicative' in tar_bonuses_stat_dct:
                multiplication_mod = 1

                for multiplicative_bonus_value in tar_bonuses_stat_dct['multiplicative'].values():
                    multiplication_mod *= 1 + multiplicative_bonus_value

                value *= multiplication_mod

        return value

    def base_ad(self, tar_name):
        """
        Calculates the value of base ad.

        Base ad is the champion's ad at lvl 1 without any bonuses,
        plus the per lvl bonus.

        :return: (float)
        """

        return self._base_stat(stat_name='ad', tar_name=tar_name)

    def move_speed_reduction(self, tar_name):
        """
        Returns final move speed reduction.

        Highest magnitude slow reduction is the only reduction applied.

        :return: (float)
        """

        # (they are always multiplicative)
        multiplicative_bonuses = self.stat_bonuses(tar_name=tar_name, stat_name='move_speed_reduction', requested_type='multiplicative').values()
        if multiplicative_bonuses:
            return min(multiplicative_bonuses)
        else:
            return 0

    def att_speed(self, tar_name):
        """
        Calculates final value of att_speed, after all bonuses and filters have been applied.

        Bonuses to att_speed are always percent, including the '_per_lvl' bonus.
        Therefor they are applied simultaneously (to preserve base value until calculation).
        Unlike other stats, _per_lvl bonus is applied at lvl 2.

        Filter applies att_speed's hard cap.

        Each reduction of att_speed is applied after all other bonuses have been applied,
        by multiplying the pre-final value with each reduction.

        :return: (float)
        """

        value = self.basic_stats_dct[tar_name]['base_att_speed']

        # _PER_LVL
        # Adds _per_lvl bonus of att_speed to the modifier.
        # TODO change 50% in base stats to 0.5 and adapt below code
        # (champion att speed is in the form of 50%)
        multiplication_mod = 100
        multiplication_mod += self.basic_stats_dct[tar_name]['att_speed_per_lvl'] * (self.champion_lvls_dct[tar_name]-1)

        # ITEM AND BUFF BONUSES
        # Adds item and buff bonuses of att_speed to the modifier.
        percent_att_speed_bonuses = self.stat_bonuses(tar_name=tar_name, stat_name='att_speed', requested_type='percent')
        for bonus_name in percent_att_speed_bonuses:
            # (att speed in non champion base stats is in the form 0.02)
            multiplication_mod += percent_att_speed_bonuses[bonus_name] * 100

        value *= multiplication_mod / 100

        # REDUCTIONS
        tar_percent_att_speed_reduction_bonuses = self.stat_bonuses(tar_name=tar_name, stat_name='att_speed_reduction', requested_type='percent')
        for bonus_name in tar_percent_att_speed_reduction_bonuses:
            value *= 1 - tar_percent_att_speed_reduction_bonuses[bonus_name]

        return value

    def slow_reduction(self, tar_name):
        """
        Calculates how much slows are reduced.

        :return: (float)
        """
        slow_mod = 1
        for slow_red_bonus_val in self.stat_bonuses(tar_name=tar_name, stat_name='slow_reduction', requested_type='multiplicative').values():
            slow_mod *= 1 - slow_red_bonus_val

        return 1-slow_mod

    @staticmethod
    def move_speed_after_soft_caps(unfiltered_stat):
        """
        Applies threshold on move_speed.

        :param unfiltered_stat: (float)
        :return: (float) final stat value

        >>> StatCalculation().move_speed_after_soft_caps(300)
        300

        """
        # TODO avoid copyrighted formula
        if (415 < unfiltered_stat) and (unfiltered_stat < 490):
            return unfiltered_stat*0.8 + 83
        elif unfiltered_stat > 490:
            return unfiltered_stat*0.5 + 230
        elif unfiltered_stat < 220:
            return unfiltered_stat*0.5 + 110
        else:
            return unfiltered_stat

    def move_speed(self, tar_name):
        """
        Calculates final value of movement speed, after all bonuses and soft caps are applied.

        -Additive bonuses are applied.
        -Multiplicative bonuses are applied by a single modifier for all bonuses.
        -Strongest speed reduction effected is fully applied, while the rest are ignored

        :return: (float)
        """

        # BASE VALUE AND BONUSES
        value = self._standard_stat(requested_stat='move_speed',
                                    tar_name=tar_name)

        # SLOW REDUCTIONS
        # Calculates the modifier that dampens slow effects (e.g. boots of swiftness)
        slow_mod = 1 - self.slow_reduction(tar_name=tar_name)

        # SPEED REDUCTIONS
        value *= 1 - (slow_mod * self.move_speed_reduction(tar_name=tar_name))

        return self.move_speed_after_soft_caps(unfiltered_stat=value)

    def innate_special_lvl(self, values_tpl):
        """
        Returns the innate "lvl" of given tuple, which may vary depending on the length of it.

        For example a tuple with 6 values would divide champion lvl by 6,
        and each value in the tuple would correspond to 3 consecutive lvls.

        :param values_tpl: (tuple)
        :return: (int) Index of tuple
        """

        divisor = 18 // len(values_tpl)

        return (self.player_lvl - 1) // divisor + 1

    def champion_lvl(self, tar_name):
        return self.champion_lvls_dct[tar_name]

    def _percent_reductions_base(self, tar_name, stat_name):
        """
        Used for "percent_"-named stats that are applied multiplicatively.

        :return: (float)
        """

        val = 1

        stat_bonuses = self.stat_bonuses(tar_name=tar_name, stat_name=stat_name, requested_type='additive')

        for buff_name in stat_bonuses:
            val *= 1 - stat_bonuses[buff_name]

        return 1-val


class StatRequest(StatCalculation):

    def __init__(self,
                 champion_lvls_dct,
                 selected_champions_dct,
                 req_buff_dct_func,
                 initial_active_buffs,
                 initial_current_stats,
                 initial_enemies_total_stats,
                 _reversed_combat_mode):

        self.req_buff_dct_func = req_buff_dct_func
        self._reversed_combat_mode = _reversed_combat_mode

        StatCalculation.__init__(self,
                                 champion_lvls_dct=champion_lvls_dct,
                                 selected_champions_dct=selected_champions_dct,
                                 initial_active_buffs=initial_active_buffs,
                                 initial_current_stats=initial_current_stats,
                                 initial_enemies_total_stats=initial_enemies_total_stats)

    SPECIAL_STATS_SET = SPECIAL_STATS_SET

    def stats_dependencies(self):
        raise NotImplementedError

    @staticmethod
    def stat_after_filters(stat_value, stat_name):
        """
        Applies upper stat limit.

        :return: (num)
        """

        if stat_name in STATS_UPPER_LIMITS:
            return min(STATS_UPPER_LIMITS[stat_name], stat_value)
        else:
            return stat_value

    def request_stat(self, target_name, stat_name):
        """
        Calculates a target's final stat value.

        :return: (None)
        """

        # Special stats have their own methods.
        if stat_name in ALLOWED_BONUS_STATS:
            val = self._bonus_stat(stat_name=stat_name, tar_name=target_name)
        elif stat_name in self.SPECIAL_STATS_SET:
            val = getattr(self, stat_name)(target_name)
        elif stat_name in PERCENT_SPECIAL_STATS_SET:
            val = self._percent_reductions_base(tar_name=target_name, stat_name=stat_name)
        elif stat_name in CURRENT_TYPE_STATS:
            val = self.current_stats[target_name][stat_name]

        # Most stats can be calculated using the '_standard_stat' method.
        else:
            val = self._standard_stat(requested_stat=stat_name, tar_name=target_name)

        return self.stat_after_filters(stat_value=val, stat_name=stat_name)

    def set_current_stats(self):
        """
        Inserts current_hp in current_stats of each target and current resource (e.g. mp, rage, etc) for player.
        If the current_stats dict is empty, or if the value doesnt exist it creates the value.

        :return: (None)
        """

        # In reversed mode, survivability (in general) is all that matters so initial stats are ignored.
        if not self._reversed_combat_mode:
            # Checks if there are any preset values for current_stats.
            if self.initial_current_stats:
                self.current_stats = copy.deepcopy(self.initial_current_stats)

        for tar in self.all_target_names:

            # If the target's current_hp has not been set, it creates it.
            self.current_stats.setdefault(tar, dict(current_hp=self.request_stat(target_name=tar, stat_name='hp')))

            # Also creates the player's 'current_'resource.
            if tar == 'player':
                resource_used = self.RESOURCE_USED
                current_resource_name = RESOURCE_TO_CURRENT_RESOURCE_MAP[self.RESOURCE_USED]
                if current_resource_name not in self.current_stats[tar]:

                    self.current_stats['player'].update(

                        {current_resource_name: self.request_stat(target_name=tar, stat_name=resource_used)})

    def _missing_current_stat(self, tar_name, non_current_stat_name):
        """
        Base for missing_hp, missing_mp etc.

        :param non_current_stat_name: (str) 'hp', 'mp', etc
        :return: (float)
        """

        max_val = self.request_stat(target_name=tar_name, stat_name=non_current_stat_name)
        curr_val = self.current_stats[tar_name]['current_' + non_current_stat_name]
        delta = max_val - curr_val
        # Missing stat can't be lower than 0.
        return max(0, delta)

    def missing_hp(self, tar_name):
        return self._missing_current_stat(tar_name=tar_name, non_current_stat_name='hp')

    def missing_mp(self, tar_name):
        return self._missing_current_stat(tar_name=tar_name, non_current_stat_name='mp')


class DmgReductionStats(StatRequest):

    """
    Contains methods for the calculation of dmg reduction related stats' values.
    """

    DEFENSE_REDUCING_MR_AND_ARMOR_MAP = _DEFENSE_REDUCING_MR_AND_ARMOR_MAP

    def reduced_armor(self, target, stat='armor'):
        """
        Calculates the armor a dmg "sees".

        Order of application is: 'flat armor reduction', 'percent armor reduction', 'percent armor penetration',
        'flat armor penetration'.

        Reductions are target based bonuses. Penetrations are player based.

        :param target: (str)
        :param (str) 'armor' or 'mr'. Used for creation of mr-equivalent method.
        :return: (float) final value of armor that attacker sees
        """

        # percent_reduction calculation
        percent_reduction_name = self.DEFENSE_REDUCING_MR_AND_ARMOR_MAP[stat]['_percent_reduction']
        percent_reduction = self.request_stat(target_name=target, stat_name=percent_reduction_name)

        # percent_penetration calculation
        percent_penetration_name = self.DEFENSE_REDUCING_MR_AND_ARMOR_MAP[stat]['_percent_penetration']
        percent_penetration = self.request_stat(target_name='player', stat_name=percent_penetration_name)
        # (Max value is 1)
        percent_penetration = min(1, percent_penetration)

        armor_after_reductions = self.request_stat(target_name=target,
                                                   stat_name=stat)
        # flat_reduction calculation
        flat_reduction_name = self.DEFENSE_REDUCING_MR_AND_ARMOR_MAP[stat]['_flat_reduction']
        armor_after_reductions -= self.request_stat(target_name=target, stat_name=flat_reduction_name)

        # (Armor can't be reduced further if negative)
        if armor_after_reductions <= 0:
            return armor_after_reductions
        else:
            # Applies percent reduction and percent penetration
            armor_after_reductions *= (1-percent_reduction) * (1-percent_penetration)

            # flat_penetration
            flat_penetration_name = self.DEFENSE_REDUCING_MR_AND_ARMOR_MAP[stat]['_flat_penetration']
            flat_penetration_val = self.request_stat(target_name='player',
                                                     stat_name=flat_penetration_name)
            if armor_after_reductions > flat_penetration_val:
                return armor_after_reductions - flat_penetration_val

            else:
                return 0.

    def reduced_mr(self, target):
        """
        Calculates the magic resist a dmg "sees".

        Same as reduced_armor().
        """
        return self.reduced_armor(target, stat='mr')

    @staticmethod
    def _percent_dmg_reduction_by_defensive_stat(stat_value):
        """
        Calculates percent dmg reduction caused by armor or mr.

        Args:
            stat_value: (str) 'armor' or 'mr'
        Returns:
            (float) dmg reduction
        """

        return stat_value / (100.+abs(stat_value))

    def percent_physical_reduction_by_armor(self, target, stat='reduced_armor'):
        """
        Calculates percent dmg reduction caused by armor.
        """

        stat_val = self.request_stat(target_name=target, stat_name=stat)

        return self._percent_dmg_reduction_by_defensive_stat(stat_value=stat_val)

    def percent_magic_reduction_by_mr(self, target):
        """
        Calculates percent dmg reduction caused by mr.
        """

        return self.percent_physical_reduction_by_armor(target=target, stat='reduced_mr')

    def physical_dmg_taken(self, tar_name):
        """
        Calculates total percent physical dmg taken.

        Initial bonus is affected only by reduction from armor. Then each other bonus is multiplied to it.

        Returns:
            (float)
        """

        # Initially it's set to percent physical dmg taken (by armor).
        value = 1 - self.percent_physical_reduction_by_armor(tar_name)

        tar_percent_red_bonuses = self.stat_bonuses(tar_name=tar_name, stat_name='percent_physical_dmg_reduction', requested_type='additive')

        for bonus_name in tar_percent_red_bonuses:
            # .. they are multiplied.
            value *= 1 - tar_percent_red_bonuses[bonus_name]

        return value

    def magic_dmg_taken(self, tar_name):
        """
        Calculates total percent magic dmg taken.

        Initial bonus is affected only by reduction from mr. Then each other bonus is multiplied to it.

        Returns:
            (float)
        """

        # Initially it's set to percent magic dmg taken (by mr).
        value = 1 - self.percent_magic_reduction_by_mr(tar_name)

        tar_percent_red_bonuses = self.stat_bonuses(tar_name=tar_name, stat_name='percent_magic_dmg_reduction', requested_type='additive')

        for bonus_name in tar_percent_red_bonuses:
            # .. they are multiplied.
            value *= 1 - tar_percent_red_bonuses[bonus_name]

        return value
