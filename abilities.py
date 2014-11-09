import buffs
import timers
import runes
import database_champion_stats
import matplotlib.pyplot as plt


class EventsGeneral(buffs.DeathAndRegen):

    def __init__(self,
                 champion_lvls_dct,
                 selected_champions_dct,
                 max_targets_dct,
                 initial_active_buffs=None,
                 initial_current_stats=None,
                 items_lst=None):

        self.max_targets_dct = max_targets_dct  # User defined dict containing number of targets abilities affected.
        self.event_times = {}
        self.current_time = 0
        self.current_target = None

        buffs.DeathAndRegen.__init__(self,
                                     current_time=self.current_time,
                                     selected_champions_dct=selected_champions_dct,
                                     champion_lvls_dct=champion_lvls_dct,
                                     initial_active_buffs=initial_active_buffs,
                                     initial_current_stats=initial_current_stats,
                                     items_lst=items_lst)

        self.resource_used = database_champion_stats.CHAMPION_BASE_STATS[selected_champions_dct['player']]['resource_used']

    def add_event_to_first_tar(self, effect_name, start_time):
        """
        Modifies event_times by applying the event to the first target.
        """

        if 'delay' in getattr(self, effect_name)():
            start_time += getattr(self, effect_name)()['delay']

        # If the event's time doesnt exist it creates it.
        if start_time not in self.event_times:
            self.event_times.update({start_time: {self.current_target: [effect_name]}})

        else:
            # If the time exists in the dictionary..
            # .. checks if the target is inside the time.
            if self.current_target in self.event_times[start_time]:
                self.event_times[start_time][self.current_target].append(effect_name)
            else:
                # If not, it adds the target as well.
                self.event_times[start_time].update({self.current_target: [effect_name]})

    def add_regenerations(self):
        """
        Modifies event_times and active_buffs, by applying hp5 for all targets and resource per 5 for player.
        """

        # For each target..
        for self.current_target in self.selected_champions_dct:
            # .. if target is enemy..
            if self.current_target != 'player':
                self.add_buff(buff_name='enemy_hp5_buff', tar_name=self.current_target)
                # ..adds hp5 event.
                self.add_event_to_first_tar(effect_name='enemy_hp5_dmg',
                                            start_time=0.5)

            # ..if target is player, adds his hp5 and resource per 5.
            else:
                self.add_buff(buff_name='player_hp5_buff', tar_name=self.current_target)
                # ..adds hp5 event.
                self.add_event_to_first_tar(effect_name='player_hp5_dmg',
                                            start_time=0.5)

                regen_event_name = None
                if self.resource_used == 'energy':
                    regen_event_name = 'ep5_dmg'
                    self.add_buff(buff_name='ep5_buff', tar_name=self.current_target)

                elif self.resource_used == 'mp':
                    regen_event_name = 'mp5_dmg'
                    self.add_buff(buff_name='mp5_buff', tar_name=self.current_target)

                # Checks if player's resource can regenerate.
                if regen_event_name:
                    # Regen starts being applied at 0.5sec.
                    self.add_event_to_first_tar(effect_name=regen_event_name,
                                                start_time=0.5)

    def add_events(self, effect_name, start_time):
        """
        Modifies event_times by applying the event (e.g. Brand W) to all affected targets.

        event_times dict structure: {0.: {'player': ['w_dmg',],},}
        """

        # Adds event to first target.
        self.add_event_to_first_tar(effect_name=effect_name, start_time=start_time)
        # Changes event start if needed.
        if 'delay' in getattr(self, effect_name)():
            start_time += getattr(self, effect_name)()['delay']

        self.targets_already_hit = 1

        # AOE DMG
        # If the effect has an externally set max number of targets (therefor it's aoe).
        if effect_name in self.max_targets_dct:
            # Until the rest of the targets are affected or no targets are left..
            while self.targets_already_hit < self.max_targets_dct[effect_name]:
                self.next_target()
                self.event_times[start_time][self.current_target].append(effect_name)

        # Otherwise if it has max_targets (therefor it's aoe).
        elif 'max_targets' in getattr(self, effect_name)():

            # If it has unlimited targets applies to every alive target.
            if getattr(self, effect_name)()['max_targets'] == 'unlimited':

                while self.targets_already_hit < len(self.champion_lvls_dct):
                    # Switches to next target.
                    # If next target is None (because no valid targets exist) the loop breaks.
                    self.next_target()
                    if not self.current_target:
                        break
                    # .. checks if the target is inside the time.
                    if self.current_target in self.event_times[start_time]:
                        self.event_times[start_time][self.current_target].append(effect_name)
                    else:
                        self.event_times[start_time].update({self.current_target: [effect_name]})

            else:
                while self.targets_already_hit < getattr(self, effect_name)()['max_targets']:
                    # Switches to next target.
                    # If next target is None (because no valid targets exist) the loop breaks.
                    self.next_target()
                    if not self.current_target:
                        break

                    # .. checks if the target is inside the time.
                    if self.current_target in self.event_times[start_time]:
                        self.event_times[start_time][self.current_target].append(effect_name)
                    else:
                        self.event_times[start_time].update({self.current_target: [effect_name]})

    def add_next_periodic_event(self, tar_name, dmg_name, only_temporary=False):
        """
        Modifies event_times, by adding next periodic tick.

        If non permanent dots are of interest, ignores dots with unlimited duration.

        -Checks active_buffs for the buff.
        -Adds event if the buff still exists.
        """

        dmg_dct = getattr(self, dmg_name)()

        def event_refresher():
            # Checks if the dot's buff is still active.
            # (Refreshed only if buff ending time is higher than event ending time,)
            # (or if ending_time doesn't exist meaning its a permanent buff.)
            if dmg_name[:-3]+'buff' in self.active_buffs[tar_name]:
                if (('ending_time' not in self.active_buffs[tar_name]) or
                        (self.active_buffs[tar_name]['ending_time'] > self.current_time)):

                    # If so, adds event.
                    self.add_events(effect_name=dmg_name,
                                    start_time=self.current_time + dmg_dct['period'])

        # Checks if event is periodic.
        if 'special' in dmg_dct:
            if 'dot' in dmg_dct['special']:
                # If only temporary periodic events are re-applied..
                if only_temporary:
                    # ..checks if their duration is not unlimited (exists).
                    if 'duration' in dmg_dct:
                        event_refresher()

                # Otherwise checks both permanent and temporary dots.
                else:
                    event_refresher()


