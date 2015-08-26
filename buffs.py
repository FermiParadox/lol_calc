import stats
import targeting
import items_module
import items_folder.items_data
import palette
import dmgs_buffs_categories
import masteries

import copy
import abc


class BuffsGeneral(stats.DmgReductionStats, targeting.Targeting,
                   masteries.MasteriesProperties, metaclass=abc.ABCMeta):

    def __init__(self,
                 selected_champions_dct,
                 champion_lvls_dct,
                 req_buff_dct_func,
                 selected_masteries_dct,
                 initial_current_stats,
                 initial_active_buffs,
                 chosen_items_dct,
                 initial_enemies_total_stats,
                 _reversed_combat_mode):

        self.current_time = 0

        stats.DmgReductionStats.__init__(self,
                                         champion_lvls_dct=champion_lvls_dct,
                                         selected_champions_dct=selected_champions_dct,
                                         req_buff_dct_func=req_buff_dct_func,
                                         initial_active_buffs=initial_active_buffs,
                                         initial_current_stats=initial_current_stats,
                                         initial_enemies_total_stats=initial_enemies_total_stats,
                                         _reversed_combat_mode=_reversed_combat_mode)

        masteries.MasteriesProperties.__init__(self,
                                               selected_masteries_dct=selected_masteries_dct,
                                               player_lvl=self.player_lvl)

        # ITEMS
        self.chosen_items_dct = chosen_items_dct
        self.fill_up_tars_and_empty_obj_in_dct(given_dct=self.chosen_items_dct, obj_type='list')
        self.player_items = self.chosen_items_dct['player']

        self._items_static_stats_buff_dct = {}
        self.create_player_static_items_buff()

    def create_player_static_items_buff(self):
        items_instance = items_module.ItemsProperties(chosen_items_lst=self.player_items)
        self._items_static_stats_buff_dct.update(items_instance.items_static_stats_buff_dct)

    def items_static_stats_buff(self):
        # Used for calling from apply_buff method.
        return self._items_static_stats_buff_dct

    @abc.abstractproperty
    def castable_spells_shortcuts(self):
        """
        Contains champion spells that can be casted.

        To be overridden for champions that castablility is dynamic (e.g. Volibear).

        :return: seq
        """
        pass

    def add_new_buff(self, buff_name, tar_name, initial_stacks_increment=1):
        """
        Inserts a new buff in active_buffs dictionary.

        Modifies:
            active_buffs
        Returns:
            (None)
        """

        buff_dct = self.req_buff_dct_func(buff_name=buff_name)

        # Inserts the new buff.
        self.active_buffs[tar_name].update(
            {buff_name: dict(
                starting_time=self.current_time)})

        # DURATION
        # If non permanent buff.
        if buff_dct['duration'] != 'permanent':

            # ..creates and inserts its duration.
            self.active_buffs[tar_name][buff_name].update(dict(
                ending_time=self.current_time + buff_dct['duration']))

        else:
            # ..otherwise sets its duration to 'permanent'.
            self.active_buffs[tar_name][buff_name].update(dict(
                ending_time='permanent'))

        # STACKS
        self.active_buffs[tar_name][buff_name].update(dict(current_stacks=initial_stacks_increment))

    def add_already_active_buff(self, buff_name, tar_name, stack_increment=1):
        """
        Changes an existing buff in active_buffs dictionary,
        by refreshing its duration and increasing its stacks.

        Modifies:
            active_buffs
        Returns:
            (None)
        """

        buff_dct = self.req_buff_dct_func(buff_name=buff_name)
        tar_buff_dct_in_act_buffs = self.active_buffs[tar_name][buff_name]

        # DURATION
        # If non permanent buff, refreshes its duration.
        if buff_dct['duration'] != 'permanent':

            tar_buff_dct_in_act_buffs['ending_time'] = self.current_time + buff_dct['duration']

        # STACKS
        # If max_stacks have not been reached..
        if tar_buff_dct_in_act_buffs['current_stacks'] < buff_dct['max_stacks']:

            # ..adds +1 to the stacks (unless increment is different).
            tar_buff_dct_in_act_buffs['current_stacks'] += stack_increment

            # Ensures max_stacks aren't exceeded for stack_increments larger than 1.
            if stack_increment > 1:

                if tar_buff_dct_in_act_buffs['current_stacks'] > buff_dct['max_stacks']:
                    # If max_stacks exceeded, set to max_stacks.
                    tar_buff_dct_in_act_buffs['current_stacks'] = buff_dct['max_stacks']

    def add_buff(self, buff_name, tar_name, stack_increment=1, initial_stacks_increment=1):
        """
        Inserts a new buff or refreshes an existing buff (duration and stacks).

        :return: (None)
        """

        # NEW BUFF
        if buff_name not in self.active_buffs[tar_name]:

            self.add_new_buff(buff_name=buff_name,
                              tar_name=tar_name,
                              initial_stacks_increment=initial_stacks_increment)

        # EXISTING BUFF
        else:
            self.add_already_active_buff(buff_name=buff_name,
                                         tar_name=tar_name,
                                         stack_increment=stack_increment)

    def add_single_ability_passive_buff(self, target_type, effects_dct, tar_name):
        """
        Adds passive buffs of a single ability on a target.

        :return: (None)
        """

        # Applies all passive buffs.
        for buff_name in effects_dct[target_type]['passives']['buffs']:
            self.add_buff(buff_name, tar_name)

    def add_items_passive_buffs(self, target_type, tar_name):
        """
        Adds all items' passive buffs on given target.

        (Enemy items don't apply any buffs here. They are to be applied in a separate method.)

        :return: (None)
        """
        if self.player_items:
            for item_name in self.player_items:
                # (If item is bought multiple times, all stacks are applied)
                self.add_single_ability_passive_buff(target_type=target_type,
                                                     effects_dct=items_folder.items_data.ITEMS_EFFECTS[item_name],
                                                     tar_name=tar_name)

    def add_abilities_and_items_passive_buffs(self, abilities_effects_dct_func, abilities_lvls):
        """
        Adds passive buffs from champion abilities (that apply on ability lvling) on all targets.

        :returns: (None)
        """

        for tar_name in self.champion_lvls_dct:
            # (player or enemy)
            target_type = self.target_type(tar_name=tar_name)

            # For Q,W,E and R...
            for ability_name in self.castable_spells_shortcuts:

                # ..if the ability has at least one lvl...
                if abilities_lvls[ability_name] > 0:

                    # .. applies the buffs.
                    self.add_single_ability_passive_buff(target_type=target_type,
                                                         effects_dct=abilities_effects_dct_func(ability_name),
                                                         tar_name=tar_name)

            # Innate passive buffs.
            self.add_single_ability_passive_buff(target_type=target_type,
                                                 effects_dct=abilities_effects_dct_func('inn'),
                                                 tar_name=tar_name)

        # Item passive buffs.
        self.add_items_passive_buffs(target_type='player', tar_name='player')


