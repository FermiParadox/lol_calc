import copy
import palette

from champions import app_champions_base_stats


ALL_RESOURCE_NAMES = frozenset({'mp', 'energy', 'rage', None, 'flow', 'hp'})


RESOURCE_CURRENT_STAT_NAMES = frozenset({'current_'+i for i in ALL_RESOURCE_NAMES if i is not None})
RESOURCE_TO_CURRENT_RESOURCE_MAP = {i: 'current_'+i for i in ALL_RESOURCE_NAMES if i is not None}

CURRENT_TYPE_STATS = RESOURCE_CURRENT_STAT_NAMES | {'current_hp',}

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
DEFENSIVE_NORMAL_STATS = {'percent_dmg_reduction', 'flat_AA_reduction',
                          'flat_dmg_reduction', 'flat_physical_dmg_reduction', 'flat_magic_dmg_reduction',
                          'percent_physical_dmg_reduction', 'percent_magic_dmg_reduction', 'flat_non_aoe_reduction',
                          'flat_aoe_reduction', 'percent_aoe_reduction', 'percent_non_aoe_reduction'}
for armor_or_mr in _DEFENSE_REDUCING_MR_AND_ARMOR_MAP:
    for _key in _DEFENSE_REDUCING_MR_AND_ARMOR_MAP[armor_or_mr]:
        DEFENSIVE_NORMAL_STATS.update({_DEFENSE_REDUCING_MR_AND_ARMOR_MAP[armor_or_mr][_key]})


# Contains all champions' base stats names.
BASE_STATS = set()
for _champ_name in app_champions_base_stats.CHAMPION_BASE_STATS:
    for _base_stat_name in app_champions_base_stats.CHAMPION_BASE_STATS[_champ_name]:
        BASE_STATS.update({_base_stat_name})


# Stats by items or buffs that are not calculated by their own (special) method.
NORMAL_STAT_NAMES = {'percent_healing_reduction', 'dmg_taken'}

# Extracted from rune_stat_names_map with: re.findall(r'\'(\w+)\'', s)
RUNE_STAT_NAMES = frozenset({'ap', 'mr', 'mr_per_lvl', 'armor_per_lvl', 'crit_chance', 'ap_per_lvl', 'hp_per_lvl',
                             'mp5', 'hp5_per_lvl', 'xp', 'energy', 'ep5_per_lvl', 'gp5', 'hp', 'att_speed',
                             'mp5_per_lvl', 'death_time_reduction', 'ep5', 'spellvamp', 'crit_modifier',
                             'mp_per_lvl', 'flat_armor_penetration', 'mp', 'ad', 'ad_per_lvl', 'hp5',
                             'lifesteal', 'move_speed', 'armor', 'energy_per_lvl', 'flat_magic_penetration',
                             'hp', 'cdr_per_lvl', 'cdr'})


ALL_STANDARD_STAT_NAMES = frozenset(
    (NORMAL_STAT_NAMES | BASE_STATS | RUNE_STAT_NAMES | RESOURCE_CURRENT_STAT_NAMES | DEFENSIVE_NORMAL_STATS)
    - ALL_RESOURCE_NAMES)


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
                               'crit_chance',
                               'cdr',
                               'move_speed_reduction',
                               } | DEFENSIVE_SPECIAL_STATS)


ALL_POSSIBLE_STAT_NAMES = ALL_STANDARD_STAT_NAMES | SPECIAL_STATS_SET | ALLOWED_BONUS_STATS | (ALL_RESOURCE_NAMES
                                                                                               - {None})

ALL_POSSIBLE_STAT_NAMES_EXCLUDING_CURRENT_TYPE = {i for i in ALL_POSSIBLE_STAT_NAMES if not i.startswith('current_')}

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