class Actions(EventsGeneral, timers.Timers, runes.RunesFinal):

    AA_COOLDOWN = 0.4   # TODO: replace functionality with 'wind_up'

    def __init__(self,
                 rotation_lst,
                 max_targets_dct,
                 selected_champions_dct,
                 champion_lvls_dct,
                 ability_lvls_dct,
                 max_combat_time=None,
                 items_lst=None,
                 initial_active_buffs=None,
                 initial_current_stats=None,
                 selected_runes=None):

        self.max_combat_time = max_combat_time
        self.rotation_lst = rotation_lst
        self.actions_dct = {}
        self.current_target_num = None
        self.everyone_dead = None

        runes.RunesFinal.__init__(self,
                                  player_lvl=champion_lvls_dct['player'],
                                  selected_runes=selected_runes)

        EventsGeneral.__init__(self,
                               champion_lvls_dct=champion_lvls_dct,
                               selected_champions_dct=selected_champions_dct,
                               max_targets_dct=max_targets_dct,
                               initial_active_buffs=initial_active_buffs,
                               initial_current_stats=initial_current_stats,
                               items_lst=items_lst)

        timers.Timers.__init__(self,
                               ability_lvls_dct=ability_lvls_dct)

    def action_cost_dct(self, action_name):
        """
        Returns dict containing:
            -resource used and it's value.
            -stack name and number of stacks.

        Used for abilities with normal or toggled cost.
        """

        cost_dct = {}

        # ACTIVATED ABILITIES
        if action_name in 'qwer':
            # NORMAL COST
            ability_stats_dct = getattr(self, action_name.upper()+'_STATS')
            resource_used = ability_stats_dct['general']['resource_used']

            # Check if ability has a fixed cost,
            # or one that scales per ability_lvl,
            # or no resource cost (none of the if's are true).
            if 'fixed_cost' in ability_stats_dct['general']:
                resource_cost = ability_stats_dct['general']['fixed_cost']
                cost_dct = {resource_used: resource_cost}
            elif 'cost_tpl' in ability_stats_dct['general']:
                resource_cost = ability_stats_dct['general']['cost_tpl'][self.ability_lvls_dct[action_name]-1]
                cost_dct = {resource_used: resource_cost}

            # STACK COST
            # (e.g. akali R stacks)
            if 'stack_cost' in ability_stats_dct['general']:
                stack_name = ability_stats_dct['general']['stack_cost']
                cost_dct.update({stack_name: ability_stats_dct['general']['stack_cost'][stack_name]})

        return cost_dct

    def cost_sufficiency(self, action_name):
        """
        Returns boolean, depending on whether there are enough resources to cast the action or not.
        """

        sufficiency = True

        for cost_name in self.action_cost_dct(action_name):
            cost_value = self.action_cost_dct(action_name)[cost_name]

            if cost_name in ('mp', 'energy', 'hp'):
                if self.current_stats['player']['current_'+cost_name] < cost_value:
                    sufficiency = False

            else:
                if cost_name not in self.active_buffs['player']:
                    sufficiency = False

        return sufficiency

    def apply_action_cost(self, action_name):
        """
        Modifies player's current_stats, and/or active_buffs, deducting the cost of an action.

        The cost may be a stat and/or buff stacks.
        """

        for cost_name in self.action_cost_dct(action_name):
            cost_value = self.action_cost_dct(action_name)[cost_name]

            if cost_name in ('mp', 'energy', 'hp', 'rage'):
                self.current_stats['player']['current_' + cost_name] -= cost_value

            else:
                del self.active_buffs['player'][cost_name]

    def apply_aa_cd_reset(self, action_name):
        """
        Modifies actions_dict, by removing an AA's cd after an AA-resetting ability is casted.
        """

        if 'special' in getattr(self, action_name.upper()+'_STATS')['general']:
            if 'resets_aa' in getattr(self, action_name.upper()+'_STATS')['general']['special']:

                for action_time in sorted(self.actions_dct, reverse=True):

                    # If an AA has been casted earlier...
                    if 'AA' == self.actions_dct[action_time]['action_name']:
                        # ..sets its cd_end to current_time.
                        self.actions_dct[action_time]['cd_end'] = self.current_time
                        break

    def add_new_action(self, action_name, cast_start):
        """
        Modifies actions_dct, by inserting a new action.

        Used by add_action.
        """

        # Checks if action is a champion ability.
        if action_name in 'qwer':
            self.actions_dct.update({cast_start: dict(
                cast_end=self.cast_end(action_name, cast_start),
                action_name=action_name
            )})

            action_stats_dct = getattr(self, action_name.upper()+'_STATS')['general']
            if ('special' in action_stats_dct) and ('cd_extendable' in action_stats_dct['special']):
                # Cooldown starts after the cast of the action ends plus the duration the extender buff.
                # (If the buff is removed earlier it sets to the normal cd in appropriate method.)

                self.actions_dct[cast_start].update(dict(
                    cd_end=(self.actions_dct[cast_start]['cast_end'] +
                            self.ability_cooldown(action_name, self.request_stat) +
                            getattr(self, action_stats_dct['special']['cd_extendable'])()['duration']
                            )
                ))

            else:
                # Cooldown starts after the cast of the action ends.
                self.actions_dct[cast_start].update(dict(
                    cd_end=(self.actions_dct[cast_start]['cast_end'] +
                            self.ability_cooldown(action_name, self.request_stat))
                ))

            # Checks if ability resets AA's cd_end, and applies it.
            self.apply_aa_cd_reset(action_name=action_name)

        # Checks if action is an AA
        elif action_name == 'AA':
            self.actions_dct.update({cast_start: dict(
                cd_end=cast_start + 1./self.request_stat(target_name='player', stat_name='att_speed'),

                action_name=action_name,

                cast_end=cast_start + self.AA_COOLDOWN
            )})

        else:

            # Otherwise action is an item's active or summoner's spell
            self.actions_dct.update({cast_start: dict(
                cast_end=cast_start,                        # cast_end is the same as..
                                                            # ..cast_start for non ..
                                                            # ..champion abilities.

                cd_end=360,                                         # Their cooldowns are too high..
                                                                    # ..to have an effect,
                                                                    # ..so they are set to a high value.
                action_name=action_name)})

    def action_cast_start(self, action_name):
        """
        Returns cast_start of an action, based on other actions' cast_end and this action's cd.
        """

        cast_start = self.current_time

        # If a previous action exists...
        if self.actions_dct:

            casted_earlier = None

            #...checks all actions inside dict from last to first.
            for action_time in sorted(self.actions_dct, reverse=True):

                # If the examined action has been casted earlier...
                if action_name == self.actions_dct[action_time]['action_name']:

                    #...compare which ends last; ..
                    cast_start = max(

                        # ..the examined action's cd ..
                        self.actions_dct[action_time]['cd_end'],

                        # .. or the last action's cast_end.
                        self.actions_dct[max(self.actions_dct)]['cast_end']) + 0.00000001
                                                                        # Tiny amount added to avoid action overwriting.

                    casted_earlier = True

                    break

            # If it hasn't been casted earlier...
            if not casted_earlier:

                #... it starts when last action's cast ends.
                cast_start = self.actions_dct[max(self.actions_dct)]['cast_end'] + 0.00000001
                                                                    # Tiny amount added to avoid action start ..
                                                                    # .. overwriting.

        return cast_start

    def add_action(self, action_name):
        """
        Modifies action_dct by inserting the time the current action starts being casted as keyword,
        and a dictionary as value.

        The second dictionary contains the time the action is applied, the action's name and the time its cooldown ends.

        e.g. action_dct = { 0: {'cd_end': 2.1, 'action_name': 'q', 'cast_end': 1, .. }, 0.3: {..} ..}

                            ________
         ___|    ___| _____|||||||||
        |___|___|___||_____|_______|
        '   '   '   '      '       '
        0   1   2   3      5     / 7.5
                    |     /     /
                    |   /     /
              cast  | /     /
              start *     /
                    |   /
                    | /
                    *
                cast
                end

        For channeled abilities, it disallows queueing another action,
        while allowing effect application.
        """

        # TODO: insert flow control for channeled abilities (when 'channel_time' exists, check that instead of cast_end)

        # Sets cast_start.
        cast_start = self.action_cast_start(action_name=action_name)
                                                    # cast_start is the moment the action is 'clicked'

        # Adds the action based on
        self.add_new_action(action_name=action_name, cast_start=cast_start)

    def remove_buff_on_action(self, buff_name):
        """
        Modifies active_buffs and actions_dict, by removing a player's buff on_hit or on_cast,
        and starting corresponding action's cd if buff delays the cd start.

        (e.g. Jax w_buff delays start of W cd)
        """

        buff_dct = getattr(self, buff_name)()

        # Checks if buff delays the start of an action's cd.
        if 'special' in buff_dct:
            if 'delay_cd_start' in buff_dct['special']:

                # Finds the affected action..
                for action_time in sorted(self.actions_dct, reverse=True):
                    if self.actions_dct[action_time]['action_name'] == buff_dct['special']['delay_cd_start']:

                        # .. and applies the new cd.
                        self.actions_dct[action_time]['cd_end'] = self.ability_cooldown(
                            ability_name=self.actions_dct[action_time]['action_name'],
                            stats_function=self.request_stat)

                        break

        # Removes buff.
        del self.active_buffs['player'][buff_name]

    def apply_on_hit_effects(self):
        """
        Modifies active_buffs and event_times, by applying dmg and buffs or removing buffs.
        """

        add_buff_function = self.add_buff

        player_active_buffs = sorted(self.active_buffs['player'])

        for buff_name in player_active_buffs:
            buff_dct = getattr(self, buff_name)()

            if 'on_hit' in buff_dct:

                # Buffs applied on hit.
                for buff_applied_on_hit in buff_dct['on_hit']['apply_buff']:

                    add_buff_function(buff_name=buff_applied_on_hit,
                                      tar_name=getattr(self, buff_applied_on_hit)()['target'])

                # If the buff is a dot, applies event as well.
                if 'period' in buff_dct:

                    first_tick = self.first_dot_tick(self.current_time,                # First tick start
                                                     buff_name)
                    self.add_events(buff_name, first_tick)

                # Dmg caused on hit.
                for dmg_name in buff_dct['on_hit']['cause_dmg']:

                    self.switch_to_first_alive_enemy()
                    self.add_events(dmg_name, self.current_time)

                # BUFFS REMOVED ON HIT.
                # For each buff that is removed on hit..
                for buff_removed_on_hit in buff_dct['on_hit']['remove_buff']:

                    # Checks if the buff exists on the player.
                    if buff_removed_on_hit in self.active_buffs['player']:
                        self.remove_buff_on_action(buff_name=buff_removed_on_hit)

                    # Checks if the buff exists on current enemy target.
                    elif buff_removed_on_hit in self.active_buffs[self.current_target]:
                        del self.active_buffs[self.current_target][buff_removed_on_hit]

    def apply_aa_effects(self, current_time):
        """
        Modifies active_buffs and event_times by applying AA effects from buffs and AA dmg event.

        Iterates throughout all active buffs,
        applies on_hit buffs (e.g. Black Cleaver armor reduction), then on_hit dmg (e.g. Warwick's innate dmg),
        and then removes buffs that are removed on hit.
        """

        # Applies on_hit effects.
        self.apply_on_hit_effects()

        # Applies direct dmg.
        self.switch_to_first_alive_enemy()
        self.add_events('aa_dmg', current_time)

    def apply_ability_effects(self, action_name, effects_dct, current_time):
        """
        Modifies active buffs and event times, by applying an actions effects.

        Used for abilities, item actives or summoner actives.
        """

        if 'player' in effects_dct[action_name]:
            self.current_target = 'player'
            # Checks if the ability has any active..
            if 'actives' in effects_dct[action_name]['player']:
                # .. buffs.
                if 'buffs' in effects_dct[action_name]['player']['actives']:
                    for buff_name in effects_dct[action_name]['player']['actives']['buffs']:
                        # Buffs.
                        self.add_buff(buff_name, self.current_target)
                        # If the buff is a dot, applies event as well.
                        if 'period' in getattr(self, buff_name)():

                            first_tick = self.first_dot_tick(current_time,                # First tick start
                                                             buff_name)
                            self.add_events(buff_name, first_tick)
                # .. dmg.
                if 'dmg' in effects_dct[action_name]['player']['actives']:
                    for dmg_name in effects_dct[action_name]['player']['actives']['dmg']:
                        self.add_events(dmg_name, current_time)

                # .. buff removal.
                if 'remove_buff' in effects_dct[action_name]['player']['actives']:
                    for buff_name_to_remove in effects_dct[action_name]['player']['actives']['remove_buff']:
                        del self.active_buffs['player'][buff_name_to_remove]

        if 'enemy' in effects_dct[action_name]:

            self.switch_to_first_alive_enemy()

            # Checks if the ability has any active..
            if 'actives' in effects_dct[action_name][self.target_type()]:
                # .. buffs.
                if 'buffs' in effects_dct[action_name][self.target_type()]['actives']:
                    for buff_name in effects_dct[action_name][self.target_type()]['actives']['buffs']:
                        # Buffs.
                        self.add_buff(buff_name, self.current_target)
                        # If the buff is a dot, applies event as well.
                        if 'period' in getattr(self, buff_name)():

                            first_tick = self.first_dot_tick(current_time,                # First tick start
                                                             buff_name)
                            self.add_events(buff_name, first_tick)

                # .. dmg.
                if 'dmg' in effects_dct[action_name][self.target_type()]['actives']:
                    for dmg_name in effects_dct[action_name][self.target_type()]['actives']['dmg']:
                        self.add_events(dmg_name, current_time)

                # .. buff removal.
                if 'remove_buff' in effects_dct[action_name][self.target_type()]['actives']:
                    for buff_name_to_remove in effects_dct[action_name][self.target_type()]['actives']['remove_buff']:
                        del self.active_buffs[self.current_target][buff_name_to_remove]

    def apply_action_effects(self, action_name, abilities_effects, items_effects):
        """
        Modifies active_buffs and event_times by applying an action's effects (buffs and dmg).
        """

        # If the action is an AA...
        if action_name == 'AA':
            #..applies AA physical dmg, and applies (or removes) on_hit buffs and dmg.
            self.apply_aa_effects(self.current_time)

        # If the action is an ability...
        elif action_name in 'qwer':

            #..applies its active buffs and dmg.
            self.apply_ability_effects(action_name=action_name,
                                       effects_dct=abilities_effects,
                                       current_time=self.current_time)

        # If the action is an item active or summoner spell..
        else:
            #..applies its active buffs and dmg.
            self.apply_ability_effects(action_name=action_name,
                                       effects_dct=items_effects,
                                       current_time=self.current_time)

    def apply_pre_action_events(self):
        """
        Modifies current_time, event_times and active_buffs.

        Applies all events preceding an action's application start.

        If a periodic event is refreshed and ticks before the the last action,
        then event_times changes and is checked again.
        If all targets die, the loop stops.
        """

        not_all_events_checked = True

        while not_all_events_checked:

            # If for loop ends with new events being added,
            # then 'not_all_events_checked' will be set to true,
            # and the for loop will repeat.
            not_all_events_checked = False

            initial_events = sorted(self.event_times)

            for event in initial_events:
                # Checks if event start exceeds last action's cast end.
                if event <= self.actions_dct[max(self.actions_dct)]['cast_end']:

                        self.current_time = event   # Must change to ensure buffs are checked.

                        # Removes expired buffs,...
                        self.remove_expired_buffs()

                        # Applies all dmg effects for all targets.
                        for self.current_target in self.event_times[self.current_time]:
                            for dmg_name in self.event_times[self.current_time][self.current_target]:
                                self.apply_dmg_or_heal(dmg_name, self.current_target)
                                self.add_next_periodic_event(tar_name=self.current_target, dmg_name=dmg_name)

                                # Checks after each periodic application if new events have been added.
                                # (Doesn't set to true if already true.)
                                if not not_all_events_checked and initial_events != sorted(self.event_times):
                                    not_all_events_checked = True

                            # After dmg has been applied checks if target has died.
                            self.apply_death(tar_name=self.current_target)

                        # Deletes the event after it's applied.
                        del self.event_times[self.current_time]

                        # If new events are added it exits and checks them all over again.
                        if not_all_events_checked:
                            break

                # Exits loop after all events prior to an action are applied.
                else:
                    break

                self.everyone_dead = True  # Must be set here as True since first action doesn't enter this loop at all.
                # Checks if alive targets exist.
                for tar_name in self.champion_lvls_dct:
                    if tar_name != 'player':
                        if self.current_stats[tar_name]['current_hp'] > 0:
                            self.everyone_dead = False
                            break

                # If everyone has died, stops applying following events.
                if self.everyone_dead:
                    break

    def apply_action_or_event(self, rotation_lst, max_time):
        """
        Modifies current_time, active_buffs and event_times.

        Applies each action and event, based on which comes first.

        -Starts by applying the first action.
        -Then applies events preceding next action (if there are any).
        -Repeats above steps.
        -Changes current_time in between.

        Note: remove_expired_buffs should also be called before add_action for some champions.
        """

        for new_action in rotation_lst:
            # Applies next action..

            # Checks if action meets the cost requirements.
            if self.cost_sufficiency(action_name=new_action):
                self.apply_action_cost(action_name=new_action)

                self.add_action(new_action)

                self.apply_pre_action_events()

                # If everyone died, stops applying actions as well.
                if self.everyone_dead:
                    break

                # Sets current_time to current action's cast end.
                self.current_time = self.actions_dct[max(self.actions_dct)]['cast_end']

                # If max time exceeded, exits loop.
                if max_time:
                    if self.current_time > max_time:
                        break

                # After previous events are applied, applies action effects.
                self.apply_action_effects(action_name=self.actions_dct[max(self.actions_dct)]['action_name'],
                                          abilities_effects=self.abilities_effects(),
                                          items_effects=self.items_effects
                                          )

            # If the cost is too high..
            else:
                pass  # TODO

    def apply_events_after_actions(self):
        """
        Modifies event_times, active_buffs and current_time.

        -Applies events after all actions have finished.
        -Non permanent dots are refreshed and their events fully applied.
        -Applies death to each target.
        """

        # Applies events after all actions have finished.
        not_all_events_checked = True

        while not_all_events_checked:

            # If for loop ends with new events being added,
            # then 'not_all_events_checked' will be set to true,
            # and the for loop will repeat.
            # Above process will repeat until all events have been marked as applied.
            not_all_events_checked = False

            initial_events = sorted(self.event_times)

            for event in initial_events:

                    self.current_time = event   # Must change to ensure buffs are checked.

                    # Removes expired buffs,...
                    self.remove_expired_buffs()
                    # Applies all dmg effects for all targets..
                    for self.current_target in self.event_times[self.current_time]:
                        # ..if they are alive.
                        if self.current_stats[self.current_target]['current_hp'] > 0:
                            for dmg_name in self.event_times[self.current_time][self.current_target]:
                                self.apply_dmg_or_heal(dmg_name, self.current_target)
                                self.add_next_periodic_event(tar_name=self.current_target,
                                                             dmg_name=dmg_name,
                                                             only_temporary=True)

                                # Checks after each periodic application if new events have been added.
                                # (Doesn't set to true if already true.)
                                if not not_all_events_checked and initial_events != sorted(self.event_times):
                                    not_all_events_checked = True

                            # If new events are added it exits and checks them all over again.
                            if not_all_events_checked:
                                break

        for tar_name in self.selected_champions_dct:
            self.apply_death(tar_name=tar_name)

    def combat_loop(self):
        """
        Modifies active_buffs, event_times,
        """

        self.current_time = 0

        # Adds runes buff.
        self.add_buff(buff_name='runes_buff', tar_name='player')

        # Adds hp5 and mp5.
        self.add_regenerations()

        # Adds passive buffs from abilities.
        self.add_passive_buffs(self.abilities_effects(), self.ability_lvls_dct)

        # Applies actions or events based on which occurs first.
        self.apply_action_or_event(self.rotation_lst, self.max_combat_time)

        # Applies events after all actions have finished.
        self.apply_events_after_actions()


