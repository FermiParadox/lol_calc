import app_champions_base_stats
import copy


ALL_RESOURCE_NAMES = frozenset({'mp', 'energy', 'rage', None, 'flow'})


RESOURCE_CURRENT_STAT_NAMES = frozenset({'current_'+i for i in ALL_RESOURCE_NAMES if i is not None})


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
DEFENSE_REDUCING_MR_AND_ARMOR_MAP = dict(
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
DEFENSIVE_NORMAL_STATS = {'percent_dmg_reduction', 'flat_dmg_reduction'}
for armor_or_mr in DEFENSE_REDUCING_MR_AND_ARMOR_MAP:
    for _key in DEFENSE_REDUCING_MR_AND_ARMOR_MAP[armor_or_mr]:
        DEFENSIVE_NORMAL_STATS.update({DEFENSE_REDUCING_MR_AND_ARMOR_MAP[armor_or_mr][_key]})


# Contains all champions' base stats names.
BASE_STATS = set()
for _champ_name in app_champions_base_stats.CHAMPION_BASE_STATS:
    for _base_stat_name in app_champions_base_stats.CHAMPION_BASE_STATS[_champ_name]:
        BASE_STATS.update({_base_stat_name})


# Stats by items or buffs that are not calculated by their own (special) method.
NORMAL_STAT_NAMES = set()

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


class NonExistingNormalStat(Exception):
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

        >>>StatFilters().filtered_crit_chance(1.2)
        1.
        >>>StatFilters().filtered_crit_chance(0.1)
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

        >>>StatFilters().filtered_att_speed(3.2)
        2.5
        >>>StatFilters().filtered_att_speed(0.1)
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

        >>>StatFilters().filtered_move_speed(300)
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

        >>>StatFilters().filtered_cdr(0.1)
        0.1
        >>>StatFilters().filtered_cdr(0.7)
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

    def __init__(self,
                 champion_lvls_dct,
                 selected_champions_dct,
                 initial_active_buffs=None,
                 initial_current_stats=None):

        self.champion_lvls_dct = champion_lvls_dct

        self.selected_champions_dct = selected_champions_dct

        self.player_resource_name = ''
        self.player_current_resource_name = ''

        self.all_target_names = self.selected_champions_dct.keys()   # e.g. ['player', 'enemy_1', ]

        self.enemy_target_names = tuple(tar for tar in self.all_target_names if tar != 'player')

        self.initial_active_buffs = initial_active_buffs    # Can contain 0 to all targets and their buffs.
        self.bonuses_dct = {}   # e.g. {target: {stat: {bonus type: {bonus name: }, }, }, }

        self.initial_current_stats = initial_current_stats  # Can contain 0 to all targets and their stats.

        self.active_buffs = {}

        self.base_stats_dct = {}
        self.set_base_stats_dct()

        self.current_stats = {}
        self.stat_dependencies = {}     # e.g. {tar_name: {stat_1: [controller_stat_1, controller_stat_2,], }, }
        self.stored_stats = {}
        self.stat_changes = {}
        self.stored_buffs = {}  # Used for storing buff (that affects stats) and its stacks, of a target.

        self.place_tar_and_empty_dct_in_dct(self.stored_stats)
        self.place_tar_and_empty_dct_in_dct(self.stat_changes)
        self.place_tar_and_empty_dct_in_dct(self.bonuses_dct)
        self.place_tar_and_empty_dct_in_dct(self.stored_buffs)

        self.set_active_buffs()
        self.set_player_resource_name()
        self.set_player_current_resource_name()

    def set_player_resource_name(self):
        """
        Creates player's resource name and stores it.

        Returns:
            (None)
        """
        player_champ_stats = app_champions_base_stats.CHAMPION_BASE_STATS[self.selected_champions_dct['player']]

        for res_name in self.ALL_RESOURCE_NAMES:
            if res_name in player_champ_stats:
                self.player_resource_name = res_name

    def set_player_current_resource_name(self):
        """
        Creates player's current resource name and stores it.

        Returns:
            (None)
        """

        self.player_current_resource_name = 'current_' + self.player_resource_name

    def set_base_stats_dct(self):
        """
        Creates base stats dict.

        Returns:
            (None)
        """

        dct = {}

        # For each selected champion..
        for tar_name in self.all_target_names:
            # .. updates base_stats_dct with his base stats.
            dct.update(
                {tar_name: app_champions_base_stats.CHAMPION_BASE_STATS[self.selected_champions_dct[tar_name]]})

        self.base_stats_dct = dct

    def place_tar_and_empty_dct_in_dct(self, dct):
        """
        Inserts into a dct target names as keywords, and empty dict as value for each targets.
        To be used for empty dicts only.

        Modifies:
            dct
        Returns:
            (None)
        Raises:
            (ValueError) If dict is not empty.
        """

        if dct:
            raise ValueError('Target will be replaced.')

        for tar in self.all_target_names:
            dct.update({tar: {}})

    def set_active_buffs(self):
        """
        Sets active_buffs to initial_active_buffs if any.
        Then inserts target in active buffs if not already there.

        Modifies:
            active_buffs
        Returns:
            (None)
        """

        # Checks if there are initial_active_buffs.
        if self.initial_active_buffs:
            self.active_buffs = copy.deepcopy(self.initial_active_buffs)

        # Fills with targets that have not been set.
        for tar in self.all_target_names:
            if tar not in self.active_buffs:
                self.active_buffs.update({tar: {}})

    def standard_stat(self, requested_stat, tar_name):
        """
        Calculates the value of a stat after applying all its bonuses to its base value found in base_stats_dct.

        Not to be used for special stats like att_speed, or ad.
        Not to be used for filtered stats.

        If stat doesnt exist it returns 0 since some stats (e.g. lifesteal)
        might not always be present in base_stats_dct.

        Args:
            requested_stat: (str)
            tar_name: (str)
        Returns:
            (float) unfiltered stat value after bonuses
        """

        if requested_stat not in ALL_POSSIBLE_STAT_NAMES:
            raise NotImplementedError(requested_stat)

        value = 0
        base_stats_tar = self.base_stats_dct[tar_name]

        # BASE VALUE
        # If the stat exists in target's base stats..
        if requested_stat in base_stats_tar:
            # .. its initial value is set to it.
            value = base_stats_tar[requested_stat]

        # PER_LVL BONUS
        # Iterates through all base stats.
        for base_stat_name in base_stats_tar:

            if requested_stat + '_per_lvl' in base_stat_name:
                # .. it adds it to the value.
                value += self.champion_lvls_dct[tar_name] * base_stats_tar[base_stat_name]

        # ITEM AND BUFF BONUSES
        # If the requested_stat has bonuses..
        tar_bonuses = self.bonuses_dct[tar_name]
        if requested_stat in tar_bonuses:

            # .. if there are additive bonuses..
            if 'additive' in tar_bonuses[requested_stat]:
                # .. adds each bonus.
                for bonus_name in tar_bonuses[requested_stat]['additive']:
                    value += tar_bonuses[requested_stat]['additive'][bonus_name]

            # if there are percent bonuses..
            if 'percent' in tar_bonuses[requested_stat]:
                multiplication_mod = 1
                # .. adds each bonus modifier..
                for bonus_name in tar_bonuses[requested_stat]['percent']:
                    multiplication_mod += tar_bonuses[requested_stat]['percent'][bonus_name]

                # .. and applies the modifier to the value.
                value *= multiplication_mod

        return value

    def _base_stat(self, stat_name, tar_name):
        """
        Returns stat value resulting from base stat value and per lvl scaling,
        that is based exclusively on champion (no items, runes, masteries etc.).

        :param stat_name: (str)
        :param tar_name: (str)
        :return: (float)
        """

        base_val = self.base_stats_dct[tar_name][stat_name]
        per_lvl_val = (self.champion_lvls_dct[tar_name] * self.base_stats_dct[tar_name]['{}_per_lvl'.format(stat_name)])
        return base_val + per_lvl_val

    def base_ad(self, tar_name):
        """
        Calculates the value of base ad.

        Base ad is the champion's ad at lvl 1 without any bonuses,
        plus the per lvl bonus.

        Returns:
            (float)
        """

        return self._base_stat(stat_name='ad', tar_name=tar_name)

    def att_speed(self, tar_name):
        """
        Calculates final value of att_speed, after all bonuses and filters have been applied.

        Bonuses to att_speed are always percent, including the '_per_lvl' bonus.
        Therefor they are applied simultaneously (to preserve base value until calculation).
        Unlike other stats, _per_lvl bonus is applied at lvl 2.

        Filter applies att_speed's hard cap.

        Each reduction of att_speed is applied after all other bonuses have been applied,
        by multiplying the pre-final value with each reduction.

        Returns:
            (float)
        """

        value = self.base_stats_dct[tar_name]['base_att_speed']

        # _PER_LVL
        # Adds _per_lvl bonus of att_speed to the modifier.
        multiplication_mod = 100
        multiplication_mod += self.base_stats_dct[tar_name]['att_speed_per_lvl'] * (self.champion_lvls_dct[tar_name]-1)

        # ITEM AND BUFF BONUSES
        # Adds item and buff bonuses of att_speed to the modifier.
        tar_bonuses = self.bonuses_dct[tar_name]
        if 'att_speed' in tar_bonuses:       # 'percent..' not checked since it can only be that.
            for bonus_name in tar_bonuses['att_speed']['percent']:
                multiplication_mod += tar_bonuses['att_speed']['percent'][bonus_name]

        value *= multiplication_mod / 100

        # REDUCTIONS
        if 'att_speed_reduction' in tar_bonuses:
            for bonus_name in tar_bonuses['att_speed_reduction']['percent']:
                value *= 1 - tar_bonuses['att_speed_reduction']['percent'][bonus_name]

        return value

    def move_speed(self, tar_name):
        """
        Calculates final value of movement speed, after all bonuses and soft caps are applied.

        -Additive bonuses are applied.
        -Multiplicative bonuses are applied by a single modifier for all bonuses.
        -Strongest speed reduction effected is fully applied.
        -The other speed reductions are applied at 35% of their max.

        Returns:
            (float)
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
            max_reduction_bonus_name = ''
            reductions_values_dct = {}
            # Creates a reverse dictionary with stat_value as key (some keys might be overwritten without problem).
            for bonus in tar_bonuses['move_speed_reduction']['percent']:
                reductions_values_dct.update(
                    {tar_bonuses['move_speed_reduction']['percent'][bonus]: bonus})

                # Bonus name of max value is stored.
                max_value = max(reductions_values_dct.keys())
                max_reduction_bonus_name = tar_bonuses['move_speed_reduction']['percent'][max_value]

            for bonus in tar_bonuses['move_speed_reduction']['percent']:
                if bonus == max_reduction_bonus_name:
                    value *= 1-tar_bonuses['move_speed_reduction']['percent'][bonus]*(1-slow_mod)
                else:
                    value *= 1-tar_bonuses['move_speed_reduction']['percent'][bonus]*(1-slow_mod)*0.35

        return self.filtered_move_speed(unfiltered_stat=value)

    def crit_chance(self, tar_name):
        """
        Returns filtered value of crit_chance.

        Returns:
            (float)
        """

        return self.filtered_crit_chance(self.standard_stat(requested_stat='crit_chance',
                                                            tar_name=tar_name))

    def cdr(self, tar_name):
        """
        Returns filtered value of cdr.

        Returns:
            (float)
        """

        return self.filtered_cdr(self.standard_stat(requested_stat='cdr',
                                                    tar_name=tar_name))


class StatRequest(StatCalculation):

    """
    Contains methods for handing requests to a stat's calculation.

    Stats are calculated once and then stored until they or their controllers (stats or buffs) change.
    """

    def __init__(self,
                 champion_lvls_dct,
                 selected_champions_dct,
                 req_buff_dct_func,
                 initial_active_buffs=None,
                 initial_current_stats=None):

        self.req_buff_dct_func = req_buff_dct_func

        StatCalculation.__init__(self,
                                 champion_lvls_dct=champion_lvls_dct,
                                 selected_champions_dct=selected_champions_dct,
                                 initial_active_buffs=initial_active_buffs,
                                 initial_current_stats=initial_current_stats)

    SPECIAL_STATS_SET = SPECIAL_STATS_SET

    def _evaluate_stat(self, target_name, stat_name):
        """
        Calculates a target's final stat value and stores it.
        Then notes that it has not changed since last calculation.

        Modifies:
            stored_stats: stores new value of a target's stat
            stat_changes: sets to False for target's stat
        Returns:
            (None)
        """

        # Special stats have their own methods.
        if stat_name in ALLOWED_BONUS_STATS:
            self.stored_stats[target_name][stat_name] = self._bonus_stat(stat_name=stat_name, tar_name=target_name)
        elif stat_name in self.SPECIAL_STATS_SET:
            self.stored_stats[target_name][stat_name] = getattr(self, stat_name)(target_name)

        # Most stats can be calculated using the 'standard_stat' method.
        else:
            self.stored_stats[target_name][stat_name] = self.standard_stat(requested_stat=stat_name,
                                                                           tar_name=target_name)

        # Sets stat_changes for given target's stat to false.
        # (if not created yet, it creates it)
        self.stat_changes[target_name][stat_name] = False

    def _check_and_update_stored_buff(self, tar_name, buff_name):
        """
        Adds a buff which affects stats (if not already added).

        Modifies:
            stored_buffs
        Returns:
            (None)
        """

        # Checks if buff exists in targets dict.
        try:
            self.stored_buffs[tar_name][buff_name]

        except KeyError:
            buff_dct = self.req_buff_dct_func(buff_name=buff_name)

            # Checks if buff modifies stats.
            if 'stats' in buff_dct:

                # If so stores each stat that gets modified by it.
                self.stored_buffs[tar_name][buff_name] = {'stats_it_mods': []}

                for stat_name in buff_dct['stats']:
                    self.stored_buffs[tar_name][buff_name]['stats_it_mods'].append(stat_name)
                    self.stat_changes[tar_name][stat_name] = True

                # Marks its current stacks.
                self.stored_buffs[tar_name][buff_name].update(
                    {'stacks': self.active_buffs[tar_name][buff_name]['current_stacks']})

    def _compare_and_update_stored_buffs(self, tar_name, stat_name):
        """
        Marks modified stats when a buff that affects them has been removed
        or its stacks changed, and then updates stored_buffs.

        Modifies:
            stat_changes
            stored_buffs
        Returns:
            (None)
        """

        tar_stored_buffs = self.stored_buffs[tar_name]
        tar_act_buffs = self.active_buffs[tar_name]

        # Checks each buff for changes.
        for buff_name in sorted(tar_stored_buffs):
            # If there are buffs that modify the given stat..
            if stat_name in tar_stored_buffs[buff_name]['stats_it_mods']:

                # .. and if buff has been removed ..
                if buff_name not in tar_act_buffs:

                    # .. marks stat affect by the buff as changed,
                    self.stored_stats[tar_name][stat_name] = True
                    # .. and updates the stored_buffs dict.
                    del tar_stored_buffs[buff_name]

                # If its stacks changed..
                else:
                    if tar_act_buffs[buff_name]['current_stacks'] != tar_stored_buffs[buff_name]['stacks']:

                        # .. marks stats the buff affects as changed.
                        self.stat_changes[tar_name][stat_name] = True
                        # .. and updates the stacks in the stored_buffs dict.
                        tar_stored_buffs[buff_name]['stacks'] = tar_act_buffs[buff_name]['current_stacks']

        # Checks if there is a new active buff (that modifies stats).
        for buff in tar_act_buffs:
            if buff not in tar_stored_buffs:
                buff_dct = self.req_buff_dct_func(buff_name=buff)
                if ('stats' in buff_dct) and (stat_name in buff_dct['stats']):

                    self._check_and_update_stored_buff(tar_name=tar_name, buff_name=buff)

    def _insert_bonus_to_tar_bonuses(self, stat_name, bonus_type, buff_dct, tar_name, buff_name):
        """
        Updates a target's bonuses_dct by adding the name and value of a bonus.

        Modifies:
            bonuses_dct
        Returns:
            (None)
        """

        value = buff_dct['stats'][stat_name][bonus_type]
        # Stacks.
        value *= self.active_buffs[tar_name][buff_name]['current_stacks']

        # Inserts bonus_name and its value in bonuses_dct.
        self.bonuses_dct[tar_name][stat_name][bonus_type].update({buff_name: value})

    def _buffs_to_bonuses(self, stat_name, tar_name):
        """
        Stores a stat's bonuses caused by buffs.

        Structure:
            bonuses_dct: {target: {stat: {bonus type: {bonus name: }, }, }, }
            buff dct: { , , 'stats': {stat_name: {'additive': value}, }, .. }
        Modifies:
            bonuses_dct

        Returns:
            (None)
        """

        for buff_name in self.active_buffs[tar_name]:
            self._check_and_update_stored_buff(tar_name=tar_name, buff_name=buff_name)

            buff_dct = self.req_buff_dct_func(buff_name=buff_name)
            # Checks if the buff has stat bonuses.
            if 'stats' in buff_dct:

                if stat_name in buff_dct['stats']:

                    tar_bonuses = self.bonuses_dct[tar_name]

                    if stat_name in tar_bonuses:
                        # Iterates through types. (additive, percent or both)
                        for bonus_type in buff_dct['stats'][stat_name]:
                            if bonus_type in tar_bonuses[stat_name]:

                                self._insert_bonus_to_tar_bonuses(stat_name=stat_name, bonus_type=bonus_type,
                                                                  buff_dct=buff_dct, tar_name=tar_name,
                                                                  buff_name=buff_name)

                            else:
                                # Inserts bonus_type in bonuses_dct.
                                tar_bonuses[stat_name].update({bonus_type: {}})

                                self._insert_bonus_to_tar_bonuses(stat_name=stat_name, bonus_type=bonus_type,
                                                                  buff_dct=buff_dct, tar_name=tar_name,
                                                                  buff_name=buff_name)

                    else:
                        for bonus_type in buff_dct['stats'][stat_name]:
                            # Inserts stat_name in bonuses_dct.
                            tar_bonuses.update({stat_name: {}})
                            # Inserts bonus_type in bonuses_dct.
                            tar_bonuses[stat_name].update({bonus_type: {}})

                            self._insert_bonus_to_tar_bonuses(stat_name=stat_name, bonus_type=bonus_type,
                                                              buff_dct=buff_dct, tar_name=tar_name,
                                                              buff_name=buff_name)

    def request_stat(self, target_name, stat_name, _return_value=True):
        """
        Calculates the final value of a stat, and modifies bonuses_dct and stat_dct.

        A stat (dependent) might depend on the value of other stats (controllers).
        If a dependent stat is requested,
        changes to its controllers are applied and then it is evaluated, and finally returned.

        If the stat or its controllers have not been modified, its stored value is returned.

        Modifies:

        Args:
            _return_value: Set to false when function used only for refreshing a stat value.
        Returns:
            (float) final value of stat
            (None)
        """

        # If the stat is being controlled by other stat..
        if stat_name in self.stat_dependencies[target_name]:

            # ..for each controller..
            for controller in self.stat_dependencies[target_name][stat_name]:

                # .. requests its value (that is, refreshes its value or fetches the stored value).
                # Recursive calls force controllers to refresh if needed.
                # (controllers' buffs to bonuses are refreshed first)
                self.request_stat(target_name=target_name, stat_name=controller, _return_value=False)

        # Check if target's buff affecting given stat have changed.
        self._compare_and_update_stored_buffs(tar_name=target_name, stat_name=stat_name)

        # Evaluates the stat if it hasn't been evaluated before or if it has changed.
        if stat_name not in self.stat_changes[target_name] or self.stat_changes[target_name][stat_name] is True:

            # Since earlier controllers have been refreshed (including their bonuses from buffs),
            # it can safely create buff bonuses for selected stat,
            # and then evaluate the stat.
            self._buffs_to_bonuses(stat_name=stat_name, tar_name=target_name)
            self._evaluate_stat(target_name=target_name, stat_name=stat_name)

        if _return_value:
            return self.stored_stats[target_name][stat_name]

    def set_current_stats(self):
        """
        Inserts current_hp in current_stats of each target and current resource (e.g. mp, rage, etc) for player.
        If the current_stats dict is empty, or if the value doesnt exist it creates the value.

        Modifies:
            current_stats
        Returns:
            (None)
        """

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
                    resource_used = self.base_stats_dct['player']['resource_used']

                    if ('current_' + resource_used) not in self.current_stats[tar]:

                        self.current_stats['player'].update(

                            {('current_' + resource_used): self.request_stat(target_name=tar,
                                                                             stat_name=resource_used)})

    def _bonus_stat(self, stat_name, tar_name):
        """
        Base method for methods that return only the bonus value of a stat,
        that is, only non-champion related value (base and per lvl).

        :param stat_name: (str)
        :param tar_name: (str)
        :return: (float)
        """

        base_val = self._base_stat(stat_name=stat_name, tar_name=tar_name)

        return self.request_stat(target_name=tar_name, stat_name=stat_name) - base_val


class DmgReductionStats(StatRequest):

    """
    Contains methods for the calculation of dmg reduction related stats' values.
    """

    DEFENSE_REDUCING_MR_AND_ARMOR_MAP = DEFENSE_REDUCING_MR_AND_ARMOR_MAP

    # structure: {tar_name: {stat_1: [controller_stat_1, controller_stat_2,], }, }
    DMG_REDUCTION_STAT_DEPENDENCIES = {
        'all_targets': dict(
            reduced_armor=list(DEFENSE_REDUCING_MR_AND_ARMOR_MAP['armor'].values()),
            reduced_mr=list(DEFENSE_REDUCING_MR_AND_ARMOR_MAP['mr'].values())), }

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
    def percent_dmg_reduction_by_defensive_stat(stat_value):
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

        return self.percent_dmg_reduction_by_defensive_stat(stat_value=stat_val)

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
        if 'percent_physical_reduction' in self.bonuses_dct[tar_name]:
            tar_percent_red_bonuses = self.bonuses_dct[tar_name]['percent_physical_reduction']['percent']

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
        if 'percent_magic_reduction' in self.bonuses_dct[tar_name]:
            tar_percent_red_bonuses = self.bonuses_dct[tar_name]['percent_magic_reduction']['percent']

            for bonus_name in tar_percent_red_bonuses:
                # .. they are multiplied.
                value *= 1 - tar_percent_red_bonuses[bonus_name]

        return value


if __name__ == '__main__':

    pass