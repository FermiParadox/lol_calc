import palette


class Timers(object):

    def __init__(self,
                 ability_lvls_dct,
                 req_dmg_dct_func,
                 req_abilities_attrs_func):

        self.ability_lvls_dct = ability_lvls_dct  # e.g. {'q': 1, }
        self.current_target = None     # e.g. player, enemy_1, enemy_2
        self.req_dmg_func = req_dmg_dct_func
        self.req_abilities_dct_func = req_abilities_attrs_func

    def request_ability_gen_attrs_dct(self, ability_name):
        """
        Returns ability_dict for selected ability.

        Structure:
            Q_STATS: {'q': {'general': {'cast_time': ,},}, 'w':{}}
        Returns:
            (dict)
        """

        return self.req_abilities_dct_func(ability_name)

    @staticmethod
    def cast_end(action_cast_start, action_gen_attrs_dct):
        """
        Calculates the time an action's cast ends.

        Returns:
            (float)
        """

        time = action_cast_start + action_gen_attrs_dct['cast_time']

        action_channel = action_gen_attrs_dct['channel_time']
        if action_channel:
            time += action_gen_attrs_dct['channel_time']

        return time

    def channel_end(self, action_cast_start, action_gen_attrs_dct):
        """
        Calculates the time an action's channel ends.

        Returns:
            (float)
        """

        time = self.cast_end(action_cast_start=action_cast_start, action_gen_attrs_dct=action_gen_attrs_dct)

        time += ability_stats_dct['channel_time']

        return time

    def ability_cooldown(self, ability_name, stats_function):
        """
        Calculates cd from an ability's base cooldown.

        Returns:
            (float)
        """

        cd_multiplier = 1 - stats_function(target_name='player', stat_name='cdr')

        cd_index = self.ability_lvls_dct[ability_name] - 1
        base_cd_value = self.request_ability_gen_attrs_dct(ability_name)['base_cd'][cd_index]

        return cd_multiplier * base_cd_value

    def ability_cd_end(self, ability_name, cast_start, stats_function, actions_dct):
        """
        Calculates the time an action's cd ends.

        Returns:
            (float)
        """

        time = actions_dct[cast_start]['cast_end']
        time += self.ability_cooldown(ability_name=ability_name, stats_function=stats_function)

        return time

    def first_dot_tick(self, current_time, dmg_name):
        """
        Calculates time of first dot tick.

        Returns:
            (float)
        """

        dmg_dct = self.req_dmg_func(dmg_name)

        start = current_time
        start += dmg_dct['delay']

        dmg_source_name = dmg_dct['dmg_source']
        if dmg_source_name in palette.ALL_POSSIBLE_SPELL_SHORTCUTS:
            start += self.request_ability_gen_attrs_dct(dmg_source_name)['travel_time']

        return start

