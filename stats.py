import database_champion_stats
import dmg_reduction
import copy


class StatFilters(object):

    """
    Contains functions that filter stats to prevent them exceeding their thresholds.
    """

    @staticmethod
    def filtered_crit(unfiltered_stat):
        """
        Applies threshold on crit.

        Args:
            unfiltered_stat: (float)
        Returns:
            (float) final stat value

        >>>StatFilters().filtered_crit(1.2)
        1.
        >>>StatFilters().filtered_crit(0.1)
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


class StatCalculation(StatFilters, dmg_reduction.DmgMitigation):

    """
    Contains methods for the calculation of each stat.
    """

    def __init__(self,
                 champion_lvls_dct,
                 selected_champions_dct,
                 initial_active_buffs=None,
                 initial_current_stats=None):

        self.champion_lvls_dct = champion_lvls_dct
        self.selected_champions_dct = selected_champions_dct

        self.initial_active_buffs = initial_active_buffs
        self.bonuses_dct = {}   # e.g. {target: {stat: {bonus type: {bonus name: }, }, }, }

        self.initial_current_stats = initial_current_stats

        self.active_buffs = None

        self.current_stats = {}
        self.stat_dependencies = {}     # e.g. {tar_name: {stat_1: [stat_2, stat_3], }, }
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

    def set_current_stats(self):
        """
        Modifies current_stats dict by inserting target's current_hp and current resource (e.g. mana, rage, etc).

        If the current_stats dict is empty, or if the value doesnt exist it creates the value.
        """

        if self.initial_current_stats:
            self.current_stats = copy.deepcopy(self.initial_current_stats)

        for tar in self.selected_champions_dct:

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

    def place_tar_and_empty_dct_in_dct(self, dct):
        """
        Modifies a dict by inserting target names as keywords, and empty dict as value for all targets.
        """

        for tar in self.selected_champions_dct:
            dct.update({tar: {}})

    def set_active_buffs(self):
        """
        Modifies active_buffs, by adding the target to the dictionary if it's not already there.
        """

        # If active_buffs is None, it makes it a dict.
        if not self.initial_active_buffs:
            self.active_buffs = {}
        else:
            self.active_buffs = copy.deepcopy(self.initial_active_buffs)

        # Fills with targets that have not been set.
        for tar in self.selected_champions_dct:
            if tar not in self.active_buffs:
                self.active_buffs.update({tar: {}})

    def base_stats_dct(self):
        """
        Returns dictionary containing the base stats of all targets.
        """

        dct = {}

        # For each target..
        for tar_name in self.selected_champions_dct:
            # .. updates base_stats_dct with his base stats.
            dct.update(
                {tar_name: database_champion_stats.CHAMPION_BASE_STATS[self.selected_champions_dct[tar_name]]})

        return dct

    def standard_stat(self, requested_stat, tar_name):
        """
        Returns the value of a stat after calculating all its bonuses.

        Not to be used for att_speed, or ad.
        Not to be used for filtered stats.

        If stat doesnt exist it returns 0.
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
        bonuses_tar = self.bonuses_dct[tar_name]
        if requested_stat in bonuses_tar:

            # .. if there are additive bonuses..
            if 'additive' in bonuses_tar[requested_stat]:
                # .. adds each bonus.
                for bonus_name in bonuses_tar[requested_stat]['additive']:
                    value += bonuses_tar[requested_stat]['additive'][bonus_name]

            # if there are percent bonuses..
            if 'percent' in bonuses_tar[requested_stat]:
                multiplicative_mod = 1
                # .. adds each bonus modifier..
                for bonus_name in bonuses_tar[requested_stat]['percent']:
                    multiplicative_mod += bonuses_tar[requested_stat]['percent'][bonus_name]

                # .. and applies the modifier to the value.
                value *= multiplicative_mod

        return value

    def base_ad_stat(self, tar_name):
        """
        Returns the value of base ad.
        """

        return self.base_stats_dct()[tar_name]['ad'] + (self.champion_lvls_dct[tar_name] *
                                                        self.base_stats_dct()[tar_name]['ad_per_lvl'])

    def bonus_ad_stat(self, tar_name):
        """Returns the value of bonus ad.
        """
        return self.standard_stat(requested_stat='ad', tar_name=tar_name) - self.base_ad_stat(tar_name=tar_name)

    def att_speed_stat(self, tar_name):
        """Returns att_speed after all bonuses have been applied, and it has been filtered.

        -Bonuses to att_speed are always percent, including the '_per_lvl' bonus.
            Therefor they are applied simultaneously. Also _per_lvl bonus is applied at lvl 2.
        -att_speed has a hard cap.
        -Each reduction of att_speed is applied after all other bonuses have been applied,
            by multiplying the pre-final value with each reduction.
        """

        value = self.base_stats_dct()[tar_name]['base_att_speed']

        # _PER_LVL
        # Adds _per_lvl bonus of att_speed to the modifier.
        multiplicative_mod = (
            1 + self.base_stats_dct()[tar_name]['att_speed_per_lvl'] * (self.champion_lvls_dct[tar_name] - 1)
        )

        # ITEM AND BUFF BONUSES
        # Adds item and buff bonuses of att_speed to the modifier.
        bonuses_tar = self.bonuses_dct[tar_name]
        if 'att_speed' in bonuses_tar:       # 'multi..' not checked since it can only be that.
            for bonus_name in bonuses_tar['att_speed']['percent']:
                multiplicative_mod += bonuses_tar['att_speed']['percent'][bonus_name]

        value *= multiplicative_mod

        # REDUCTIONS
        if 'att_speed_reduction' in bonuses_tar:
            for bonus_name in bonuses_tar['att_speed_reduction']['percent']:
                value *= 1 - bonuses_tar['att_speed_reduction']['percent'][bonus_name]

        return value

    def move_speed_stat(self, tar_name):
        """Returns movement speed after all bonuses and soft caps are applied.

        -Additive bonuses to speed are applied.
        -Multiplicative bonuses are applied by a single modifier for all bonuses.
        -Strongest speed reduction effected is fully applied.
        -The other speed reductions are applied at 35% of their max.
        """

        # BASE VALUE AND BONUSES
        value = self.standard_stat(requested_stat='move_speed',
                                   tar_name=tar_name)

        # SLOW REDUCTIONS
        # Calculates the modifier that dampens slow effects (e.g. boots of swiftness)
        bonuses_tar = self.bonuses_dct[tar_name]
        slow_mod = 1
        if 'slow_reduction' in bonuses_tar:
            for slow_red_bonus in bonuses_tar['slow_reduction']['percent']:
                slow_mod -= slow_red_bonus

        # SPEED REDUCTIONS
        if 'move_speed_reduction' in bonuses_tar:
            max_reduction_bonus_name = ''
            reductions_values_dct = {}
            # Creates a reverse dictionary with stat_value as key (some keys might be overwritten without problem).
            for bonus in bonuses_tar['move_speed_reduction']['percent']:
                reductions_values_dct.update(
                    {bonuses_tar['move_speed_reduction']['percent'][bonus]: bonus})

                # Bonus name of max value is stored.
                max_value = max(reductions_values_dct.keys())
                max_reduction_bonus_name = bonuses_tar['move_speed_reduction']['percent'][max_value]

            for bonus in bonuses_tar['move_speed_reduction']['percent']:
                if bonus == max_reduction_bonus_name:
                    value *= 1-bonuses_tar['move_speed_reduction']['percent'][bonus]*(1-slow_mod)
                else:
                    value *= 1-bonuses_tar['move_speed_reduction']['percent'][bonus]*(1-slow_mod)*0.35

        return self.filtered_move_speed(unfiltered_stat=value)

    def crit_stat(self, tar_name):
        """Returns filtered value of crit.
        """

        return self.filtered_crit(self.standard_stat(requested_stat='crit',
                                                     tar_name=tar_name))

    def cdr_stat(self, tar_name):
        """Returns filtered value of cdr.
        """

        return self.filtered_cdr(self.standard_stat(requested_stat='cdr',
                                                    tar_name=tar_name))

    def physical_reduction_by_armor_stat(self, tar_name):
        """
        Returns physical dmg reduction caused by armor.
        """

        return self.percent_physical_reduction_by_armor(request_stat=self.request_stat,
                                                        bonuses_dct=self.bonuses_dct,
                                                        target=tar_name)

    def magic_reduction_by_mr_stat(self, tar_name):
        """
        Returns magic dmg reduction caused by mr.
        """

        return self.percent_magic_reduction_by_mr(request_stat=self.request_stat,
                                                  bonuses_dct=self.bonuses_dct,
                                                  target=tar_name)

    def percent_physical_reduction(self, tar_name):
        """
        Returns percent physical reduction.

        Initial bonus is equal to reduction from armor. Then each other bonus is multiplied to it.
        """

        # Initially it's set to physical reduction by armor.
        value = 1 - self.physical_reduction_by_armor_stat(tar_name)

        # If there are any bonuses to physical reduction..
        if 'percent_physical_reduction' in self.bonuses_dct[tar_name]:

            for bonus_name in self.bonuses_dct[tar_name]['percent_physical_reduction']['percent']:
                # .. they are multiplied.
                value *= 1 - self.bonuses_dct[tar_name]['percent_physical_reduction']['percent'][bonus_name]

        return 1-value

    def percent_magic_reduction(self, tar_name):
        """
        Returns percent magic reduction.

        Initial bonus is equal to reduction from mr. Then each other bonus is multiplied to it.
        """

        # Initially it's set to physical reduction by armor.
        value = 1 - self.magic_reduction_by_mr_stat(tar_name)

        # If there are any bonuses to physical reduction..
        if 'percent_magic_reduction' in self.bonuses_dct[tar_name]:

            for bonus_name in self.bonuses_dct[tar_name]['percent_magic_reduction']['percent']:
                # .. they are multiplied.
                value *= 1 - self.bonuses_dct[tar_name]['percent_magic_reduction']['percent'][bonus_name]

        return 1-value

    def evaluate_stat(self, target_name, stat_name):
        """
        -Modifies stored_stats by storing the new value of a stat of target.
        -Modifies stat_changes by setting it False for given stat of target.
        """

        special_stat_tpl = ('base_ad',
                            'bonus_ad',
                            'att_speed',
                            'move_speed',
                            'crit',
                            'cdr',
                            'physical_reduction_by_armor',
                            'magic_reduction_by_mr',)

        special_stat_tpl_2 = ('percent_physical_reduction',
                              'percent_magic_reduction',)

        # Most stats can be calculated using the 'standard_stat' method.
        if stat_name in special_stat_tpl:
            self.stored_stats[target_name][stat_name] = getattr(self, stat_name + '_stat')(target_name)

        # Special stats have their own methods.
        elif stat_name in special_stat_tpl_2:
            self.stored_stats[target_name][stat_name] = getattr(self, stat_name)(target_name)
        else:
            self.stored_stats[target_name][stat_name] = self.standard_stat(stat_name, target_name)

        # Creates stat_changes for given stat (if not created yet) and sets it to False.
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
        Returns the value of a stat, and modifies bonuses_dct and stat_dct.

        A stat (dependent) might depend on the value of other stats (controllers).
        If a dependent stat is requested,
        changes to its controllers are applied and then it is evaluated, and finally returned.

        If the stat or its controllers have not been modified, its stored value is returned.

        Args:
            return_value: Set to false when function used only for refreshing a stat value.
        Returns:
            float (stat value)
            None
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


