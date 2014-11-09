class InnateListValue(object):

    def __init__(self, champion_lvls_dct):
        self.champion_lvls_dct = champion_lvls_dct

    def innate_value(self, list_of_values):
        """
        Returns the value of the player's innate, based on the current champion lvl.

        >>>InnateListValue({'player':1},[4, 6, 8, 10, 12, 14]).innate_value()
        """
        lvl_partition_size = 18 // len(list_of_values)
        return list_of_values[(self.champion_lvls_dct['player'] - 1) // lvl_partition_size]

    def __repr__(self):
        return ('\nClass: %s\n'
                'Innate list: %s \n'
                'Champion lvl: %s \n'
                'Innate value: %s\n'
                '') % (self.__class__.__name__,
                       [4, 6, 8, 10, 12, 14],
                       self.champion_lvls_dct['player'],
                       self.innate_value([4, 6, 8, 10, 12, 14]))


class Categories(InnateListValue):

    def __init__(self,
                 tot_stats,
                 current_stats,
                 current_target,
                 champion_lvls_dct,
                 current_target_num):

        self.tot_stats = tot_stats
        self.current_stats = current_stats
        self.current_target = current_target
        self.current_target_num = current_target_num
        InnateListValue.__init__(self, champion_lvls_dct)

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

        # Otherwise 'base_dmg' is inside instead of 'base_dmg_tpl'.
        else:
            total_dmg = ability_dct['base_dmg']

        # Adds bonus dmg to base dmg.
        for stat in ability_dct['scaling_stats']:

            if stat == 'target_max_hp':
                total_dmg += self.tot_stats(self.current_target, 'hp') * ability_dct['scaling_stats'][stat]

            elif stat == 'target_current_hp':
                total_dmg += (self.current_stats[self.current_target]['current_hp'] *
                              ability_dct['scaling_stats'][stat])

            elif stat == 'target_missing_hp':
                total_dmg += (
                    (self.tot_stats(self.current_target, 'hp') - self.current_stats[self.current_target]['current_hp'])
                    * ability_dct['scaling_stats'][stat])

            elif stat == 'player_max_hp':
                total_dmg += self.tot_stats('player', 'hp') * ability_dct['scaling_stats'][stat]

            else:
                total_dmg += self.tot_stats('player', stat) * ability_dct['scaling_stats'][stat]

        return total_dmg

    def innate_dmg(self, ability_dct):
        """
        (int, dict, dict) -> float

        Returns dmg of innate that changes every few lvls.
        (e.g. Darius innate)
        """
        total_dmg = self.innate_value(ability_dct['base_dmg_tpl'])

        for stat in ability_dct['scaling_stats']:
            total_dmg += self.tot_stats('player', stat) * ability_dct['scaling_stats'][stat]

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
        """Returns average AA dmg after applying crit.

        -Extra bonuses that can crit are applied as well.
        -Modifiers can be applied as well (e.g. Runaan's Hurricane, Miss Fortune's Q etc).
        """

        crit_chance = self.tot_stats('player', 'crit')

        crit_mod_val = self.tot_stats('player', 'crit_modifier')

        if critable_bonus:
            value = (crit_chance*crit_mod_val + 1 - crit_chance) * (self.tot_stats('player', 'ad') +
                                                                    critable_bonus)

        else:
            value = (crit_chance*crit_mod_val + 1 - crit_chance) * self.tot_stats('player', 'ad')

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
            target='enemy'
        )


