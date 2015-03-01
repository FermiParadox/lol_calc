s = """

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
"""

import re

m = re.findall(r'\'(\w+)\'', s)

print(m)
for i in m:
    print(i)