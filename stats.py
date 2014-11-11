import database_champion_stats
import copy


class StatFilters(object):

    """
    Contains functions that filter stats to prevent them exceeding their thresholds.
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
    Contains methods for the calculation of each stat.
    """

    def __init__(self,
                 champion_lvls_dct,
                 selected_champions_dct,
                 initial_active_buffs=None,
                 initial_current_stats=None):

        self.champion_lvls_dct = champion_lvls_dct
        self.selected_champions_dct = selected_champions_dct    # (Dependency of many methods.)

        self.initial_active_buffs = initial_active_buffs    # Can contain 0 to all targets and their buffs.
        self.bonuses_dct = {}   # e.g. {target: {stat: {bonus type: {bonus name: }, }, }, }

        self.initial_current_stats = initial_current_stats  # Can contain 0 to all targets and their stats.

        self.active_buffs = {}

        self.current_stats = {}
        self.stat_dependencies = {}     # e.g. {tar_name: {stat_1: [controller_stat_1, controller_stat_2,], }, }
        self.stored_stats = {}
        self.stat_changes = {}
        self.stored_buffs = {}  # Used for storing buff (that affects stats) and its stacks, of a target.

        self.place_tar_and_empty_dct_in_dct(self.stored_stats)
        self.place_tar_and_empty_dct_in_dct(self.stat_changes)
        self.place_tar_and_empty_dct_in_dct(self.stat_dependencies)
        self.place_tar_and_empty_dct_in_dct(self.bonuses_dct)
        self.place_tar_and_empty_dct_in_dct(self.stored_buffs)

        self.set_active_buffs()
        self.set_current_stats()

    # Stat names contains 2 stat variants of a defense reducing stat; armor and mr.
    # e.g. percent_armor_reduction and percent_mr_reduction
    DEFENSE_REDUCING_STATS = dict(
        armor=dict(
            percent_reduction='percent_armor_reduction',
            percent_penetration='percent_armor_penetration',
            flat_reduction='flat_armor_reduction',
            flat_penetration='flat_armor_penetration',
        ),
        mr=dict(
            percent_reduction='percent_mr_reduction',
            percent_penetration='percent_mr_penetration',
            flat_reduction='flat_mr_reduction',
            flat_penetration='flat_mr_penetration',
        )
    )

    SPECIAL_STATS_LST = ('base_ad',
                         'bonus_ad',
                         'att_speed',
                         'move_speed',
                         'crit_chance',
                         'cdr',
                         'physical_reduction_by_armor',
                         'magic_reduction_by_mr',
                         'reduced_armor',
                         'reduced_mr',
                         'physical_dmg_taken',
                         'magic_dmg_taken',)

    def base_stats_dct(self):
        """
        Creates a dict containing champion base stats for all targets.

        Returns:
            (dict) Base stats of all targets.
        """

        dct = {}

        # For each target..
        for tar_name in self.selected_champions_dct:
            # .. updates base_stats_dct with his base stats.
            dct.update(
                {tar_name: database_champion_stats.CHAMPION_BASE_STATS[self.selected_champions_dct[tar_name]]})

        return dct

    def place_tar_and_empty_dct_in_dct(self, dct):
        """
        Inserts into a dct target names as keywords, and empty dict as value for each targets.
        To be used for empty dicts only.

        Modifies:
            dct
        Returns:
            (None)
        Raises:
            (BaseException) If dict is not empty.
        """

        if dct:
            raise BaseException('Target will be replaced.')

        for tar in self.selected_champions_dct:
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
        for tar in self.selected_champions_dct:
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

        value = 0
        base_stats_tar = self.base_stats_dct()[tar_name]

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

    def base_ad(self, tar_name):
        """
        Calculates the value of base ad.

        Base ad is the champion's ad at lvl 1 without any bonuses,
        plus the per lvl bonus.

        Returns:
            (float)
        """

        return self.base_stats_dct()[tar_name]['ad'] + (self.champion_lvls_dct[tar_name] *
                                                        self.base_stats_dct()[tar_name]['ad_per_lvl'])

    def bonus_ad(self, tar_name):
        """Returns the value of bonus ad.
        """
        return self.standard_stat(requested_stat='ad', tar_name=tar_name) - self.base_ad(tar_name=tar_name)

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

        value = self.base_stats_dct()[tar_name]['base_att_speed']

        # _PER_LVL
        # Adds _per_lvl bonus of att_speed to the modifier.
        multiplication_mod = (
            1 + self.base_stats_dct()[tar_name]['att_speed_per_lvl'] * (self.champion_lvls_dct[tar_name] - 1)
        )

        # ITEM AND BUFF BONUSES
        # Adds item and buff bonuses of att_speed to the modifier.
        tar_bonuses = self.bonuses_dct[tar_name]
        if 'att_speed' in tar_bonuses:       # 'percent..' not checked since it can only be that.
            for bonus_name in tar_bonuses['att_speed']['percent']:
                multiplication_mod += tar_bonuses['att_speed']['percent'][bonus_name]

        value *= multiplication_mod

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

    def evaluate_stat(self, target_name, stat_name):
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
        if stat_name in self.SPECIAL_STATS_LST:
            self.stored_stats[target_name][stat_name] = getattr(self, stat_name)(target_name)

        # Most stats can be calculated using the 'standard_stat' method.
        else:
            self.stored_stats[target_name][stat_name] = self.standard_stat(stat_name, target_name)

        # Sets stat_changes for given target's stat to false.
        # (if not created yet, it creates it)
        self.stat_changes[target_name][stat_name] = False

    def check_and_update_stored_buff(self, tar_name, buff_name):
        """
        Modifies stored_buffs, by adding a buff which affects stats (if not already added).
        """

        try:
            self.stored_buffs[tar_name][buff_name]

        except KeyError:
            buff_dct = getattr(self, buff_name)()

            # Checks if buff modifies stats and if it's not permanent.
            if ('stats' in buff_dct) and ('duration' in buff_dct):

                self.stored_buffs[tar_name][buff_name] = {'stats_it_mods': []}

                for stat_name in buff_dct['stats']:
                    self.stored_buffs[tar_name][buff_name]['stats_it_mods'].append(stat_name)
                    self.stat_changes[tar_name][stat_name] = True

                if 'max_stacks' in buff_dct:
                    self.stored_buffs[tar_name][buff_name].update(
                        {'stacks': self.active_buffs[tar_name][buff_name]['current_stacks']})

    def compare_stored_buffs(self, tar_name, stat_name):
        """
        Modifies stat_changes and stored_buffs, by marking modified stats when a buff that affects them has been removed
        or its stacks changed, and then updating the stored_buffs.
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
                elif tar_act_buffs[buff_name]['current_stacks'] != tar_stored_buffs[buff_name]['stacks']:

                    # .. marks stats the buff affects as changed.
                    self.stat_changes[tar_name][stat_name] = True
                    # .. and updates the stacks in the stored_buffs dict.
                    tar_stored_buffs[buff_name]['stacks'] = tar_act_buffs[buff_name]['current_stacks']

        # Checks if there is a new active buff (that modifies stats).
        for buff in tar_act_buffs:
            if buff not in tar_stored_buffs:
                if ('stats' in getattr(self, buff)()) and (stat_name in getattr(self, buff)()['stats']):

                    self.check_and_update_stored_buff(tar_name=tar_name, buff_name=buff)

    def buffs_to_bonuses(self, stat_name, tar_name):
        """
        Modifies bonuses_dct by inserting a stat's bonuses caused by buffs.

        Bonuses dict structure: {target: {stat: {bonus type: {bonus name: }, }, }, }
        Buff dict structure: { , , 'stats': {stat_name: {'additive': value}, }, .. }
        """

        tar_act_buffs = self.active_buffs[tar_name]

        for buff_name in tar_act_buffs:
            self.check_and_update_stored_buff(tar_name=tar_name, buff_name=buff_name)

            buff_dct = getattr(self, buff_name)()
            # Checks if the buff has stat bonuses.
            if 'stats' in buff_dct:
                if stat_name in buff_dct['stats']:
                    if stat_name in self.bonuses_dct[tar_name]:
                        # Iterates through types. (additive, percent or both)
                        for bonus_type in buff_dct['stats'][stat_name]:
                            if bonus_type in self.bonuses_dct[tar_name][stat_name]:

                                # Value
                                value = buff_dct['stats'][stat_name][bonus_type]
                                # If the buff has stacks, multiplies value with stacks.
                                if 'current_stacks' in tar_act_buffs[buff_name]:
                                    value *= tar_act_buffs[buff_name]['current_stacks']

                                # Inserts bonus_name and its value in bonuses_dct.
                                self.bonuses_dct[tar_name][stat_name][bonus_type].update({buff_name: value})

                            else:
                                # Inserts bonus_type in bonuses_dct.
                                self.bonuses_dct[tar_name][stat_name].update({bonus_type: {}})
                                # Value
                                value = buff_dct['stats'][stat_name][bonus_type]
                                # If the buff has stacks, multiplies value with stacks.
                                if 'current_stacks' in tar_act_buffs[buff_name]:
                                    value *= tar_act_buffs[buff_name]['current_stacks']

                                # Inserts bonus_name and its value in bonuses_dct.
                                self.bonuses_dct[tar_name][stat_name][bonus_type].update({buff_name: value})

                    else:
                        for bonus_type in buff_dct['stats'][stat_name]:
                            # Inserts stat_name in bonuses_dct.
                            self.bonuses_dct[tar_name].update({stat_name: {}})
                            # Inserts bonus_type in bonuses_dct.
                            self.bonuses_dct[tar_name][stat_name].update({bonus_type: {}})
                            # Value
                            value = buff_dct['stats'][stat_name][bonus_type]
                            # If the buff has stacks, multiplies value with stacks.
                            if 'current_stacks' in tar_act_buffs[buff_name]:
                                value *= tar_act_buffs[buff_name]['current_stacks']

                            # Inserts bonus_name and its value in bonuses_dct.
                            self.bonuses_dct[tar_name][stat_name][bonus_type].update({buff_name: value})

    def request_stat(self, target_name, stat_name, return_value=True):
        """
        Calculates the final value of a stat, and modifies bonuses_dct and stat_dct.

        A stat (dependent) might depend on the value of other stats (controllers).
        If a dependent stat is requested,
        changes to its controllers are applied and then it is evaluated, and finally returned.

        If the stat or its controllers have not been modified, its stored value is returned.

        Modifies:

        Args:
            return_value: Set to false when function used only for refreshing a stat value.
        Returns:
            (float) final value of stat
            (None)
        """

        # If the stat is being controlled by other stat..
        if stat_name in self.stat_dependencies[target_name]:

            # ..for each controller..
            for controller in self.stat_dependencies[target_name][stat_name]:

                #.. requests its value (that is, refreshes or fetches its value).
                # Recursive calls force controllers to refresh if needed.
                # (controllers' buffs to bonuses are refreshed first)
                self.request_stat(target_name=target_name, stat_name=controller, return_value=False)

        # Check if target's buff affecting given stat have changed.
        self.compare_stored_buffs(tar_name=target_name, stat_name=stat_name)

        # Evaluates the stat if it hasn't been evaluated before or if it has changed.
        if stat_name not in self.stat_changes[target_name] or self.stat_changes[target_name][stat_name] is True:

            # Since earlier controllers have been refreshed (including their bonuses from buffs),
            # it can safely create buff bonuses for selected stat,
            # and then evaluate the stat.
            self.buffs_to_bonuses(stat_name=stat_name, tar_name=target_name)
            self.evaluate_stat(target_name=target_name, stat_name=stat_name)

        if return_value:
            return self.stored_stats[target_name][stat_name]

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
        percent_reduction_name = self.DEFENSE_REDUCING_STATS[stat]['percent_reduction']
        if percent_reduction_name in tar_bonuses:
            percent_reduction = self.request_stat(target_name=target,
                                                  stat_name=percent_reduction_name)
        else:
            percent_reduction = 0

        # percent_penetration calculation
        percent_penetration_name = self.DEFENSE_REDUCING_STATS[stat]['percent_penetration']
        if percent_penetration_name in self.bonuses_dct['player']:
            percent_penetration = self.request_stat(target_name='player',
                                                    stat_name=percent_penetration_name)
        else:
            percent_penetration = 0

        armor_after_reductions = self.request_stat(target_name=target,
                                                   stat_name=stat)
        # flat_reduction calculation
        flat_reduction_name = self.DEFENSE_REDUCING_STATS[stat]['flat_reduction']
        if flat_reduction_name in tar_bonuses:
            armor_after_reductions -= self.request_stat(target_name=target,
                                                        stat_name=flat_reduction_name)

        # Applies percent reduction and percent penetration
        if armor_after_reductions <= 0:
            return armor_after_reductions                               # Armor can't be reduced further if negative
        else:
            armor_after_reductions *= (1-percent_reduction) * (1-percent_penetration)

        # flat_penetration
        flat_penetration_name = self.DEFENSE_REDUCING_STATS[stat]['flat_penetration']
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
        """Returns the magic resist a dmg "sees".

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

    def set_current_stats(self):
        """
        Inserts current_hp in current_stats of each target and current resource (e.g. mana, rage, etc) for player.
        If the current_stats dict is empty, or if the value doesnt exist it creates the value.

        Modifies:
            current_stats
        Returns:
            (None)
        """

        # Checks if there are any preset values for current_stats.
        if self.initial_current_stats:
            self.current_stats = copy.deepcopy(self.initial_current_stats)

        for tar in self.selected_champions_dct:

            # If the target's current_hp has not been set, it creates it.
            if tar not in self.current_stats:
                self.current_stats.update({tar: {}})

                self.current_stats.update(
                    {tar: dict(current_hp=self.request_stat(target_name=tar, stat_name='hp'))})

            # Also creates the player's 'current_'resource.
            if tar == 'player':
                resource_used = self.base_stats_dct()['player']['resource_used']

                if ('current_' + resource_used) not in self.current_stats[tar]:

                    self.current_stats['player'].update(

                        {('current_' + resource_used): self.request_stat(target_name=tar,
                                                                         stat_name=resource_used)})


if __name__ == '__main__':

    pass