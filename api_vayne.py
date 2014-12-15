ABILITIES = {
   "id": 67,
   "title": "the Night Hunter",
   "name": "Vayne",
   "spells": [
      {
         "range": [
            300,
            300,
            300,
            300,
            300
         ],
         "leveltip": {
            "effect": [
               "{{ e2 }}% -> {{ e2NL }}%",
               "{{ cooldown }} -> {{ cooldownnNL }}"
            ],
            "label": [
               "Bonus Damage",
               "Cooldown"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "",
            "30/35/40/45/50",
            "6"
         ],
         "image": {
            "w": 48,
            "full": "VayneTumble.png",
            "sprite": "spell11.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 288
         },
         "cooldown": [
            6,
            5,
            4,
            3,
            2
         ],
         "cost": [
            30,
            30,
            30,
            30,
            30
         ],
         "vars": [{
            "link": "attackdamage",
            "coeff": [
               0.3,
               0.35,
               0.4,
               0.45,
               0.5
            ],
            "key": "f1"
         }],
         "sanitizedDescription": "Vayne tumbles, maneuvering to carefully place her next shot. Her next attack deals bonus damage.",
         "rangeBurn": "300",
         "costType": "Mana",
         "effect": [
            "null",
            "null",
            [
               30,
               35,
               40,
               45,
               50
            ],
            [
               6,
               6,
               6,
               6,
               6
            ]
         ],
         "cooldownBurn": "6/5/4/3/2",
         "description": "Vayne tumbles, maneuvering to carefully place her next shot. Her next attack deals bonus damage.",
         "name": "Tumble",
         "sanitizedTooltip": "Rolls a short distance. The next basic attack within {{ e3 }} seconds deals {{ f1 }} bonus physical damage, equal to {{ e2 }}% of total Attack Damage.",
         "key": "VayneTumble",
         "costBurn": "30",
         "tooltip": "Rolls a short distance. The next basic attack within {{ e3 }} seconds deals <span class=\"colorFF8C00\">{{ f1 }}<\/span> bonus physical damage, equal to {{ e2 }}% of total Attack Damage."
      },
      {
         "range": "self",
         "leveltip": {
            "effect": [
               "{{ e2 }} -> {{ e2NL }}",
               "{{ e1 }}% -> {{ e1NL }}%"
            ],
            "label": [
               "Base Damage",
               "Max Health Damage"
            ]
         },
         "resource": "Passive ",
         "maxrank": 5,
         "effectBurn": [
            "",
            "4/5/6/7/8",
            "20/30/40/50/60"
         ],
         "image": {
            "w": 48,
            "full": "VayneSilveredBolts.png",
            "sprite": "spell11.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 336
         },
         "cooldown": [
            6,
            6,
            6,
            6,
            6
         ],
         "cost": [
            55,
            60,
            65,
            70,
            75
         ],
         "sanitizedDescription": "Vayne tips her bolts with a rare metal, toxic to evil things. The third consecutive attack or ability against the same target deals a percentage of the target's maximum Health as bonus true damage. (Max: 200 damage vs. Monsters)",
         "rangeBurn": "self",
         "costType": "Passive",
         "effect": [
            "null",
            [
               4,
               5,
               6,
               7,
               8
            ],
            [
               20,
               30,
               40,
               50,
               60
            ]
         ],
         "cooldownBurn": "6",
         "description": "Vayne tips her bolts with a rare metal, toxic to evil things. The third consecutive attack or ability against the same target deals a percentage of the target's maximum Health as bonus true damage. (Max: 200 damage vs. Monsters)",
         "name": "Silver Bolts",
         "sanitizedTooltip": "Every third consecutive attack or ability against an enemy deals an additional {{ e2 }} plus {{ e1 }}% of the enemy's maximum Health as true damage. (Max: 200 damage vs. Monsters)",
         "key": "VayneSilveredBolts",
         "costBurn": "55/60/65/70/75",
         "tooltip": "Every third consecutive attack or ability against an enemy deals an additional {{ e2 }} plus {{ e1 }}% of the enemy's maximum Health as true damage. (Max: 200 damage vs. Monsters)"
      },
      {
         "range": [
            710,
            710,
            710,
            710,
            710
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e2 }} -> {{ e2NL }}",
               "{{ cooldown }} -> {{ cooldownnNL }}"
            ],
            "label": [
               "Initial Damage",
               "Collision Damage",
               "Cooldown"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "45/80/115/150/185",
            "45/80/115/150/185",
            "1.5"
         ],
         "image": {
            "w": 48,
            "full": "VayneCondemn.png",
            "sprite": "spell11.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 384
         },
         "cooldown": [
            20,
            18,
            16,
            14,
            12
         ],
         "cost": [
            90,
            90,
            90,
            90,
            90
         ],
         "vars": [{
            "link": "bonusattackdamage",
            "coeff": [0.5],
            "key": "f1"
         }],
         "sanitizedDescription": "Vayne draws a heavy crossbow from her back, and fires a huge bolt at her target, knocking them back and dealing damage. If they collide with terrain, they are impaled, dealing bonus damage and stunning them.",
         "rangeBurn": "710",
         "costType": "Mana",
         "effect": [
            "null",
            [
               45,
               80,
               115,
               150,
               185
            ],
            [
               45,
               80,
               115,
               150,
               185
            ],
            [
               1.5,
               1.5,
               1.5,
               1.5,
               1.5
            ]
         ],
         "cooldownBurn": "20/18/16/14/12",
         "description": "Vayne draws a heavy crossbow from her back, and fires a huge bolt at her target, knocking them back and dealing damage. If they collide with terrain, they are impaled, dealing bonus damage and stunning them.",
         "name": "Condemn",
         "sanitizedTooltip": "Fires a bolt that knocks back target enemy and deals {{ e1 }} (+{{ f1 }}) physical damage. Enemies that collide with terrain take {{ e2 }} (+{{ f1 }}) additional physical damage and are stunned for {{ e3 }} seconds.",
         "key": "VayneCondemn",
         "costBurn": "90",
         "tooltip": "Fires a bolt that knocks back target enemy and deals {{ e1 }} <span class=\"colorFF8C00\">(+{{ f1 }})<\/span> physical damage. Enemies that collide with terrain take {{ e2 }} <span class=\"colorFF8C00\">(+{{ f1 }})<\/span> additional physical damage and are stunned for {{ e3 }} seconds."
      },
      {
         "range": "self",
         "leveltip": {
            "effect": [
               "{{ e5 }} -> {{ e5NL }}",
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e2 }} -> {{ e2NL }}"
            ],
            "label": [
               "Cooldown",
               "<\/postScriptTitle><postScriptLeft>Bonus Attack Damage",
               "Duration"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 3,
         "effectBurn": [
            "",
            "30/50/70",
            "8/10/12",
            "1",
            "90",
            "100/85/70"
         ],
         "image": {
            "w": 48,
            "full": "VayneInquisition.png",
            "sprite": "spell11.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 432
         },
         "cooldown": [
            100,
            85,
            70
         ],
         "cost": [
            80,
            80,
            80
         ],
         "sanitizedDescription": "Readying herself for an epic confrontation, Vayne gains increased Attack Damage, invisibility during Tumble, and triple the bonus Movement Speed from Night Hunter.",
         "rangeBurn": "self",
         "costType": "Mana",
         "effect": [
            "null",
            [
               30,
               50,
               70
            ],
            [
               8,
               10,
               12
            ],
            [
               1,
               1,
               1
            ],
            [
               90,
               90,
               90
            ],
            [
               100,
               85,
               70
            ]
         ],
         "cooldownBurn": "100/85/70",
         "description": "Readying herself for an epic confrontation, Vayne gains increased Attack Damage, invisibility during Tumble, and triple the bonus Movement Speed from Night Hunter.",
         "name": "Final Hour",
         "sanitizedTooltip": "Gains {{ e1 }} Bonus Attack Damage for {{ e2 }} seconds. While active, Tumble grants invisibility for {{ e3 }} second, and Night Hunter's bonus Movement Speed is increased to {{ e4 }}.",
         "key": "VayneInquisition",
         "costBurn": "80",
         "tooltip": "Gains {{ e1 }} Bonus Attack Damage for {{ e2 }} seconds. While active, Tumble grants invisibility for {{ e3 }} second, and Night Hunter's bonus Movement Speed is increased to {{ e4 }}."
      }
   ],
   "key": "Vayne"
}