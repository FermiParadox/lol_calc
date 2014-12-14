ABILITIES = {
   "id": 17,
   "title": "the Swift Scout",
   "name": "Teemo",
   "spells": [
      {
         "range": [
            680,
            680,
            680,
            680,
            680
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               " {{ e2 }} -> {{ e2NL }}",
               " {{ cost }} -> {{ costnNL }}"
            ],
            "label": [
               "Damage",
               "Duration",
               "Mana Cost"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "80/125/170/215/260",
            "1.5/1.75/2/2.25/2.5"
         ],
         "image": {
            "w": 48,
            "full": "BlindingDart.png",
            "sprite": "spell10.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 288
         },
         "cooldown": [
            8,
            8,
            8,
            8,
            8
         ],
         "cost": [
            70,
            80,
            90,
            100,
            110
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.8],
            "key": "a1"
         }],
         "sanitizedDescription": "Obscures an enemy's vision with a powerful venom, dealing damage to the target unit and blinding it for the duration.",
         "rangeBurn": "680",
         "costType": "Mana",
         "effect": [
            "null",
            [
               80,
               125,
               170,
               215,
               260
            ],
            [
               1.5,
               1.75,
               2,
               2.25,
               2.5
            ]
         ],
         "cooldownBurn": "8",
         "description": "Obscures an enemy's vision with a powerful venom, dealing damage to the target unit and blinding it for the duration.",
         "name": "Blinding Dart",
         "sanitizedTooltip": "Deals {{ e1 }} (+{{ a1 }}) magic damage and blinds the target for {{ e2 }} seconds.",
         "key": "BlindingDart",
         "costBurn": "70/80/90/100/110",
         "tooltip": "Deals {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> magic damage and blinds the target for {{ e2 }} seconds. "
      },
      {
         "range": "self",
         "leveltip": {
            "effect": [" {{ e1 }}% -> {{ e1NL }}%"],
            "label": ["Base Movement Speed Bonus"]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "10/14/18/22/26"
         ],
         "image": {
            "w": 48,
            "full": "MoveQuick.png",
            "sprite": "spell10.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 336
         },
         "cooldown": [
            17,
            17,
            17,
            17,
            17
         ],
         "cost": [
            40,
            40,
            40,
            40,
            40
         ],
         "sanitizedDescription": "Teemo scampers around, passively increasing his Movement Speed until he is struck by an enemy champion or turret. Teemo can sprint to gain bonus Movement Speed that isn't stopped by being struck for a short time.",
         "rangeBurn": "self",
         "costType": "Mana",
         "effect": [
            "null",
            [
               10,
               14,
               18,
               22,
               26
            ]
         ],
         "cooldownBurn": "17",
         "description": "Teemo scampers around, passively increasing his Movement Speed until he is struck by an enemy champion or turret. Teemo can sprint to gain bonus Movement Speed that isn't stopped by being struck for a short time.",
         "name": "Move Quick",
         "sanitizedTooltip": "Passive: Teemo's Movement Speed is increased by {{ e1 }}% unless he has been damaged by an enemy champion or turret in the last 5 seconds. Active: Teemo sprints, gaining twice his normal bonus for 3 seconds. This bonus is not lost when struck.",
         "key": "MoveQuick",
         "costBurn": "40",
         "tooltip": "<span class=\"colorFF9900\">Passive: <\/span>Teemo's Movement Speed is increased by {{ e1 }}% unless he has been damaged by an enemy champion or turret in the last 5 seconds.<br><br><span class=\"colorFF9900\">Active: <\/span>Teemo sprints, gaining twice his normal bonus for 3 seconds. This bonus is not lost when struck."
      },
      {
         "range": "self",
         "leveltip": {
            "effect": [
               " {{ e3 }} -> {{ e3NL }}",
               " {{ e1 }} -> {{ e1NL }}"
            ],
            "label": [
               "Impact Damage",
               "Damage per Second "
            ]
         },
         "resource": "Passive ",
         "maxrank": 5,
         "effectBurn": [
            "",
            "6/12/18/24/30",
            "65/90/115/140/165",
            "10/20/30/40/50"
         ],
         "image": {
            "w": 48,
            "full": "ToxicShot.png",
            "sprite": "spell10.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 384
         },
         "cooldown": [
            8,
            8,
            8,
            8,
            8
         ],
         "cost": [
            30,
            35,
            40,
            45,
            50
         ],
         "vars": [
            {
               "link": "spelldamage",
               "coeff": [0.3],
               "key": "a1"
            },
            {
               "link": "spelldamage",
               "coeff": [0.1],
               "key": "a2"
            }
         ],
         "sanitizedDescription": "Each of Teemo's attacks will poison the target, dealing damage on impact and each second after for 4 seconds.",
         "rangeBurn": "self",
         "costType": "Passive",
         "effect": [
            "null",
            [
               6,
               12,
               18,
               24,
               30
            ],
            [
               65,
               90,
               115,
               140,
               165
            ],
            [
               10,
               20,
               30,
               40,
               50
            ]
         ],
         "cooldownBurn": "8",
         "description": "Each of Teemo's attacks will poison the target, dealing damage on impact and each second after for 4 seconds.",
         "name": "Toxic Shot",
         "sanitizedTooltip": "Teemo's basic attacks poison their target, dealing {{ e3 }} (+{{ a1 }}) magical damage upon impact and {{ e1 }} (+{{ a2 }}) magical damage each second for 4 seconds.",
         "key": "ToxicShot",
         "costBurn": "30/35/40/45/50",
         "tooltip": "Teemo's basic attacks poison their target, dealing {{ e3 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> magical damage upon impact and {{ e1 }} <span class=\"color99FF99\">(+{{ a2 }})<\/span> magical damage each second for 4 seconds."
      },
      {
         "range": [
            230,
            230,
            230
         ],
         "leveltip": {
            "effect": [
               " {{ e1 }} -> {{ e1NL }}",
               " {{ e2 }}% -> {{ e2NL }}%",
               "{{ e3 }} -> {{ e3NL }} ",
               "{{ f1 }} -> {{ f2 }} "
            ],
            "label": [
               "Damage ",
               "Slow Percent ",
               "Mana Cost ",
               "Forage Timer"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 3,
         "effectBurn": [
            "",
            "200/325/450",
            "30/40/50",
            "75/100/125",
            "30/26/22",
            "10"
         ],
         "image": {
            "w": 48,
            "full": "BantamTrap.png",
            "sprite": "spell10.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 432
         },
         "cooldown": [
            1,
            1,
            1
         ],
         "cost": [
            75,
            100,
            125
         ],
         "vars": [
            {
               "link": "spelldamage",
               "coeff": [0.5],
               "key": "a1"
            },
            {
               "link": "@cooldownchampion",
               "coeff": [
                  35,
                  31,
                  27
               ],
               "key": "f1"
            },
            {
               "link": "@cooldownchampion",
               "coeff": [
                  31,
                  27
               ],
               "key": "f2"
            }
         ],
         "sanitizedDescription": "Teemo places an explosive poisonous trap using one of the mushrooms stored in his pack. If an enemy steps on the trap, it will release a poisonous cloud, slowing enemies and damaging them over time.",
         "rangeBurn": "230",
         "costType": "Mana",
         "effect": [
            "null",
            [
               200,
               325,
               450
            ],
            [
               30,
               40,
               50
            ],
            [
               75,
               100,
               125
            ],
            [
               30,
               26,
               22
            ],
            [
               10,
               10,
               10
            ]
         ],
         "cooldownBurn": "1",
         "description": "Teemo places an explosive poisonous trap using one of the mushrooms stored in his pack. If an enemy steps on the trap, it will release a poisonous cloud, slowing enemies and damaging them over time.",
         "name": "Noxious Trap",
         "sanitizedTooltip": "Uses a stored mushroom to place a trap that detonates if an enemy steps on it, spreading poison to nearby enemies that slows Movement Speed by {{ e2 }}% and deals {{ e1 }} (+{{ a1 }}) magic damage over 4 seconds. Traps last {{ e5 }} minutes. Teemo forages for a mushroom every {{ f1 }} seconds, but he is only big enough to carry 3 at once.",
         "key": "BantamTrap",
         "costBurn": "75/100/125",
         "tooltip": "Uses a stored mushroom to place a trap that detonates if an enemy steps on it, spreading poison to nearby enemies that slows Movement Speed by {{ e2 }}% and deals {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> magic damage over 4 seconds. Traps last {{ e5 }} minutes.<br><br>Teemo forages for a mushroom every <span class=\"colorFFFFFF\">{{ f1 }}<\/span> seconds, but he is only big enough to carry 3 at once."
      }
   ],
   "key": "Teemo"
}