class Counters(BuffsGeneral):

    AOE_SPELLVAMP_MOD = 30/100
    EXTRA_STATS_SET = {'lifesteal', 'spellvamp', 'ap'}

    def __init__(self,
                 selected_champions_dct,
                 champion_lvls_dct,
                 req_buff_dct_func,
                 selected_masteries_dct,
                 initial_enemies_total_stats,
                 initial_current_stats,
                 initial_active_buffs,
                 chosen_items_dct,
                 max_combat_time,
                 _reversed_combat_mode):

        BuffsGeneral.__init__(self,
                              selected_champions_dct=selected_champions_dct,
                              champion_lvls_dct=champion_lvls_dct,
                              initial_current_stats=initial_current_stats,
                              initial_active_buffs=initial_active_buffs,
                              chosen_items_dct=chosen_items_dct,
                              req_buff_dct_func=req_buff_dct_func,
                              selected_masteries_dct=selected_masteries_dct,
                              initial_enemies_total_stats=initial_enemies_total_stats,
                              _reversed_combat_mode=_reversed_combat_mode)

        self.max_combat_time = max_combat_time
        self.total_movement = 0
        self.combat_end_time = 0

        self.actions_dct = {}
        self.combat_history = {}
        self.combat_results = {}

        self.set_combat_history()
        self.set_combat_results()

    def internally_displayed_player_stat_names(self):
        """
        Creates and returns all player stats to be stored (for internal display and testing purposes).

        Returns:
            (list)
        """

        lst = list(self.base_stats_dct['player'])
        lst += self.SPECIAL_STATS_SET
        lst += self.EXTRA_STATS_SET
        lst.append('current_hp')

        return lst

    def internally_displayed_enemy_stat_names(self):
        """
        Creates and returns all enemy stats to be stored (for internal display and testing purposes).

        Returns:
            (list)
        """

        lst = ['armor', 'mr', 'ap', 'current_hp']

        lst += self.DEFENSIVE_SPECIAL_STATS

        return lst

    # HISTORY ---------------------------------------------------------------------------------------------------------
    def set_combat_history(self):
        """
        Sets up combat_history by inserting history blueprints for all targets.

        :return: (None)
        """

        for tar in self.all_target_names:

            self.combat_history.update(
                {tar: dict(
                    true={},
                    magic={},
                    physical={},
                    total={},
                    current_hp={},
                )})

        self.combat_history['player'].update(dict(
            # Each dmg_name and its value
            # (e.g. {'AA': 56.1, 'w_dmg': 20.,})
            source={},

            # AA related dmg, including on_hit dmg.
            # (e.g. {'AA': [56.1, ], 'w_dmg': [],})
            AA_related=0.,

            ability=dict(
                inn=0.,
                q=0.,
                w=0.,
                e=0.,
                r=0.
            ),

            lifesteal={},
            spellvamp={},
            resource={},
            heals={},
            dmg_or_heal_taken=[]
        ))

    def add_dmg_tot_history(self):
        """
        Inserts a single dmg event (total dmg done during a given moment) regardless of type for each target.

        That is, if multiple dmg events occur simultaneously they are stored as a single dmg event.

        Modifies:
            combat_history
        Returns:
            (None)
        """

        for target_name in self.combat_history:
            if target_name != 'player':

                tar_dmg_hist = self.combat_history[target_name]

                for dmg_type in tar_dmg_hist:
                    if dmg_type not in ('total', 'current_hp'):
                        for dmg_time in tar_dmg_hist[dmg_type]:

                            dmg_value = tar_dmg_hist[dmg_type][dmg_time]

                            # Checks if event's time doesn't exist in 'total'.
                            if dmg_time not in tar_dmg_hist['total']:
                                tar_dmg_hist['total'].update({dmg_time: dmg_value})

                            else:
                                # If it exists, it adds the dmg value to the previous.
                                tar_dmg_hist['total'][dmg_time] += dmg_value

    def refined_combat_history(self):
        """
        Returns dict containing dmg history types as keywords and total dmg as values, for all enemy targets.

        History types:
            -true
            -physical
            -magic
            -healing (not included in 'all_targets')

            -lifesteal
            -spellvamp

            -aa_related
            -ability

        Dict format:
            {'enemy_1': {'true': 10.2, 'magic': ..}, 'enemy_2': .. , 'all_targets': {'true': ..} }
        """

        dct = {}

        # Total for all targets
        tot_true = 0
        tot_physical = 0
        tot_magic = 0

        for tar_name in self.combat_history:

            # Total for each target separately.
            tot_true_tar = 0
            tot_physical_tar = 0
            tot_magic_tar = 0
            tot_healing_tar = 0

            if tar_name != 'player':
                for hist_cat in self.combat_history[tar_name]:
                    for dmg_event in self.combat_history[tar_name][hist_cat]:
                        # Handles true, magic, and physical history.
                        if hist_cat in ('true', 'magic', 'physical'):
                            dmg_value = self.combat_history[tar_name][hist_cat][dmg_event]

                            # If it's dmg:
                            if dmg_value > 0:
                                if hist_cat == 'true':
                                    tot_true_tar += dmg_value
                                    tot_true += dmg_value

                                elif hist_cat == 'magic':
                                    tot_magic_tar += dmg_value
                                    tot_magic += dmg_value

                                elif hist_cat == 'physical':
                                    tot_physical_tar += dmg_value
                                    tot_physical += dmg_value

                            # Else it's a healing.
                            else:
                                tot_healing_tar += dmg_value

                        # Handles source related dmg history.
                        elif hist_cat == 'source':
                            for source_name in self.combat_history[tar_name][hist_cat]:
                                source_sum = sum(self.combat_history[tar_name][hist_cat][source_name])
                                # Updates with sum of each source.
                                dct.update(dict(source={source_name: source_sum}))

                        # Handles ability related dmg history.
                        elif hist_cat == 'ability':

                            # For Q, W, E, R..
                            for ability_name in self.combat_history[tar_name][hist_cat]:
                                for dmg_name in self.combat_history[tar_name][hist_cat][ability_name]:
                                    dmg_sum = sum(self.combat_history[tar_name][hist_cat][dmg_name])
                                    # ..updates with sum for each ability.
                                    dct.update(dict(ability={dmg_name: dmg_sum}))

                        elif hist_cat in ('lifesteal', 'spellvamp'):
                            for heal_type in self.combat_history[tar_name][hist_cat]:
                                heal_sum = sum(self.combat_history[tar_name][hist_cat][heal_type])
                                # Updates with sum of each source.
                                dct.update({hist_cat: {heal_type: heal_sum}})

                # Updates with values for each target.
                dct.update({tar_name: dict(true=tot_true_tar,
                                           magic=tot_magic_tar,
                                           physical=tot_physical_tar,
                                           healing=tot_healing_tar,
                                           )})

            # Updates with total values for each type.
            dct.update(dict(all_targets=dict(true=tot_true,
                                             magic=tot_magic,
                                             physical=tot_physical,
                                             )))

            # Updates with total dmg.
            tot_dmg = 0
            for dmg_type in dct['all_targets']:
                tot_dmg += dct['all_targets'][dmg_type]
            dct['all_targets'].update(dict(total_dmg=tot_dmg))

        return dct

    def note_lifesteal_or_spellvamp_in_history(self, value, heal_type='lifesteal'):
        """
        Notes spellvamp or lifesteal of an effect, on a particular time in history.

        Modifies:
            combat_history
        Args:
            heal_type: (string)
                'lifesteal'
                'spellvamp'
        Returns:
            None
        """

        # Checks if time already exists in history.
        if self.current_time in self.combat_history['player'][heal_type]:
            self.combat_history['player'][heal_type][self.current_time] += value
        else:
            self.combat_history['player'][heal_type].update({self.current_time: value})

    def note_heal_in_history(self, value):
        """
        Notes player's heals in history.

        :return: (None)
        """

        if self.current_time in self.combat_history['player']['heals']:
            self.combat_history['player']['heals'][self.current_time] += value
        else:
            self.combat_history['player']['heals'].update({self.current_time: value})

    def note_current_hp_in_history(self, target_name):
        """
        Stores current_hp of a target.

        Replaces previous value for specific time if events occur simultaneously.

        :return: (None)
        """

        self.combat_history[target_name]['current_hp'].update(
            {self.current_time: self.current_stats[target_name]['current_hp']})

    def note_player_dmg_taken(self, dmg_name, unmitigated_dmg_value, mitigated_dmg_value):
        """
        Notes in history dmg and heals the player takes.

        NOTE: It is tracked separately in history, since it isn't used for results as other dmgs.

        :return: (None)
        """

        appended_dct = {'dmg_name': dmg_name,
                        'unmitigated_dmg_value': unmitigated_dmg_value,
                        'mitigated_dmg_value': mitigated_dmg_value,
                        'current_time': self.current_time}

        self.combat_history['player']['dmg_or_heal_taken'].append(appended_dct)

    def note_non_hp_resource_in_history(self, curr_resource_str):
        """
        Stores player's 'current_'resource value in history.

        Args:
            current_resource_name: (str) e.g. "current_rage"
        Returns:
            (None)
        """

        new_val = self.current_stats['player'][curr_resource_str]
        self.combat_history['player']['resource'][self.current_time] = new_val

    def note_dmg_in_history(self, dmg_type, final_dmg_value, target_name):
        """
        Calculates and stores total dmg of a particular type, at a moment,
        and stores current_hp at each moment for a target.

        Modifies:
            combat_history
        Returns:
            (None)
        """

        # Filters out heals.
        if final_dmg_value < 0:
            return

        # (AA type is converted to physical before being stored.)
        if dmg_type == 'AA':
            dmg_type = 'physical'

        dmg_type_combat_history_dct = self.combat_history[target_name][dmg_type]

        if self.current_time in dmg_type_combat_history_dct:
            dmg_type_combat_history_dct[self.current_time] += final_dmg_value
        else:
            dmg_type_combat_history_dct.update({self.current_time: final_dmg_value})

    # RESULTS ---------------------------------------------------------------------------------------------------------
    def set_combat_results(self):
        """
        NOTE: Not all keys are inserted here.

        :return: (None)
        """

        self.place_tars_and_empty_dct_in_dct(self.combat_results)
        self.combat_results['player'].update({'source': {}, 'total_physical': 0, 'total_magic': 0, 'total_true': 0})

    def note_dmg_totals_movement_and_heals_in_results(self):
        """
        Calculates total dmg for each dmg type and stores it,
        and total overall dmg.

        :return: (None)
        """

        self.combat_results['player']['total_dmg_done'] = 0

        for tar_name in self.enemy_target_names:
            tot_value = 0

            for dmg_type, type_dmg_name in zip(('physical', 'magic', 'true'),
                                               ('total_physical', 'total_magic', 'total_true')):
                type_dmg_value = 0
                for event_time in self.combat_history[tar_name][dmg_type]:
                    type_dmg_value += self.combat_history[tar_name][dmg_type][event_time]

                # TYPE TOTALS
                self.combat_results['player'][type_dmg_name] += type_dmg_value
                tot_value += type_dmg_value

            # OVERALL TOTALS
            self.combat_results['player']['total_dmg_done'] += tot_value

        self.note_lifesteal_spellvamp_totals_in_results()
        self.note_heals_in_results()
        self.note_dps_in_results()
        self.note_movement_in_results()
        self.note_movement_per_sec_in_results()

    def note_lifesteal_spellvamp_totals_in_results(self):
        """
        Calculates and stores total values of lifesteal and spellvamp.

        Returns:
            (None)
        """

        # PLAYER
        for regen_type in ('lifesteal', 'spellvamp'):
            # (resets tot_val for each regen type)
            tot_regen_val = 0
            for event_time in self.combat_history['player'][regen_type]:
                tot_regen_val += self.combat_history['player'][regen_type][event_time]

            # Stores regen_type.
            self.combat_results['player'][regen_type] = tot_regen_val

    def note_heals_in_results(self):
        tot_regen_val = 0
        for event_time in self.combat_history['player']['heals']:
            tot_regen_val += self.combat_history['player']['heals'][event_time]

        # Stores regen_type.
        self.combat_results['player']['heals'] = tot_regen_val

    def _last_action_end(self):

        if not self.actions_dct:
            return 0
        else:
            last_action_time = max(self.actions_dct)
            last_action_dct = self.actions_dct[last_action_time]
            if 'channel_end' in last_action_dct:
                last_action_end = self.actions_dct[last_action_time]['channel_end']

            else:
                last_action_end = self.actions_dct[last_action_time]['cast_end']

            return last_action_end

    def dps_result(self):
        """
        Calculates player's dps value..

        :return: (float)
        """
        # TODO change method name after other method is removed.

        last_action_end = self._last_action_end()
        if not last_action_end:
            last_action_end += 0.1
        return self.combat_results['player']['total_dmg_done'] / last_action_end

    def note_dps_in_results(self):
        """
        Stores player's dps.

        Returns:
            (None)
        """

        self.combat_results['player']['dps'] = self.dps_result()

    def note_movement_in_results(self):
        """
        Stores player's dps.

        Returns:
            (None)
        """

        self.combat_results['player']['total_movement'] = self.total_movement

    def movement_per_sec(self):
        return self.total_movement / self.combat_end_time

    def note_movement_per_sec_in_results(self):
        self.combat_results['player']['movement_per_sec'] = self.movement_per_sec()

    def note_source_dmg_in_results(self, dmg_dct, final_dmg_value):
        """
        Stores a source's total dmg.

        Returns:
            (None)
        """

        source_name = dmg_dct['dmg_source']

        if source_name in self.combat_results['player']['source']:
            self.combat_results['player']['source'][source_name] += final_dmg_value
        else:
            self.combat_results['player']['source'][source_name] = final_dmg_value

    def __note_stats_pre_or_post_combat_in_results(self, stats_category_name):
        """
        Stores all precombat stats for all targets.

        Stats must be stored after application of passive effects.

        Args:
            stats_category_name: (str) 'pre_combat_stats', 'post_combat_stats'
        Returns:
            (None)
        """

        for tar_name in self.all_target_names:
            self.combat_results[tar_name].update({stats_category_name: {}})

            if tar_name == 'player':
                for stat_name in self.internally_displayed_player_stat_names():
                    self.combat_results[tar_name][stats_category_name].update(
                        {stat_name: self.request_stat(target_name=tar_name, stat_name=stat_name)})

            else:
                for stat_name in self.internally_displayed_enemy_stat_names():

                    if stat_name not in self.RESOURCE_CURRENT_STAT_NAMES:
                        self.combat_results[tar_name][stats_category_name].update(
                            {stat_name: self.request_stat(target_name=tar_name, stat_name=stat_name)})

                    else:
                        stat_val = self.current_stats[tar_name][stat_name]
                        self.combat_results[tar_name][stats_category_name].update(
                            {stat_name: stat_val})

    def note_pre_combat_stats_in_results(self):
        return self.__note_stats_pre_or_post_combat_in_results(stats_category_name='pre_combat_stats')

    def note_post_combat_stats_in_results(self):
        """
        Stores all postcombat stats for all targets.

        Stats must be stored after combat ends.

        Returns:
            (None)
        """

        self.__note_stats_pre_or_post_combat_in_results(stats_category_name='post_combat_stats')

    def __note_active_buffs(self, str_pre_or_post):
        """
        Notes active buffs in results.

        :param str_pre_or_post: (str) 'precombat_active_buffs' or 'postcombat_active_buffs'
        :return: (None)
        """

        self.combat_results.update({str_pre_or_post: self.active_buffs})

    def note_precombat_active_buffs(self):
        return self.__note_active_buffs(str_pre_or_post='precombat_active_buffs')

    def note_postcombat_active_buffs(self):
        return self.__note_active_buffs(str_pre_or_post='postcombat_active_buffs')


