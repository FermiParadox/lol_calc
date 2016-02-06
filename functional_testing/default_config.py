import copy


EMPTY_DATA = dict(

    selected_champions_dct=dict(
        player='',
        enemy_1='melee_creep',),

    champion_lvls_dct=dict(
        player=1,
        enemy_1=1,
        enemy_2=1,
        enemy_3=1
    ),

    ability_lvls_dct={},

    max_targets_dct={},

    max_combat_time=10,

    rotation_lst=[],
    chosen_items_dct={'player': [],
                      'enemy_1': [],
                      'enemy_2': [],
                      'enemy_3': [],
                      'enemy_4': [],
                      'enemy_5': [], },
    initial_enemies_total_stats=None,
    initial_active_buffs=None,
    initial_current_stats={},

    _reversed_combat_mode=False,

    selected_summoner_spells=[],

    selected_runes=dict(),

    selected_masteries_dct=dict(),

    enemies_originating_dmg_data=None,
)


ALL_DATA = dict(

    selected_champions_dct=dict(
        player='jax',
        enemy_1='melee_creep',),

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
    chosen_items_dct={'player': ['blade_of_the_ruined_king', 'trinity_force', 'youmuus_ghostblade', 'sunfire_cape',
                                 'guinsoos_rageblade', 'the_black_cleaver', 'last_whisper'],
                      'enemy_1': ['blade_of_the_ruined_king', 'chain_vest', 'chain_vest'],
                      'enemy_2': ['dorans_shield', 'blade_of_the_ruined_king'],
                      'enemy_3': ['dorans_shield', 'blade_of_the_ruined_king'], },
    initial_enemies_total_stats=None,
    initial_active_buffs=None,
    initial_current_stats={},

    _reversed_combat_mode=False,

    selected_summoner_spells=[
        'exhaust', 'ignite'
    ],

    selected_runes=dict(
        red=dict(
            ad_per_lvl=dict(
                additive=6))),

    selected_masteries_dct=dict(),

    enemies_originating_dmg_data=None,
)


def all_data_deepcopy():
    return copy.deepcopy(ALL_DATA)
