class Timers(object):

    def __init__(self,
                 ability_lvls_dct):

        self.ability_lvls_dct = ability_lvls_dct  # e.g. {'q': 1, }
        self.current_target = None     # e.g. player, enemy_1, enemy_2

    ABILITIES_STATS_NAMES = dict(
        q='Q_STATS',
        w='W_STATS',
        e='E_STATS',
        r='R_STATS',)

    def request_ability_stats(self, ability_name):
        """
        Returns ability_dict for selected ability.

        Structure:
            Q_STATS: {'q': {'general': {'cast_time': ,},}, 'w':{}}
        Returns:
            (dict)
        """

        dct_name = self.ABILITIES_STATS_NAMES[ability_name]

        return getattr(self, dct_name)

    def cast_end(self, ability_name, action_cast_start):
        """
        Calculates the time an action's cast ends.

        Returns:
            (float)
        """
        time = action_cast_start + self.request_ability_stats(ability_name)['general']['cast_time']

        if 'channel_time' in self.request_ability_stats(ability_name)['general']:
            time += self.request_ability_stats(ability_name)['general']['channel_time']

        return time

    def ability_cooldown(self, ability_name, stats_function):
        """
        Calculates cd from an ability's base cooldown.

        Returns:
            (float)
        """
        if 'fixed_base_cd' in self.request_ability_stats(ability_name)['general']:
            return (1-stats_function(target_name='player',
                                     stat_name='cdr')) * self.request_ability_stats(ability_name)['general']['fixed_base_cd']

        else:
            return (
                (1-stats_function(target_name='player', stat_name='cdr')) *

                self.request_ability_stats(ability_name)['general']['base_cd_tpl'][self.ability_lvls_dct[ability_name]-1]
            )

    def first_dot_tick(self, current_time, ability_name, travel_time=None):
        """
        Calculates time of first dot tick.

        Returns:
            (float)
        """
        start = current_time

        if 'delay' in self.request_ability_stats(ability_name)['general']:
            start += self.request_ability_stats(ability_name)['general']['delay']

        if travel_time:
            start += travel_time

        return start

    def next_dot_tick(self, previous_tick, ability_name):
        """
        Calculates time of next dot tick.

        Returns:
            (float)
        """
        return previous_tick + self.request_ability_stats(ability_name)['general']['period']