class DmgApplication(Counters, dmgs_buffs_categories.DmgCategories):

    IGNORED_DMG_NAMES = ['regen', ]

    def __init__(self,
                 selected_champions_dct,
                 champion_lvls_dct,
                 max_combat_time,
                 initial_enemies_total_stats,
                 initial_current_stats,
                 initial_active_buffs,
                 chosen_items_dct,
                 req_dmg_dct_func,
                 req_buff_dct_func,
                 ability_lvls_dct,
                 selected_masteries_dct,
                 _reversed_combat_mode
                 ):

        Counters.__init__(self,
                          selected_champions_dct=selected_champions_dct,
                          champion_lvls_dct=champion_lvls_dct,
                          max_combat_time=max_combat_time,
                          initial_current_stats=initial_current_stats,
                          initial_active_buffs=initial_active_buffs,
                          chosen_items_dct=chosen_items_dct,
                          req_buff_dct_func=req_buff_dct_func,
                          selected_masteries_dct=selected_masteries_dct,
                          initial_enemies_total_stats=initial_enemies_total_stats,
                          _reversed_combat_mode=_reversed_combat_mode)

        dmgs_buffs_categories.DmgCategories.__init__(self,
                                                     req_stats_func=self.request_stat,
                                                     req_dmg_dct_func=req_dmg_dct_func,
                                                     current_stats=self.current_stats,
                                                     current_target=self.current_target,
                                                     champion_lvls_dct=champion_lvls_dct,
                                                     current_target_num=self.current_target_num,
                                                     active_buffs=self.active_buffs,
                                                     ability_lvls_dct=ability_lvls_dct)

    def apply_spellvamp_or_lifesteal(self, tar_name, dmg_name, dmg_value, dmg_type):
        """
        Applies lifesteal or spellvamp to the player and notes it in history.

        Lifesteal is applied on AAs or dmg effects marked in their dict.

        Spellvamp is applied to true, physical, or magic dmg types,
        excluding AAs and some on hit dmg effects (not marked in their dict).
        """

        if tar_name == 'player':
            return
        # Checks if the event is not a heal.
        if dmg_value > 0:

            # If it's an AA applies lifesteal.
            if dmg_type == 'AA':
                lifesteal_value = dmg_value * self.request_stat(target_name='player', stat_name='lifesteal')

                self.apply_heal_value(tar_name='player',
                                      heal_value=lifesteal_value)

                # NOTE IN HISTORY
                self.note_lifesteal_or_spellvamp_in_history(value=lifesteal_value, heal_type='lifesteal')

            # If it's not an AA checks if either lifesteal or spellvamp is applicable.
            else:

                dmg_dct = self.req_dmg_dct_func(dmg_name=dmg_name)
                life_conversion_type = dmg_dct['life_conversion_type']
                # If it can cause spellvamp..
                if life_conversion_type == 'spellvamp':

                    # .. sets the healing done.
                    spellvamp_value = dmg_value * self.request_stat(target_name='player',
                                                                    stat_name='spellvamp')

                    # If it's an aoe affect, applies modifier.
                    if dmg_dct['max_targets'] != 1:
                        spellvamp_value *= self.AOE_SPELLVAMP_MOD

                    self.apply_heal_value(tar_name='player',
                                          heal_value=spellvamp_value)

                    # Then notes in history.
                    self.note_lifesteal_or_spellvamp_in_history(value=spellvamp_value, heal_type='spellvamp')

                # (Lifesteal and spellvamp are exclusive so 'elif' is used)
                # If the dmg can cause lifesteal..
                elif life_conversion_type == 'lifesteal':

                    # .. sets the healing done.
                    lifesteal_value = dmg_value * self.request_stat(target_name='player', stat_name='lifesteal')

                    self.apply_heal_value(tar_name='player',
                                          heal_value=lifesteal_value)

                    # NOTE IN HISTORY
                    self.note_lifesteal_or_spellvamp_in_history(value=lifesteal_value, heal_type='lifesteal')

    def apply_heal_value(self, tar_name, heal_value):
        """
        Applies a heal to a target.

        Modifies:
            current_stats
        Returns:
            (None)
        """

        # Applies heal_reduction.
        heal_value *= 1 - self.request_stat(target_name=tar_name, stat_name='percent_healing_reduction')

        self.note_heal_in_history(value=heal_value)

        # Ensures target is not overhealed.
        # If current_hp is going to become less than max hp..
        if (
            (self.current_stats[tar_name]['current_hp'] + heal_value) < self.request_stat(target_name=tar_name,
                                                                                          stat_name='hp')
        ):

            # .. applies heal.
            self.current_stats[tar_name]['current_hp'] += heal_value

        # If current_hp will exceed max hp, sets current_hp to max.
        else:
            self.current_stats[tar_name]['current_hp'] = self.request_stat(target_name=tar_name,
                                                                           stat_name='hp')

    def apply_resource_dmg_or_heal(self, dmg_name):
        """
        Reduces or increases player's 'current_'resource and stores it in combat_history.

        Regen events can be natural (e.g. mp5) or buff based (e.g. Jayce's W) or item based (e.g. AA with Muramana).

        This method is NOT used for ability cost.

        Modifies:
            current_stats
            combat_history
        Returns:
            (None)
        """

        dmg_value = self.request_dmg_value(dmg_name=dmg_name)
        resource_type = self.req_dmg_dct_func(dmg_name=dmg_name)['resource_type']

        # DMG
        if dmg_value >= 0:
            self.current_stats['player'][self.player_current_resource_name] -= dmg_value

        # HEAL
        # (If the value is negative it's a resource replenish effect.)
        else:
            # Checks if resource heal exceeds max possible value.
            max_value = self.request_stat(target_name='player', stat_name=resource_type)

            if self.current_stats['player'][self.player_current_resource_name] - dmg_value > max_value:
                self.current_stats['player'][self.player_current_resource_name] = max_value
            else:
                self.current_stats['player'][self.player_current_resource_name] -= dmg_value

        # RESOURCE HISTORY
        self.note_non_hp_resource_in_history(curr_resource_str=self.player_current_resource_name)

    @staticmethod
    def aoe_bool(max_targets):
        """
        Determines if effect is single or multi-target.

        :param max_targets: (int)
        :return: (bool)
        """
        if max_targets == 1:
            return False
        else:
            return True

    def mitigated_dmg(self, dmg_value, dmg_type, target, is_aoe):
        """
        Calculates the dmg value based on its type (magic, physical, AA, true) and various reductions.

        :return: (float)
        """

        # True dmg remains unmitigated.
        if dmg_type == 'true':
            return dmg_value

        if is_aoe:
            dmg_value *= 1-self.request_stat(target_name=target, stat_name='percent_aoe_reduction')
            dmg_value -= self.request_stat(target_name=target, stat_name='flat_aoe_reduction')
        else:
            dmg_value *= 1-self.request_stat(target_name=target, stat_name='percent_non_aoe_reduction')
            dmg_value -= self.request_stat(target_name=target, stat_name='flat_non_aoe_reduction')

        dmg_value *= 1-self.request_stat(target_name=target, stat_name='percent_dmg_reduction')

        # Magic dmg.
        if dmg_type == 'magic':
            # Checks if there is any percent magic reduction and applies it.
            dmg_value *= self.request_stat(target_name=target, stat_name='magic_dmg_taken')

            # Checks if there is flat magic reduction
            dmg_value -= self.request_stat(target_name=target, stat_name='flat_magic_dmg_reduction')

            # Checks if there is flat reduction
            dmg_value -= self.request_stat(target_name=target, stat_name='flat_dmg_reduction')

        # Physical (AA or non-AA)..
        else:
            # Applies physical dmg reduction.
            dmg_value *= self.request_stat(target_name=target, stat_name='physical_dmg_taken')

            # Checks if there is flat physical reduction
            dmg_value -= self.request_stat(target_name=target, stat_name='flat_physical_dmg_reduction')

            # Checks if there is flat reduction
            dmg_value -= self.request_stat(target_name=target, stat_name='flat_dmg_reduction')

            # AA reduction.
            if dmg_type == 'AA':
                dmg_value *= 1 - self.request_stat(target_name=target, stat_name='percent_AA_reduction')
                self.request_stat(target_name='player', stat_name='bonus_ad')
                dmg_value -= self.request_stat(target_name=target, stat_name='flat_AA_reduction')

        return max(dmg_value, 0.)

    def apply_hp_dmg_or_heal(self, dmg_name, target_name):
        """
        Applies a dmg or heal value to a target, along with lifesteal or spellvamp, and notes in history.

        Modifies:
            current_stats
            combat_history
        Returns:
            (None)
        """

        dmg_dct = self.req_dmg_dct_func(dmg_name=dmg_name)
        dmg_type = dmg_dct['dmg_type']
        aoe = self.aoe_bool(max_targets=dmg_dct['max_targets'])
        unmitigated_dmg_value = self.request_dmg_value(dmg_name=dmg_name)

        final_dmg_value = self.mitigated_dmg(dmg_value=unmitigated_dmg_value,
                                             dmg_type=dmg_type,
                                             target=target_name,
                                             is_aoe=aoe)

        # VALUE APPLICATION
        # If it's a dmg.
        if final_dmg_value >= 0:
            self.current_stats[target_name]['current_hp'] -= final_dmg_value

            if dmg_name not in self.IGNORED_DMG_NAMES:
                # DMG COUNTERS
                # (dmg on player is not needed)
                # (dps by enemies is not needed)
                if target_name != 'player':
                    self.note_dmg_in_history(dmg_type=dmg_type,
                                             final_dmg_value=final_dmg_value,
                                             target_name=target_name)
                    self.note_source_dmg_in_results(dmg_dct=dmg_dct, final_dmg_value=final_dmg_value)
            if target_name == 'player':
                self.note_player_dmg_taken(dmg_name=dmg_name,
                                           unmitigated_dmg_value=unmitigated_dmg_value,
                                           mitigated_dmg_value=final_dmg_value)
            self.note_current_hp_in_history(target_name=target_name)

        # Otherwise it's a heal.
        else:
            # (minus used to reverse value)
            self.apply_heal_value(tar_name=target_name,
                                  heal_value=-final_dmg_value)

        # LIFESTEAL/SPELLVAMP
        self.apply_spellvamp_or_lifesteal(tar_name=target_name,
                                          dmg_name=dmg_name,
                                          dmg_value=final_dmg_value,
                                          dmg_type=dmg_type)

    def apply_dmg_or_heal(self, dmg_name, target_name):
        """
        Applies dmg or heal to either current_hp or the player's resource.

        Returns:
            (None)
        """

        dmg_dct = self.req_dmg_dct_func(dmg_name=dmg_name)

        # Checks if the effect is affecting a resource or hp.
        if dmg_dct['resource_type'] == 'hp':
            self.apply_hp_dmg_or_heal(dmg_name=dmg_name,
                                      target_name=target_name)

        else:
            self.apply_resource_dmg_or_heal(dmg_name=dmg_name)

    def times_of_death(self):
        """
        Creates a dict containing all dead targets and their time of death.

        Returns:
            (dict)
        """
        dct = {}

        for tar_name in self.active_buffs:
            if tar_name != 'player':

                for buff_name in self.active_buffs[tar_name]:
                    if buff_name == 'dead_buff':

                        dct.update({tar_name: self.active_buffs[tar_name]['dead_buff']['starting_time']})

        return dct

    def dps(self):
        """
        Calculates dps of player.

        Healing and regeneration of enemy targets, not taken into account
        (might want to take into account to make dots after death have more "correct" effect on dps).

        Returns:
            (float)
        """

        last_action_time = max(self.actions_dct)

        last_cast_completion = self.actions_dct[last_action_time]['cast_end']
        if last_cast_completion == 0:
            last_cast_completion += 0.2

        return self.refined_combat_history()['all_targets']['total_dmg'] / last_cast_completion