class StatFilters(object):

    """
    Contains functions that filter stats to prevent them exceeding their thresholds,
    and functions that reduce stat values that exceed their soft-caps.
    """

    @staticmethod
    def filtered_crit_chance(unfiltered_stat):
        """
        Applies threshold on crit_chance.

        Args:
            unfiltered_stat: (float)
        Returns:
            (float) final stat value

        >>> StatFilters().filtered_crit_chance(1.2)
        1.0
        >>> StatFilters().filtered_crit_chance(0.1)
        0.1

        """

        return min(1., unfiltered_stat)

    @staticmethod
    def filtered_att_speed(unfiltered_stat):
        """
        Applies threshold on att_speed.

        Args:
            unfiltered_stat: (float)
        Returns:
            (float) final stat value

        >>> StatFilters().filtered_att_speed(3.2)
        2.5
        >>> StatFilters().filtered_att_speed(0.1)
        0.1

        """

        return min(2.5, unfiltered_stat)

    @staticmethod
    def filtered_move_speed(unfiltered_stat):
        """
        Applies threshold on move_speed.

        Args:
            unfiltered_stat: (float)
        Returns:
            (float) final stat value

        >>> StatFilters().filtered_move_speed(300)
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

    @staticmethod
    def filtered_cdr(unfiltered_stat):
        """
        Applies threshold on cdr.

        Args:
            unfiltered_stat: (float)
        Returns:
            (float) final stat value

        >>> StatFilters().filtered_cdr(0.1)
        0.1
        >>> StatFilters().filtered_cdr(0.7)
        0.4

        """

        return min(0.4, unfiltered_stat)


class StatCalculation(StatFilters):

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

        self.all_target_names = self.selected_champions_dct.keys()   # e.g. ['player', 'enemy_1', ]

        self.enemy_target_names = tuple(tar for tar in sorted(self.all_target_names) if tar != 'player')

        self.initial_active_buffs = initial_active_buffs    # Can contain 0 to all targets and their buffs.
        self.bonuses_dct = {}   # e.g. {target: {stat: {stat type: {buff name: stat val}, }, }, }

        self.initial_current_stats = initial_current_stats  # Can contain 0 to all targets and their stats.

        self.active_buffs = {}

        self.initial_enemies_total_stats = initial_enemies_total_stats
        # Contains player's base stats ..
        # (e.g. ad at lvl1 without per lvl bonus, ad_per_lvl, etc.)
        # .. and enemies TOTAL stats.
        # (that is, after applying enemy items, enemy masteries, runes, abilities etc).
        self.base_stats_dct = {}
        self.set_base_stats_dct()

        self.current_stats = {}

        self.place_tars_and_empty_dct_in_dct(self.bonuses_dct)
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
            if tar not in given_dct:
                given_dct.update({tar: empty_obj})

    def set_base_stats_dct(self):
        """
        Creates base stats dict.

        Returns:
            (None)
        """

        if self.initial_enemies_total_stats:
            self.base_stats_dct.update(self.initial_enemies_total_stats)

        all_base_stats_dct = app_champions_base_stats.CHAMPION_BASE_STATS

        player_base_stats = all_base_stats_dct[self.selected_champions_dct['player']]
        self.base_stats_dct.update({'player': player_base_stats})

        for tar_name in self.enemy_target_names:
            if tar_name not in self.base_stats_dct:
                self.base_stats_dct.update({tar_name: {}})

                tar_champ = self.selected_champions_dct[tar_name]
                tar_hp = all_base_stats_dct[tar_champ]['hp']
                tar_hp_per_lvl = all_base_stats_dct[tar_champ]['hp_per_lvl']
                self.base_stats_dct[tar_name].update({'hp': tar_hp, 'hp_per_lvl': tar_hp_per_lvl})

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

    # TODO: memoization
    def _base_stat(self, stat_name, tar_name):
        """
        Returns stat value resulting from base stat value and per lvl scaling,
        that is based exclusively on champion (no items, runes, masteries etc.).

        :param stat_name: (str)
        :param tar_name: (str)
        :return: (float)
        """
        value = 0

        tar_base_stats_dct = self.base_stats_dct[tar_name]

        # If the stat exists in target's base stats..
        if stat_name in tar_base_stats_dct:
            # .. its initial value is set to it.
            value = tar_base_stats_dct[stat_name]

        # PER_LVL BONUS
        # Iterates through all base stats.
        base_stat_per_lvl_name = stat_name + '_per_lvl'
        if base_stat_per_lvl_name in tar_base_stats_dct:
            # .. it adds it to the value.
            value += (self.champion_lvls_dct[tar_name]-1) * tar_base_stats_dct[base_stat_per_lvl_name]

        return value

    def _bonus_stat(self, stat_name, tar_name):
        """
        Returns only the bonus value of a stat,
        that is, only champion related value (base and per lvl),
        without abilities, items, masteries, runes, etc.

        :param stat_name: (str)
        :param tar_name: (str)
        :return: (float)
        """

        value = 0

        tar_bonuses = self.bonuses_dct[tar_name]
        if stat_name in tar_bonuses:

            tar_bonuses_stat_dct = tar_bonuses[stat_name]

            # .. if there are additive bonuses..
            if 'additive' in tar_bonuses_stat_dct:
                # .. adds each bonus.
                for bonus_name in tar_bonuses_stat_dct['additive']:
                    value += tar_bonuses_stat_dct['additive'][bonus_name]

            # if there are percent bonuses..
            if 'percent' in tar_bonuses_stat_dct:
                multiplication_mod = 1
                # .. adds each bonus modifier..
                for bonus_name in tar_bonuses_stat_dct['percent']:
                    multiplication_mod += tar_bonuses_stat_dct['percent'][bonus_name]

                # .. and applies the modifier to the value.
                value *= multiplication_mod

            if 'multiplicative' in tar_bonuses_stat_dct:
                multiplication_mod = 1
                # .. adds each bonus modifier..
                for bonus_name in tar_bonuses_stat_dct['multiplicative']:
                    multiplication_mod *= 1 + tar_bonuses_stat_dct['multiplicative'][bonus_name]

                # .. and applies the modifier to the value.
                value *= multiplication_mod

        return value

    def standard_stat(self, requested_stat, tar_name):
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

        # ITEM AND BUFF BONUSES
        # If the requested_stat has bonuses..
        per_lvl_value = self._bonus_stat(stat_name=requested_stat, tar_name=tar_name)

        if per_lvl_value:
            return value + per_lvl_value
        else:
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
        Calculates final move speed reduction.

        Highest magnitude slow reduction is applied first.


        :param tar_name:
        :return: (float)
        """

        tar_bonuses = self.bonuses_dct[tar_name]

        try:
            return min(tar_bonuses['move_speed_reduction']['multiplicative'])
        # If no reductions are found.
        except KeyError:
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

        value = self.base_stats_dct[tar_name]['base_att_speed']

        # _PER_LVL
        # Adds _per_lvl bonus of att_speed to the modifier.
        # TODO change 50% in base stats to 0.5 and adapt below code
        # (champion att speed is in the form of 50%)
        multiplication_mod = 100
        multiplication_mod += self.base_stats_dct[tar_name]['att_speed_per_lvl'] * (self.champion_lvls_dct[tar_name]-1)

        # ITEM AND BUFF BONUSES
        # Adds item and buff bonuses of att_speed to the modifier.
        tar_bonuses = self.bonuses_dct[tar_name]
        if 'att_speed' in tar_bonuses:       # 'percent..' not checked since it can only be that.
            tar_percent_att_speed_bonuses = tar_bonuses['att_speed']['percent']
            for bonus_name in tar_percent_att_speed_bonuses:
                # (att speed in non champion base stats is in the form 0.02)
                multiplication_mod += tar_percent_att_speed_bonuses[bonus_name] * 100

        value *= multiplication_mod / 100

        # REDUCTIONS
        if 'att_speed_reduction' in tar_bonuses:
            tar_percent_att_speed_reduction_bonuses = tar_bonuses['att_speed_reduction']['percent']
            for bonus_name in tar_percent_att_speed_reduction_bonuses:
                value *= 1 - tar_percent_att_speed_reduction_bonuses[bonus_name]

        return value

    def move_speed(self, tar_name):
        """
        Calculates final value of movement speed, after all bonuses and soft caps are applied.

        -Additive bonuses are applied.
        -Multiplicative bonuses are applied by a single modifier for all bonuses.
        -Strongest speed reduction effected is fully applied.
        -The other speed reductions are applied at 35% of their max.

        :return: (float)
        """

        # BASE VALUE AND BONUSES
        value = self.standard_stat(requested_stat='move_speed',
                                   tar_name=tar_name)

        # SLOW REDUCTIONS
        # Calculates the modifier that dampens slow effects (e.g. boots of swiftness)
        tar_bonuses = self.bonuses_dct[tar_name]
        slow_mod = 1
        if 'slow_reduction' in tar_bonuses:
            for slow_red_bonus in tar_bonuses['slow_reduction']['percent']:
                slow_mod -= slow_red_bonus

        # SPEED REDUCTIONS
        if 'move_speed_reduction' in tar_bonuses:
            value *= self.move_speed_reduction(tar_name=tar_name)

        return self.filtered_move_speed(unfiltered_stat=value)

    def crit_chance(self, tar_name):
        """
        Returns filtered value of crit_chance.

        :return: (float)
        """

        return self.filtered_crit_chance(self.standard_stat(requested_stat='crit_chance',
                                                            tar_name=tar_name))

    def cdr(self, tar_name):
        """
        Returns filtered value of cdr.

        :return: (float)
        """

        return self.filtered_cdr(self.standard_stat(requested_stat='cdr',
                                                    tar_name=tar_name))

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

        self.set_current_stats()

    SPECIAL_STATS_SET = SPECIAL_STATS_SET

    def request_stat(self, target_name, stat_name):
        """
        Calculates a target's final stat value and stores it.
        Then notes that it has not changed since last calculation.

        Returns:
            (None)
        """

        # Special stats have their own methods.
        if stat_name in ALLOWED_BONUS_STATS:
            return self._bonus_stat(stat_name=stat_name, tar_name=target_name)
        elif stat_name in self.SPECIAL_STATS_SET:
            return getattr(self, stat_name)(target_name)
        elif stat_name in CURRENT_TYPE_STATS:
            return self.current_stats[target_name][stat_name]

        # Most stats can be calculated using the 'standard_stat' method.
        else:
            return self.standard_stat(requested_stat=stat_name, tar_name=target_name)

    def _insert_bonus_to_tar_bonuses(self, stat_name, bonus_type, buff_dct, tar_name, buff_name, buff_stats_dct):
        """
        Updates a target's bonuses_dct by adding the name and value of a bonus.

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

        # Inserts bonus_name and its value in bonuses_dct.
        self.bonuses_dct[tar_name][stat_name][bonus_type].update({buff_name: stat_val})

    def apply_bonuses_by_buffs(self, tar_name):
        """
        Creates all bonuses to stats caused by buffs.

        :return: (None)
        """

        tar_active_buffs = self.active_buffs[tar_name]

        time_sorted_tar_active_buffs = sorted(tar_active_buffs, key=lambda x: tar_active_buffs[x]['starting_time'])

        for buff_name in time_sorted_tar_active_buffs:

            buff_dct = self.req_buff_dct_func(buff_name=buff_name)
            # (All buff stats dict)
            buff_stats_dct = buff_dct['stats']
            # Checks if the buff has stat bonuses.
            if buff_stats_dct:

                for stat_name in buff_stats_dct:
                    # (single stat dict)
                    stat_dct = buff_stats_dct[stat_name]

                    for bonus_type in stat_dct:
                        if not stat_dct[bonus_type]:
                            continue

                        tar_bonuses = self.bonuses_dct[tar_name]

                        if stat_name not in tar_bonuses:
                            # Inserts stat_name in bonuses_dct.
                            tar_bonuses.update({stat_name: {}})

                        if bonus_type not in tar_bonuses[stat_name]:
                            # Inserts bonus_type in bonuses_dct.
                            tar_bonuses[stat_name].update({bonus_type: {}})

                        self._insert_bonus_to_tar_bonuses(stat_name=stat_name, bonus_type=bonus_type,
                                                          buff_dct=buff_dct, tar_name=tar_name,
                                                          buff_name=buff_name, buff_stats_dct=buff_stats_dct)

    def refresh_stats_bonuses(self):
        self.place_tars_and_empty_dct_in_dct(self.bonuses_dct, ensure_empty_dct=False)

        for tar_name in self.all_target_names:
            self.apply_bonuses_by_buffs(tar_name=tar_name)

    def set_current_stats(self):
        """
        Inserts current_hp in current_stats of each target and current resource (e.g. mp, rage, etc) for player.
        If the current_stats dict is empty, or if the value doesnt exist it creates the value.

        :return: (None)
        """

        # In reversed mode survivability (in generally) is all that matters so initial stats are ignored.
        if not self._reversed_combat_mode:
            # Checks if there are any preset values for current_stats.
            if self.initial_current_stats:
                self.current_stats = copy.deepcopy(self.initial_current_stats)

        for tar in self.all_target_names:

            # If the target's current_hp has not been set, it creates it.
            if tar not in self.current_stats:
                self.current_stats.update({tar: {}})

                self.current_stats.update(
                    {tar: dict(current_hp=self.request_stat(target_name=tar, stat_name='hp'))})

                # Also creates the player's 'current_'resource.
                if tar == 'player':
                    resource_used = self.RESOURCE_USED
                    current_resource_name = RESOURCE_TO_CURRENT_RESOURCE_MAP[self.RESOURCE_USED]
                    if current_resource_name not in self.current_stats[tar]:

                        self.current_stats['player'].update(

                            {current_resource_name: self.request_stat(target_name=tar, stat_name=resource_used)})


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

        Args:
            target: (str)
            stat: (str) 'armor' or 'mr'. Used for creation of mr-equivalent method.
        Returns:
            (float) final value of armor that attacker sees
        """

        # Checks if stat is inside target's bonuses dict
        # Since some stats don't exist in base_stats they can only be created by bonuses.
        tar_bonuses = self.bonuses_dct[target]

        # percent_reduction calculation
        percent_reduction_name = self.DEFENSE_REDUCING_MR_AND_ARMOR_MAP[stat]['_percent_reduction']
        if percent_reduction_name in tar_bonuses:
            percent_reduction = self.request_stat(target_name=target,
                                                  stat_name=percent_reduction_name)
        else:
            percent_reduction = 0

        # percent_penetration calculation
        percent_penetration_name = self.DEFENSE_REDUCING_MR_AND_ARMOR_MAP[stat]['_percent_penetration']
        if percent_penetration_name in self.bonuses_dct['player']:
            percent_penetration = self.request_stat(target_name='player',
                                                    stat_name=percent_penetration_name)
        else:
            percent_penetration = 0

        armor_after_reductions = self.request_stat(target_name=target,
                                                   stat_name=stat)
        # flat_reduction calculation
        flat_reduction_name = self.DEFENSE_REDUCING_MR_AND_ARMOR_MAP[stat]['_flat_reduction']
        if flat_reduction_name in tar_bonuses:
            armor_after_reductions -= self.request_stat(target_name=target,
                                                        stat_name=flat_reduction_name)

        # Applies percent reduction and percent penetration
        # (Armor can't be reduced further if negative)
        if armor_after_reductions <= 0:
            return armor_after_reductions
        else:
            armor_after_reductions *= (1-percent_reduction) * (1-percent_penetration)

        # flat_penetration
        flat_penetration_name = self.DEFENSE_REDUCING_MR_AND_ARMOR_MAP[stat]['_flat_penetration']
        if flat_penetration_name in self.bonuses_dct['player']:
            if armor_after_reductions > self.request_stat(target_name='player',
                                                          stat_name=flat_penetration_name):
                return armor_after_reductions - self.request_stat(target_name='player',
                                                                  stat_name=flat_penetration_name)

            else:
                return 0.
        else:
            return armor_after_reductions

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

        # If there are any bonuses to physical reduction..
        if 'percent_physical_dmg_reduction' in self.bonuses_dct[tar_name]:
            tar_percent_red_bonuses = self.bonuses_dct[tar_name]['percent_physical_dmg_reduction']['percent']

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

        # If there are any bonuses to magic dmg reduction..
        if 'percent_magic_dmg_reduction' in self.bonuses_dct[tar_name]:
            tar_percent_red_bonuses = self.bonuses_dct[tar_name]['percent_magic_dmg_reduction']['percent']

            for bonus_name in tar_percent_red_bonuses:
                # .. they are multiplied.
                value *= 1 - tar_percent_red_bonuses[bonus_name]

        return value
