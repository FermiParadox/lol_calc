class NewAbilities(object):
    def effect_applier(self):
        # For each action...
        for current_time in event_times:

            action_name = actions_dct[current_time]['action_name']        # Shorter for clarity

            # If the action is an AA...
            if action_name == 'AA':

                #...for each target in active_buffs dict...
                for target in active_buffs:

                    if target == 'player':
                        # ...applies each player-targeted on_hit effect.
                        for buff_name in on_hit_buffs_dct['player']:

                            self.buff_adder(buff_name, available_buffs, active_buffs['player'], current_time)
                            # ...removes expired buffs...
                            self.buff_remover(buff_name, active_buffs['player'], current_time)

                    # ... and on the target.
                    for buff_name in on_hit_buffs_dct['enemy']:

                        self.buff_adder(buff_name, current_time, active_buffs[target])

            # If the action is an ability
            elif action_name in 'QWER':

                for target in active_buffs:
                    # Debuffs applied during ability cast.
                    for buff_name in champion_abilities_dct[action_name]['actives']['buffs'][applied_on]:

                        buff_stats = available_buffs[buff_name]

                        self.buff_adder(buff_name, current_time, active_buffs[target])
        # ...removes expired buffs...
        self.buff_remover(buff_name, active_buffs['player'], current_time)


    @staticmethod
    def event_times_modifier(active_buffs, event_times):
        """
        Modifies event_time dictionary by adding time of occurrence as keyword
        and appending the name of the effect on a list as a value.
        """
        # Checks each currently active buff.
        for buff_name in active_buffs:
            # If it's a dot...
            if 'next_tick' in active_buffs:
                time = active_buffs[buff_name]['start']
                event = [buff_name]
                #...and if it's not inside event_times...
                if time not in event_times:
                    #...creates its time of occurrence and adds its name to the list.
                    event_times.update(dict(time=event))
                #...if inside event_times, adds its name to the list.
                else:
                    event_times[time].append(event)

    @staticmethod
    def buff_remover(buff_name, active_buffs, current_time):
        """
        Modifies active_buffs by removing the ones that expired.
        """
        if current_time >= active_buffs[buff_name]['ending_time']:
            del active_buffs[buff_name]


class DmgCategories(object):
        #==================================== Ability ways of application =======================================
    categories_by_application = ['dot', 'stacking_dot', 'wave', 'boomerang', 'flat_and_dot']


    def dot(ability_lvl, ability_dct, player_stats, time_start=0.):
        """
        (int, dict, dict,[float]) -> float

        Returns a dictionary with time as key and dmg as value.
        (e.g. Malzahar E)
        """
        dmg = standard(ability_lvl, ability_dct, player_stats)

        if 'first_tick_delay' in ability_dct:
            time_start += ability_dct['first_tick_delay']
        dct = {}
        #Creates time of each tick.
        for ticks in xrange(ability_dct['total_ticks']):
            dct.update({time_start + ticks*ability_dct['period']: dmg})

        return dct


    def stacking_dot(ability_lvl, ability_dct, player_stats, max_stacks, time_start=0.):
        pass


    def wave(
            ability_lvl, ability_dct, player_stats, n_th_target,
            target_distance=None):
        """
        (int, dict, dict, float, int, int, int) -> dict

        Assuming N targets are in a row, returns a dictionary with impact_time as key and dmg as value, on the N-th target
        (e.g. Ezreal R)
        """
        #For unknown target_distance, set to ability max_range.
        if not target_distance:
            target_distance = ability_dct['max_range']

        dmg = chain_limited_decay(
            ability_lvl, ability_dct, player_stats, n_th_target)

        #Calculate travel time
        impact_time = float(target_distance) / ability_dct['missile_speed']

        return {impact_time: dmg}


    def boomerang(
            ability_lvl, ability_dct, player_stats, n_th_target, total_targets, target_distance=None):
        """
        (int, dict, dict, float, int, int, int, int) -> dict

        Assuming N targets are in a row, returns a dictionary with impact_time as key and dmg on the N-th target as value,
        for abilities that hit twice. For resource convenience second event is considered to occur 0.3 seconds later.
        (e.g. Sivir Q)
        """
        convenience_time = 0.3

        dct = wave(
            ability_lvl, ability_dct, player_stats, n_th_target, target_distance)

        new_key = wave(
            ability_lvl, ability_dct, player_stats, total_targets-n_th_target, target_distance).keys()[0] + convenience_time

        new_value = wave(
            ability_lvl, ability_dct, player_stats, total_targets-n_th_target, target_distance).keys()[1]

        return dct.update({new_key: new_value})


    def flat_and_dot(ability_lvl, ability_dct, player_stats, time_start=0.):
        """
        Returns dmg of abilities that apply a direct portion of dmg and a dot.
        (e.g. Teemo E)
        """
        first_value = standard(ability_lvl, ability_dct, player_stats)
        dct = {0: first_value}

        return dct.update(dot(ability_lvl, ability_dct, player_stats, time_start))

