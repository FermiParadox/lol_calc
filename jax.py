import dmg_categories

"""
Temp note: 'special={}' must be inside all dmg dicts of all champs.
"""


class TotalChampionAttributes(dmg_categories.Categories):

    def __init__(self,
                 ability_lvls_dct,
                 tot_stats,
                 act_buffs,
                 current_stats,
                 current_target,
                 champion_lvls_dct,
                 current_target_num,
                 hits_dodged=0):

        self.act_buffs = act_buffs
        self.hits_dodged = hits_dodged
        self.ability_lvls_dct = ability_lvls_dct

        dmg_categories.Categories.__init__(self,
                                           tot_stats=tot_stats,
                                           current_stats=current_stats,
                                           current_target=current_target,
                                           champion_lvls_dct=champion_lvls_dct,
                                           current_target_num=current_target_num)

    INNATE_ATT_SPEED_TPL = (4./100, 6./100, 8./100, 10./100, 12./100, 14./100)

    def innate_att_speed_buff(self):
        return dict(
            displayed_name='Relentless Assault',

            max_stacks=6,
            stats=dict(
                att_speed=dict(
                    percent=self.innate_value(self.INNATE_ATT_SPEED_TPL))),
            duration=2.5,
            target='player'
        )

    INNATE_INITIATOR_BUFF = dict(
        on_hit=dict(apply_buff=['innate_att_speed_buff'],
                    cause_dmg=[],
                    remove_buff=[]),
        target='player',
        duration='permanent',
    )

    def innate_initiator_buff(self):
        """
        Returns dictionary containing Jax's innate applier.
        """

        return self.INNATE_INITIATOR_BUFF

    @staticmethod
    def inn_effects():
        return dict(
            player=dict(
                # buffs and effects activated at skill lvl up
                passives=dict(buffs=['innate_initiator_buff']))
        )

    Q_STATS = dict(
        general=dict(
            displayed_name='Leap Strike',

            range=700,

            base_cd_tpl=(10, 9, 8, 7, 6),

            resource_used='mp',
            fixed_cost=65,

            base_dmg_tpl=(70, 110, 150, 190, 230),
            dmg_type='physical',
            scaling_stats=dict(
                ap=0.6,
                bonus_ad=1.
            ),

            cast_time=0.5)   # TODO: Find actual value. Consider using a higher one to include jump time.
    )

    def q_dmg_value(self):
        return self.standard_dmg(ability_dct=self.Q_STATS['general'],
                                 ability_lvl=self.ability_lvls_dct['q'])

    Q_DMG = dict(
        dmg_category='standard_dmg',
        dmg_type=Q_STATS['general']['dmg_type'],
        target='enemy',
        special={'spellvamp': None},)

    def q_dmg(self):
        return self.Q_DMG

    def q_effects(self):

        dct = dict(
            player=dict(
                actives=dict(
                    remove_buffs=['w_buff'])),

            enemy=dict(
                # buffs and effects activated at spell cast
                actives=dict(
                    dmg=['q_dmg'])))

        if 'w_buff' in self.act_buffs['player']:
            dct['enemy']['actives']['dmg'].append('w_buff')

        return dct

    # W ------------------------------------------------------------------------------------------------------------
    W_STATS = dict(
        general=dict(
            displayed_name='Empower',

            base_cd_tpl=(7, 6, 5, 4, 3),

            resource_used='mp',
            fixed_cost=30,

            base_dmg_tpl=(40, 75, 110, 145, 180),
            dmg_type='magic',
            scaling_stats=dict(
                ap=0.6
            ),

            duration=10,
            cast_time=0.,
            special={'resets_aa': None, 'cd_extendable': 'w_buff'})
    )

    def w_dmg_value(self):
        return self.standard_dmg(ability_dct=self.W_STATS['general'],
                                 ability_lvl=self.ability_lvls_dct['w'])

    W_DMG = dict(
        dmg_type=W_STATS['general']['dmg_type'],
        dmg_category='standard_dmg',
        target='enemy',
        special={'spellvamp': None}
    )

    def w_dmg(self):
        return self.W_DMG

    W_BUFF = dict(
        duration=W_STATS['general']['duration'],
        target='player',
        on_hit=dict(
            apply_buff=[],
            cause_dmg=['w_dmg'],
            remove_buff=['w_buff']
        ),
        special={'delay_cd_start': 'w'}
    )

    def w_buff(self):
        return self.W_BUFF

    W_EFFECTS = dict(
        player=dict(
            # buffs and effects activated at spell cast
            actives=dict(buffs=['w_buff']))
    )

    def w_effects(self):
        return self.W_EFFECTS

    # E --------------------------------------------------------------------------------
    E_STATS = dict(
        general=dict(
            displayed_name='Counter Strike',

            range=0,
            radius=187.5,

            base_cd_tpl=(18, 16, 14, 12, 10),

            resource_used='mp',
            cost_tpl=(70, 75, 80, 85, 90),

            base_dmg_tpl=(50, 75, 100, 125, 150),
            dmg_type='physical',
            scaling_stats=dict(
                bonus_ad=0.5
            ),

            special_modifier=0.2,   # Dmg modifier for each dodged attack.
            delay=2,    # Can range anywhere from 1 to 2.

            max_targets='unlimited',

            cast_time=0.),
        stun=dict(
            duration=1,
            max_targets='unlimited',
            special_effect='stun',
            aoe=None,
        ),
        buff=dict(
            stats=dict(aoe_percent_dmg_reduction=0.25)
        )
    )

    E_DMG = dict(
        dmg_type=E_STATS['general']['dmg_type'],
        dmg_category='standard_dmg',
        target='enemy',
        max_targets=E_STATS['general']['max_targets'],
        delay=E_STATS['general']['delay'],
        special={'spellvamp': None, 'aoe': None},)

    def e_dmg(self):
        return self.E_DMG

    def e_dmg_value(self):

        return ((1 + self.E_STATS['general']['special_modifier']*self.hits_dodged) *
                self.standard_dmg(ability_dct=self.E_STATS['general'],
                                  ability_lvl=self.ability_lvls_dct['e']))

    E_STUN_ENEMY = dict(
        stun=None,
        duration=E_STATS['stun']['duration'],
        displayed_name=E_STATS['general']['displayed_name'],
        target='enemy',
        delay=E_STATS['general']['delay'],)

    def e_stun_enemy(self):
        return self.E_STUN_ENEMY

    @staticmethod
    def e_effects():
        return dict(
            enemy=dict(
                # buffs and effects activated at spell cast
                actives=dict(buffs=['e_stun_enemy'],
                             dmg=['e_dmg']))
        )

    # R -------------------------------------------------------------------------------
    R_STATS = dict(
        general=dict(
            displayed_name="Grandmaster's Might",

            fixed_base_cd=80,
            resource_used='mp',
            fixed_cost=100,

            base_dmg_tpl=(100, 160, 220),
            dmg_type='magic',
            scaling_stats=dict(
                ap=0.7),

            cast_time=0.),
        counter_buff=dict(
            duration=2.5,
            hits_to_trigger=3))

    def r_dmg_value(self):
        return self.standard_dmg(ability_dct=self.R_STATS['general'],
                                 ability_lvl=self.ability_lvls_dct['r'])
    R_DMG = dict(
        dmg_type=R_STATS['general']['dmg_type'],
        dmg_category='standard_dmg',
        target='enemy',
        special={'spellvamp': None},)

    def r_dmg(self):
        return self.R_DMG

    R_COUNTER_BUFF = dict(
        duration=R_STATS['counter_buff']['duration'],
        target='player',
        max_stacks=2
    )

    def r_counter_buff(self):
        return self.R_COUNTER_BUFF

    def r_dmg_initiator(self):
        """
        Returns dictionary containing Jax's R counter.
        """

        # If Jax has done less than 3 hits, increases his hit counter by one on hits, ...
        dct = dict(
            on_hit=dict(apply_buff=['r_counter_buff'],
                        cause_dmg=[],
                        remove_buff=[]),
            target='player',
            duration='permanent',
        )

        #... otherwise it causes the dmg and resets the counter.
        if 'r_counter_buff' in self.act_buffs['player']:
            if self.act_buffs['player']['r_counter_buff']['current_stacks'] == 2:
                dct['on_hit'] = dict(
                    apply_buff=[],
                    cause_dmg=['r_dmg'],
                    remove_buff=['r_counter_buff'])

        return dct

    R_EFFECTS = dict(
        player=dict(
            # buffs and effects activated at skill lvl up
            passives=dict(buffs=['r_dmg_initiator']))
    )

    def r_effects(self):
        return self.R_EFFECTS

    def abilities_effects(self):
        return dict(
            inn=self.inn_effects(),
            q=self.q_effects(),
            w=self.w_effects(),
            e=self.e_effects(),
            r=self.r_effects()
        )