NATURAL_REGEN_PERIOD = 0.5  # Tick period of hp5, mp5, etc.
NATURAL_REGEN_START_DELAY = 0.5
PER_5_DIVISOR = 5 / NATURAL_REGEN_PERIOD  # Divides "per 5" stats. Used to create per tick value.


# ----------------------------------------------------------------------------------------------------------------------
# REGEN BUFF BASE
_DEAD_BUFF_DCT_BASE = palette.buff_dct_base_deepcopy()
_DEAD_BUFF_DCT_BASE['duration'] = 'permanent'
_DEAD_BUFF_DCT_BASE['max_stacks'] = 1
_DEAD_BUFF_DCT_BASE['stats'] = None
_DEAD_BUFF_DCT_BASE['on_hit'] = None
_DEAD_BUFF_DCT_BASE['prohibit_cd_start'] = None


# ----------------------------------------------------------------------------------------------------------------------
# REGEN BUFF BASE

# Creates base dict for regenerations (hp, mp, energy, etc).
REGEN_BUFF_DCT_BASE = palette.buff_dct_base_deepcopy()
# Sets values correctly for regenerations.
for regen_buff_base_key in ('on_hit', 'prohibit_cd_start', 'stats'):
    REGEN_BUFF_DCT_BASE[regen_buff_base_key] = None
