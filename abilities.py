import buffs
import timers
import runes
import app_champions_base_stats
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


class EnemyTargetsDeadException(Exception):
    """
    To be used (and handled) when no other valid targets are available for an event application.
    """
    pass


class EventsGeneral(buffs.DeathAndRegen):

    NATURAL_REGEN_START_TIME = 0.5

    def __init__(self,
                 champion_lvls_dct,
                 selected_champions_dct,
                 max_targets_dct,
                 max_combat_time,
                 initial_active_buffs=None,
                 initial_current_stats=None,
                 items_lst=None):

        # (User defined dict containing number of targets affected by abilities.)
        self.max_targets_dct = max_targets_dct
        self.event_times = {}
        self.current_time = 0
        self.current_target = None
        # (Used to note that a periodic event might have been added between current events and last action.)
        self.intermediate_events_changed = None

        buffs.DeathAndRegen.__init__(self,
                                     current_time=self.current_time,
                                     selected_champions_dct=selected_champions_dct,
                                     champion_lvls_dct=champion_lvls_dct,
                                     max_combat_time=max_combat_time,
                                     initial_active_buffs=initial_active_buffs,
                                     initial_current_stats=initial_current_stats,
                                     items_lst=items_lst)

        self.resource_used = app_champions_base_stats.CHAMPION_BASE_STATS[selected_champions_dct['player']][
            'resource_used']

    def add_event_to_first_tar(self, effect_name, start_time):
        """
        Applies a dmg event to the first target.

        Modifies:
            event_times
        Returns:
            (None)
        """

        # If the event's time doesn't exist it creates it.
        if start_time not in self.event_times:
            self.event_times.update({start_time: {self.current_target: [effect_name]}})

        else:
            # If the time exists in the dictionary,
            # checks if the target is inside the time.
            if self.current_target in self.event_times[start_time]:
                self.event_times[start_time][self.current_target].append(effect_name)
            else:
                # If not, it adds the target as well.
                self.event_times[start_time].update({self.current_target: [effect_name]})

    def add_regenerations(self):
        """
        Adds hp5 (both event and buff) for all targets, and resource per 5 for player.

        Modifies:
            event_times
            active_buffs
        Returns:
            (None)
        """

        for self.current_target in self.all_target_names:
            # ENEMY
            if self.current_target != 'player':
                self.add_buff(buff_name='enemy_hp5_buff', tar_name=self.current_target)
                # HP5
                self.add_event_to_first_tar(effect_name='enemy_hp5_dmg',
                                            start_time=self.NATURAL_REGEN_START_TIME)

            # PLAYER
            else:
                self.add_buff(buff_name='player_hp5_buff', tar_name=self.current_target)
                # HP5
                self.add_event_to_first_tar(effect_name='player_hp5_dmg',
                                            start_time=self.NATURAL_REGEN_START_TIME)

                # RESOURCE
                regen_event_name = None
                if self.resource_used == 'energy':
                    regen_event_name = 'ep5_dmg'
                    self.add_buff(buff_name='ep5_buff', tar_name=self.current_target)

                elif self.resource_used == 'mp':
                    regen_event_name = 'mp5_dmg'
                    self.add_buff(buff_name='mp5_buff', tar_name=self.current_target)

                # Checks if player's resource can regenerate per 5.
                if regen_event_name:
                    self.add_event_to_first_tar(effect_name=regen_event_name,
                                                start_time=self.NATURAL_REGEN_START_TIME)

    def add_aoe_events(self, effect_name, start_time):
        """
        Adds an aoe dmg event to affected target. If all unaffected targets are dead raises exception.

        Modifies:
            event_times
            targets_already_hit
            current_target
        Returns:
            (None)
        Raises:
            EnemyTargetsDeadException: No viable targets exist.
        """

        # NEXT TARGET
        # If next target is None (because no valid targets exist) the loop breaks.
        self.next_target(enemy_tar_names=self.enemy_target_names)
        if self.current_target is None:
            raise EnemyTargetsDeadException

        self.targets_already_hit += 1

        # ADD EVENT
        # Checks if the target is inside the time.
        if self.current_target in self.event_times[start_time]:
            self.event_times[start_time][self.current_target].append(effect_name)
        else:
            self.event_times[start_time].update({self.current_target: [effect_name]})

    def add_events(self, effect_name, start_time):
        """
        Adds a dmg event (e.g. Brand W) to all affected targets.

        Modifies:
            event_times
            targets_already_hit
            current_target
        Structure:
            event_times: {0.: {'player': ['w_dmg',],},}
        Returns:
            (None)
        """

        effect_dct = getattr(self, effect_name)()
        # Changes event start if needed.
        if 'delay' in effect_dct:
            start_time += effect_dct['delay']

        # Adds event to first target.
        self.add_event_to_first_tar(effect_name=effect_name, start_time=start_time)

        self.targets_already_hit = 1

        # AOE DMG
        # Aoe dmg has 'max_targets' in dmg dct. It can also additionally have externally set max_targets.
        # Tries to add events to targets.
        try:
            # External max targets.
            if effect_name in self.max_targets_dct:

                # While the last target number is less than max targets, adds event.
                while self.targets_already_hit < self.max_targets_dct[effect_name]:
                    self.add_aoe_events(effect_name=effect_name, start_time=start_time)

            # If it has max_targets (implying it's aoe).
            elif 'max_targets' in effect_dct:
                if effect_dct['max_targets'] == 'unlimited':

                    # While the last target number is less than max targets, adds event.
                    while self.targets_already_hit < len(self.enemy_target_names):
                        self.add_aoe_events(effect_name=effect_name, start_time=start_time)

                else:
                    while self.targets_already_hit < effect_dct['max_targets']:
                        self.add_aoe_events(effect_name=effect_name, start_time=start_time)

        except EnemyTargetsDeadException:
            pass

    def refresh_periodic_event(self, dmg_name, tar_name, dmg_dct):
        """
        Re-adds a periodic effect and notes the change.

        Refreshed only if buff ending time is higher than event ending time,
        or if it's a permanent buff.

        Returns:
            (None)
        """

        tar_act_buffs = self.active_buffs[tar_name]
        buff_name = dmg_name[:-3]+'buff'

        # Checks dot's buff.
        if buff_name in tar_act_buffs:
            if ((tar_act_buffs[buff_name]['ending_time'] == 'permanent') or
                    (tar_act_buffs[buff_name]['ending_time'] > self.current_time)):

                self.add_events(effect_name=dmg_name,
                                start_time=self.current_time + dmg_dct['period'])

                self.intermediate_events_changed = True

    def add_next_periodic_event(self, tar_name, dmg_name, only_temporary=False):
        """
        Adds next periodic tick.

        Checks active_buffs for the dot buff, then adds event if the buff still exists.

        Modifies:
            event_times
        Args:
            only_temporary: (boolean) Used for filtering out permanent dots (e.g. sunfire) if needed.
        Returns:
            (None)
        """

        dmg_dct = getattr(self, dmg_name)()

        # Checks if event is periodic.
        if dmg_dct['dot'] is True:
            # If only temporary periodic events are re-applied..
            if only_temporary:
                # ..checks if their duration is not permanent.
                if dmg_dct['duration'] != 'permanent':
                    self.refresh_periodic_event(dmg_name=dmg_name, tar_name=tar_name, dmg_dct=dmg_dct)

            # Otherwise checks both permanent and temporary dots.
            else:
                self.refresh_periodic_event(dmg_name=dmg_name, tar_name=tar_name, dmg_dct=dmg_dct)


