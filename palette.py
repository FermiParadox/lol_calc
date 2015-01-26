# Matched rune names.
API_TO_APP_STAT_NAME_MAP = dict(
    FlatMagicDamageMod=dict(additive='ap'),
    FlatSpellBlockMod=dict(additive='mr'),
    rFlatSpellBlockModPerLevel=dict(additive='mr_per_lvl'),
    rFlatArmorModPerLevel=dict(additive='armor_per_lvl'),
    FlatCritChanceMod=dict(additive='crit'),
    rFlatMagicDamageModPerLevel=dict(additive='ap_per_lvl'),
    rFlatHPModPerLevel=dict(additive='hp_per_lvl'),
    FlatMPRegenMod=dict(additive='mp5'),
    rFlatHPRegenModPerLevel=dict(additive='hp5_per_lvl'),
    PercentEXPBonus=dict(percent='xp'),
    FlatEnergyPoolMod=dict(additive='energy'),
    rFlatEnergyRegenModPerLevel=dict(additive='ep5_per_lvl'),
    rFlatGoldPer10Mod=dict(additive='gp5'),
    FlatHPPoolMod=dict(additive='hp'),
    PercentAttackSpeedMod=dict(percent='att_speed'),
    rFlatMPRegenModPerLevel=dict(additive='mp5_per_lvl'),
    rPercentTimeDeadMod=dict(additive='death_time_reduction'),
    FlatEnergyRegenMod=dict(additive='ep5'),
    PercentSpellVampMod=dict(additive='spellvamp'),
    FlatCritDamageMod=dict(additive='crit_modifier'),
    rFlatMPModPerLevel=dict(additive='mp_per_lvl'),
    rFlatArmorPenetrationMod=dict(additive='flat_armor_penetration'),
    FlatMPPoolMod=dict(additive='mp'),
    FlatPhysicalDamageMod=dict(additive='ad'),
    rFlatPhysicalDamageModPerLevel=dict(additive='ad_per_lvl'),
    FlatHPRegenMod=dict(additive='hp5'),
    PercentLifeStealMod=dict(additive='lifesteal'),
    PercentMovementSpeedMod=dict(percent='move_speed'),
    FlatArmorMod=dict(additive='armor'),
    rFlatEnergyModPerLevel=dict(additive='energy_per_lvl'),
    rFlatMagicPenetrationMod=dict(additive='flat_magic_penetration'),
    PercentHPPoolMod=dict(percent='hp'),
    rPercentCooldownModPerLevel=dict(additive='cdr_per_lvl'),
    rPercentCooldownMod=dict(additive='cdr')
)


class ChampionBase(object):

    def __init__(self):
        pass

    def abilities_effects(self):
        pass


class ChampionsStats(object):
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
