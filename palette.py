class ChampionBase(object):
    """
    Class attributes should not be called directly from this class.
    """

    def abilities_attrs(self):
        return self.ABILITIES_ATTRS

    def abilities_effects(self):
        return self.ABILITIES_EFFECTS


class ChampionsStats(object):

    @staticmethod
    def on_hit_effects():
        return dict(
            apply_dmg=[],
            add_buff=[],
            remove_buff=[],
            change_cd=[],
        )




    @staticmethod
    def inn_effects():
        return dict(
            enemy=dict(

                # buffs and effects activated at skill lvl up
                passives=dict(buffs=[],
                              remove_buff=[])),

            player=dict(

                # buffs and effects activated at skill lvl up
                passives=dict(buffs=[],
                              remove_buff=[]))
        )

    @staticmethod
    def spell_effects():
        return dict(
            enemy=dict(

                # Buffs and effects activated at skill lvl up.
                passives=dict(buffs=[],
                              remove_buff=[],
                              dmg=[]),

                # Buffs and effects activated on cast.
                actives=dict(buffs=[],
                             remove_buff=[],
                             dmg=[])),

            player=dict(

                # Buffs and effects activated at skill lvl up.
                passives=dict(buffs=[],
                              remove_buff=[],
                              dmg=[]),

                # Buffs and effects activated on cast.
                actives=dict(buffs=[],
                             remove_buff=[],
                             dmg=[],
                             cds_modified={}))
        )

    @staticmethod
    def item_effects():
        return dict(
            enemy=dict(

                # Buffs and effects activated at purchase.
                passives=dict(buffs=[],
                              dmg=[]),

                # Buffs and effects activated on cast.
                actives=dict(buffs=[],
                             dmg=[])),

            player=dict(

                # Buffs and effects activated at purchase.
                passives=dict(buffs=[],
                              dmg=[]),

                # Buffs and effects activated on cast.
                actives=dict(buffs=[],
                             dmg=[]))
        )

    def champion_abilities(self):
        return dict(
            inn=self.inn_effects(),
            q=self.q_effects(),
            w=self.w_effect(),
            e=self.e_effect(),
            r=self.r_effect()
        )

    def champion_aa(self):
        return dict(

        )


class BaseStatsWithMana(object):

    CHAMPION_BASE_STATS = dict(
        hp=0,
        hp_per_lvl=0,

        hp5=0,
        hp5_per_lvl=0,

        mp=0,
        mp_per_lvl=0,

        mp5=0,
        mp5_per_lvl=0,

        resource_used='mp',

        attack_range=0,

        ad=0,
        ad_per_lvl=0,

        attack_speed_offset=0,
        base_att_speed=0,
        att_speed_per_lvl=0/100.,

        armor=0,
        armor_per_lvl=0,

        mr=0,
        mr_per_lvl=0,

        move_speed=0,

        # Set always to 2.
        crit_modifier=2,
        )

    def buff(self):
        return dict(
            max_stacks=0,
            _stat=dict(additive_bonus='_buff'),
            duration=0
        )