class Actions(EventsGeneral, timers.Timers, runes.RunesFinal):

    AA_COOLDOWN = 0.4   # TODO: replace functionality with 'wind_up'

    def __init__(self,
                 rotation_lst,
                 max_targets_dct,
                 selected_champions_dct,
                 champion_lvls_dct,
                 ability_lvls_dct,
                 max_combat_time,
                 items_lst=None,
                 initial_active_buffs=None,
                 initial_current_stats=None,
                 selected_runes=None):

        self.rotation_lst = rotation_lst
        self.current_target_num = None
        self.everyone_dead = None
        self.total_movement = 0

        runes.RunesFinal.__init__(self,
                                  player_lvl=champion_lvls_dct['player'],
                                  selected_runes=selected_runes)

        EventsGeneral.__init__(self,
                               champion_lvls_dct=champion_lvls_dct,
                               selected_champions_dct=selected_champions_dct,
                               max_targets_dct=max_targets_dct,
                               max_combat_time=max_combat_time,
                               initial_active_buffs=initial_active_buffs,
                               initial_current_stats=initial_current_stats,
                               items_lst=items_lst)

        timers.Timers.__init__(self,
                               ability_lvls_dct=ability_lvls_dct)

    # COSTS
    def ability_cost_dct(self, action_name):
        """
        Creates a dict containing each resource used,
        it's value cost, buff name cost and number of buff's stacks.

        Not to be used for abilities with toggled cost.

        Returns:
            (dict)
        """

        cost_dct = {}

        # ACTIVATED ABILITIES
        if action_name in 'qwer':
            # NORMAL COST
            ability_stats_dct = self.request_ability_stats(ability_name=action_name)
            resource_cost_type = ability_stats_dct['general']['resource_cost_type']

            # Check if ability has a fixed cost,
            # or one that scales per ability_lvl,
            # or no resource cost (none of the if's are true).
            if 'fixed_cost' in ability_stats_dct['general']:
                resource_cost = ability_stats_dct['general']['fixed_cost']
                cost_dct = {resource_cost_type: resource_cost}
            elif 'cost_tpl' in ability_stats_dct['general']:
                resource_cost = ability_stats_dct['general']['cost_tpl'][self.ability_lvls_dct[action_name]-1]
                cost_dct = {resource_cost_type: resource_cost}

            # STACK COST
            # (e.g. Akali R stacks)
            if 'stack_cost' in ability_stats_dct['general']:
                stack_name = ability_stats_dct['general']['stack_cost']
                cost_dct.update({stack_name: ability_stats_dct['general']['stack_cost'][stack_name]})

        return cost_dct

    def cost_sufficiency(self, action_name):
        """
        Determines whether there are enough resources to cast the action or not.

        Returns:
            (boolean)
        """

        sufficiency = True

        for cost_name in self.ability_cost_dct(action_name):
            cost_value = self.ability_cost_dct(action_name)[cost_name]

            if cost_name in ('mp', 'energy', 'hp'):
                if self.current_stats['player']['current_'+cost_name] < cost_value:
                    sufficiency = False

            else:
                if cost_name not in self.active_buffs['player']:
                    sufficiency = False

        return sufficiency

    def apply_action_cost(self, action_name):
        """
        Deducts the cost of an action (resource and/or buff stack).

        Modifies:
            current_stats['player']
            active_buffs
        Returns:
            (None)
        """

        for cost_name in self.ability_cost_dct(action_name):
            cost_value = self.ability_cost_dct(action_name)[cost_name]

            if cost_name in ('mp', 'energy', 'hp', 'rage'):
                self.current_stats['player']['current_' + cost_name] -= cost_value

            else:
                del self.active_buffs['player'][cost_name]

    # MOVEMENT
    def between_action_walking(self):
        """
        Calculates movement between actions and adds them to distance player moved.

        Returns:
            (None)
        """

        sorted_action_times = sorted(self.actions_dct, reverse=True)

        # Last action's cast start.
        upper_limit = sorted_action_times[0]

        # Checks if there was only one action (therefor lower limit should be 0)
        if len(sorted_action_times) == 1:
            pre_last_action_start = 0
        else:
            pre_last_action_start = sorted_action_times[1]

        pre_last_action_name = self.actions_dct[pre_last_action_start]['action_name']

        # Movement starts after cast (or channelling) ends,
        # unless action allows movement during cast.
        if ((pre_last_action_name != 'AA') and
                (self.request_ability_stats(ability_name=pre_last_action_name)['general']['move_while_casting'] is True)):
            lower_limit = pre_last_action_start

        elif 'channel_end' in self.actions_dct[pre_last_action_start]:
            lower_limit = self.actions_dct[pre_last_action_start]['channel_end']

        else:
            lower_limit = self.actions_dct[pre_last_action_start]['cast_end']

        # Calculates and adds meaningful values.
        move_value = (upper_limit-lower_limit) * self.request_stat(target_name='player', stat_name='move_speed')
        if move_value > 0.1:
            self.total_movement += move_value

    def add_action_dash(self):
        """
        Adds last action's dash distance.

        Returns:
            (None)
        """
        last_action_time = sorted(self.actions_dct, reverse=True)[0]
        last_action_name = self.actions_dct[last_action_time]['action_name']

        # Abilities
        if last_action_name in 'qwer':
            ability_gen_stats = self.request_ability_stats(ability_name=last_action_name)['general']

            self.total_movement += ability_gen_stats['dashed_distance']

    def add_kalista_dash(self):
        """
        Adds Kalista's dash after an AA.
        
        Returns:
            (None)
        """

        if self.selected_champions_dct['player'] == 'kalista':
            self.total_movement += app_champions_base_stats.CHAMPION_BASE_STATS['kalista']['dashed_distance_on_aa']

    # ABILITIES
    def reset_aa_cd(self, action_name):
        """
        Removes an AA's cd after an AA-resetting ability is casted.

        Modifies:
            actions_dict
        Returns:
            (None)
        """

        if self.request_ability_stats(ability_name=action_name)['general']['resets_aa']:

            for action_time in sorted(self.actions_dct, reverse=True):

                # If an AA has been casted earlier...
                if 'AA' == self.actions_dct[action_time]['action_name']:
                    # ..sets its cd_end to current_time.
                    self.actions_dct[action_time]['cd_end'] = self.current_time
                    break

    def action_cast_start(self, action_name):
        """
        Calculates cast_start of an action, based on other actions' cast_end and this action's cd.

        Returns:
            (float)
        """

        def end_name(action_dct):
            """
            Returns:
                (str)
            """
            if 'channel_end' in action_dct:
                string = 'channel_end'
            else:
                string = 'cast_end'
            return string

        cast_start = self.current_time

        # If a previous action exists...
        if self.actions_dct:

            casted_earlier = None

            # ..checks all actions inside dict from last to first.
            for action_time in sorted(self.actions_dct, reverse=True):

                name = end_name(action_dct=self.actions_dct[action_time])

                # If the examined action has been casted earlier...
                if action_name == self.actions_dct[action_time]['action_name']:

                    # ..compare which ends last;
                    # the examined action's cd or or the last action's cast end.
                    cast_start = max(
                        self.actions_dct[action_time]['cd_end'],
                        # (tiny amount added to avoid action overwriting)
                        self.actions_dct[max(self.actions_dct)][name]) + 0.00000001

                    casted_earlier = True
                    break

            # If it hasn't been casted earlier, it starts when last action's cast ends.
            if not casted_earlier:
                last_action_time = max(self.actions_dct)
                name = end_name(action_dct=self.actions_dct[last_action_time])
                # (tiny amount added to avoid action overwriting)
                cast_start = self.actions_dct[last_action_time][name] + 0.00000001

        return cast_start

    def add_new_action(self, action_name):
        """
        Inserts a new action.

        First dictionary has current action's cast start as keyword,
        and a dictionary as value.

        The second dictionary contains the time the action's animation ends (cast_end),
        the time the action's application ends, the action's name and the time its cooldown ends.

        Modifies:
            actions_dct
        Returns:
            (None)
        """

        # (cast_start is the moment the action is 'clicked')
        cast_start = self.action_cast_start(action_name=action_name)

        # CHAMPION ABILITIES
        if action_name in 'qwer':
            self.actions_dct.update(
                {cast_start: dict(
                    cast_end=self.cast_end(action_name, cast_start),
                    action_name=action_name,)})

            # (cd_end is applied later since it requires cast_end)
            self.actions_dct[cast_start].update(dict(
                cd_end=self.ability_cd_end(ability_name=action_name,
                                           cast_start=cast_start,
                                           stats_function=self.request_stat,
                                           actions_dct=self.actions_dct)))

            if 'channel_time' in self.request_ability_stats(ability_name=action_name)['general']:
                self.actions_dct[cast_start].update(dict(
                    channel_end=self.channel_end(ability_name=action_name,
                                                 action_cast_start=cast_start)))

            # Checks if ability resets AA's cd_end, and applies it.
            self.reset_aa_cd(action_name=action_name)
            # Movement
            self.add_action_dash()

        # AAs
        elif action_name == 'AA':
            self.actions_dct.update({
                cast_start: dict(
                    cd_end=cast_start + 1./self.request_stat(target_name='player', stat_name='att_speed'),
                    action_name=action_name,
                    cast_end=cast_start + self.AA_COOLDOWN)})

            self.add_kalista_dash()

        # ITEM ACTIVES OR SUMMONER SPELLS
        else:
            # (cast_end is the same as cast_start)
            # (item actives and summoner spells have too high cooldowns, so they are set to a high value)
            self.actions_dct.update({cast_start: dict(
                cast_end=cast_start,
                cd_end=360,
                action_name=action_name)})

    def add_buff(self, buff_name, tar_name, stack_increment=1, initial_stacks_increment=1):
        """
        (Overrides previous method)

        Additionally, checks if buff applied is a dot buff and adds periodic event (unless dot already active).

        Returns:
            (None)
        """

        # Checks if dot already applied.
        new_periodic_event = True
        if buff_name in self.active_buffs[tar_name]:
            new_periodic_event = False

        super().add_buff(buff_name=buff_name, tar_name=tar_name,
                         stack_increment=stack_increment, initial_stacks_increment=initial_stacks_increment)

        # If it's a new dot..
        if new_periodic_event:
            # If the buff is a dot, applies event as well.
            if 'period' in getattr(self, buff_name)():

                first_tick = self.first_dot_tick(current_time=self.current_time, ability_name=buff_name)

                self.add_events(effect_name=buff_name, start_time=first_tick)

    def remove_buff_on_action(self, buff_name):
        """
        Removes a player's buff on_hit or on_cast,
        and starts corresponding action's cd if buff delays the cd start.

        (e.g. Jax w_buff delays start of W cd)

        Modifies:
            active_buffs
            actions_dict
        Return:
            (None)
        """

        buff_dct = getattr(self, buff_name)()

        # Checks if buff delays the start of an action's cd.
        if buff_dct['prohibit_cd_start']:
            prohibited_ability_dc = buff_dct['prohibit_cd_start']

            # Finds the affected action..
            for action_time in sorted(self.actions_dct, reverse=True):
                if self.actions_dct[action_time]['action_name'] == prohibited_ability_dc:

                    # .. and applies the new cd.
                    self.actions_dct[action_time]['cd_end'] = self.ability_cooldown(
                        ability_name=self.actions_dct[action_time]['action_name'],
                        stats_function=self.request_stat)

                    break

        # Removes buff.
        del self.active_buffs['player'][buff_name]

    def apply_on_hit_effects(self):
        """
        Applies on hit effects.

        On hit effects can be dmg and buffs application, or buff removal.

        Iterates throughout all active buffs, and applies:
            -on_hit dmg (e.g. Warwick's innate dmg),
            -on_hit buffs (e.g. Black Cleaver armor reduction),
            -and finally removes buffs that are removed on hit.


        Modifies:
            active_buffs
            event_times
        Returns:
            (None)
        """

        for buff_name in frozenset(self.active_buffs['player']):
            buff_dct = getattr(self, buff_name)()

            if 'on_hit' in buff_dct:

                # DMG CAUSED ON HIT.
                for dmg_name in buff_dct['on_hit']['cause_dmg']:

                    self.switch_to_first_alive_enemy()
                    self.add_events(effect_name=dmg_name, start_time=self.current_time)

                # BUFFS APPLIED ON HIT.
                for buff_applied_on_hit in buff_dct['on_hit']['apply_buff']:

                    self.add_buff(buff_name=buff_applied_on_hit,
                                  tar_name=getattr(self, buff_applied_on_hit)()['target'])

                # BUFFS REMOVED ON HIT.
                for buff_removed_on_hit in buff_dct['on_hit']['remove_buff']:

                    # Checks if the buff exists on the player.
                    if buff_removed_on_hit in self.active_buffs['player']:
                        self.remove_buff_on_action(buff_name=buff_removed_on_hit)

                    # Checks if the buff exists on current enemy target.
                    elif buff_removed_on_hit in self.active_buffs[self.current_target]:
                        del self.active_buffs[self.current_target][buff_removed_on_hit]

    def apply_aa_effects(self, current_time):
        """
        Applies AA effects from buffs and AA dmg event.

        Modifies:
            active_buffs
            event_times
        Returns:
            (None)
        """

        # Applies on_hit effects.
        self.apply_on_hit_effects()

        # Applies direct dmg.
        self.switch_to_first_alive_enemy()
        self.add_events('aa_dmg', current_time)

    def apply_ability_actives_on_tar(self, tar_type, effects_dct, action_name):
        """
        Applies an action's effect on target, if action has actives.

        Target is automatically chosen.

        Args:
            tar_type: (str) 'player' or 'enemy'
        Returns:
            (None)
        """

        # Checks if the ability has any active effects.
        if 'actives' in effects_dct[action_name][tar_type]:
            # BUFFS
            if 'buffs' in effects_dct[action_name][tar_type]['actives']:
                for buff_name in effects_dct[action_name][tar_type]['actives']['buffs']:
                    self.add_buff(buff_name=buff_name, tar_name=self.current_target)

            # DMG
            if 'dmg' in effects_dct[action_name][tar_type]['actives']:
                for dmg_name in effects_dct[action_name][tar_type]['actives']['dmg']:
                    self.add_events(effect_name=dmg_name, start_time=self.current_time)

            # BUFF REMOVAL
            if 'remove_buff' in effects_dct[action_name][tar_type]['actives']:
                for buff_name_to_remove in effects_dct[action_name][tar_type]['actives']['remove_buff']:
                    del self.active_buffs[tar_type][buff_name_to_remove]

    def apply_ability_effects(self, action_name, effects_dct):
        """
        Applies an action's effects.

        Used for abilities, item actives or summoner actives.

        Chooses the first viable enemy for actives on enemies.

        Modifies:
            active_buffs
            event_times
            current_target
        Returns:
            (None)
        """

        if 'player' in effects_dct[action_name]:
            self.current_target = 'player'

            self.apply_ability_actives_on_tar(tar_type='player', effects_dct=effects_dct, action_name=action_name)

        if 'enemy' in effects_dct[action_name]:

            self.switch_to_first_alive_enemy()

            self.apply_ability_actives_on_tar(tar_type='enemy', effects_dct=effects_dct, action_name=action_name)

    def apply_action_effects(self, action_name, abilities_effects, items_effects):
        """
        Applies an action's effects (buffs, dmg, buff removal).

        Modifies:
            active_buffs
            event_times
        Returns:
            (None)
        """

        # AA
        if action_name == 'AA':
            # ..applies AA physical dmg, and applies (or removes) on_hit buffs and dmg.
            self.apply_aa_effects(current_time=self.current_time)

        # ABILITY
        elif action_name in 'qwer':
            self.apply_ability_effects(action_name=action_name,
                                       effects_dct=abilities_effects)

        # ITEM ACTIVE - SUMMONER SPELL
        else:
            self.apply_ability_effects(action_name=action_name,
                                       effects_dct=items_effects)

    def apply_pre_action_events(self):
        """
        Applies all events preceding last action's application start.

        If a periodic event is refreshed and ticks before the last action,
        then event_times changes and is checked again.
        If all targets die, the loop stops.

        Modifies:
            current_time
            event_times
            active_buffs
            intermediate_events_changed
        Returns:
            (None)
        """

        self.intermediate_events_changed = True

        while self.intermediate_events_changed:

            self.intermediate_events_changed = False

            # If for loop ends with new events being added,
            # then intermediate_events_changed will be set to true,
            # and the for loop will repeat.          

            initial_events = sorted(self.event_times)

            # EVENTS BEFORE ACTION
            for event in initial_events:
                # Checks if event's application time exceeds last action's application start.
                # (cast_end and application start are different for channelled abilities)
                if event <= self.actions_dct[max(self.actions_dct)]['cast_end']:

                    # (must change to ensure buffs are checked)
                    self.current_time = event

                    self.remove_expired_buffs()

                    # Applies all dmg effects for all targets.
                    for self.current_target in self.event_times[self.current_time]:
                        for dmg_name in self.event_times[self.current_time][self.current_target]:
                            self.apply_dmg_or_heal(dmg_name, self.current_target)
                            self.add_next_periodic_event(tar_name=self.current_target, dmg_name=dmg_name)

                        # After dmg has been applied checks if target has died.
                        self.apply_death(tar_name=self.current_target)

                    # Deletes the event after it's applied.
                    del self.event_times[self.current_time]

                    # If new events are added it exits and checks them all over again.
                    if self.intermediate_events_changed:
                        break

                # EXIT INNER LOOP
                # Exits loop after all events prior to an action are applied.
                else:
                    break

                # DEATHS
                self.everyone_dead = True
                # Checks if alive targets exist.
                for tar_name in self.champion_lvls_dct:
                    if tar_name != 'player':
                        if 'dead_buff' not in self.active_buffs[tar_name]:
                            self.everyone_dead = False
                            break

                # EXIT METHOD
                # If everyone has died, stops applying following events.
                if self.everyone_dead:
                    # TODO: check if "return" can replace below code
                    # (break outer loop)
                    self.intermediate_events_changed = False
                    # (break inner loop)
                    break

    def apply_all_actions(self):
        """
        Applies all actions, and events in between,
        until everyone is dead or the max_time is exceeded.

        NOTE: To be overridden by a method that chooses "preferred" action.

        Returns:
            (None)
        """

        for new_action in self.rotation_lst:

            # (used for champions that action application is affected by existing buffs)
            self.remove_expired_buffs()

            # Checks if action meets the cost requirements.
            if self.cost_sufficiency(action_name=new_action):

                self.apply_action_cost(action_name=new_action)

                self.add_new_action(new_action)

                # (movement distance)
                self.between_action_walking()

                self.apply_pre_action_events()

                # If everyone died, stops applying actions as well.
                if self.everyone_dead:
                    break

                # Sets current_time to current action's cast end.
                self.current_time = self.actions_dct[max(self.actions_dct)]['cast_end']

                # If max time exceeded, exits loop.
                if self.max_combat_time:
                    if self.current_time > self.max_combat_time:
                        break

                # After previous events are applied, applies action effects.
                self.apply_action_effects(action_name=self.actions_dct[max(self.actions_dct)]['action_name'],
                                          abilities_effects=self.abilities_effects(),
                                          items_effects=self.items_effects)

            # If the cost is too high, action is skipped.
            else:
                pass  # TODO: Make it a new method (ignore mode, wait mode)

    def apply_events_after_actions(self, fully_apply_dots=False):
        """
        Applies events after all actions have finished.

        Non permanent dots are refreshed and their events fully applied.
        Applies death to each viable target.

        Modifies:
            current_time
            event_times
            active_buffs
            intermediate_events_changed
        Returns:
            (None)
        """

        self.intermediate_events_changed = True

        while self.intermediate_events_changed:

            # If for loop ends with new events being added,
            # then 'self.intermediate_events_changed' will be set to true,
            # and the for loop will repeat.
            # Above process will repeat until all events have been marked as applied.
            self.intermediate_events_changed = False

            initial_events = sorted(self.event_times)

            for event in initial_events:

                # (must change to ensure buffs are checked)
                self.current_time = event

                self.remove_expired_buffs()

                # Applies all dmg effects to alive targets.
                for self.current_target in self.event_times[self.current_time]:
                    if self.current_stats[self.current_target]['current_hp'] > 0:
                        for dmg_name in self.event_times[self.current_time][self.current_target]:
                            self.apply_dmg_or_heal(dmg_name=dmg_name, target_name=self.current_target)

                            # Extends dots.
                            if fully_apply_dots:
                                self.add_next_periodic_event(tar_name=self.current_target,
                                                             dmg_name=dmg_name,
                                                             only_temporary=True)
        # DEATHS
        for tar_name in self.enemy_target_names:
            self.apply_death(tar_name=tar_name)

    def combat_loop(self):
        """
        Returns:
            (None)
        """

        self.current_time = 0

        # Adds runes buff.
        self.add_buff(buff_name='runes_buff', tar_name='player')

        # Adds hp5 and mp5.
        self.add_regenerations()

        # Adds passive buffs from abilities.
        self.add_passive_buffs(self.abilities_effects(), self.ability_lvls_dct)

        # Stores precombat stats.
        self.note_pre_combat_stats_in_results()

        # Applies actions or events based on which occurs first.
        self.apply_all_actions()

        # Applies events after all actions have finished.
        self.apply_events_after_actions()

        # Stores postcombat stats.
        self.note_dmg_totals_in_results()
        self.note_post_combat_stats_in_results()


