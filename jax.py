import dmg_categories

"""
Temp note: 'special={}' must be inside all dmg dicts of all champs.
"""


class TotalChampionAttributes(dmg_categories.Categories):

    def __init__(self,
                 ability_lvls_dct,
                 req_stats_func,
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
                                           req_stats_func=req_stats_func,
                                           current_stats=current_stats,
                                           current_target=current_target,
                                           champion_lvls_dct=champion_lvls_dct,
                                           current_target_num=current_target_num)

    INNATE_ATT_SPEED_TPL = (4., 6., 8., 10., 12., 14.)

    INN_STATS = dict(
        inn_att_speed_buff=dict(
            max_stacks=6,
            affected_stat=dict(
                att_speed=dict(
                    percent=(4., 6., 8., 10., 12., 14.))),
            duration=2.5,
            target='player', ))

    def innate_att_speed_buff(self):
        return dict(
            max_stacks=6,
            stats=dict(
                att_speed=dict(
                    percent=self.innate_value(self.INNATE_ATT_SPEED_TPL))),
            duration=2.5,
            target='player',)

    INNATE_INITIATOR_BUFF = dict(
        on_hit=dict(cause_dmg=[],
                    apply_buff=['innate_att_speed_buff'],
                    remove_buff=[]),
        target='player',
        duration='permanent',)

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
            range=700,

            base_cd_tpl=(10, 9, 8, 7, 6),

            resource_cost_type='mp',
            fixed_cost=65,

            base_dmg_tpl=(70, 110, 150, 190, 230),
            dmg_type='physical',
            scaling_stats=dict(
                ap=0.6,
                bonus_ad=1.
            ),

            cast_time=0.5)
    )

    # TODO: Make all _dmg_value methods use 'standard_dmg' (etc.) with single param (e.g. ability_name='q')
    # TODO: and detect the dict in Q_STATS by name (that is, same name as dmg or buff).
    def q_dmg_value(self):
        return self.standard_dmg(ability_dct=self.Q_STATS['general'],
                                 ability_lvl=self.ability_lvls_dct['q'])

    Q_DMG = dict(
        dmg_category='standard_dmg',
        dmg_type=Q_STATS['general']['dmg_type'],
        target='enemy',
        dmg_source='q',
        life_conversion_type='spellvamp',
        special=dict(spellvamp=None, dash_distance=Q_STATS['general']['range']),)

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
            base_cd_tpl=(7, 6, 5, 4, 3),

            resource_cost_type='mp',
            fixed_cost=30,

            base_dmg_tpl=(40, 75, 110, 145, 180),
            dmg_type='magic',
            scaling_stats=dict(
                ap=0.6
            ),

            duration=10,
            cast_time=0.,
            special=dict(resets_aa=None, cd_extendable='w_buff'))
    )

    def w_dmg_value(self):
        return self.standard_dmg(ability_dct=self.W_STATS['general'],
                                 ability_lvl=self.ability_lvls_dct['w'])

    W_DMG = dict(
        dmg_type=W_STATS['general']['dmg_type'],
        dmg_category='standard_dmg',
        target='enemy',
        dmg_source='w',
        life_conversion_type='spellvamp',
        special=dict( )
    )

    def w_dmg(self):
        return self.W_DMG

    W_BUFF = dict(
        duration=W_STATS['general']['duration'],
        target='player',
        on_hit=dict(
            cause_dmg=['w_dmg'],
            apply_buff=[],
            remove_buff=['w_buff']
        ),
        special=dict(delay_cd_start='w')
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
            range=0,
            radius=187.5,

            base_cd_tpl=(18, 16, 14, 12, 10),

            resource_cost_type='mp',
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
        dmg_source='e',
        life_conversion_type='spellvamp',
        special=dict(aoe=None, ),)

    def e_dmg(self):
        return self.E_DMG

    def e_dmg_value(self):

        return ((1 + self.E_STATS['general']['special_modifier']*self.hits_dodged) *
                self.standard_dmg(ability_dct=self.E_STATS['general'],
                                  ability_lvl=self.ability_lvls_dct['e']))

    E_STUN_ENEMY = dict(
        stun=None,
        duration=E_STATS['stun']['duration'],
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
            fixed_base_cd=80,
            resource_cost_type='mp',
            fixed_cost=100,

            base_dmg_tpl=(100, 160, 220),
            dmg_type='magic',
            scaling_stats=dict(
                ap=0.7),

            cast_time=0.),
        counter_buff=dict(
            duration=2.5,
            hits_to_trigger=3),
        armor_buff=dict(
            duration=8,
            base_stat_tpl=(25, 35, 45),
            armor_scaling_stats=dict(
                ad=0.3,),
            base_mr_tpl=(25, 35, 45),
            mr_scaling_stats=dict(
                ap=0.2)
        ))

    def r_dmg_value(self):
        return self.standard_dmg(ability_dct=self.R_STATS['general'],
                                 ability_lvl=self.ability_lvls_dct['r'])
    R_DMG = dict(
        dmg_type=R_STATS['general']['dmg_type'],
        dmg_category='standard_dmg',
        target='enemy',
        dmg_source='r',
        life_conversion_type='spellvamp',
        special=dict( ),)

    def r_dmg(self):
        return self.R_DMG

    R_COUNTER_BUFF = dict(
        duration=R_STATS['counter_buff']['duration'],
        target='player',
        max_stacks=2)

    def r_counter_buff(self):
        return self.R_COUNTER_BUFF

    def r_dmg_initiator(self):
        """
        Returns dictionary containing Jax's R counter.
        """

        # If Jax has done less than 3 hits, increases his hit counter by one on hits, ..
        dct = dict(
            on_hit=dict(cause_dmg=[],
                        apply_buff=['r_counter_buff'],
                        remove_buff=[]),
            target='player',
            duration='permanent',)

        # .. otherwise it causes the dmg and resets the counter.
        if 'r_counter_buff' in self.act_buffs['player']:
            if self.act_buffs['player']['r_counter_buff']['current_stacks'] == 2:
                dct['on_hit'] = dict(
                    cause_dmg=['r_dmg'],
                    apply_buff=[],
                    remove_buff=['r_counter_buff'])

        return dct

    # TODO make method for similar abilities.
    def r_armor_value(self):
        value = self.R_STATS['armor_buff']['armor']['base_armor_tpl'][self.ability_lvls_dct['r']-1]
        value += self.R_STATS['armor_buff']['armor']['armor_scaling_stats']
        return value

    def r_armor_buff(self):
        dct = dict(
            duration=self.R_STATS['armor_buff']['duration'],
            target='player',
            stats=dict(
                armor=dict(
                    additive=self.scaling_stat_buff(list_of_values=self.R_STATS['armor_buff']['base_stat_tpl'],
                                                    req_stat_function=self.req_stats_func,
                                                    scaling_dct=self.R_STATS['armor_buff']['armor_scaling_stats'])
                )
            ))

        return dct

    R_EFFECTS = dict(
        player=dict(
            # buffs and effects activated at skill lvl up
            passives=dict(buffs=['r_dmg_initiator', ]),
            # actives=dict(buffs=['r_armor_buff', 'r_mr_buff', ])
        )
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
    print('\nNo tests\n')