REGEN_BUFF_DCT_BASE['max_stacks'] = 1
REGEN_BUFF_DCT_BASE['duration'] = 'permanent'
# (adds dot data)
REGEN_BUFF_DCT_BASE['dot'] = {'period': None, 'dmg_names': []}
REGEN_BUFF_DCT_BASE['dot']['period'] = NATURAL_REGEN_PERIOD


# PLAYER hp5 buff base.
_HP5_BUFF_DCT_BASE_PLAYER = copy.deepcopy(REGEN_BUFF_DCT_BASE)
_HP5_BUFF_DCT_BASE_PLAYER['target_type'] = 'player'
_HP5_BUFF_DCT_BASE_PLAYER['dot']['dmg_names'] = ['player_hp5_dmg']
# PLAYER rp5 buff base.
_RESOURCE_P5_BUFF_DCT_BASE_PLAYER = copy.deepcopy(REGEN_BUFF_DCT_BASE)
_RESOURCE_P5_BUFF_DCT_BASE_PLAYER['target_type'] = 'player'
_RESOURCE_P5_BUFF_DCT_BASE_PLAYER['dot']['dmg_names'] = []

# ENEMY buff base.
_REGEN_BUFF_DCT_BASE_ENEMY = copy.deepcopy(REGEN_BUFF_DCT_BASE)
_REGEN_BUFF_DCT_BASE_ENEMY['target_type'] = 'enemy'
_REGEN_BUFF_DCT_BASE_ENEMY['dot']['dmg_names'] = ['enemy_hp5_dmg']


