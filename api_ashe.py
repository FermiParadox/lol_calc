ABILITIES = {
   "id": 22,
   "title": "the Frost Archer",
   "name": "Ashe",
   "spells": [
      {
         "range": "self",
         "leveltip": {
            "effect": [" {{ e1 }}% -> {{ e1NL }}%"],
            "label": ["Slow Amount"]
         },
         "resource": "{{ e3 }} Mana per Attack",
         "maxrank": 5,
         "effectBurn": [
            "",
            "15/20/25/30/35",
            "2",
            "8"
         ],
         "image": {
            "w": 48,
            "full": "FrostShot.png",
            "sprite": "spell1.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 96
         },
         "cooldown": [
            0,
            0,
            0,
            0,
            0
         ],
         "cost": [
            0,
            0,
            0,
            0,
            0
         ],
         "sanitizedDescription": "While active, each of Ashe's basic attacks slow her targets. This drains Mana with each attack.",
         "rangeBurn": "self",
         "costType": "ManaperAttack",
         "effect": [
            "null",
            [
               15,
               20,
               25,
               30,
               35
            ],
            [
               2,
               2,
               2,
               2,
               2
            ],
            [
               8,
               8,
               8,
               8,
               8
            ]
         ],
         "cooldownBurn": "0",
         "description": "While active, each of Ashe's basic attacks slow her targets. This drains Mana with each attack.",
         "name": "Frost Shot",
         "sanitizedTooltip": "Toggle: Basic attacks slow enemies by {{ e1 }}% for {{ e2 }} seconds.",
         "key": "FrostShot",
         "costBurn": "0",
         "tooltip": "<span class=\"colorFF9900\">Toggle: <\/span>Basic attacks slow enemies by {{ e1 }}% for {{ e2 }} seconds."
      },
      {
         "range": [
            600,
            600,
            600,
            600,
            600
         ],
         "leveltip": {
            "effect": [
               "{{ e2 }} -> {{ e2NL }}",
               "{{ cooldown }} -> {{ cooldownnNL }}"
            ],
            "label": [
               "Damage",
               "Cooldown"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "16/13/10/7/4",
            "40/50/60/70/80",
            "7"
         ],
         "image": {
            "w": 48,
            "full": "Volley.png",
            "sprite": "spell1.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 144
         },
         "cooldown": [
            16,
            13,
            10,
            7,
            4
         ],
         "cost": [
            60,
            60,
            60,
            60,
            60
         ],
         "vars": [{
            "link": "attackdamage",
            "coeff": [1],
            "key": "f1"
         }],
         "sanitizedDescription": "Ashe fires 7 arrows in a cone for increased damage. Volley also applies Ashe's current level of Frost Shot.",
         "rangeBurn": "600",
         "costType": "Mana",
         "effect": [
            "null",
            [
               16,
               13,
               10,
               7,
               4
            ],
            [
               40,
               50,
               60,
               70,
               80
            ],
            [
               7,
               7,
               7,
               7,
               7
            ]
         ],
         "cooldownBurn": "16/13/10/7/4",
         "description": "Ashe fires 7 arrows in a cone for increased damage. Volley also applies Ashe's current level of Frost Shot.",
         "name": "Volley",
         "sanitizedTooltip": "Fires arrows in a cone, dealing {{ e2 }} (+{{ f1 }}) physical damage. Volley applies Frost Shot's slow effect.",
         "key": "Volley",
         "costBurn": "60",
         "tooltip": "Fires arrows in a cone, dealing {{ e2 }} <span class=\"colorFF8C00\">(+{{ f1 }})<\/span> physical damage. Volley applies Frost Shot's slow effect."
      },
      {
         "range": [
            2500,
            3250,
            4000,
            4750,
            5500
         ],
         "leveltip": {
            "effect": [
               " {{ cooldown }} -> {{ cooldownnNL }}",
               " {{ e3 }} -> {{ e3NL }}"
            ],
            "label": [
               "Cooldown",
               "Range"
            ]
         },
         "resource": "No Cost",
         "maxrank": 5,
         "effectBurn": [
            "",
            "3",
            "50/90/130/170/210",
            "2500/3250/4000/4750/5500"
         ],
         "image": {
            "w": 48,
            "full": "AsheSpiritOfTheHawk.png",
            "sprite": "spell1.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 192
         },
         "cooldown": [
            60,
            55,
            50,
            45,
            40
         ],
         "cost": [
            0,
            0,
            0,
            0,
            0
         ],
         "vars": [{
            "link": "@stacks",
            "coeff": [
               1,
               2,
               3,
               4,
               5
            ],
            "key": "f1"
         }],
         "sanitizedDescription": "Ashe gains bonus Gold when killing enemy units or structures. Ashe can activate to send her Hawk Spirit on a scouting mission.",
         "rangeBurn": "2500/3250/4000/4750/5500",
         "costType": "NoCost",
         "effect": [
            "null",
            [
               3,
               3,
               3,
               3,
               3
            ],
            [
               50,
               90,
               130,
               170,
               210
            ],
            [
               2500,
               3250,
               4000,
               4750,
               5500
            ]
         ],
         "cooldownBurn": "60/55/50/45/40",
         "description": "Ashe gains bonus Gold when killing enemy units or structures. Ashe can activate to send her Hawk Spirit on a scouting mission.",
         "name": "Hawkshot",
         "sanitizedTooltip": "Passive: Gains {{ e1 }} bonus Gold whenever Ashe kills an enemy unit or structure. Active: Reveals terrain as it flies toward target location. Grants vision for 5 seconds. Total Gold Retrieved: {{ f1 }} gold.",
         "key": "AsheSpiritOfTheHawk",
         "costBurn": "0",
         "tooltip": "<span class=\"colorFF9900\">Passive: <\/span>Gains {{ e1 }} bonus Gold whenever Ashe kills an enemy unit or structure.<br><br><span class=\"colorFF9900\">Active: <\/span>Reveals terrain as it flies toward target location. Grants vision for 5 seconds.<br><br><span class=\"colorFF9900\">Total Gold Retrieved: <\/span>{{ f1 }} gold."
      },
      {
         "range": [
            20000,
            20000,
            20000
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ cooldown }} -> {{ cooldownnNL }}"
            ],
            "label": [
               "Damage",
               "Cooldown"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 3,
         "effectBurn": [
            "",
            "250/425/600",
            "3.5",
            "50",
            "3"
         ],
         "image": {
            "w": 48,
            "full": "EnchantedCrystalArrow.png",
            "sprite": "spell1.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 240
         },
         "cooldown": [
            100,
            90,
            80
         ],
         "cost": [
            100,
            100,
            100
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [1],
            "key": "a1"
         }],
         "sanitizedDescription": "Ashe fires a missile of ice in a straight line. If the arrow collides with an enemy Champion, it deals damage and stuns the Champion for up to 3.5 seconds, based on how far the arrow has traveled. In addition, surrounding enemy units take damage and are slowed.",
         "rangeBurn": "20000",
         "costType": "Mana",
         "effect": [
            "null",
            [
               250,
               425,
               600
            ],
            [
               3.5,
               3.5,
               3.5
            ],
            [
               50,
               50,
               50
            ],
            [
               3,
               3,
               3
            ]
         ],
         "cooldownBurn": "100/90/80",
         "description": "Ashe fires a missile of ice in a straight line. If the arrow collides with an enemy Champion, it deals damage and stuns the Champion for up to 3.5 seconds, based on how far the arrow has traveled. In addition, surrounding enemy units take damage and are slowed.",
         "name": "Enchanted Crystal Arrow",
         "sanitizedTooltip": "Launches a crystal arrow of ice in a line that stuns an enemy Champion dealing {{ e1 }} (+{{ a1 }}) magic damage. The farther the arrow flies, the longer the stun, up to {{ e2 }} seconds. Surrounding enemies are slowed by {{ e3 }}% for {{ e4 }} seconds and take half damage.",
         "key": "EnchantedCrystalArrow",
         "costBurn": "100",
         "tooltip": "Launches a crystal arrow of ice in a line that stuns an enemy Champion dealing {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> magic damage. The farther the arrow flies, the longer the stun, up to {{ e2 }} seconds. Surrounding enemies are slowed by {{ e3 }}% for {{ e4 }} seconds and take half damage."
      }
   ],
   "key": "Ashe"
}