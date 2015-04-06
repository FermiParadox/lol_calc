import json
obj_name = 'MY_DCT = '
obj_body_as_dct = MY_DCT = {
    "buffs": {
        "e_dmg_red": {
            "target_type": "player",
            "affected_stats": {
                "aoe_dmg_reduction": {
                    "stat_values": 0.25,
                    "stat_mods": {},
                    "bonus_type": "percent"
                },
                "aa_dmg_reduction": {
                    "stat_values": 1.0,
                    "stat_mods": {},
                    "bonus_type": "percent"
                }
            },
            "max_stacks": 1,
            "on_hit": null,
            "duration": 2,
            "prohibit_cd_start": null
        },
        "r_n_hit_initiator": {
            "target_type": "player",
            "affected_stats": null,
            "max_stacks": 1,
            "on_hit": {
                "remove_buff": [],
                "apply_buff": [
                    "r_hit_counter"
                ],
                "add_dmg": [],
                "reduce_cd": {}
            },
            "duration": "permanent",
            "prohibit_cd_start": null
        },
        "r_hit_counter": {
            "target_type": "player",
            "affected_stats": null,
            "max_stacks": 3,
            "on_hit": null,
            "duration": 5,
            "prohibit_cd_start": null
        },
        "w_buff_0": {
            "target_type": "player",
            "affected_stats": null,
            "max_stacks": 1,
            "on_hit": null,
            "duration": 7,
            "prohibit_cd_start": "w"
        },
        "r_dmg_red": {
            "target_type": "player",
            "affected_stats": {
                "mr": {
                    "stat_values": [
                        20.0,
                        35.0,
                        50.0
                    ],
                    "stat_mods": {
                        "ap": [
                            0.3
                        ]
                    },
                    "bonus_type": "additive"
                },
                "armor": {
                    "stat_values": [
                        20.0,
                        35.0,
                        50.0
                    ],
                    "stat_mods": null,
                    "bonus_type": "additive"
                }
            },
            "max_stacks": 1,
            "on_hit": null,
            "duration": 8,
            "prohibit_cd_start": null
        },
        "e_stun": {
            "target_type": "enemy",
            "affected_stats": null,
            "max_stacks": 1,
            "on_hit": null,
            "duration": 1,
            "prohibit_cd_start": null
        }
    },
    "general_attributes": {
        "inn": {},
        "r": {
            "castable": true,
            "cost": {
                "stack_cost": null,
                "standard_cost": {
                    "COST CATEGORY": "normal",
                    "resource_type": "mp",
                    "values": [
                        100,
                        100,
                        100
                    ]
                }
            },
            "dashed_distance": null,
            "toggled": false,
            "cast_time": 0,
            "base_cd": [
                80.0,
                80.0,
                80.0
            ],
            "resets_aa": false,
            "range": 0,
            "channel_time": null,
            "independent_cast": false,
            "move_while_casting": true,
            "travel_time": 0,
            "reduces_ability_cd": null
        },
        "e": {
            "castable": true,
            "cost": {
                "stack_cost": null,
                "standard_cost": {
                    "COST CATEGORY": "normal",
                    "resource_type": "mp",
                    "values": [
                        70,
                        75,
                        80,
                        85,
                        90
                    ]
                }
            },
            "dashed_distance": null,
            "toggled": false,
            "cast_time": 0,
            "base_cd": [
                16.0,
                14.0,
                12.0,
                10.0,
                8.0
            ],
            "resets_aa": false,
            "range": 0,
            "channel_time": null,
            "independent_cast": false,
            "move_while_casting": true,
            "travel_time": 0,
            "reduces_ability_cd": null
        },
        "w": {
            "castable": true,
            "cost": {
                "stack_cost": null,
                "standard_cost": {
                    "COST CATEGORY": "normal",
                    "resource_type": "mp",
                    "values": [
                        30,
                        30,
                        30,
                        30,
                        30
                    ]
                }
            },
            "dashed_distance": null,
            "toggled": false,
            "cast_time": 0,
            "base_cd": [
                7.0,
                6.0,
                5.0,
                4.0,
                3.0
            ],
            "resets_aa": true,
            "range": 0,
            "channel_time": null,
            "independent_cast": false,
            "move_while_casting": true,
            "travel_time": 0,
            "reduces_ability_cd": null
        },
        "q": {
            "castable": true,
            "cost": {
                "stack_cost": null,
                "standard_cost": {
                    "COST CATEGORY": "normal",
                    "resource_type": "mp",
                    "values": [
                        65,
                        65,
                        65,
                        65,
                        65
                    ]
                }
            },
            "dashed_distance": 600,
            "toggled": false,
            "cast_time": 0.25,
            "base_cd": [
                10.0,
                9.0,
                8.0,
                7.0,
                6.0
            ],
            "resets_aa": false,
            "range": [
                700,
                700,
                700,
                700,
                700
            ],
            "channel_time": null,
            "independent_cast": false,
            "move_while_casting": false,
            "travel_time": 0,
            "reduces_ability_cd": null
        }
    },
    "dmgs": {
        "w_dmg_0": {
            "delay": 0,
            "dmg_category": "standard_dmg",
            "dmg_values": [
                40.0,
                75.0,
                110.0,
                145.0,
                180.0
            ],
            "dot": false,
            "life_conversion_type": "spellvamp",
            "mods": {
                "enemy": {},
                "player": {
                    "ap": 0.6
                }
            },
            "dmg_type": "magic",
            "radius": null,
            "dmg_source": "w",
            "target_type": "enemy",
            "usual_max_targets": 1,
            "max_targets": 1
        },
        "r_dmg_0": {
            "delay": 0,
            "dmg_category": "standard_dmg",
            "dmg_values": [
                100.0,
                160.0,
                220.0
            ],
            "dot": false,
            "life_conversion_type": "spellvamp",
            "mods": {
                "enemy": {},
                "player": {
                    "ap": 0.7
                }
            },
            "dmg_type": "magic",
            "radius": null,
            "dmg_source": "r",
            "target_type": "enemy",
            "usual_max_targets": 1,
            "max_targets": 1
        },
        "e_dmg_0": {
            "delay": 0,
            "dmg_category": "standard_dmg",
            "dmg_values": [
                1.0,
                1.0,
                1.0,
                1.0,
                1.0
            ],
            "dot": false,
            "life_conversion_type": "spellvamp",
            "mods": {
                "enemy": {},
                "player": {
                    "bonus_ad": 0.5
                }
            },
            "dmg_type": "physical",
            "radius": 150,
            "dmg_source": "e",
            "target_type": "enemy",
            "usual_max_targets": 2,
            "max_targets": 5
        },
        "q_dmg_0": {
            "delay": 0,
            "dmg_category": "standard_dmg",
            "dmg_values": [
                70.0,
                110.0,
                150.0,
                190.0,
                230.0
            ],
            "dot": false,
            "life_conversion_type": "spellvamp",
            "mods": {
                "enemy": {},
                "player": {
                    "ap": 0.6,
                    "bonus_ad": 1.0
                }
            },
            "dmg_type": "physical",
            "radius": null,
            "dmg_source": "q",
            "target_type": "enemy",
            "usual_max_targets": 1,
            "max_targets": 1
        }
    }
}

stringy = "\"\"\"" + obj_name + "{" + str(json.dumps(obj_body_as_dct, indent=4, separators=(',', ': ')))[1:] + "\"\"\""
print(stringy)