# ----------------------------------------------------------------------------------------------------------------------
# DMG BASE
# A mod 1 is used (hp5, mp5, etc.) and 0 dmg value.
# Final regen value is calculated as it would normally do for any other dmg with a mod;
# mod*mod_val + base_dmg_val

# Creates base dict for regenerations' dmg dicts.
_REGEN_DMG_DCT_BASE = dict(
    target_type='placeholder',
    dmg_category='standard_dmg',
    resource_type='placeholder',
    dmg_type='true',
    # Regen is "healing" a stat so it has to be negative.
    dmg_values=-1/PER_5_DIVISOR,
    dmg_source='regen',
    # (None or {'enemy': {}, 'player': {'bonus_ad': 0.5}})
    mods='placeholder',
    # (None or lifesteal or spellvamp)
    life_conversion_type=None,
    radius=None,
    dot={'buff_name': 'placeholder'},
    max_targets=1,
    usual_max_targets=1,
    delay=NATURAL_REGEN_START_DELAY,)

# HEALTH
_HP5_DMG_DCT_BASE = copy.deepcopy(_REGEN_DMG_DCT_BASE)
_HP5_DMG_DCT_BASE['resource_type'] = 'hp'
# Player
_PLAYER_HP5_DMG_DCT = copy.deepcopy(_HP5_DMG_DCT_BASE)
_PLAYER_HP5_DMG_DCT['target_type'] = 'player'
_PLAYER_HP5_DMG_DCT['mods'] = {'player': {'hp5': {'multiplicative': 1}}}
_PLAYER_HP5_DMG_DCT['dot']['buff_name'] = 'player_hp5_buff'
# Enemy
_ENEMY_HP5_DMG_DCT_BASE = copy.deepcopy(_HP5_DMG_DCT_BASE)
_ENEMY_HP5_DMG_DCT_BASE['target_type'] = 'enemy'
_ENEMY_HP5_DMG_DCT_BASE['dot']['buff_name'] = 'enemy_hp5_buff'
_ENEMY_HP5_DMG_DCT_BASE['mods'] = {'enemy': {'hp5': {'multiplicative': 1}}}