class VisualRepresentation(Actions):

    def subplot_pie_chart(self, subplot_name):

        dmg_values = []
        slice_names = []
        slice_distance = []

        counter_var = 1

        for dmg_type in self.refined_dmg_history()['all_targets']:
            # Filters out non used keywords.
            if ('heal' not in dmg_type) and ('total' not in dmg_type):

                # Filters out 0 value dmg.
                if self.refined_dmg_history()['all_targets'][dmg_type] > 0:

                    slice_distance.append(0.02 * counter_var)
                    slice_names.append(dmg_type)
                    dmg_values.append(self.refined_dmg_history()['all_targets'][dmg_type])

                    counter_var += 1

        subplot_name.pie(x=dmg_values, labels=slice_names, explode=slice_distance, autopct='%1.1f%%')

    def subplot_dmg_graph(self, subplot_name):

        subplot_name.grid(b=True)

        # Line at y=0.
        plt.axhline(y=0, color='black')
        # Line at x=0.
        plt.axvline(x=0, color='black')

        plt.ylabel('health')

        color_counter_var = 0

        color_lst = ('b', 'g', 'y', 'r')

        for tar_name in sorted(self.dmg_history):
            if tar_name != 'player':

                hp_change_times = sorted(self.dmg_history[tar_name]['current_hp'])
                max_hp = self.request_stat(target_name=tar_name, stat_name='hp')

                # Inserts initial point.
                subplot_name.plot([0], max_hp, color=color_lst[color_counter_var], alpha=0.8,
                                  label=tar_name)

                # Left boundary is initially set to max hp.
                x_1 = 0
                current_hp = max_hp

                x_values = []
                y_values = []

                for event_time in hp_change_times:

                    x_area_lst = [i for i in range(int(x_1 / 0.01), int((event_time + 0.01) / 0.01))]

                    for x_element in x_area_lst:
                        x_values.append(x_element/100)
                        y_values.append(current_hp)

                    current_hp = self.dmg_history[tar_name]['current_hp'][event_time]
                    x_1 = event_time

                subplot_name.plot(x_values, y_values, color=color_lst[color_counter_var], alpha=0.7)
                color_counter_var += 1

        plt.legend(prop={'size': 10},
                   bbox_to_anchor=(1.0, 1),
                   loc=2,
                   )

        # ACTIONS IN PLOT
        x_actions = []
        y_actions = []
        counter_var = 1
        previous_action_name_x = -100
        prev_high = False

        for x_var in sorted(self.actions_dct):
            x_actions.append(x_var)
            y_actions.append(0)

            # If names are too close..
            if x_var - previous_action_name_x < 1:

                # ..and if previous was low..
                if not prev_high:

                    # ..increases the height of the name.
                    higher_y = 40
                    prev_high = True

                else:
                    prev_high = False
                    higher_y = 0
            else:
                # If names are too far, it sets it on the lowest height.
                prev_high = False
                higher_y = 0

            subplot_name.annotate(self.actions_dct[x_var]['action_name'], xy=(x_var, -70 + higher_y), color='grey')

            previous_action_name_x = x_var

            # Action vertical lines
            plt.axvline(x=x_var, color='grey', linestyle='dashed', alpha=0.6)
            counter_var += 1

    def subplot_resource_vamp_lifesteal_graph(self, subplot_name):

        subplot_name.grid(b=True)

        # Line at y=0.
        plt.axhline(y=0, color='black')
        # Line at x=0.
        plt.axvline(x=0, color='black')

        plt.xlabel('time')
        plt.ylabel('value')

        # LIFESTEAL, SPELLVAMP, RESOURCE
        stat_color = {'lifesteal': 'y', 'spellvamp': 'g', 'resource': 'b'}

        # Places initial resource.
        subplot_name.plot([0], self.request_stat(target_name='player', stat_name=self.resource_used),
                          color=stat_color['resource'], marker='.')

        for examined in stat_color:
            # Inserts each time and value into graph.
            if examined == 'resource':
                # (Sets initial value of resource)
                x_val = [0, ]
                y_val = [self.request_stat(target_name='player', stat_name=self.resource_used), ]

            else:
                x_val = []
                y_val = []

            for event_time in sorted(self.dmg_history['player'][examined]):
                x_val.append(event_time)
                y_val.append(self.dmg_history['player'][examined][event_time])

            subplot_name.plot(x_val, y_val, color=stat_color[examined], marker='.', label=examined)

        plt.legend(prop={'size': 10},
                   bbox_to_anchor=(1.01, 1),
                   loc=2,
                   )

    def subplot_table_of_setup(self, subplot_name):

        stat_names_lst = [
            'ad',
            'ap',
            'att_speed',
            'crit',
            'armor',
            'mr'
        ]

        couple_lst = []

        # BASE STATS
        # Creates stat_values and inserts them in corresponding order of stat_names.
        for stat_name in stat_names_lst:
            couple_lst.append((stat_name, self.request_stat(target_name='player',
                                                            stat_name=stat_name)))

        # AFTERMATH STATS
        couple_lst.append(('dps', "{0:.3f}".format(self.dps())))

        subplot_name.axis('off')
        subplot_name.table(
            cellText=couple_lst,
            cellLoc='left',
            loc='center'
        )