if __name__ == '__main__':

    class TestStatCalculation(object):

        def __init__(self):

            self.DELIMITER = '\n--------------------------------'
            self.filtered_stats_max = {'crit': 1., 'move_speed': None, 'att_speed': 2.5, 'cdr': 0.4}

            self.selected_champions_dct = None
            self.champion_lvls_dct = None
            self.initial_active_buffs = None
            self.initial_current_stats = None
            self.items_stats_bonuses = None

        def set_up(self):

            self.selected_champions_dct = dict(
                player='jax',
                enemy_1='jax',
                enemy_2='jax',
                enemy_3='jax')

            self.champion_lvls_dct = dict(
                player=1,
                enemy_1=1,
                enemy_2=1,
                enemy_3=1
            )

            self.initial_active_buffs = None
            self.initial_current_stats = {'player': {'current_mana': 100}}

        @staticmethod
        def combiner_class():

            class BuffClass(object):

                @staticmethod
                def buff_att_speed_percent():
                    return dict(
                        stats=dict(
                            att_speed=dict(
                                percent=0.5)))

                @staticmethod
                def buff_ad_flat():
                    return dict(
                        stats=dict(
                            ad=dict(
                                additive=10)))

                @staticmethod
                def buff_kass_reduction():
                    return dict(
                        stats=dict(
                            percent_magic_reduction=dict(
                                percent=0.15)))

            class CombinerClass(StatCalculation, BuffClass):

                def __init__(self,
                             champion_lvls_dct,
                             selected_champions_dct,
                             active_buffs):

                    StatCalculation.__init__(self,
                                             champion_lvls_dct=champion_lvls_dct,
                                             selected_champions_dct=selected_champions_dct,
                                             initial_active_buffs=active_buffs)

            return CombinerClass

        def test_standard_stat_no_bonuses(self, player_lvl):
            self.set_up()

            self.champion_lvls_dct['player'] = player_lvl

            inst = StatCalculation(champion_lvls_dct=self.champion_lvls_dct,
                                   selected_champions_dct=self.selected_champions_dct,
                                   initial_active_buffs=self.initial_active_buffs)

            msg = self.DELIMITER
            msg += '\nTesting method: standard_stats'
            msg += '(no bonuses)\n\n'
            msg += 'player lvl: %s\n' % self.champion_lvls_dct['player']

            for stat_name in ('ad', 'mr', 'armor', 'move_speed', 'range', 'mp5', 'hp5'):
                msg += str(stat_name) + ': ' + str(inst.standard_stat(stat_name, 'player')) + '\n'

            return msg

        def test_request_stat_no_bonuses(self, enemy_1_lvl):
            self.set_up()

            self.champion_lvls_dct['enemy_1'] = enemy_1_lvl

            inst = StatCalculation(champion_lvls_dct=self.champion_lvls_dct,
                                   selected_champions_dct=self.selected_champions_dct)

            msg = self.DELIMITER
            msg += '\nTesting method: request_stat (special stats)'
            msg += '(no bonuses)\n\n'
            msg += 'enemy_1 lvl: %s\n' % self.champion_lvls_dct['enemy_1']

            for stat_name in ('base_ad',
                              'bonus_ad',
                              'att_speed',
                              'move_speed',
                              'cdr',
                              'physical_reduction_by_armor',
                              'magic_reduction_by_mr'):
                msg += str(stat_name) + ': ' + str(inst.request_stat('enemy_1', stat_name)) + '\n'

            return msg

        def test_current_stats(self, target):
            self.set_up()

            msg = ''

            init_curr_stats_1 = None
            init_curr_stats_2 = dict(player=dict(current_hp=100,
                                                 current_mp=50),
                                     enemy_1={'current_hp': 100})

            for dct in (init_curr_stats_1, init_curr_stats_2):
                inst = StatCalculation(champion_lvls_dct=self.champion_lvls_dct,
                                       selected_champions_dct=self.selected_champions_dct,
                                       initial_current_stats=dct)

                msg += self.DELIMITER
                msg += '\nTesting method: set_current_stats \n\n'
                if not dct:
                    msg += '(initial stats not set)\n\n'

                msg += '%s max hp: %s\n' % (target, inst.request_stat(target, 'hp'))
                msg += '%s current hp: %s\n' % (target, inst.current_stats[target]['current_hp'])

                if target == 'player':
                    msg += '%s max mp: %s\n' % (target, inst.request_stat(target, 'mp'))
                    msg += '%s current mp: %s\n' % (target, inst.current_stats['player']['current_mp'])

            return msg

        def test_request_stat_plus_bonuses(self, enemy_1_lvl):
            self.set_up()

            self.champion_lvls_dct['enemy_1'] = enemy_1_lvl

            self.initial_active_buffs = dict(
                player={},
                enemy_1={'buff_ad_flat': None, 'buff_att_speed_percent': None})

            inst = self.combiner_class()(champion_lvls_dct=self.champion_lvls_dct,
                                         selected_champions_dct=self.selected_champions_dct,
                                         active_buffs=self.initial_active_buffs)

            inst.buffs_to_bonuses()

            msg = self.DELIMITER
            msg += '\nTesting method: request_stat (special stats)'
            msg += '\nbonuses:\n'

            msg += 'ad: 10 flat)\n'
            msg += 'att_speed: 50%\n\n'

            msg += 'enemy_1 lvl: %s\n' % self.champion_lvls_dct['enemy_1']

            for stat_name in ('base_ad',
                              'bonus_ad',
                              'ad',
                              'att_speed',
                              'move_speed'):
                msg += str(stat_name) + ': ' + str(inst.request_stat('enemy_1', stat_name)) + '\n'

            return msg

        def test_percent_magic_reduction(self, tar_name):
            self.set_up()

            self.initial_active_buffs = dict(
                player={'buff_kass_reduction': None},
                enemy_1={})

            inst = self.combiner_class()(champion_lvls_dct=self.champion_lvls_dct,
                                         selected_champions_dct=self.selected_champions_dct,
                                         active_buffs=self.initial_active_buffs)

            inst.buffs_to_bonuses()

            msg = ''

            msg += self.DELIMITER

            msg += '\nTesting method: percent_magic_reduction \n'

            msg += ('\npercent magic reduction from buff: %s\n'
                    '') % self.initial_active_buffs[tar_name]

            msg += 'target: %s, \nmagic reduction: %s' % (tar_name, inst.percent_magic_reduction(tar_name=tar_name))

            return msg

        def __repr__(self):

            msg = ''
            for player_lvl in (1, 2, 18):
                msg += self.test_standard_stat_no_bonuses(player_lvl)

            msg += self.DELIMITER

            for enemy_1_lvl in (1, 2):
                msg += self.test_request_stat_no_bonuses(enemy_1_lvl)

            msg += self.DELIMITER

            for tar_name in ('player', 'enemy_1'):
                msg += self.test_current_stats(tar_name)

            msg += self.DELIMITER

            for tar_name in ('player', 'enemy_1'):
                msg += self.test_percent_magic_reduction(tar_name)

            msg += self.DELIMITER

            for enemy_1_lvl in (1, 2):
                msg += self.test_request_stat_plus_bonuses(enemy_1_lvl)

            msg += self.DELIMITER

            return msg

    print(TestStatCalculation())