###############################
class ChampionSettings(object):

    def __init__(self, selected_champions_dct, items_lst, runes_dct, summoner_spells):
        self.selected_champions_dct = selected_champions_dct
        self.items_lst = items_lst
        self.runes_dct = runes_dct
        self.summoner_spells = summoner_spells


class Final(ChampionSettings, abilities.Actions):

    def __init__(self, items_lst, runes_dct, summoner_spells,

                 champion_buffs_and_dmg, active_buffs, selected_champions_dct,
                 champion_lvls_dct, initial_bonuses, ability_lvl_dct, total_stats, abilities_stats, abilities_effects,
                 max_targets_dct):

        ChampionSettings.__init__(self, selected_champions_dct, items_lst, runes_dct, summoner_spells)

        abilities.Actions.__init__(self, champion_buffs_and_dmg, active_buffs, selected_champions_dct,
                                   champion_lvls_dct, initial_bonuses, ability_lvl_dct, total_stats, abilities_stats,
                                   abilities_effects, max_targets_dct)


initialStatsDct = dict(
        player=dict(
            bonuses=dict(
                additive=dict(
                    ad=dict(
                        brutaliser=20),
                    armor_pen=dict(
                        brutaliser=10
                    ),
                    crit=dict(
                        zeal_crit=0.1)),
                multiplicative=dict(
                    ap=dict(
                        deathcap=20),
                    hp=dict(
                        d=0.1)
                )
            )
        ),
        enemy_1=dict(
            bonuses=dict(
                additive=dict(
                    ad=dict(
                        brutaliser=20),
                    crit=dict(
                        d=0.1)),
                multiplicative=dict(
                    ap=dict(
                        deathcap=20),
                    crit=dict(
                        d=0.1)
                )
            )
        )
    )

def apply_aa_effects(self, current_time):
        """
        Modifies active_buffs and event_times by applying AA effects from buffs and AA dmg event.

        Iterates throughout all active buffs,
        applies on_hit buffs (e.g. Black Cleaver armor reduction), then on_hit dmg (e.g. Warwick's innate dmg),
        and then removes buffs that are removed on hit.
        """
        remove_lst = []
        add_lst = []

        for buff_name in self.active_buffs['player']:
            if 'on_hit' in self.all_buffs_and_dmg()[buff_name]:
                # Buffs applied on hit.

                for buff_applied_on_hit in self.all_buffs_and_dmg()[buff_name]['on_hit']['apply_buff']:
                    add_lst.append(buff_applied_on_hit)

                # If the buff is a dot, applies event as well.
                if 'period' in self.all_buffs_and_dmg()[buff_name]:

                    first_tick = self.first_dot_tick(current_time,                # First tick start
                                                     buff_name)
                    self.add_events(buff_name, first_tick, self.active_buffs)

                # Dmg caused on hit.
                for dmg_name in self.all_buffs_and_dmg()[buff_name]['on_hit']['cause_dmg']:

                    # TODO: check if 'enemy_1' (being static) is correct.
                    self.current_target = 'enemy_1'   # Sets target for add_events.
                    self.add_events(dmg_name, current_time, self.active_buffs)

                # Buffs removed on hit.
                for buff_removed_on_hit in self.all_buffs_and_dmg()[buff_name]['on_hit']['remove_buff']:
                    # Checks if the buff exists on the player.
                    if buff_removed_on_hit in self.active_buffs['player']:
                        remove_lst.append({'player': buff_removed_on_hit})
                    # Checks if the buff exists on an enemy.
                    elif buff_removed_on_hit in self.active_buffs[self.current_target]:
                        remove_lst.append([self.current_target, buff_removed_on_hit])

        for couple_num in remove_lst:
            del self.active_buffs[remove_lst[couple_num][0]][remove_lst[couple_num][1]]
        for buff_to_add in add_lst:
            self.add_buff(buff_to_add)

        #TODO: check all current_targets that are set to enemy_1
        # Direct dmg.
        self.current_target = 'enemy_1'
        self.add_events('aa_dmg', current_time, self.active_buffs)