if __name__ == '__main__':

    class TestCounters(object):

        def __init__(self,
                     player_champ='jax'):

            """
            Values must NOT be assigned here.
            """

            self.player_champ = player_champ

            self.DELIMITER = '\n--------------------------------'
            self.filtered_stats_max = {'crit': 1., 'speed': None, 'att_speed': 2.5, 'cdr': 0.4}

            self.rotation_lst = None
            self.max_targets_dct = None
            self.selected_champions_dct = None
            self.champion_lvls_dct = None
            self.ability_lvls_dct = None
            self.initial_active_buffs = None
            self.initial_current_stats = None
            self.current_target_num = None
            self.items_lst = []
            self.selected_runes = None
            self.max_combat_time = None

        def set_up(self):

            self.selected_champions_dct = dict(
                player=self.player_champ,
                enemy_1='jax',
                enemy_2='jax',
                enemy_3='jax')

            self.champion_lvls_dct = dict(
                player=1,
                enemy_1=1,
                enemy_2=17,
                enemy_3=18
            )

            self.ability_lvls_dct = dict(
                q=5,
                w=5,
                e=5,
                r=3)

            self.max_targets_dct = {}

        def subclass_jax_actions(self):

            player_champ_name = self.selected_champions_dct['player']
            player_champ_module = __import__(player_champ_name)
            player_champ_tot_attr_class = getattr(player_champ_module, 'TotalChampionAttributes')

            class CombinerClass(player_champ_tot_attr_class, VisualRepresentation):

                def __init__(self,
                             rotation_lst,
                             max_targets_dct,
                             selected_champions_dct,
                             champion_lvls_dct,
                             ability_lvls_dct,
                             max_combat_time,
                             initial_active_buffs=None,
                             initial_current_stats=None,
                             items_lst=self.items_lst,
                             selected_runes=None):

                    VisualRepresentation.__init__(self,
                                                  rotation_lst=rotation_lst,
                                                  max_targets_dct=max_targets_dct,
                                                  selected_champions_dct=selected_champions_dct,
                                                  champion_lvls_dct=champion_lvls_dct,
                                                  ability_lvls_dct=ability_lvls_dct,
                                                  max_combat_time=max_combat_time,
                                                  initial_active_buffs=initial_active_buffs,
                                                  initial_current_stats=initial_current_stats,
                                                  items_lst=items_lst,
                                                  selected_runes=selected_runes)

                    player_champ_module.TotalChampionAttributes.__init__(self,
                                                                         ability_lvls_dct=ability_lvls_dct,
                                                                         tot_stats=self.request_stat,
                                                                         act_buffs=self.active_buffs,
                                                                         current_stats=self.current_stats,
                                                                         current_target=self.current_target,
                                                                         champion_lvls_dct=champion_lvls_dct,
                                                                         current_target_num=self.current_target_num)

            return CombinerClass

        def test_loop(self, rotation, use_runes=False):

            self.set_up()

            msg = self.DELIMITER

            self.rotation_lst = rotation

            if use_runes:
                self.selected_runes = dict(
                    red=dict(
                        ad_per_lvl=dict(
                            additive=2)))

            inst = self.subclass_jax_actions()(rotation_lst=self.rotation_lst,
                                               max_targets_dct=self.max_targets_dct,
                                               selected_champions_dct=self.selected_champions_dct,
                                               champion_lvls_dct=self.champion_lvls_dct,
                                               ability_lvls_dct=self.ability_lvls_dct,
                                               initial_active_buffs=self.initial_active_buffs,
                                               initial_current_stats=self.initial_current_stats,
                                               selected_runes=self.selected_runes,
                                               max_combat_time=self.max_combat_time)

            msg += '\nTesting method: combat_loop\n'
            msg += '\nrotation: %s\n' % inst.rotation_lst

            msg += 'player active_buffs: %s\n\n' % inst.active_buffs['player']

            # Runs loop.
            inst.combat_loop()

            msg += 'actions dict: %s\n' % sorted(inst.actions_dct)
            msg += 'actions dict: %s\n\n' % inst.actions_dct

            msg += 'active_buffs: %s\n' % inst.active_buffs
            msg += 'player att_speed: %s\n' % inst.request_stat(target_name='player', stat_name='att_speed')

            if use_runes:
                msg += 'used runes: %s\n' % inst.runes_buff()
                msg += 'player ad: %s\n' % inst.request_stat(target_name='player', stat_name='ad')

            msg += 'enemy_1: \nmax hp: %s, ' % inst.request_stat(target_name='enemy_1', stat_name='hp')
            msg += ('enemy_1 current_stats: %s \n'
                    'all current_stats: %s\n') % (inst.current_stats['enemy_1'], inst.current_stats)

            msg += '\nr_dmg_initiator: %s' % inst.r_dmg_initiator()

            msg += '\ndmg_history: %s' % inst.dmg_history

            msg += '\ntotal dmg types: %s' % inst.refined_dmg_history()

            msg += '\ntimes of death: %s' % inst.times_of_death()

            return msg

        def test_dmg_graphs(self, rotation_lst, item_lst):
            self.set_up()

            self.items_lst = item_lst

            inst = self.subclass_jax_actions()(rotation_lst=rotation_lst,
                                               max_targets_dct=self.max_targets_dct,
                                               selected_champions_dct=self.selected_champions_dct,
                                               champion_lvls_dct=self.champion_lvls_dct,
                                               max_combat_time=self.max_combat_time,
                                               ability_lvls_dct=self.ability_lvls_dct,
                                               initial_active_buffs=self.initial_active_buffs,
                                               initial_current_stats=self.initial_current_stats)

            inst.combat_loop()
            inst.add_dmg_history_tot()

            inst.subplot_pie_chart(plt.figure(1).add_subplot(222))
            inst.subplot_dmg_graph(plt.figure(1).add_subplot(221))
            inst.subplot_resource_vamp_lifesteal_graph(plt.figure(1).add_subplot(223))
            inst.subplot_table_of_setup(plt.figure(1).add_subplot(224))

            msg = '\nrotation: %s\n' % inst.rotation_lst
            msg += '\ntotal dmg types: %s' % inst.refined_dmg_history()
            msg += '\ntimes of death: %s' % inst.times_of_death()
            msg += '\nactions: %s' % sorted(inst.actions_dct)
            msg += '\ndps: %s' % inst.dps()
            msg += '\nmax mp: %s, current_mp: %s' % (inst.request_stat('player', 'mp'),
                                                     inst.current_stats['player']['current_mp'])

            msg += '\nlifesteal: %s, spellvamp: %s' % (inst.request_stat('player', 'lifesteal'),
                                                       inst.request_stat('player', 'spellvamp'))

            msg += '\nlifesteal history: %s' % inst.dmg_history['player']['lifesteal']

            msg += str(inst.active_buffs['player'])

            print(msg)

            return plt.show()

        def __repr__(self):

            msg = self.DELIMITER

            msg += self.test_loop(['w', 'AA'])
            msg += self.DELIMITER

            # At 3 AAs there should be more dmg from passive R.
            msg += self.test_loop(['AA', 'AA', 'AA'])
            msg += self.DELIMITER

            # Time between AAs should become progressively shorted up to 6 AAs because of att_speed increase.
            msg += self.test_loop(['AA', 'AA', 'AA', 'AA', 'AA', 'AA'])
            msg += self.DELIMITER

            # Action 'w' on its own does not cause dmg.
            msg += self.test_loop(['w', 'w'])
            msg += self.DELIMITER

            # AA after 'w' causes aa_dmg plus w_dmg.
            msg += self.test_loop(['w', 'AA'])
            msg += self.DELIMITER

            msg += self.test_loop(['w', 'AA', 'q', 'w', 'AA'])
            msg += self.DELIMITER

            msg += self.test_loop(['AA', 'AA', 'e'])
            msg += self.DELIMITER

            # When a target dies it switches to next target until all targets are dead.
            msg += self.test_loop(['AA', 'w', 'AA', 'AA', 'AA', 'AA', 'AA', 'AA', 'w', 'AA', 'AA', 'AA'])
            msg += self.DELIMITER

            # Since Jax's E is AoE it causes dmg to other targets as well.
            # Also, its total dmg is 3 times greater than single.
            msg += self.test_loop(['e'])
            msg += self.DELIMITER

            msg += self.test_loop(['e'], use_runes=True)
            msg += self.DELIMITER

            return msg

    #print(TestCounters())

    rot1 = ['q', 'AA', 'w', 'AA', 'AA', 'AA', 'AA', 'AA', 'AA', 'AA', 'w', 'AA', 'AA']
    rot2 = ['w', 'AA', 'e', 'AA', 'AA', 'AA']
    rot3 = ['AA', 'AA', 'AA']
    rot4 = ['AA']

    itemLst1 = []
    itemLst2 = ['gunblade']
    itemLst3 = ['gunblade', 'gunblade']

    TestCounters().test_dmg_graphs(rotation_lst=rot4, item_lst=itemLst1)

    # Crude time testing.
    import cProfile
    test_text = 'TestCounters().test_loop(rotation=rot1*4, use_runes=True)\n' * 100
    cProfile.run(test_text, sort='cumtime')

#rot1, itemLst3
#dps: 368.394550825117 (before bug/functionality fix/changes)
#dps: 360.32183952512594