import copy


ALL_DATA = dict(

    selected_champions_dct=dict(
        player='jax',
        enemy_1='jax',
        enemy_2='jax',
        enemy_3='jax'),

    champion_lvls_dct=dict(
        player=18,
        enemy_1=18,
        enemy_2=17,
        enemy_3=16
    ),

    ability_lvls_dct={},

    max_targets_dct={},

    max_combat_time=10,

    rotation_lst=[],
    chosen_items_dct={'player': ['hextech_gunblade', 'wits_end', 'dorans_blade', 'crystalline_bracer'],
                      'enemy_1': ['hextech_gunblade'],
                      'enemy_2': ['dorans_shield', 'hextech_gunblade'],
                      'enemy_3': ['dorans_shield', 'hextech_gunblade'],},
    initial_enemies_total_stats=None,
    initial_active_buffs=None,
    initial_current_stats={},
    
    _reversed_combat_mode=False,

    selected_summoner_spells=[],

    selected_runes=dict(
        red=dict(
            ad_per_lvl=dict(
                additive=6))),

    selected_masteries_dct=dict(archmage=3),

    enemies_originating_dmg_data=None,
)


def all_data_deepcopy():
    return copy.deepcopy(ALL_DATA)



