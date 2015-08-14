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

    ability_lvls_dct=dict(),

    max_targets_dct={},

    max_combat_time=10,

    rotation_lst=None,
    items_lst=['hextech_gunblade', 'hextech_gunblade'],

    selected_summoner_spells=[],

    selected_runes=dict(
        red=dict(
            ad_per_lvl=dict(
                additive=6))),

    selected_masteries_dct=dict(archmage=3))


def all_data_deepcopy():
    return copy.deepcopy(ALL_DATA)



