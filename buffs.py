import stats
import targeting
import items


class BuffsGeneral(stats.DmgReductionStats, targeting.Targeting, items.AllItems):

    def __init__(self,
                 current_time,
                 selected_champions_dct,
                 champion_lvls_dct,
                 initial_current_stats=None,
                 initial_active_buffs=None,
                 items_lst=None
                 ):

        self.current_time = current_time

        stats.DmgReductionStats.__init__(self,
                                         champion_lvls_dct=champion_lvls_dct,
                                         selected_champions_dct=selected_champions_dct,
                                         initial_active_buffs=initial_active_buffs,
                                         initial_current_stats=initial_current_stats)

        items.AllItems.__init__(self,
                                items_lst=items_lst,
                                kwargs=dict(tot_stats=self.request_stat,
                                            act_buffs=self.active_buffs,
                                            current_stats=self.current_stats,
                                            current_target=self.current_target,
                                            champion_lvls_dct=champion_lvls_dct,
                                            current_target_num=self.current_target_num))

    def add_new_buff(self, buff_name, tar_name, initial_stacks_increment=1):
        """
        Inserts a new buff in active_buffs dictionary.

        Modifies:
            active_buffs
        Returns:
            (None)
        """

        buff_dct = getattr(self, buff_name)

        # Inserts the new buff.
        self.active_buffs[tar_name].update(
            {buff_name: dict(
                starting_time=self.current_time)})

        # DURATION
        # If non permanent buff.
        if buff_dct()['duration'] != 'permanent':

            # ..creates and inserts its duration.
            self.active_buffs[tar_name][buff_name].update(dict(
                ending_time=self.current_time + buff_dct()['duration']))

        else:
            # ..otherwise sets its duration to 'unlimited'.
            self.active_buffs[tar_name][buff_name].update(dict(
                ending_time='unlimited'))

        # STACKS
        # If it can stack...
        if 'max_stacks' in buff_dct():
            # ...adds current_stacks keyword.
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

        buff_dct = getattr(self, buff_name)
        tar_buff_dct_in_act_buffs = self.active_buffs[tar_name][buff_name]

        # DURATION
        # If non permanent buff, refreshes its duration.
        if buff_dct()['duration'] != 'permanent':

            tar_buff_dct_in_act_buffs['ending_time'] = self.current_time + buff_dct()['duration']

        # STACKS
        # If the applied buff can stack..
        if 'current_stacks' in tar_buff_dct_in_act_buffs:

            # ..and if max_stacks have not been reached..
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

                if tar_buff_dct_in_act_buffs['ending_time'] != 'unlimited':
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

    def add_passive_buffs(self, abilities_effects_dct, abilities_lvls):
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

                #...if the ability has at least one lvl...
                if abilities_lvls[ability_name] > 0:

                    #... applies the buffs.
                    self.add_single_ability_passive_buff(ability_name=ability_name,
                                                         target_type=target_type,
                                                         effects_dct=abilities_effects_dct,
                                                         tar_name=tar_name)

            # Innate passive buffs.
            self.add_single_ability_passive_buff(ability_name='inn',
                                                 target_type=target_type,
                                                 effects_dct=abilities_effects_dct,
                                                 tar_name=tar_name)

            # Item passive buffs.
            for item_name in self.items_lst:
                # (If item is bought multiple times, all stacks are applied)
                self.add_single_ability_passive_buff(ability_name=item_name,
                                                     target_type=target_type,
                                                     effects_dct=self.items_effects,
                                                     tar_name=tar_name)


