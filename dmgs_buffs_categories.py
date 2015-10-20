import palette
import copy

_AA_DMG_DCT = copy.deepcopy(palette.DMG_DCT_BASE)
_AA_DMG_DCT['delay'] = None
_AA_DMG_DCT['dmg_category'] = 'aa_dmg'
_AA_DMG_DCT['dmg_type'] = 'AA'
_AA_DMG_DCT['dmg_source'] = 'AA'
_AA_DMG_DCT['max_targets'] = 1
_AA_DMG_DCT['usual_max_targets'] = 1
_AA_DMG_DCT['dot'] = False
_AA_DMG_DCT['usual_targets'] = 1
_AA_DMG_DCT['radius'] = 0
_AA_DMG_DCT['target_type'] = 'enemy'
_AA_DMG_DCT['life_conversion_type'] = 'lifesteal'
_AA_DMG_DCT['resource_type'] = 'hp'
_AA_DMG_DCT['dmg_values'] = 1
_AA_DMG_DCT['mods'] = None
_AA_DMG_DCT['crit_type'] = 'normal'
_AA_DMG_DCT['heal_for_dmg_amount'] = False


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
        self.current_enemy = current_target
        self.current_target_num = current_target_num
        self.active_buffs = active_buffs

    def effect_lvl_by_champ_lvl(self, seq_of_values):
        """
        Determines the value of a buff or dmg based on champion lvl.
        e.g. jax inn, darius inn, etc

        :param seq_of_values:
        :return: (int)
        """
        lvl_partition_size = 18 // len(seq_of_values)
        return (self.player_lvl - 1) // lvl_partition_size

    def innate_value(self, list_of_values):
        """
        Returns the value of the player's innate, based on the current champion lvl.
        """

        return list_of_values[self.effect_lvl_by_champ_lvl(seq_of_values=list_of_values)]


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

    # TODO: memoization
    """
    Possible memoization:

    An aoe dmg that is applied simultaneously to multiple targets (e.g. brand W, NOT brand R) leaving no time in-between
    for dmg-triggers or stats to change, would have the same starting raw-dmg values.

    Also, in case time between Veigar's Q dmgs is not taken into account (which currently isn't),
    memoization would have an even bigger effect.

    A possible way to implement it would be to create the raw value when distributing a multi-targeted event.
    A different way would be to give (globally) the same value for all events that occur at the same time.

    WARNING:
    Some dmg values scale of target's stats (e.g. Malza W) making it very tricky to implement.

    --------------------------------------------------------------------------------------------------------------------
    Obsolete concepts:

    -splash: It can be represented as chain_decay with 2 tar stabilization.
    -non_critable_dmg: This is equal to 'total_ad'.
    -limited_chain_decay: Incorporated into chain_decay.
    """

    def aa_dmg_value(self):
        """
        Returns the AVERAGE value of AA dmg, after applying crit change and crit mod.

        :return: (float)
        """

        crit_chance = self.req_stats_func(target_name='player', stat_name='crit_chance')
        crit_mod_val = self.req_stats_func(target_name='player', stat_name='crit_modifier')
        crit_dmg_reduction = self.req_stats_func(target_name=self.current_enemy, stat_name='crit_dmg_reduction')

        average_crit_dmg_multiplier = (crit_chance*crit_mod_val*crit_dmg_reduction + 1 - crit_chance)

        return average_crit_dmg_multiplier * self.req_stats_func(target_name='player', stat_name='ad')

    def _dmg_or_shield_mod_value(self, given_mod_seq_or_val, dmg_or_shield_dct):
        """
        Returns the value of a mod.

        The mod can scale with lvl or have a stable value.

        :return: (num)
        """
        if isinstance(given_mod_seq_or_val, (float, int)):
            return given_mod_seq_or_val

        else:
            source_name = dmg_or_shield_dct['dmg_source']

            if source_name in palette.ALL_POSSIBLE_ABILITIES_SHORTCUTS:
                ability_lvl = self.ability_lvls_dct[source_name]
                return given_mod_seq_or_val[ability_lvl-1]

            else:
                index = self.effect_lvl_by_champ_lvl(seq_of_values=given_mod_seq_or_val)
                return given_mod_seq_or_val[index]

    def _value_after_mods(self, dmg_or_shield_dct, mods_dct, value):
        if mods_dct:

            for owner_type in mods_dct:
                if owner_type == 'player':
                    owner = 'player'
                else:
                    owner = self.current_enemy

                owner_mods_dct = mods_dct[owner_type]
                for mod_name in sorted(owner_mods_dct):
                    mod_dct = owner_mods_dct[mod_name]

                    if 'additive' in mod_dct:
                        additive_mod_val = mod_dct['additive']
                        additive_mod_val = self._dmg_or_shield_mod_value(given_mod_seq_or_val=additive_mod_val,
                                                                         dmg_or_shield_dct=dmg_or_shield_dct)
                        value += additive_mod_val * self.req_stats_func(target_name=owner, stat_name=mod_name)

                for mod_name in sorted(owner_mods_dct):
                    mod_dct = owner_mods_dct[mod_name]

                    if 'multiplicative' in owner_mods_dct:
                        mult_mod_val = mod_dct['multiplicative']
                        mult_mod_val = self._dmg_or_shield_mod_value(given_mod_seq_or_val=mult_mod_val,
                                                                     dmg_or_shield_dct=dmg_or_shield_dct)
                        value *= mult_mod_val * self.req_stats_func(target_name=owner, stat_name=mod_name)

        return value

    def standard_dmg_value(self, dmg_dct):
        """
        Calculates raw dmg value of given dmg name, by applying all stat-caused mods to base value.

        :return: (float)
        """

        # Checks if it dependents on ability-lvl.
        dmg_vals = dmg_dct['dmg_values']
        dmg_source_name = dmg_dct['dmg_source']

        if dmg_source_name in palette.ALL_POSSIBLE_SPELL_SHORTCUTS:
            # (Ability name is found by dmg_source, and ability lvl by ability_lvls_dct.)
            spell_lvl = self.ability_lvls_dct[dmg_source_name]
            val = dmg_vals[spell_lvl-1]
        else:
            val = dmg_vals

        # MODS
        mods_dct = dmg_dct['mods']
        val_after_mods = self._value_after_mods(dmg_or_shield_dct=dmg_dct, mods_dct=mods_dct, value=val)

        return val_after_mods

    def raw_dmg_value(self, dmg_name):
        """
        Calculates raw dmg value of given dmg name.

        Takes into account all related stat-caused mods and dmg_category.

        :return: (float)
        """

        dmg_dct = self.req_dmg_dct_func(dmg_name=dmg_name)
        cat = dmg_dct['dmg_category']

        if cat == 'aa_dmg':
            return self.aa_dmg_value()
        else:
            val = self.standard_dmg_value(dmg_dct=dmg_dct)

        if cat in ('standard_dmg', 'ring_dmg'):
            return val

        elif cat == 'chain_decay':
            coef = dmg_dct['decay_coef']
            stabilized_tar_num = dmg_dct['stabilized_tar_num']

            if self.current_target_num <= stabilized_tar_num:
                return val * (1 - coef(self.current_target_num - 1))

        else:
            raise palette.UnexpectedValueError

    @staticmethod
    def aa_dmg():
        return _AA_DMG_DCT
