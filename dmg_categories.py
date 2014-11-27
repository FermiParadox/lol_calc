class Categories(object):

    def __init__(self,
                 req_stats_func,
                 current_stats,
                 current_target,
                 champion_lvls_dct,
                 current_target_num):

        self.champion_lvls_dct = champion_lvls_dct
        self.player_lvl = self.champion_lvls_dct['player']
        self.req_stats_func = req_stats_func
        self.current_stats = current_stats
        self.current_target = current_target
        self.current_target_num = current_target_num

    def innate_value(self, list_of_values):
        """
        Returns the value of the player's innate, based on the current champion lvl.
        """
        lvl_partition_size = 18 // len(list_of_values)
        return list_of_values[(self.player_lvl - 1) // lvl_partition_size]

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

    def standard_dmg(self, ability_dct, ability_lvl=1):
        """
        (int, dict, dict) -> float

        Returns dmg of single event direct-dmg.
        (e.g. Ashe W)

        Args:
            -ability_lvl: Int ranging from 1 to 5.
        """

        # If base dmg scales with ability lvl..
        if 'base_dmg_tpl' in ability_dct:
            total_dmg = ability_dct['base_dmg_tpl'][ability_lvl-1]

        # Otherwise 'fixed_base_dmg' is inside instead of 'base_dmg_tpl'.
        else:
            total_dmg = ability_dct['fixed_base_dmg']

        # Adds bonus dmg to base dmg.
        for stat in ability_dct['scaling_stats']:

            if stat == 'target_max_hp':
                total_dmg += self.req_stats_func(target_name=self.current_target,
                                                 stat_name='hp') * ability_dct['scaling_stats'][stat]

            elif stat == 'target_current_hp':
                total_dmg += (self.current_stats[self.current_target]['current_hp'] *
                              ability_dct['scaling_stats'][stat])

            elif stat == 'target_missing_hp':
                total_dmg += (
                    (self.req_stats_func(target_name=self.current_target,
                                         stat_name='hp') - self.current_stats[self.current_target]['current_hp'])
                    * ability_dct['scaling_stats'][stat])

            elif stat == 'player_max_hp':
                total_dmg += self.req_stats_func(target_name='player',
                                                 stat_name='hp') * ability_dct['scaling_stats'][stat]

            else:
                total_dmg += self.req_stats_func(target_name='player',
                                                 stat_name=stat) * ability_dct['scaling_stats'][stat]

        return total_dmg

    def innate_dmg(self, ability_dct):
        """
        (int, dict, dict) -> float

        Returns dmg of innate that changes every few lvls.
        (e.g. Darius innate)
        """
        total_dmg = self.innate_value(ability_dct['base_dmg_tpl'])

        for stat in ability_dct['scaling_stats']:
            total_dmg += self.req_stats_func(target_name='player',
                                             stat_name=stat) * ability_dct['scaling_stats'][stat]

        return total_dmg

    def chain_decay(self, ability_dct, ability_lvl, current_target_num=None):
        """
        (int, dict, dict, float, int) -> float

        Returns dmg on the n-th target of an ability that hits consecutive targets,
        decaying linearly on each hit without limit.
        (e.g. Caitlyn Q on 2nd target)

        Argument is used later on in another method.
        """
        # Checks if an argument is given to the method (modification used by method later on).
        if current_target_num:
            curr_num = current_target_num
        else:
            curr_num = self.current_target_num

        return self.standard_dmg(ability_dct, ability_lvl) * (1-ability_dct['decay_coefficient']*(curr_num-1))

    def chain_limited_decay(self, ability_dct, ability_lvl):
        """
        (int, dict, dict, float, int) -> float

        Returns dmg on the n-th target of an ability that hits consecutive targets, decaying on each hit.
        The dmg decays down to a threshold after which it remains stable.
        (e.g. Caitlyn Q on 5th target)
        """
        if self.current_target_num > ability_dct['targets_hit_threshold']:
            return self.chain_decay(ability_dct=ability_dct,
                                    ability_lvl=ability_lvl,
                                    current_target_num=ability_dct['targets_hit_threshold'])
        else:
            return self.chain_decay(ability_dct, ability_lvl)

    def aa_dmg_value(self, critable_bonus=None, aa_reduction_mod=None):
        """
        Returns average AA dmg after applying crit_chance.

        -Extra bonuses that can crit are applied as well.
        -Modifiers can be applied as well (e.g. Runaan's Hurricane, Miss Fortune's Q etc).
        """

        crit_chance = self.req_stats_func(target_name='player',
                                          stat_name='crit_chance')

        crit_mod_val = self.req_stats_func(target_name='player',
                                           stat_name='crit_modifier')

        if critable_bonus:
            value = (crit_chance*crit_mod_val + 1 - crit_chance) * (critable_bonus +
                                                                    self.req_stats_func(target_name='player',
                                                                                        stat_name='ad'))

        else:
            value = (crit_chance*crit_mod_val + 1 - crit_chance) * self.req_stats_func(target_name='player',
                                                                                       stat_name='ad')

        if aa_reduction_mod:
            return value * aa_reduction_mod
        else:
            return value

    @staticmethod
    def aa_dmg():
        """Returns dmg dictionary of an AA.

        Value includes critable bonuses and modifiers.
        """
        return dict(
            dmg_category='aa_dmg_value',
            dmg_type='AA',
            target='enemy',
            special={'dmg_source': 'AA'})


# Test module.
if __name__ == '__main__':
    print('\nNo tests found.')