# Test module.
if __name__ == '__main__':
    # InnateListValue class
    class TestInnate(object):

        @staticmethod
        def test_values_vs_lvls():
            """
            Returns a string, with the values of the innate for each given lvl.

            Values should be the same each 3 lvls, changing on the next lvl.
            """
            effect_values_tpl = (10, 20, 30, 40, 50, 60)

            def value(player_lvl):
                return InnateListValue(dict(player=player_lvl)).innate_value(effect_values_tpl)

            msg = ('\n\n-------------------------------------'
                   '\nInnate'
                   '\nvalues tuple: ') + str(effect_values_tpl)

            for lvl in (1, 3, 4, 18):
                msg += '\nlvl: %s, value: %s' % (lvl, value(lvl))

            msg += '\n-------------------------------------'
            return msg

    print(TestInnate.test_values_vs_lvls())

    # Categories class
    class TestCategories(object):

        def __init__(self):
            self.ability_dct = None
            self.innate_dmg_tpl = None
            self.tot_stats_dct = None
            self.current_stats = None
            self.current_stats = None
            self.player_lvl = None
            self.champion_lvls_dct = None
            self.ability_lvl = None
            self.current_target = None
            self.current_target_num = None
            self.forced_decay_coefficient = None
            self.init_args = None

        def tot_stats(self, tar, stat):
                return self.tot_stats_dct[tar][stat]

        def set_up(self):

            self.ability_dct = dict(
                base_dmg_tpl=(100, 200, 300, 400, 500),

                scaling_stats=dict(),

                decay_coefficient=0.5,
                targets_hit_threshold=2,
                secondary_target_dmg_coefficient=0.5)

            self.innate_dmg_tpl = (100, 200, 300, 400, 500, 600)

            self.tot_stats_dct = dict(
                player=dict(
                    ap=100,
                    ad=200,
                    hp=2000,
                    crit=0.,
                    crit_modifier=2.),
                enemy_1=dict(
                    hp=2500),
                enemy_2=dict(
                    hp=2500),
                enemy_3=dict(
                    hp=2500))

            self.current_stats = dict(
                player=dict(
                    current_hp=1000,
                ),
                enemy_1=dict(
                    current_hp=1000,
                ),
                enemy_2=dict(
                    current_hp=1000,
                ),
                enemy_3=dict(
                    current_hp=1000,
                )
            )

            self.player_lvl = 1
            self.champion_lvls_dct = dict(player=self.player_lvl)
            self.ability_lvl = 1
            self.current_target = 'enemy_1'
            self.current_target_num = 1
            self.forced_decay_coefficient = 0.1

            self.init_args = dict(
                tot_stats=self.tot_stats,
                current_stats=self.current_stats,
                current_target=self.current_target,
                champion_lvls_dct=self.champion_lvls_dct,
                current_target_num=self.current_target_num)

        # Tested method: standard_dmg
        def test_standard_other(self):

            self.set_up()

            self.ability_dct['scaling_stats'] = dict(ad=0.1,
                                                     ap=0.1)
            inst = Categories(**self.init_args)

            msg = ('\n-----------------------'
                   '\nStandard dmg (non special stats)'
                   '\nbase dmg tuple: ') + str(self.ability_dct['base_dmg_tpl'])

            msg += '\nability lvl: ' + str(self.ability_lvl)

            msg += '\nscaling stats '
            for stat_name in self.ability_dct['scaling_stats']:
                msg += ('\n     %s: %s'
                        '') % (stat_name, self.ability_dct['scaling_stats'][stat_name])

            msg += "\nplayer's ad: %s" % self.tot_stats('player', 'ad')
            msg += "\nplayer's ad: %s" % self.tot_stats('player', 'ap')

            msg += ('\ndmg value: %s'
                    '\n---------------------------'
                    '') % inst.standard_dmg(ability_dct=self.ability_dct,
                                            ability_lvl=self.ability_lvl)

            return msg

        def test_standard_tar_curr_hp(self):

            self.set_up()

            self.ability_dct['scaling_stats'] = dict(target_current_hp=0.1)
            inst = Categories(**self.init_args)

            msg = ('\n-----------------------'
                   '\nStandard dmg (target current hp)'
                   '\nbase dmg tuple: ') + str(self.ability_dct['base_dmg_tpl'])

            msg += '\nability lvl: ' + str(self.ability_lvl)

            msg += '\nscaling stats '
            for stat_name in self.ability_dct['scaling_stats']:
                msg += ('\n     %s: %s'
                        '') % (stat_name, self.ability_dct['scaling_stats'][stat_name])

            msg += "\ntarget's current_hp: %s" % self.current_stats['enemy_1']['current_hp']

            msg += ('\ndmg value: %s'
                    '\n---------------------------'
                    '') % inst.standard_dmg(ability_dct=self.ability_dct,
                                            ability_lvl=self.ability_lvl)

            return msg

        def test_standard_tar_missing_hp(self):

            self.set_up()

            self.ability_dct['scaling_stats'] = dict(target_missing_hp=0.1)
            inst = Categories(**self.init_args)

            msg = ('\n-----------------------'
                   '\nStandard dmg (target missing hp)'
                   '\nbase dmg tuple: ') + str(self.ability_dct['base_dmg_tpl'])

            msg += '\nability lvl: ' + str(self.ability_lvl)

            msg += '\nscaling stats '
            for stat_name in self.ability_dct['scaling_stats']:
                msg += ('\n     %s: %s'
                        '') % (stat_name, self.ability_dct['scaling_stats'][stat_name])

            msg += ("\ntarget's max hp: %s"
                    "\ntarget's current hp: %s"
                    "\ntarget's missing hp: %s") % (self.tot_stats(self.current_target, 'hp'),
                                                    self.current_stats[self.current_target]['current_hp'],

                                                    (self.tot_stats(self.current_target, 'hp') -
                                                    self.current_stats[self.current_target]['current_hp']))

            msg += ('\ndmg value: %s'
                    '') % inst.standard_dmg(ability_dct=self.ability_dct,
                                            ability_lvl=self.ability_lvl)

            return msg

        def test_standard_tar_max_hp(self):

            self.set_up()

            self.ability_dct['scaling_stats'] = dict(target_max_hp=0.1)
            inst = Categories(**self.init_args)

            msg = ('\n-----------------------'
                   '\nStandard dmg (target max hp)'
                   '\nbase dmg tuple: ') + str(self.ability_dct['base_dmg_tpl'])

            msg += '\nability lvl: ' + str(self.ability_lvl)

            msg += '\nscaling stats '
            for stat_name in self.ability_dct['scaling_stats']:
                msg += ('\n     %s: %s'
                        '') % (stat_name, self.ability_dct['scaling_stats'][stat_name])

            msg += ("\ntarget's max hp: %s"
                    "") % self.tot_stats(self.current_target, 'hp')

            msg += ('\ndmg value: %s'
                    '') % inst.standard_dmg(ability_dct=self.ability_dct,
                                            ability_lvl=self.ability_lvl)

            return msg

        def test_standard_player_max_hp(self):

            self.set_up()

            self.ability_dct['scaling_stats'] = dict(player_max_hp=0.1)
            inst = Categories(**self.init_args)

            msg = ('\n-----------------------'
                   '\nStandard dmg (target max hp)'
                   '\nbase dmg tuple: ') + str(self.ability_dct['base_dmg_tpl'])

            msg += '\nability lvl: ' + str(self.ability_lvl)

            msg += '\nscaling stats '
            for stat_name in self.ability_dct['scaling_stats']:
                msg += ('\n     %s: %s'
                        '') % (stat_name, self.ability_dct['scaling_stats'][stat_name])

            msg += ("\nplayer's max hp: %s"
                    "") % self.tot_stats('player', 'hp')

            msg += ('\ndmg value: %s'
                    '') % inst.standard_dmg(ability_dct=self.ability_dct,
                                            ability_lvl=self.ability_lvl)

            return msg

        # Tested method: innate_dmg
        def test_innate_dmg(self, lvl):

            self.set_up()

            self.champion_lvls_dct['player'] = lvl
            self.ability_dct['base_dmg_tpl'] = self.innate_dmg_tpl
            self.ability_dct['scaling_stats'] = dict(ad=0.1,
                                                     ap=0.1)
            inst = Categories(**self.init_args)

            msg = ('\n-----------------------'
                   '\nInnate dmg'
                   '\nbase dmg tuple: ') + str(self.ability_dct['base_dmg_tpl'])

            msg += '\nplayer lvl: ' + str(self.champion_lvls_dct['player'])

            msg += '\nscaling stats '
            for stat_name in self.ability_dct['scaling_stats']:
                msg += ('\n     %s: %s'
                        '') % (stat_name, self.ability_dct['scaling_stats'][stat_name])

            msg += "\nplayer's ad: %s" % self.tot_stats('player', 'ad')
            msg += "\nplayer's ad: %s" % self.tot_stats('player', 'ap')

            msg += ('\ndmg value: %s'
                    '') % inst.innate_dmg(ability_dct=self.ability_dct)

            return msg

        # Tested method: chain decay
        def test_chain_decay(self, curr_tar_num):

            self.set_up()

            self.init_args['current_target_num'] = curr_tar_num
            self.ability_lvl = 5
            self.ability_dct['scaling_stats'] = dict(ad=0.1,
                                                     ap=0.1)
            inst = Categories(**self.init_args)

            msg = ('\n-----------------------'
                   '\nChain decay'
                   '\nbase dmg tuple: ') + str(self.ability_dct['base_dmg_tpl'])

            msg += '\nability lvl: ' + str(self.ability_lvl)

            msg += '\ncurrent target number: ' + str(self.init_args['current_target_num'])

            msg += '\ndecay coefficient: ' + str(self.ability_dct['decay_coefficient'])

            msg += '\nscaling stats '
            for stat_name in self.ability_dct['scaling_stats']:
                msg += ('\n     %s: %s'
                        '') % (stat_name, self.ability_dct['scaling_stats'][stat_name])

            msg += "\nplayer's ad: %s" % self.tot_stats('player', 'ad')
            msg += "\nplayer's ad: %s" % self.tot_stats('player', 'ap')

            msg += ('\ndmg value: %s'
                    '') % inst.chain_decay(ability_dct=self.ability_dct,
                                           ability_lvl=self.ability_lvl)

            return msg

        def test_chain_limited_decay(self, curr_tar_num):

            self.set_up()

            self.init_args['current_target_num'] = curr_tar_num
            self.ability_lvl = 5
            self.ability_dct['scaling_stats'] = dict(ad=0.1,
                                                     ap=0.1)
            inst = Categories(**self.init_args)

            msg = ('\n-----------------------'
                   '\nChain limited decay'
                   '\nbase dmg tuple: ') + str(self.ability_dct['base_dmg_tpl'])

            msg += '\nability lvl: ' + str(self.ability_lvl)

            msg += '\ncurrent target number: ' + str(self.init_args['current_target_num'])

            msg += '\ndecay coefficient: ' + str(self.ability_dct['decay_coefficient'])

            msg += '\nscaling stats '
            for stat_name in self.ability_dct['scaling_stats']:
                msg += ('\n     %s: %s'
                        '') % (stat_name, self.ability_dct['scaling_stats'][stat_name])

            msg += "\nplayer's ad: %s" % self.tot_stats('player', 'ad')
            msg += "\nplayer's ad: %s" % self.tot_stats('player', 'ap')

            msg += ('\ndmg value: %s'
                    '') % inst.chain_limited_decay(ability_dct=self.ability_dct,
                                                   ability_lvl=self.ability_lvl)

            return msg

        # Tested method: aa_dmg_value
        def test_aa_dmg_value(self, crit_change, crit_mod):
            self.set_up()

            self.tot_stats_dct['player']['crit'] = crit_change
            self.tot_stats_dct['player']['crit_modifier'] = crit_mod

            inst = Categories(**self.init_args)

            msg = ('\n-----------------------'
                   '\nAA dmg')

            msg += "\ntotal ad: %s" % self.tot_stats('player', 'ad')
            msg += "\ncrit chance: %s" % self.tot_stats('player', 'crit')
            msg += "\ncrit modifier: %s" % self.tot_stats('player', 'crit_modifier')

            msg += ('\ndmg value: %s'
                    '') % inst.aa_dmg_value()

            return msg

        def __repr__(self):
            msg = (self.test_standard_other() +
                   self.test_standard_tar_missing_hp() +
                   self.test_standard_tar_curr_hp() +
                   self.test_standard_tar_max_hp() +
                   self.test_standard_player_max_hp()
                   )
            for lvl_value in (1, 3, 4, 18):
                msg += self.test_innate_dmg(lvl_value)

            msg += '\n---------------------------'

            for cur_tar in (1, 2, 3):
                msg += self.test_chain_decay(cur_tar)

            msg += '\n---------------------------'

            for cur_tar in (1, 2, 3):
                msg += self.test_chain_limited_decay(cur_tar)

            msg += '\n---------------------------'

            msg += self.test_aa_dmg_value(0, 2)
            msg += self.test_aa_dmg_value(0.5, 2)
            msg += self.test_aa_dmg_value(1, 2)

            return msg

    print(TestCategories())