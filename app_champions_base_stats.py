CHAMPION_BASE_STATS = dict(
    jax=dict(

        stat_dependencies=dict(
            player=dict(
                armor=['ad', ], mr=['ap'])),

        hp=450,
        hp_per_lvl=85,

        hp5=7.45,
        hp5_per_lvl=0.55,

        mp=230,
        mp_per_lvl=35,

        mp5=6.4,
        mp5_per_lvl=0.7,

        resource_used='mp',

        attack_range=125,

        ad=56.3,
        ad_per_lvl=3.375,

        base_att_speed=0.638,
        att_speed_per_lvl=3.4,

        armor=22,
        armor_per_lvl=3.,

        mr=30,
        mr_per_lvl=1.25,

        move_speed=350,

        crit_modifier=2
    ),
    yasuo=dict(
        ad=50,
        move_speed=350,
        attack_range=175,
        mp=60,
        hp5_per_lvl=0.9,
        ad_per_lvl=3.2,
        hp=430,
        armor_per_lvl=3.4,
        attack_speed_offset=-0.05,
        crit_modifier=2,
        att_speed_per_lvl=3.2,
        hp_per_lvl=82,
        base_att_speed=0,
        mr=30,
        armor=19,
        hp5=5,)
)