class VisualRepresentation(Actions):

    PLAYER_STATS_DISPLAYED = ('ap', 'ad', 'armor', 'mr', 'hp', 'mp', 'att_speed')
    ENEMY_STATS_DISPLAYED = ('armor', 'mr', 'physical_dmg_taken', 'magic_dmg_taken',)

    def __init__(self,
                 rotation_lst,
                 max_targets_dct,
                 selected_champions_dct,
                 champion_lvls_dct,
                 ability_lvls_dct,
                 max_combat_time,
                 items_lst=None,
                 initial_active_buffs=None,
                 initial_current_stats=None,
                 selected_runes=None):

        Actions.__init__(self,
                         rotation_lst=rotation_lst,
                         max_targets_dct=max_targets_dct,
                         selected_champions_dct=selected_champions_dct,
                         champion_lvls_dct=champion_lvls_dct,
                         ability_lvls_dct=ability_lvls_dct,
                         max_combat_time=max_combat_time,
                         items_lst=items_lst,
                         initial_active_buffs=initial_active_buffs,
                         initial_current_stats=initial_current_stats,
                         selected_runes=selected_runes)

    def subplot_pie_chart_dmg_types(self, subplot_name):

        dmg_values = []
        slice_names = []

        for dmg_total_name in ('total_physical', 'total_magic', 'total_true'):

            # Filters out 0 value dmg.
            if self.combat_results['player'][dmg_total_name] > 0:

                slice_names.append(dmg_total_name)
                dmg_values.append(self.combat_results['player'][dmg_total_name])

        subplot_name.pie(x=dmg_values, labels=slice_names, autopct='%1.1f%%')

    def subplot_pie_chart_sources(self, subplot_name):

        dmg_values = []
        slice_names = []

        for source_name in sorted(self.combat_results['player']['source']):

            # Filters out 0 value dmg.
            if self.combat_results['player']['source'][source_name] > 0:

                slice_names.append(source_name)
                dmg_values.append(self.combat_results['player']['source'][source_name])

        subplot_name.pie(x=dmg_values, labels=slice_names, autopct='%1.1f%%')

    def add_actions_on_plot(self, subplot_name, annotated=True):
        # ACTIONS IN PLOT
        x_actions = []
        y_actions = []
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

            # ANNOTATE
            if annotated is True:
                subplot_name.annotate(self.actions_dct[x_var]['action_name'], xy=(x_var, -70 + higher_y), color='grey')

            previous_action_name_x = x_var

            # Action vertical lines
            plt.axvline(x=x_var, color='grey', linestyle='dashed', alpha=0.6)

    def subplot_dmg_graph(self, subplot_name):

        subplot_name.grid(b=True)

        # Line at y=0, and at x=0.
        plt.axhline(y=0, color='black')
        plt.axvline(x=0, color='black')

        plt.ylabel('hp')

        color_counter_var = 0
        color_lst = ('b', 'g', 'y', 'r')

        # Creates graph for each target.
        for tar_name in self.enemy_target_names:

            hp_change_times = sorted(self.combat_history[tar_name]['current_hp'])
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

                # (x values for same-height-points cluster)
                x_area_lst = [i for i in range(int(x_1 * 100), int((event_time + 0.01) * 100))]

                for x_element in x_area_lst:
                    x_values.append(x_element/100)
                    y_values.append(current_hp)

                current_hp = self.combat_history[tar_name]['current_hp'][event_time]
                x_1 = event_time

            if hp_change_times:
                # When events finish, adds one last point so that last event cluster is included.
                x_values.append(hp_change_times[-1])
                y_values.append(current_hp)

            subplot_name.plot(x_values, y_values, color=color_lst[color_counter_var], alpha=0.7)
            color_counter_var += 1

        plt.legend(prop={'size': 10},
                   bbox_to_anchor=(1.0, 1),
                   loc=2,)

        self.add_actions_on_plot(subplot_name=subplot_name, annotated=True)

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

            for event_time in sorted(self.combat_history['player'][examined]):
                x_val.append(event_time)
                y_val.append(self.combat_history['player'][examined][event_time])

            subplot_name.plot(x_val, y_val, color=stat_color[examined], marker='.', label=examined)

        plt.legend(prop={'size': 10},
                   bbox_to_anchor=(1.01, 1),
                   loc=2,)

        self.add_actions_on_plot(subplot_name=subplot_name, annotated=False)

    def subplot_player_stats_table(self, subplot_name):
        """
        Subplots player's pre and post combat stats.

        Stat values are rounded.

        Returns:
            (None)
        """

        table_lst = [('PLAYER STATS', 'PRE', 'POST'), ]

        # Creates lines.
        for stat_name in self.PLAYER_STATS_DISPLAYED:

            precombat_value = self.combat_results['player']['pre_combat_stats'][stat_name]
            precombat_value = round(precombat_value, 4)

            postcombat_value = self.combat_results['player']['post_combat_stats'][stat_name]
            postcombat_value = round(postcombat_value, 4)

            line_tpl = (stat_name+': ', precombat_value, postcombat_value)

            # Inserts in data to be displayed
            table_lst.append(line_tpl)

        subplot_name.axis('off')
        subplot_name.table(
            cellText=table_lst,
            cellLoc='left',
            loc='center').auto_set_font_size(False)

    def subplot_enemy_stats_table(self, subplot_name):
        """
        Subplots player's pre combat stats.

        Stat values are rounded.

        Returns:
            (None)
        """

        table_lst = []

        for tar_name in self.enemy_target_names:
            tar_lvl = self.champion_lvls_dct[tar_name]
            tar_champ = self.selected_champions_dct[tar_name]
            table_lst.append(('%s' % tar_name.upper(), ''))
            table_lst.append((tar_champ.upper(), 'Lvl: %s' % tar_lvl))

            # Creates lines.
            for stat_name in self.ENEMY_STATS_DISPLAYED:

                precombat_value = self.combat_results[tar_name]['pre_combat_stats'][stat_name]
                precombat_value = round(precombat_value, 4)

                line_tpl = (stat_name+': ', precombat_value)

                # Inserts in data to be displayed
                table_lst.append(line_tpl)

        subplot_name.axis('off')
        subplot_name.table(
            cellText=table_lst,
            cellLoc='left',
            loc='center').auto_set_font_size(False)

    def subplot_preset_and_results_table(self, subplot_name):

        # Rotation
        table_lst = [('ROTATION',), (self.rotation_lst,), ('DPS',)]

        # Dps
        dps_value = self.combat_results['player']['dps']
        # (too short combat time results in string dps)
        if type(dps_value) is not str:
            dps_value = round(dps_value, 1)
        table_lst.append((dps_value,))

        # Movement
        table_lst.append(('MOVEMENT',))
        table_lst.append((int(self.total_movement),))

        subplot_name.axis('off')
        subplot_name.table(
            cellText=table_lst,
            cellLoc='left',
            loc='center').auto_set_font_size(False)

    def represent_results_visually(self):

        gs = gridspec.GridSpec(3, 3)

        # Graphs
        self.subplot_dmg_graph(subplot_name=plt.figure(1).add_subplot(gs[:1, :1]))
        self.subplot_resource_vamp_lifesteal_graph(subplot_name=plt.figure(1).add_subplot(gs[1:2, :1]))

        # Pies
        self.subplot_pie_chart_dmg_types(subplot_name=plt.figure(1).add_subplot(gs[:1, 1:2]))
        self.subplot_pie_chart_sources(subplot_name=plt.figure(1).add_subplot(gs[:1, 2:3]))

        # Tables
        self.subplot_player_stats_table(subplot_name=plt.figure(1).add_subplot(gs[2, :1]))
        self.subplot_enemy_stats_table(subplot_name=plt.figure(1).add_subplot(gs[2, 1:2]))
        self.subplot_preset_and_results_table(subplot_name=plt.figure(1).add_subplot(gs[2, 2:3]))


