import palette


class GeneralCategories(object):

    def __init__(self,
                 req_stats_func,
                 req_dmg_dct_func,
                 current_stats,
                 current_target,
                 champion_lvls_dct,
                 current_target_num,
                 active_buffs,
                 ability_lvls_dct):

        self.ability_lvls_dct = ability_lvls_dct
        self.champion_lvls_dct = champion_lvls_dct
        self.player_lvl = self.champion_lvls_dct['player']
        self.req_stats_func = req_stats_func
        self.req_dmg_dct_func = req_dmg_dct_func
        self.current_stats = current_stats
        self.current_target = current_target
        self.current_target_num = current_target_num
        self.active_buffs = active_buffs

    def innate_value(self, list_of_values):
        """
        Returns the value of the player's innate, based on the current champion lvl.
        """
        lvl_partition_size = 18 // len(list_of_values)
        return list_of_values[(self.player_lvl - 1) // lvl_partition_size]


class BuffCategories(GeneralCategories):

    def scaling_stat_buff(self, list_of_values, scaling_dct, req_stat_function):
        """
        Calculates the value of a bonus to a stat from a buff.

        Returns:
            (float)
        """

        value = list_of_values * (self.player_lvl-1)

        for scaling_stat in scaling_dct:
            value += scaling_dct[scaling_stat] * req_stat_function(stat_name=scaling_stat, tar_name='player')

        return value


class DmgCategories(BuffCategories):

    """
    SUGGESTION: Memoization

    An aoe dmg that is applied simultaneously to multiple targets (e.g. brand W, NOT brand R) leaving no time in-between
    for dmg-triggers or stats to change, would have the same starting raw-dmg values.

    Also, in case time between Caitlyn's Q dmgs is not taken into account (which currently isn't),
    memoization would have an even bigger effect.

    --------------------------------------------------------------------------------------------------------------------
    Obsolete concepts:

    -splash: It can be represented as chain_decay with 2 tar stabilization
    -non_critable_dmg: This is equal to 'total_ad'.
    -limited_chain_decay: Incorporated into chain_decay.
    """

    def aa_dmg_value(self):
        """
        Returns the AVERAGE value of AA dmg, after applying crit change and crit mod.

        Returns:
            (float)
        """

        crit_chance = self.req_stats_func(target_name='player',
                                          stat_name='crit_chance')

        crit_mod_val = self.req_stats_func(target_name='player',
                                           stat_name='crit_modifier')

        average_crit_dmg_multiplier = (crit_chance*crit_mod_val + 1 - crit_chance)

        return average_crit_dmg_multiplier * self.req_stats_func(target_name='player',
                                                                 stat_name='ad')

    def standard_dmg_value(self, dmg_dct):
        """
        Calculates raw dmg value of given dmg name, by applying all stat-caused mods to base value.

        Returns:
            (float)
        """

        # Checks if it dependents on ability-lvl.
        try:
            # Ability name is found by dmg_source, and then ability lvl in ability_lvls_dct.
            val = dmg_dct['dmg_values'][self.ability_lvls_dct[dmg_dct['dmg_source']]]
        except KeyError:
            val = dmg_dct['dmg_values']

        # MODS
        for mod_name in dmg_dct['mods']['player']:
            val += dmg_dct['mods']['player'][mod_name] * self.req_stats_func(target_name='player',
                                                                             stat_name=mod_name)

        for mod_name in dmg_dct['mods']['enemy']:
            val += dmg_dct['mods'][self.current_target][mod_name] * self.req_stats_func(target_name=self.current_target,
                                                                                        stat_name=mod_name)

        return val

    def dmg_value(self, dmg_name):
        """
        Calculates raw dmg value of given dmg name.

        Takes into account all related stat-caused mods and dmg_category.

        Returns:
            (float)
        """

        dmg_dct = self.req_dmg_dct_func(dmg_name=dmg_name)
        cat = dmg_dct['dmg_category']

        val = self.standard_dmg_value(dmg_dct=dmg_dct)

        if cat == 'standard_dmg':
            return val

        elif cat == 'chain_decay':
            coef = dmg_dct['decay_coef']
            stabilized_tar_num = dmg_dct['stabilized_tar_num']

            if self.current_target <= stabilized_tar_num:
                return val * (1 - coef(self.current_target - 1))

        elif cat == 'aa_dmg':
            return self.aa_dmg_value()

        else:
            raise palette.UnexpectedValueError

    @staticmethod
    def aa_dmg():
        """Returns dmg dictionary of an AA.

        Value includes critable bonuses and modifiers.
        """
        return dict(
            dmg_category='aa_dmg_value',
            dmg_type='AA',
            target='enemy',
            dmg_source='AA',
            max_targets=1,
            dot=False,)