class DmgApplicationAndCounters(BuffsGeneral):

    AOE_SPELLVAMP_MOD = 30/100

    def __init__(self,
                 current_time,
                 selected_champions_dct,
                 champion_lvls_dct,
                 initial_current_stats=None,
                 initial_active_buffs=None,
                 items_lst=None):

        BuffsGeneral.__init__(self,
                              current_time=current_time,
                              selected_champions_dct=selected_champions_dct,
                              champion_lvls_dct=champion_lvls_dct,
                              initial_current_stats=initial_current_stats,
                              initial_active_buffs=initial_active_buffs,
                              items_lst=items_lst)
        self.dmg_history = {}
        self.actions_dct = {}

        self.set_dmg_history()

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

    def set_dmg_history(self):
        """
        Sets up dmg_history by inserting history blueprints for all targets.

        Modifies:
            dmg_history dict.

        Returns:
            (None)
        """

        for tar in self.selected_champions_dct:

            self.dmg_history.update(
                {tar: dict(
                    true={},
                    magic={},
                    physical={},
                    total={},
                    current_hp={},)})

            if tar == 'player':
                self.dmg_history['player'].update(dict(
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
            dmg_history
        Returns:
            (None)
        """

        for target_name in self.dmg_history:
            if target_name != 'player':

                tar_dmg_hist = self.dmg_history[target_name]

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

    def refined_dmg_history(self):
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

        for tar_name in self.dmg_history:

            # Total for each target separately.
            tot_true_tar = 0
            tot_physical_tar = 0
            tot_magic_tar = 0
            tot_healing_tar = 0

            if tar_name != 'player':

                for hist_cat in self.dmg_history[tar_name]:

                    for dmg_event in self.dmg_history[tar_name][hist_cat]:

                        # Handles true, magic, and physical history.
                        if hist_cat in ('true', 'magic', 'physical'):

                            dmg_value = self.dmg_history[tar_name][hist_cat][dmg_event]

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
                            for source_name in self.dmg_history[tar_name][hist_cat]:
                                source_sum = sum(self.dmg_history[tar_name][hist_cat][source_name])

                                # Updates with sum of each source.
                                dct.update(dict(source={source_name: source_sum}))

                        # Handles ability related dmg history.
                        elif hist_cat == 'ability':

                            # For Q, W, E, R..
                            for ability_name in self.dmg_history[tar_name][hist_cat]:
                                for dmg_name in self.dmg_history[tar_name][hist_cat][ability_name]:

                                    dmg_sum = sum(self.dmg_history[tar_name][hist_cat][dmg_name])

                                    # ..updates with sum for each ability.
                                    dct.update(dict(ability={dmg_name: dmg_sum}))

                        elif hist_cat in ('lifesteal', 'spellvamp'):
                            for heal_type in self.dmg_history[tar_name][hist_cat]:
                                heal_sum = sum(self.dmg_history[tar_name][hist_cat][heal_type])

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
        Inserts spellvamp or lifesteal of an effect, on a particular time.

        Modifies:
            dmg_history
        Args:
            heal_type: (string)
                'lifesteal'
                'spellvamp'
        Returns:
            None
        """

        # Checks if time already exists in history.
        if self.current_time in self.dmg_history['player'][heal_type]:
            self.dmg_history['player'][heal_type][self.current_time] += value
        else:
            self.dmg_history['player'][heal_type].update({self.current_time: value})

    def apply_spellvamp_or_lifesteal(self, dmg_name, dmg_value, dmg_type):
        """
        Applies lifesteal or spellvamp to the player and notes it in history.

        Lifesteal is applied on AAs or dmg effects marked in their dict.

        Spellvamp is applied to true, physical, or magic dmg types,
        excluding AAs and some on hit dmg effects (not marked in their dict).

        Modifies:
            current_stats
            dmg_history
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

                # If it can cause spellvamp..
                if 'spellvamp' in getattr(self, dmg_name)()['special']:

                    # .. sets the healing done.
                    spellvamp_value = dmg_value * self.request_stat(target_name='player',
                                                                    stat_name='spellvamp')

                    # If it's an aoe affect, applies modifier.
                    if 'aoe' in getattr(self, dmg_name)()['special']:
                        spellvamp_value *= self.AOE_SPELLVAMP_MOD

                    self.apply_heal_value(tar_name='player',
                                          heal_value=spellvamp_value)

                    # Then notes in history.
                    self.note_lifesteal_or_spellvamp_in_history(value=spellvamp_value, heal_type='spellvamp')

                # (Lifesteal and spellvamp are exclusive so 'elif' is used)
                # If the dmg can cause lifesteal..
                elif 'lifesteal' in getattr(self, dmg_name)()['special']:

                    # .. sets the healing done.
                    lifesteal_value = dmg_value * self.request_stat(target_name='player', stat_name='lifesteal')

                    self.apply_heal_value(tar_name='player',
                                          heal_value=lifesteal_value)

                    # NOTE IN HISTORY
                    self.note_lifesteal_or_spellvamp_in_history(value=lifesteal_value, heal_type='lifesteal')

    def dmg_related_counters(self, dmg_type, final_dmg_value, target_name):
        """
        Calculates and stores total dmg of a particular type, at a each moment,
        and stores current_hp at a each moment for a target.

        Modifies:
            dmg_history
        Returns:
            (None)
        """

        # Modifies dmg_history.
        if dmg_type == 'AA':
            # AA type is converted to physical before being stored.
            dmg_type = 'physical'

        # Filters out heals.
        if final_dmg_value > 0:
            if self.current_time in self.dmg_history[target_name][dmg_type]:
                self.dmg_history[target_name][dmg_type][self.current_time] += final_dmg_value
            else:
                self.dmg_history[target_name][dmg_type].update({self.current_time: final_dmg_value})

        # Stores current_hp.
        # Replaces previous value for specific time if events occur simultaneously.
        self.dmg_history[target_name]['current_hp'].update(
            {self.current_time: self.current_stats[target_name]['current_hp']})

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
        Reduces or increases player's 'current_'resource and stores it in dmg_history.

        Regen events can be natural (e.g. mp5) or buff based (e.g. Jayce's W) or item based (e.g. AA with Muramana).

        This method is NOT used for ability cost.

        Modifies:
            current_stats
            dmg_history
        Returns:
            (None)
        """

        dmg_value = getattr(self, dmg_name + '_value')()
        resource_type = getattr(self, dmg_name)()['resource_type']
        curr_resource_string = 'current_'+resource_type

        if dmg_value >= 0:
            self.current_stats['player'][curr_resource_string] -= dmg_value

        # (If the value is negative it's a resource replenish effect.)
        else:
            # Checks if resource heal exceeds max possible value.
            max_value = self.request_stat(target_name='player', stat_name=resource_type)

            if self.current_stats['player'][curr_resource_string] - dmg_value > max_value:
                self.current_stats['player'][curr_resource_string] = max_value
            else:
                self.current_stats['player'][curr_resource_string] -= dmg_value

        # Adds time and current resource value in dmg_history.
        self.dmg_history['player']['resource'].update(
            {self.current_time: self.current_stats['player'][curr_resource_string]})

    def apply_hp_dmg_or_heal(self, dmg_name, target_name):
        """
        Applies a dmg or heal value to a target, along with lifesteal or spellvamp, and notes in history.

        -Modifies current_stats of a target by applying a dmg/heal value to his current_hp.

        Modifies:
            current_stats
            dmg_history
        Returns:
            (None)
        """

        dmg_type = getattr(self, dmg_name)()['dmg_type']

        final_dmg_value = self.mitigated_dmg(dmg_value=getattr(self, dmg_name + '_value')(),
                                             dmg_type=dmg_type,
                                             target=target_name)

        # VALUE APPLICATION
        # If it's a dmg.
        if final_dmg_value >= 0:
            self.current_stats[target_name]['current_hp'] -= final_dmg_value

        # Otherwise it's a heal.
        else:
            # (minus used to reverse value)
            self.apply_heal_value(tar_name=target_name,
                                  heal_value=-final_dmg_value)

        # LIFESTEAL/SPELLVAMP
        self.apply_spellvamp_or_lifesteal(dmg_name=dmg_name,
                                          dmg_value=final_dmg_value,
                                          dmg_type=dmg_type)

        # COUNTERS
        self.dmg_related_counters(dmg_type=dmg_type,
                                  final_dmg_value=final_dmg_value,
                                  target_name=target_name)

    def apply_dmg_or_heal(self, dmg_name, target_name):
        """
        Applies dmg or heal to either current_hp or the player's resource.

        Returns:
            (None)
        """

        # Checks if the effect is affecting a resource or hp.
        if 'resource_type' in getattr(self, dmg_name)():
            self.apply_resource_dmg_or_heal(dmg_name=dmg_name)

        elif 'dmg_type' in getattr(self, dmg_name)():
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

        return self.refined_dmg_history()['all_targets']['total_dmg'] / last_cast_completion


class DeathAndRegen(DmgApplicationAndCounters):

    PER_5_DIVISOR = 10.  # Divides "per 5" stats. Used to create per tick value (ticks have 0.5s period)

    @staticmethod
    def dead_buff():
        return dict(
            duration='permanent',)

    def apply_death(self, tar_name):
        """
        Checks if the target is dead. If dead, removes its other buffs and marks it as dead.

        Modifies:
            active_buffs
        Returns:
            (None)
        """

        # If target is already dead, it doesnt check it.
        if 'dead_buff' not in self.active_buffs[tar_name]:
            # Checks if target died.
            if self.current_stats[tar_name]['current_hp'] <= 0:

                # Clears buffs
                self.active_buffs[tar_name] = {}

                # Adds 'dead_buff'.
                self.add_buff(buff_name='dead_buff', tar_name=tar_name)

    @staticmethod
    def enemy_hp5_dmg():

        return dict(
            period=0.5,
            dmg_type='true',
            target='enemy',
            special={'dot': None},
            duration='permanent',)

    @staticmethod
    def enemy_hp5_buff():
        return dict(
            duration='permanent',)

    def enemy_hp5_dmg_value(self):
        """
        Returns healing per 0.5 seconds by regeneration.
        """
        return -self.request_stat(stat_name='hp5', target_name=self.current_target)/self.PER_5_DIVISOR

    @staticmethod
    def player_hp5_dmg():

        return dict(
            period=0.5,
            dmg_type='true',
            target='player',
            special={'dot': None},
            duration='permanent',)

    @staticmethod
    def player_hp5_buff():
        return dict(
            duration='permanent',)

    def player_hp5_dmg_value(self):
        """
        Returns healing per 0.5 seconds by regeneration.
        """
        return -self.request_stat(stat_name='hp5', target_name='player')/self.PER_5_DIVISOR

    @staticmethod
    def mp5_buff():
        return dict(
            duration='permanent',)

    @staticmethod
    def mp5_dmg():
        return dict(
            period=0.5,
            resource_type='mp',
            target='player',
            special={'dot': None},
            duration='permanent',
        )

    def mp5_dmg_value(self):
        return -self.request_stat(stat_name='mp5', target_name='player')/self.PER_5_DIVISOR


if __name__ == '__main__':

    class TestBuffsGeneral(object):

        def __init__(self):
            """Values must NOT be assigned here.
            """

            self.DELIMITER = '\n--------------------------------'
            self.filtered_stats_max = {'crit': 1., 'speed': None, 'att_speed': 2.5, 'cdr': 0.4}

            self.selected_champions_dct = None
            self.champion_lvls_dct = None
            self.initial_current_stats = None
            self.ability_lvls_dct = None
            self.current_time = None
            self.current_target_num = None
            self.initial_active_buffs = None

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

            self.ability_lvls_dct = dict(
                q=0,
                w=0,
                e=0,
                r=0)

            self.initial_active_buffs = None

        def subclass_jax_buffs_general(self):

            import jax

            class CombinerClass(BuffsGeneral, jax.TotalChampionAttributes):

                def __init__(self,
                             ability_lvls_dct,
                             selected_champions_dct,
                             current_time,
                             current_target,
                             champion_lvls_dct,
                             current_target_num,
                             initial_active_buffs=None):

                    BuffsGeneral.__init__(self,
                                          current_time=current_time,
                                          selected_champions_dct=selected_champions_dct,
                                          champion_lvls_dct=champion_lvls_dct,
                                          initial_active_buffs=initial_active_buffs)

                    jax.TotalChampionAttributes.__init__(self,
                                                         ability_lvls_dct=ability_lvls_dct,
                                                         tot_stats=self.request_stat,
                                                         act_buffs=self.active_buffs,
                                                         current_stats=self.current_stats,
                                                         current_target=current_target,
                                                         champion_lvls_dct=champion_lvls_dct,
                                                         current_target_num=current_target_num)

            return CombinerClass

        def test_add_buff(self):
            """Tests adding an already active buff.
            """

            self.set_up()

            self.initial_active_buffs = dict(
                player=dict(
                    innate_att_speed_buff=dict(current_stacks=1)),
                enemy_1={})

            inst = self.subclass_jax_buffs_general()(ability_lvls_dct=self.ability_lvls_dct,
                                                     selected_champions_dct=self.selected_champions_dct,
                                                     current_time=0,
                                                     current_target='player',
                                                     champion_lvls_dct=self.champion_lvls_dct,
                                                     current_target_num=1,
                                                     initial_active_buffs=self.initial_active_buffs)

            msg = self.DELIMITER

            msg += '\nTesting method: add_buff\n'
            msg += '\n(no initial active buffs)\n'

            msg += '\nadd buff: innate_att_speed_buff (max stacks: %s)' % inst.innate_att_speed_buff()['max_stacks']

            inst.add_buff('innate_att_speed_buff', tar_name='player')
            msg += '\nactive_buffs: %s' % inst.active_buffs['player']

            # Apply 7 times the buff to test stacks.
            msg += '\n\nadd innate_att_speed_buff x7'
            for i in range(7):
                inst.add_buff('innate_att_speed_buff', tar_name='player')
            msg += '\nactive_buffs: %s' % inst.active_buffs['player']

            return msg

        def test_add_buff_preexisting(self):
            """Tests adding a new buff and tests its max stacks.
            """

            self.set_up()

            self.initial_active_buffs = dict(
                player={'innate_att_speed_buff': {'current_stacks': 1, 'ending_time': 1}})

            inst = self.subclass_jax_buffs_general()(ability_lvls_dct=self.ability_lvls_dct,
                                                     selected_champions_dct=self.selected_champions_dct,
                                                     current_time=0,
                                                     current_target='player',
                                                     champion_lvls_dct=self.champion_lvls_dct,
                                                     current_target_num=1,
                                                     initial_active_buffs=self.initial_active_buffs)

            msg = self.DELIMITER

            msg += '\nTesting method: add_buff (already active buff)\n'
            msg += '\ninitial active buffs: %s\n' % inst.initial_active_buffs

            msg += '\nadd buff: innate_att_speed_buff (max stacks: %s)' % inst.innate_att_speed_buff()['max_stacks']

            inst.add_buff('innate_att_speed_buff', tar_name='player')
            msg += '\nactive_buffs: %s' % inst.active_buffs['player']

            return msg

        def test_remove_expired_buffs(self):
            """Tests adding removing expired buffs.

            WARNING: Does not take into account stacks when calculating bonuses.
            """

            self.set_up()
            self.initial_active_buffs = dict(player={'innate_att_speed_buff': {'current_stacks': 1, 'ending_time': 1}})
            self.current_time = 2

            inst = self.subclass_jax_buffs_general()(ability_lvls_dct=self.ability_lvls_dct,
                                                     selected_champions_dct=self.selected_champions_dct,
                                                     current_time=self.current_time,
                                                     current_target='player',
                                                     champion_lvls_dct=self.champion_lvls_dct,
                                                     current_target_num=1,
                                                     initial_active_buffs=self.initial_active_buffs)

            msg = self.DELIMITER

            msg += '\nTesting method: remove_expired_buffs\n'
            msg += '\ninitial active buffs: %s\n' % str(inst.initial_active_buffs)

            inst.remove_expired_buffs()
            msg += '\nactive_buffs: %s' % inst.active_buffs['player']

            return msg

        def test_add_abilities_passive_buffs(self):
            """Tests if passive buffs are added to player and enemies.

            -Passive buffs with 0 lvl abilities.
            -Passive buffs with max lvl abilities.
            """

            self.set_up()

            # Abilities lvl 0.
            inst = self.subclass_jax_buffs_general()(ability_lvls_dct=self.ability_lvls_dct,
                                                     selected_champions_dct=self.selected_champions_dct,
                                                     current_time=self.current_time,
                                                     current_target='player',
                                                     champion_lvls_dct=self.champion_lvls_dct,
                                                     current_target_num=1,
                                                     initial_active_buffs=self.initial_active_buffs)

            # Abilities non 0 lvl.
            self.set_up()
            self.ability_lvls_dct = dict(
                q=5,
                w=5,
                e=5,
                r=3)

            inst_2 = self.subclass_jax_buffs_general()(ability_lvls_dct=self.ability_lvls_dct,
                                                       selected_champions_dct=self.selected_champions_dct,
                                                       current_time=self.current_time,
                                                       current_target='player',
                                                       champion_lvls_dct=self.champion_lvls_dct,
                                                       current_target_num=1,
                                                       initial_active_buffs=self.initial_active_buffs)

            msg = self.DELIMITER

            for instance_name in (inst, inst_2):
                msg += '\nTesting method: add_abilities_passive_buffs\n\n'
                msg += 'ability lvls: %s\n' % instance_name.ability_lvls_dct

                instance_name.add_abilities_passive_buffs(instance_name.abilities_effects(),
                                                          instance_name.ability_lvls_dct)

                msg += 'active_buffs: %s' % instance_name.active_buffs

                msg += self.DELIMITER

            return msg

        def __repr__(self):

                msg = ''

                msg += self.DELIMITER

                msg += self.test_add_buff()

                msg += self.DELIMITER

                msg += self.test_add_buff_preexisting()

                msg += self.DELIMITER

                msg += self.test_remove_expired_buffs()

                msg += self.DELIMITER

                msg += self.test_add_abilities_passive_buffs()

                msg += self.DELIMITER

                return msg

    print(TestBuffsGeneral())