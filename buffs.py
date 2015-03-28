import stats
import targeting
import items
import dmgs_buffs_categories


class BuffsGeneral(stats.DmgReductionStats, targeting.Targeting, items.AllItems):

    def __init__(self,
                 selected_champions_dct,
                 champion_lvls_dct,
                 req_buff_dct_func,
                 initial_current_stats=None,
                 initial_active_buffs=None,
                 items_lst=None):

        self.current_time = 0

        stats.DmgReductionStats.__init__(self,
                                         champion_lvls_dct=champion_lvls_dct,
                                         selected_champions_dct=selected_champions_dct,
                                         req_buff_dct_func=req_buff_dct_func,
                                         initial_active_buffs=initial_active_buffs,
                                         initial_current_stats=initial_current_stats)

        items.AllItems.__init__(self,
                                items_lst=items_lst,
                                kwargs=dict(req_stats_func=self.request_stat,
                                            act_buffs=self.active_buffs,
                                            current_stats=self.current_stats,
                                            current_target=self.current_target,
                                            champion_lvls_dct=champion_lvls_dct,
                                            current_target_num=self.current_target_num))
        self.set_stat_dependencies()
        self.set_current_stats()

    def apply_stat_dependency_to_tar(self, tar, dependent_stat_dct):
        """
        Applies dependency to
        """
        for controlled_stat in dependent_stat_dct:

            # Creates controller stat keyword if not present.
            if controlled_stat not in self.stat_dependencies[tar]:
                self.stat_dependencies[tar].update({controlled_stat: []})

            # Appends all controllers.
            for controller in dependent_stat_dct[controlled_stat]:
                # Skips appending if controller already exists.
                if controller not in self.stat_dependencies[tar][controlled_stat]:
                    self.stat_dependencies[tar][controlled_stat].append(controller)

    def set_stat_dependencies(self):
        """
        Returns:
            (None)
        """

        self.place_tar_and_empty_dct_in_dct(self.stat_dependencies)

        for target_name in self.DMG_REDUCTION_STAT_DEPENDENCIES:

            if target_name == 'all_targets':
                # Applies dependency to all targets.
                for tar_name in self.all_target_names:
                    self.apply_stat_dependency_to_tar(tar=tar_name,
                                                      dependent_stat_dct=self.DMG_REDUCTION_STAT_DEPENDENCIES[
                                                          target_name])

            else:
                self.apply_stat_dependency_to_tar(tar=target_name,
                                                  dependent_stat_dct=self.DMG_REDUCTION_STAT_DEPENDENCIES[target_name])

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
        if buff_dct()['duration'] != 'permanent':

            tar_buff_dct_in_act_buffs['ending_time'] = self.current_time + buff_dct()['duration']

        # STACKS
        # If max_stacks have not been reached..
        if tar_buff_dct_in_act_buffs['current_stacks'] < buff_dct()['max_stacks']:

            # ..adds +1 to the stacks (unless increment is different).
            tar_buff_dct_in_act_buffs['current_stacks'] += stack_increment

            # Ensures max_stacks aren't exceeded for stack_increments larger than 1.
            if stack_increment > 1:

                if tar_buff_dct_in_act_buffs['current_stacks'] > buff_dct()['max_stacks']:
                    # If max_stacks exceeded, set to max_stacks.
                    tar_buff_dct_in_act_buffs['current_stacks'] = buff_dct()['max_stacks']

    def add_buff(self, buff_name, tar_name, stack_increment=1, initial_stacks_increment=1):
        """
        Inserts a new buff or refreshes an existing buff (duration and stacks).

        Modifies:
            active_buffs
        Returns:
            (None)
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

    def remove_expired_buffs(self):
        """
        Removes all expired buffs.

        Modifies:
            active_buffs
        Return:
            (None)
        """

        for tar_name in self.active_buffs:
            tar_act_buffs = self.active_buffs[tar_name]

            for buff_name in sorted(tar_act_buffs):
                tar_buff_dct_in_act_buffs = tar_act_buffs[buff_name]

                if tar_buff_dct_in_act_buffs['ending_time'] != 'permanent':
                    if tar_buff_dct_in_act_buffs['ending_time'] < self.current_time:

                        # Removes the buff.
                        del tar_buff_dct_in_act_buffs

    def add_single_ability_passive_buff(self, ability_name, target_type, effects_dct, tar_name):
        """
        Adds passive buffs of a single ability on a target.

        Modifies:
            active_buffs
        Returns:
            (None)
        """

        # Checks if selected ability has passive buffs.
        if target_type in effects_dct[ability_name]:
            if 'passives' in effects_dct[ability_name][target_type]:
                if 'buffs' in effects_dct[ability_name][target_type]['passives']:
                    # Applies all passive buffs.
                    for buff_name in effects_dct[ability_name][target_type]['passives']['buffs']:
                        self.add_buff(buff_name, tar_name)

    def add_passive_buffs(self, abilities_effects_dct_func, abilities_lvls):
        """
        Adds passive buffs from champion abilities (that apply on ability lvling) on all targets.

        Modifies:
            active_buffs
        Returns:
            (None)
        """

        for tar_name in self.champion_lvls_dct:
            # (player or enemy)
            target_type = self.target_type(tar_name=tar_name)

            # For Q,W,E and R...
            for ability_name in 'qwer':

                # ..if the ability has at least one lvl...
                if abilities_lvls[ability_name] > 0:

                    # .. applies the buffs.
                    self.add_single_ability_passive_buff(ability_name=ability_name,
                                                         target_type=target_type,
                                                         effects_dct=abilities_effects_dct_func,
                                                         tar_name=tar_name)

            # Innate passive buffs.
            self.add_single_ability_passive_buff(ability_name='inn',
                                                 target_type=target_type,
                                                 effects_dct=abilities_effects_dct_func,
                                                 tar_name=tar_name)

            # Item passive buffs.
            for item_name in self.items_lst:
                # (If item is bought multiple times, all stacks are applied)
                self.add_single_ability_passive_buff(ability_name=item_name,
                                                     target_type=target_type,
                                                     effects_dct=self.items_effects,
                                                     tar_name=tar_name)


class Counters(BuffsGeneral):

    AOE_SPELLVAMP_MOD = 30/100
    LOWEST_MEANINGFUL_COMBAT_TIME = 5
    EXTRA_STATS_SET = {'lifesteal', 'spellvamp', 'ap'}

    def __init__(self,
                 selected_champions_dct,
                 champion_lvls_dct,
                 req_buff_dct_func,
                 max_combat_time=20,
                 initial_current_stats=None,
                 initial_active_buffs=None,
                 items_lst=None):

        BuffsGeneral.__init__(self,
                              selected_champions_dct=selected_champions_dct,
                              champion_lvls_dct=champion_lvls_dct,
                              initial_current_stats=initial_current_stats,
                              initial_active_buffs=initial_active_buffs,
                              items_lst=items_lst,
                              req_buff_dct_func=req_buff_dct_func)

        self.max_combat_time = max_combat_time

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

        return lst

    def internally_displayed_enemy_stat_names(self):
        """
        Creates and returns all enemy stats to be stored (for internal display and testing purposes).

        Returns:
            (list)
        """

        lst = ['armor', 'mr', 'ap', ]

        lst += self.DEFENSIVE_SPECIAL_STATS

        return lst

    # HISTORY ---------------------------------------------------------------------------------------------------------
    def set_combat_history(self):
        """
        Sets up combat_history by inserting history blueprints for all targets.

        Modifies:
            combat_history dict.

        Returns:
            (None)
        """

        for tar in self.all_target_names:

            self.combat_history.update(
                {tar: dict(
                    true={},
                    magic={},
                    physical={},
                    total={},
                    current_hp={},)})

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
            resource={},))

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

    def note_current_hp_in_history(self, target_name):
        """
        Stores current_hp of a target.

        Replaces previous value for specific time if events occur simultaneously.

        Returns:
            (None)
        """

        self.combat_history[target_name]['current_hp'].update(
            {self.current_time: self.current_stats[target_name]['current_hp']})

    def note_resource_in_history(self, curr_resource_str):
        """
        Stores player's 'current_'resource value in history.

        Replaces previous value, if one exists.

        Args:
            current_resource_name: (str) e.g. "current_rage"
        Returns:
            (None)
        """

        # Adds time and current resource value
        self.combat_history['player']['resource'][self.current_time] = self.current_stats['player'][curr_resource_str]

    def note_dmg_in_history(self, dmg_type, final_dmg_value, target_name):
        """
        Calculates and stores total dmg of a particular type, at a moment,
        and stores current_hp at each moment for a target.

        Modifies:
            combat_history
        Returns:
            (None)
        """

        # (AA type is converted to physical before being stored.)
        if dmg_type == 'AA':
            dmg_type = 'physical'

        # Filters out heals.
        if final_dmg_value > 0:
            if self.current_time in self.combat_history[target_name][dmg_type]:
                self.combat_history[target_name][dmg_type][self.current_time] += final_dmg_value
            else:
                self.combat_history[target_name][dmg_type].update({self.current_time: final_dmg_value})

    # RESULTS ---------------------------------------------------------------------------------------------------------
    def set_combat_results(self):
        """
        Returns:
            (None)
        """
        self.place_tar_and_empty_dct_in_dct(self.combat_results)

        self.combat_results['player'].update({'source': {}, 'total_physical': 0, 'total_magic': 0, 'total_true': 0})

    def note_dmg_totals_in_results(self):
        """
        Calculates total dmg for each dmg type and stores it,
        and total overall dmg.

        Returns:
            (None)
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

    def dps_result(self):
        """
        Calculates player's dps value if combat time is higher than threshold.

        Returns:
            (float)
            (str) 'Not available'
        """
        # TODO change method name after other method is removed.

        # COMBAT DURATION
        last_action_time = max(self.actions_dct)
        last_action_dct = self.actions_dct[last_action_time]
        if 'channel_end' in last_action_dct:
            last_action_end = self.actions_dct[last_action_time]['channel_end']

        else:
            last_action_end = self.actions_dct[last_action_time]['cast_end']

        # DPS
        # (if time is too short for dps to be meaningful, returns message)
        if last_action_end >= self.LOWEST_MEANINGFUL_COMBAT_TIME:
            return self.combat_results['player']['total_dmg_done'] / last_action_end
        else:
            return 'Not available (combat time too short).'

    def note_dps_in_results(self):
        """
        Stores player's dps.

        Returns:
            (None)
        """

        self.combat_results['player']['dps'] = self.dps_result()

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

    def note_pre_combat_stats_in_results(self, stats_category_name='pre_combat_stats'):
        """
        Stores all precombat stats for all targets.

        Stats must be stored after application of passive effects.

        Args:
            stats_category_name: (str) Used for similar method below.
                'pre_combat_stats'
                'post_combat_stats'
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
                    self.combat_results[tar_name][stats_category_name].update(
                        {stat_name: self.request_stat(target_name=tar_name, stat_name=stat_name)})

    def note_post_combat_stats_in_results(self):
        """
        Stores all postcombat stats for all targets.

        Stats must be stored after combat ends.

        Returns:
            (None)
        """

        self.note_pre_combat_stats_in_results(stats_category_name='post_combat_stats')
        self.note_lifesteal_spellvamp_totals_in_results()
        self.note_dps_in_results()


class DmgApplication(Counters, dmgs_buffs_categories.DmgCategories):

    def __init__(self,
                 selected_champions_dct,
                 champion_lvls_dct,
                 max_combat_time,
                 initial_current_stats,
                 initial_active_buffs,
                 items_lst,
                 req_dmg_dct_func,
                 req_buff_dct_func,
                 ability_lvls_dct,
                 ):

        Counters.__init__(self,
                          selected_champions_dct=selected_champions_dct,
                          champion_lvls_dct=champion_lvls_dct,
                          max_combat_time=max_combat_time,
                          initial_current_stats=initial_current_stats,
                          initial_active_buffs=initial_active_buffs,
                          items_lst=items_lst,
                          req_buff_dct_func=req_buff_dct_func)

        dmgs_buffs_categories.DmgCategories.__init__(self,
                                                     req_stats_func=self.request_stat,
                                                     req_dmg_dct_func=req_dmg_dct_func,
                                                     current_stats=self.current_stats,
                                                     current_target=self.current_target,
                                                     champion_lvls_dct=champion_lvls_dct,
                                                     current_target_num=self.current_target_num,
                                                     active_buffs=self.active_buffs,
                                                     ability_lvls_dct=ability_lvls_dct)

    def apply_spellvamp_or_lifesteal(self, dmg_name, dmg_value, dmg_type):
        """
        Applies lifesteal or spellvamp to the player and notes it in history.

        Lifesteal is applied on AAs or dmg effects marked in their dict.

        Spellvamp is applied to true, physical, or magic dmg types,
        excluding AAs and some on hit dmg effects (not marked in their dict).

        Modifies:
            current_stats
            combat_history
        """

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
            if dmg_type != 'AA':

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
        heal_value *= 1 - self.request_stat(target_name=tar_name, stat_name='healing_reduction')

        # Ensures target is not overhealed.
        # If current_hp is going to become less than max hp..
        if ((self.current_stats[tar_name]['current_hp'] + heal_value) <
                self.request_stat(target_name=tar_name,
                                  stat_name='hp')):

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

        if dmg_value >= 0:
            self.current_stats['player'][self.player_current_resource_name] -= dmg_value

        # (If the value is negative it's a resource replenish effect.)
        else:
            # Checks if resource heal exceeds max possible value.
            max_value = self.request_stat(target_name='player', stat_name=resource_type)

            if self.current_stats['player'][self.player_current_resource_name] - dmg_value > max_value:
                self.current_stats['player'][self.player_current_resource_name] = max_value
            else:
                self.current_stats['player'][self.player_current_resource_name] -= dmg_value

        # RESOURCE HISTORY
        self.note_resource_in_history(curr_resource_str=self.player_current_resource_name)

    def mitigated_dmg(self, dmg_value, dmg_type, target):
        """
        Calculates the dmg value based on its type (magic, physical, AA, true).

        Returns:
            (float)
        """

        # True dmg remains unmitigated.
        if dmg_type == 'true':
            return dmg_value

        tar_bonuses = self.bonuses_dct[target]
        # Checks if there is any percent dmg reduction and applies it.
        if 'percent_dmg_reduction' in tar_bonuses:
            dmg_value *= 1-self.request_stat(target_name=target, stat_name='percent_dmg_reduction')

        # Magic dmg.
        if dmg_type == 'magic':
            # Checks if there is any percent magic reduction and applies it.
            dmg_value *= self.request_stat(target_name=target, stat_name='magic_dmg_taken')

            # Checks if there is flat magic reduction
            if 'flat_magic_reduction' in tar_bonuses:
                dmg_value -= self.request_stat(target_name=target, stat_name='flat_magic_reduction')

            # Checks if there is flat reduction
            if 'flat_reduction' in tar_bonuses:
                dmg_value -= self.request_stat(target_name=target, stat_name='flat_reduction')

        # Physical (AA or non-AA)..
        else:
            # Applies physical dmg reduction.
            dmg_value *= self.request_stat(target_name=target, stat_name='physical_dmg_taken')

            # Checks if there is flat physical reduction
            if 'flat_physical_reduction' in tar_bonuses:
                dmg_value -= self.request_stat(target_name=target, stat_name='flat_physical_reduction')

            # Checks if there is flat reduction
            if 'flat_reduction' in tar_bonuses:
                dmg_value -= self.request_stat(target_name=target, stat_name='flat_reduction')

            # AA reduction.
            if dmg_type == 'AA':
                if 'flat_AA_reduction' in tar_bonuses:
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

        final_dmg_value = self.mitigated_dmg(dmg_value=self.request_dmg_value(dmg_name=dmg_name),
                                             dmg_type=dmg_type,
                                             target=target_name)

        # VALUE APPLICATION
        # If it's a dmg.
        if final_dmg_value >= 0:
            self.current_stats[target_name]['current_hp'] -= final_dmg_value

            # DMG COUNTERS
            self.note_dmg_in_history(dmg_type=dmg_type,
                                     final_dmg_value=final_dmg_value,
                                     target_name=target_name)
            self.note_source_dmg_in_results(dmg_dct=dmg_dct, final_dmg_value=final_dmg_value)
            self.note_current_hp_in_history(target_name=target_name)

        # Otherwise it's a heal.
        else:
            # (minus used to reverse value)
            self.apply_heal_value(tar_name=target_name,
                                  heal_value=-final_dmg_value)

        # LIFESTEAL/SPELLVAMP
        self.apply_spellvamp_or_lifesteal(dmg_name=dmg_name,
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
        if 'resource_type' in dmg_dct:
            self.apply_resource_dmg_or_heal(dmg_name=dmg_name)

        elif 'dmg_type' in dmg_dct:
            self.apply_hp_dmg_or_heal(dmg_name=dmg_name,
                                      target_name=target_name)

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


class DeathAndRegen(DmgApplication):

    NATURAL_REGEN_PERIOD = 0.5  # Tick period of hp5, mp5,
    PER_5_DIVISOR = 10.  # Divides "per 5" stats. Used to create per tick value (ticks have 0.5s period)

    @staticmethod
    def dead_buff():
        return dict(
            max_stacks=1,
            duration='permanent',)

    def apply_death(self, tar_name):
        """
        Checks if the target is dead. If dead, removes its other buffs and marks it as dead.

        Modifies:
            active_buffs
        Returns:
            (None)
        """

        # Checks if target has already died (earlier).
        if 'dead_buff' not in self.active_buffs[tar_name]:
            # Checks if target died.
            if self.current_stats[tar_name]['current_hp'] <= 0:

                # Clears buffs
                self.active_buffs[tar_name] = {}

                # Adds 'dead_buff'.
                self.add_buff(buff_name='dead_buff', tar_name=tar_name)

    def enemy_hp5_dmg(self):

        return dict(
            period=self.NATURAL_REGEN_PERIOD,
            dmg_type='true',
            target='enemy',
            dot=True,
            duration='permanent',)

    @staticmethod
    def enemy_hp5_buff():
        # Used only as a marker.
        return dict(
            max_stacks=1,
            duration='permanent',)

    def enemy_hp5_dmg_value(self):
        """
        Calculates healing per 0.5 seconds by regeneration.
        """
        return -self.request_stat(stat_name='hp5', target_name=self.current_target)/self.PER_5_DIVISOR

    def player_hp5_dmg(self):

        return dict(
            period=self.NATURAL_REGEN_PERIOD,
            dmg_type='true',
            target='player',
            dot=True,
            duration='permanent',)

    @staticmethod
    def player_hp5_buff():
        return dict(
            max_stacks=1,
            duration='permanent',)

    def player_hp5_dmg_value(self):
        """
        Returns healing per 0.5 seconds by regeneration.
        """
        return -self.request_stat(stat_name='hp5', target_name='player')/self.PER_5_DIVISOR

    @staticmethod
    def mp5_buff():
        return dict(
            max_stacks=1,
            duration='permanent',)

    def mp5_dmg(self):
        return dict(
            period=self.NATURAL_REGEN_PERIOD,
            resource_type='mp',
            target='player',
            dot=True,
            duration='permanent',
            )

    def mp5_dmg_value(self):
        return -self.request_stat(stat_name='mp5', target_name='player')/self.PER_5_DIVISOR


if __name__ == '__main__':

    print('\nNo tests.')