# Resources
_RESOURCE_P5_BUFFS_DCTS = {'mp5': None, 'ep5': None, 'rp5': None}
for _key in _RESOURCE_P5_BUFFS_DCTS:
    _new_rp5_dct = copy.deepcopy(_RESOURCE_P5_BUFF_DCT_BASE_PLAYER)
    _new_rp5_dct['dot']['dmg_names'].append('player_{}_dmg'.format(_key))
    _new_rp5_dct['buff_source'] = 'regen'
    _RESOURCE_P5_BUFFS_DCTS[_key] = _new_rp5_dct

_RESOURCE_P5_DMGS_DCTS = {i: {} for i in _RESOURCE_P5_BUFFS_DCTS}
for _key in _RESOURCE_P5_DMGS_DCTS:
    _new_rp5_dct = copy.deepcopy(_REGEN_DMG_DCT_BASE)
    _new_rp5_dct['resource_type'] = _key[:-1]
    _new_rp5_dct['mods'] = {'player': {_key: {'multiplicative': 1}}}
    _new_rp5_dct['dot']['buff_name'] = '{}_buff'.format(_key)
    _RESOURCE_P5_DMGS_DCTS[_key] = _new_rp5_dct


class DeathAndRegen(DmgApplication):

    HP5_BUFF_DCT_BASE_PLAYER = _HP5_BUFF_DCT_BASE_PLAYER
    RP5_BUFF_DCT_BASE_PLAYER = _RESOURCE_P5_BUFF_DCT_BASE_PLAYER
    REGEN_BUFF_DCT_BASE_ENEMY = _REGEN_BUFF_DCT_BASE_ENEMY
    ENEMY_HP5_DMG_DCT_BASE = _ENEMY_HP5_DMG_DCT_BASE
    PLAYER_HP5_DMG_DCT = _PLAYER_HP5_DMG_DCT
    RESOURCE_P5_BUFFS_DCTS = _RESOURCE_P5_BUFFS_DCTS
    RESOURCE_P5_DMGS_DCTS = _RESOURCE_P5_DMGS_DCTS

    @staticmethod
    def dead_buff():
        return _DEAD_BUFF_DCT_BASE

    def apply_death(self, tar_name):
        """
        If target is dead, he is marked in buffs.

        Returns:
            (None)
        """

        # Checks if target has already died (earlier).
        if 'dead_buff' not in self.active_buffs[tar_name]:
            # Checks if target died.
            if self.current_stats[tar_name]['current_hp'] <= 0:

                # Adds 'dead_buff'.
                self.add_buff(buff_name='dead_buff', tar_name=tar_name)

    def enemy_hp5_dmg(self):
        return self.ENEMY_HP5_DMG_DCT_BASE

    def enemy_hp5_buff(self):
        return self.REGEN_BUFF_DCT_BASE_ENEMY

    def player_hp5_dmg(self):

        return self.PLAYER_HP5_DMG_DCT

    def player_hp5_buff(self):
        return self.HP5_BUFF_DCT_BASE_PLAYER

    # Resource buffs
    def mp5_buff(self):
        return self.RESOURCE_P5_BUFFS_DCTS['mp5']

    def rp5_buff(self):
        # Rage per 5
        return self.RESOURCE_P5_BUFFS_DCTS['rp5']

    def ep5_buff(self):
        return self.RESOURCE_P5_BUFFS_DCTS['ep5']

    # Resource dmgs
    def player_mp5_dmg(self):
        return self.RESOURCE_P5_DMGS_DCTS['mp5']

    def player_rp5_dmg(self):
        # Rage per 5
        return self.RESOURCE_P5_DMGS_DCTS['rp5']

    def player_ep5_dmg(self):
        return self.RESOURCE_P5_DMGS_DCTS['ep5']