if __name__ == '__main__':

    class TestCounters(object):

        def __init__(self,
                     player_champ='jax'):

            """
            Values must NOT be assigned here.
            """

            self.player_champ = player_champ

            self.DELIMITER = '\n' + '-'*100
            self.filtered_stats_max = {'crit_chance': 1., 'speed': None, 'att_speed': 2.5, 'cdr': 0.4}

            self.rotation_lst = None
            self.max_targets_dct = None
            self.selected_champions_dct = None
            self.champion_lvls_dct = None
            self.ability_lvls_dct = None
            self.initial_active_buffs = None
            self.initial_current_stats = None
            self.current_target_num = None
            self.items_lst = ['gunblade', 'gunblade']
            self.selected_runes = None
            self.max_combat_time = None

        def set_up(self):

            self.selected_champions_dct = dict(
                player=self.player_champ,
                enemy_1='jax',
                enemy_2='jax',
                enemy_3='jax')

            self.champion_lvls_dct = dict(
                player=18,
                enemy_1=18,
                enemy_2=17,
                enemy_3=16
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
                                                                         req_stats_func=self.request_stat,
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

            msg += '\ncombat_history: %s' % inst.combat_history

            msg += '\ntotal dmg types: %s' % inst.refined_combat_history()

            msg += '\ntimes of death: %s' % inst.times_of_death()

            msg += '\ntotal movement distance: %s' % str(inst.total_movement)

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
            inst.add_dmg_tot_history()

            inst.represent_results_visually()

            msg = '\nrotation: %s\n' % inst.rotation_lst
            msg += '\ntotal dmg types: %s' % inst.refined_combat_history()
            msg += '\ntimes of death: %s' % inst.times_of_death()
            msg += '\nactions: %s' % sorted(inst.actions_dct)
            msg += '\ndps: %s' % inst.dps()
            msg += '\nmax mp: %s, current_mp: %s' % (inst.request_stat('player', 'mp'),
                                                     inst.current_stats['player']['current_mp'])

            msg += '\nlifesteal: %s, spellvamp: %s' % (inst.request_stat('player', 'lifesteal'),
                                                       inst.request_stat('player', 'spellvamp'))

            msg += '\nlifesteal history: %s' % inst.combat_history['player']['lifesteal']

            msg += '\ntotal movement distance: %s' % str(inst.total_movement)

            del inst.combat_results['player']['pre_combat_stats']
            del inst.combat_results['player']['post_combat_stats']
            msg += '\nhistory: %s' % inst.combat_history['enemy_1']['current_hp']

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

            # Since Jax's E is AoE it causes dmg to other targets as well.
            # Also, its total dmg is 3 times greater than single.
            msg += self.test_loop(['e'])
            msg += self.DELIMITER

            msg += self.test_loop(['e'], use_runes=True)
            msg += self.DELIMITER

            # When a target dies it switches to next target until all targets are dead.
            msg += self.test_loop(['AA', 'w', 'AA', 'AA', 'AA', 'AA', 'AA', 'AA', 'w', 'AA', 'AA', 'AA'])
            msg += self.DELIMITER

            return msg

    print(TestCounters())

    rot1 = ['e', 'r', 'q', 'AA', 'w', 'AA', 'AA', 'gunblade', 'AA', 'AA', 'AA', 'AA', 'AA', 'w', 'AA', 'AA',
            'AA', 'AA', 'w', 'AA', 'q']
    rot2 = ['w', 'AA', 'e', 'AA', 'AA', 'AA']
    rot3 = ['AA', 'AA', 'AA']
    rot4 = ['AA']
    rot5 = ['e', 'e']
    rot6 = ['q', 'AA']

    itemLst0 = []
    itemLst1 = ['gunblade']
    itemLst2 = ['gunblade', 'gunblade']

    run_graph_test = True
    if run_graph_test:
        TestCounters().test_dmg_graphs(rotation_lst=rot1, item_lst=itemLst2)

    run_time_test = True
    if run_time_test:
        # Crude time testing.
        import cProfile
        test_text = 'TestCounters().test_loop(rotation=rot1, use_runes=True)\n'*1000
        cProfile.run(test_text, 'cprof_results', sort='cumtime')

        import pstats
        results_run = pstats.Stats('cprof_results').sort_stats('cumtime')
        results_run.strip_dirs().sort_stats('cumtime').print_stats(5)
        # print(results_run.strip_dirs().sort_stats('cumtime').stats)


# rot1, itemLst2
# dps: 331.07415420245394 (after changing dps method)
# dps: 338.4234113818222 (unexpected change, after changing bonus_ad method to get stats by 'evaluate' instead of direct)
# dps: 406.06856388086914 (rotation and targets changed)
# dps: 414.08610981856975 (rotation and targets changed) 1.1sec / 100 rotations
# dps: 414.1, 2434 movement, 1.1sec / 100 rotations