if __name__ == '__main__':

    class TestTotalAttributes(object):

        MSG_START = '\n\n-----------------------------'

        def tot_stats(self, target_name, stat_name):

            return self.tot_stats_dct[target_name][stat_name]

        def set_up(self):

            self.ability_lvls_dct = dict(
                q=1,
                w=1,
                e=2,
                r=3)

            self.tot_stats_dct = dict(
                player=dict(
                    ap=100,
                    ad=200,
                    hp=2000,
                    bonus_ad=0),
                enemy_1=dict(
                    hp=2500),
                enemy_2=dict(
                    hp=2500),
                enemy_3=dict(
                    hp=2500))

            self.champion_lvls_dct = dict(
                player=1,
                enemy_1=1)

            self.act_buffs = dict(
                player={},
                enemy_1={})

            self.current_stats = dict(
                player=dict(
                    current_hp=100
                ),
                enemy_1=dict(
                    current_hp=400
                ))

            self.current_target = 'enemy_1'

            self.current_target_num = None

            self.init_tot_attr = dict(
                ability_lvls_dct=self.ability_lvls_dct,
                tot_stats=self.tot_stats,
                act_buffs=self.act_buffs,
                current_stats=self.current_stats,
                current_target=self.current_target,
                champion_lvls_dct=self.champion_lvls_dct,
                current_target_num=self.current_target_num)

        def test_innate(self):

            self.set_up()

            msg = self.MSG_START
            msg += '\nInnate (single stack)\n'

            msg += '\nbonus tuple: %s' % str(TotalChampionAttributes.INNATE_ATT_SPEED_TPL)
            msg += '\n'

            for player_lvl in (1, 3, 4, 18):

                self.init_tot_attr['champion_lvls_dct']['player'] = player_lvl

                msg += '\nplayer lvl: %s, ' % player_lvl

                msg += ('att speed bonus: ' +
                        str(TotalChampionAttributes(**self.init_tot_attr)
                            .innate_att_speed_buff()['stats']['att_speed']['percent']))

            return msg

        def test_dmg_values(self, ability_name):

            self.set_up()

            msg = self.MSG_START

            stat_dct = getattr(TotalChampionAttributes, ability_name.upper() + '_STATS')

            msg += '\nbase dmg tuple: ' + str(stat_dct['general']['base_dmg_tpl'])
            for stat_name in self.tot_stats_dct['player']:
                msg += '\n%s: %s' % (stat_name, self.tot_stats('player', stat_name=stat_name))

            # Checks all lvls
            if ability_name != 'r':
                ability_lvl_tpl = (1, 2, 3, 4, 5)
            else:
                ability_lvl_tpl = (1, 2, 3)
            for ability_lvl in ability_lvl_tpl:
                self.init_tot_attr['ability_lvls_dct'][ability_name] = ability_lvl

                inst = TotalChampionAttributes(**self.init_tot_attr)

                msg += '\n%s lvl: %s, ' % (ability_name, self.init_tot_attr['ability_lvls_dct'][ability_name])

                value = getattr(inst, ability_name + '_dmg_value')

                msg += '%s dmg value: %s' % (ability_name, value())

            return msg

        def __repr__(self):

            msg = self.test_innate()

            for ability_name in 'qwer':
                msg += '\n-----------------------------'

                msg += self.test_dmg_values(ability_name)

            return msg

    print(TestTotalAttributes())