ABILITIES = {
   "id": 23,
   "title": "the Barbarian King",
   "name": "Tryndamere",
   "spells": [
      {
         "range": "self",
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e2 }} -> {{ e2NL }}",
               "{{ e3 }} -> {{ e3NL }}",
               "{{ e4 }} -> {{ e4NL }}"
            ],
            "label": [
               "Attack Damage",
               "Attack Damage per Health % Missing",
               "Heal",
               "Heal Per Fury"
            ]
         },
         "resource": "No Cost",
         "maxrank": 5,
         "effectBurn": [
            "",
            "5/10/15/20/25",
            "0.15/0.2/0.25/0.3/0.35",
            "30/40/50/60/70",
            "0.5/0.95/1.4/1.85/2.3",
            "2"
         ],
         "image": {
            "w": 48,
            "full": "Bloodlust.png",
            "sprite": "spell10.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 96
         },
         "cooldown": [
            12,
            12,
            12,
            12,
            12
         ],
         "cost": [
            0,
            0,
            0,
            0,
            0
         ],
         "vars": [
            {
               "link": "spelldamage",
               "coeff": [0.3],
               "key": "a1"
            },
            {
               "link": "spelldamage",
               "coeff": [1.2],
               "key": "f2"
            }
         ],
         "sanitizedDescription": "Tryndamere thrives on the thrills of combat, increasing his Attack Damage as he is more and more wounded. He can cast Bloodlust to consume his Fury and heal himself.",
         "rangeBurn": "self",
         "costType": "NoCost",
         "effect": [
            "null",
            [
               5,
               10,
               15,
               20,
               25
            ],
            [
               0.15,
               0.2,
               0.25,
               0.3,
               0.35
            ],
            [
               30,
               40,
               50,
               60,
               70
            ],
            [
               0.5,
               0.95,
               1.4,
               1.85,
               2.3
            ],
            [
               2,
               2,
               2,
               2,
               2
            ]
         ],
         "cooldownBurn": "12",
         "description": "Tryndamere thrives on the thrills of combat, increasing his Attack Damage as he is more and more wounded. He can cast Bloodlust to consume his Fury and heal himself.",
         "name": "Bloodlust",
         "sanitizedTooltip": "Passive: Tryndamere thirsts for blood, gaining {{ e1 }} Attack Damage plus {{ e2 }} per 1% Health missing. Active: Tryndamere consumes his Fury, restoring {{ e3 }} (+{{ a1 }}) Health, plus {{ e4 }} (+{{ f2 }}) Health per Fury consumed.",
         "key": "Bloodlust",
         "costBurn": "0",
         "tooltip": "<span class=\"colorFF9900\">Passive: <\/span>Tryndamere thirsts for blood, gaining {{ e1 }} Attack Damage plus {{ e2 }} per 1% Health missing.<br><br><span class=\"colorFF9900\">Active: <\/span>Tryndamere consumes his Fury, restoring {{ e3 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> Health, plus {{ e4 }} <span class=\"color99FF99\"> (+{{ f2 }}) <\/span>Health per Fury consumed."
      },
      {
         "range": [
            850,
            850,
            850,
            850,
            850
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e2 }}% -> {{ e2NL }}%"
            ],
            "label": [
               "Attack Damage Reduction",
               "Movement Speed Reduction"
            ]
         },
         "resource": "No Cost",
         "maxrank": 5,
         "effectBurn": [
            "",
            "20/35/50/65/80",
            "30/37.5/45/52.5/60",
            "25",
            "4"
         ],
         "image": {
            "w": 48,
            "full": "MockingShout.png",
            "sprite": "spell10.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 144
         },
         "cooldown": [
            14,
            14,
            14,
            14,
            14
         ],
         "cost": [
            0,
            0,
            0,
            0,
            0
         ],
         "sanitizedDescription": "Tryndamere lets out an insulting cry, decreasing surrounding champions' Attack Damage. Enemies with their backs turned to Tryndamere also have their Movement Speed reduced.",
         "rangeBurn": "850",
         "costType": "NoCost",
         "effect": [
            "null",
            [
               20,
               35,
               50,
               65,
               80
            ],
            [
               30,
               37.5,
               45,
               52.5,
               60
            ],
            [
               25,
               25,
               25,
               25,
               25
            ],
            [
               4,
               4,
               4,
               4,
               4
            ]
         ],
         "cooldownBurn": "14",
         "description": "Tryndamere lets out an insulting cry, decreasing surrounding champions' Attack Damage. Enemies with their backs turned to Tryndamere also have their Movement Speed reduced.",
         "name": "Mocking Shout",
         "sanitizedTooltip": "Decreases surrounding champions' Attack Damage by {{ e1 }} for {{ e4 }} seconds, and enemies with their backs turned also have their Movement Speed reduced by {{ e2 }}%.",
         "key": "MockingShout",
         "costBurn": "0",
         "tooltip": "Decreases surrounding champions' Attack Damage by {{ e1 }} for {{ e4 }} seconds, and enemies with their backs turned also have their Movement Speed reduced by {{ e2 }}%."
      },
      {
         "range": [
            650,
            650,
            650,
            650,
            650
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ cooldown }} -> {{ cooldownnNL }}"
            ],
            "label": [
               "Base Damage",
               "Cooldown"
            ]
         },
         "resource": "No Cost",
         "maxrank": 5,
         "effectBurn": [
            "",
            "70/100/130/160/190",
            "40/50/60/70/80",
            "2"
         ],
         "image": {
            "w": 48,
            "full": "slashCast.png",
            "sprite": "spell10.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 192
         },
         "cooldown": [
            13,
            12,
            11,
            10,
            9
         ],
         "cost": [
            0,
            0,
            0,
            0,
            0
         ],
         "vars": [
            {
               "link": "bonusattackdamage",
               "coeff": [1.2],
               "key": "f1"
            },
            {
               "link": "spelldamage",
               "coeff": [1],
               "key": "a1"
            }
         ],
         "sanitizedDescription": "Tryndamere slices toward a target unit, dealing damage to enemies in his path.",
         "rangeBurn": "650",
         "costType": "NoCost",
         "effect": [
            "null",
            [
               70,
               100,
               130,
               160,
               190
            ],
            [
               40,
               50,
               60,
               70,
               80
            ],
            [
               2,
               2,
               2,
               2,
               2
            ]
         ],
         "cooldownBurn": "13/12/11/10/9",
         "description": "Tryndamere slices toward a target unit, dealing damage to enemies in his path.",
         "name": "Spinning Slash",
         "sanitizedTooltip": "Tryndamere spins through his enemies, dealing {{ e1 }} (+{{ f1 }}) (+{{ a1 }}) physical damage to enemies in his path and generating Fury. Spinning Slash's cooldown is reduced by 1 second whenever Tryndamere critically strikes. This effect is doubled against champions.",
         "key": "slashCast",
         "costBurn": "0",
         "tooltip": "Tryndamere spins through his enemies, dealing {{ e1 }} <span class=\"colorFF8C00\">(+{{ f1 }})<\/span> <span class=\"color99FF99\">(+{{ a1 }})<\/span> physical damage to enemies in his path and generating Fury.<br><br>Spinning Slash's cooldown is reduced by 1 second whenever Tryndamere critically strikes. This effect is doubled against champions."
      },
      {
         "range": "self",
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ cooldown }} -> {{ cooldownnNL }}"
            ],
            "label": [
               "Fury Gained",
               "Cooldown"
            ]
         },
         "resource": "No Cost",
         "maxrank": 3,
         "effectBurn": [
            "",
            "50/75/100",
            "1",
            "5"
         ],
         "image": {
            "w": 48,
            "full": "UndyingRage.png",
            "sprite": "spell10.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 240
         },
         "cooldown": [
            110,
            100,
            90
         ],
         "cost": [
            0,
            0,
            0
         ],
         "sanitizedDescription": "Tryndamere's lust for battle becomes so strong that he is unable to die, no matter how wounded he becomes.",
         "rangeBurn": "self",
         "costType": "NoCost",
         "effect": [
            "null",
            [
               50,
               75,
               100
            ],
            [
               1,
               1,
               1
            ],
            [
               5,
               5,
               5
            ]
         ],
         "cooldownBurn": "110/100/90",
         "description": "Tryndamere's lust for battle becomes so strong that he is unable to die, no matter how wounded he becomes.",
         "name": "Undying Rage",
         "sanitizedTooltip": "Tryndamere becomes completely immune to death for {{ e3 }} seconds, refusing to be reduced below {{ e2 }} Health and instantly gaining {{ e1 }} Fury.",
         "key": "UndyingRage",
         "costBurn": "0",
         "tooltip": "Tryndamere becomes completely immune to death for {{ e3 }} seconds, refusing to be reduced below {{ e2 }} Health and instantly gaining {{ e1 }} Fury."
      }
   ],
   "key": "Tryndamere"
}