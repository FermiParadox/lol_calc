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
                 ):

        self.act_buffs = act_buffs
        self.ability_lvls_dct = ability_lvls_dct

        dmg_categories.Categories.__init__(self,
                                           tot_stats=tot_stats,
                                           current_stats=current_stats,
                                           current_target=current_target,
                                           champion_lvls_dct=champion_lvls_dct,
                                           current_target_num=current_target_num)

    # Permanent buff.
    # Gets removed on first AA and never applied again.
    INNATE_CRIT_BUFF = dict(
        stats=dict(
            crit=dict(
                additive=1.)),
        target='player',)

    def innate_crit_buff(self):
        return self.INNATE_CRIT_BUFF

    INNATE_CRIT_REMOVER_BUFF = dict(
        target='player',
        on_hit=dict(
            apply_buff=[],
            cause_dmg=[],
            remove_buff=['innate_crit_buff']),
    )

    def innate_crit_remover_buff(self):
        return self.INNATE_CRIT_REMOVER_BUFF

    @staticmethod
    def inn_effects():
        return dict(
            player=dict(
                # buffs and effects activated at skill lvl up
                passives=dict(buffs=['innate_crit_buff', 'innate_crit_remover_buff'])))

    # Q ------------------------------------------------------------------------------------------------
    Q_STATS = dict(
        general=dict(# TODO

            base_cd_tpl=(1,),

            resource_used='mp',
            fixed_cost_per_attack=8,))

    Q_SLOW_BUFF = dict(
        # TODO
        target='player',
        special={'slow': 'freeze'},)

    Q_SLOW_APPLIER_BUFF = dict(
        target='player',
        on_hit=dict(
            apply_buff=['q_slow_buff'],
            cause_dmg=[],
            remove_buff=[]),)

    def q_slow_applier_buff(self):
        return self.Q_SLOW_APPLIER_BUFF

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
        special={'spellvamp': None},)

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
            target='player'
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

    pass