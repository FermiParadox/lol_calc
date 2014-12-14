ABILITIES = {
   "id": 84,
   "title": "the Fist of Shadow",
   "name": "Akali",
   "spells": [
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
               "{{ e5 }} -> {{ e5NL }}",
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e2 }} -> {{ e2NL }}",
               "{{ cooldown }} -> {{ cooldownnNL }}"
            ],
            "label": [
               "Initial Damage",
               "Secondary Damage",
               "Energy Return",
               "Cooldown"
            ]
         },
         "resource": "{{ cost }} Energy",
         "maxrank": 5,
         "effectBurn": [
            "",
            "45/70/95/120/145",
            "20/25/30/35/40",
            "6/5.5/5/4.5/4",
            "6",
            "35/55/75/95/115"
         ],
         "image": {
            "w": 48,
            "full": "AkaliMota.png",
            "sprite": "spell0.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 48
         },
         "cooldown": [
            6,
            5.5,
            5,
            4.5,
            4
         ],
         "cost": [
            60,
            60,
            60,
            60,
            60
         ],
         "vars": [
            {
               "link": "spelldamage",
               "coeff": [0.4],
               "key": "a1"
            },
            {
               "link": "spelldamage",
               "coeff": [0.5],
               "key": "a2"
            }
         ],
         "sanitizedDescription": "Akali spins her kama at a target enemy to deal Magic Damage and mark the target for 6 seconds. Akali's melee attacks against a marked target will trigger and consume the mark to cause additional damage and restore Energy.",
         "rangeBurn": "600",
         "costType": "Energy",
         "effect": [
            "null",
            [
               45,
               70,
               95,
               120,
               145
            ],
            [
               20,
               25,
               30,
               35,
               40
            ],
            [
               6,
               5.5,
               5,
               4.5,
               4
            ],
            [
               6,
               6,
               6,
               6,
               6
            ],
            [
               35,
               55,
               75,
               95,
               115
            ]
         ],
         "cooldownBurn": "6/5.5/5/4.5/4",
         "description": "Akali spins her kama at a target enemy to deal Magic Damage and mark the target for 6 seconds. Akali's melee attacks against a marked target will trigger and consume the mark to cause additional damage and restore Energy.",
         "name": "Mark of the Assassin",
         "sanitizedTooltip": "Akali throws her kama at a target enemy to deal {{ e5 }} (+{{ a1 }}) Magic Damage and mark the target for {{ e4 }} seconds. Akali's melee attacks against a marked target will consume the mark to cause {{ e1 }} (+{{ a2 }}) Magic Damage and restore {{ e2 }} Energy.",
         "key": "AkaliMota",
         "costBurn": "60",
         "tooltip": "Akali throws her kama at a target enemy to deal {{ e5 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> Magic Damage and mark the target for {{ e4 }} seconds.<br><br>Akali's melee attacks against a marked target will consume the mark to cause {{ e1 }} <span class=\"color99FF99\">(+{{ a2 }})<\/span> Magic Damage and restore {{ e2 }} Energy."
      },
      {
         "range": [
            700,
            700,
            700,
            700,
            700
         ],
         "leveltip": {
            "effect": [
               "{{ e2 }}% -> {{ e2NL }}%",
               "{{ e3 }}% -> {{ e3NL }}%",
               "{{ cost }} -> {{ costnNL }}"
            ],
            "label": [
               "Movement Speed Bonus",
               "Slow Amount",
               "Energy Cost"
            ]
         },
         "resource": "{{ cost }} Energy",
         "maxrank": 5,
         "effectBurn": [
            "",
            "8",
            "20/40/60/80/100",
            "14/18/22/26/30"
         ],
         "image": {
            "w": 48,
            "full": "AkaliSmokeBomb.png",
            "sprite": "spell0.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 96
         },
         "cooldown": [
            20,
            20,
            20,
            20,
            20
         ],
         "cost": [
            80,
            75,
            70,
            65,
            60
         ],
         "sanitizedDescription": "Akali throws down a cover of smoke. While inside the area, Akali becomes invisible and gains a short burst of Movement Speed. Attacking or using abilities will briefly reveal her. Enemies inside the smoke have their Movement Speed reduced.",
         "rangeBurn": "700",
         "costType": "Energy",
         "effect": [
            "null",
            [
               8,
               8,
               8,
               8,
               8
            ],
            [
               20,
               40,
               60,
               80,
               100
            ],
            [
               14,
               18,
               22,
               26,
               30
            ]
         ],
         "cooldownBurn": "20",
         "description": "Akali throws down a cover of smoke. While inside the area, Akali becomes invisible and gains a short burst of Movement Speed. Attacking or using abilities will briefly reveal her. Enemies inside the smoke have their Movement Speed reduced.",
         "name": "Twilight Shroud",
         "sanitizedTooltip": "Akali throws down a cover of smoke that lasts for {{ e1 }} seconds. While inside the area, Akali becomes invisible and gains a {{ e2 }}% burst of Movement Speed which decays over 1 second. Attacking or using abilities will briefly reveal her. Enemies inside the smoke are slowed by {{ e3 }}%.",
         "key": "AkaliSmokeBomb",
         "costBurn": "80/75/70/65/60",
         "tooltip": "Akali throws down a cover of smoke that lasts for {{ e1 }} seconds. While inside the area, Akali becomes invisible and gains a {{ e2 }}% burst of Movement Speed which decays over 1 second. Attacking or using abilities will briefly reveal her.<br><br>Enemies inside the smoke are slowed by {{ e3 }}%."
      },
      {
         "range": [
            325,
            325,
            325,
            325,
            325
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ cooldown }} -> {{ cooldownnNL }}",
               "{{ cost }} -> {{ costnNL }}"
            ],
            "label": [
               "Base Damage",
               "Cooldown",
               "Energy Cost"
            ]
         },
         "resource": "{{ cost }} Energy",
         "maxrank": 5,
         "effectBurn": [
            "",
            "30/55/80/105/130",
            "30",
            "60"
         ],
         "image": {
            "w": 48,
            "full": "AkaliShadowSwipe.png",
            "sprite": "spell0.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 144
         },
         "cooldown": [
            7,
            6,
            5,
            4,
            3
         ],
         "cost": [
            60,
            55,
            50,
            45,
            40
         ],
         "vars": [
            {
               "link": "attackdamage",
               "coeff": [0.6],
               "key": "f1"
            },
            {
               "link": "spelldamage",
               "coeff": [0.3],
               "key": "a1"
            }
         ],
         "sanitizedDescription": "Akali flourishes her kamas, dealing damage based on her Attack Damage and Ability Power.",
         "rangeBurn": "325",
         "costType": "Energy",
         "effect": [
            "null",
            [
               30,
               55,
               80,
               105,
               130
            ],
            [
               30,
               30,
               30,
               30,
               30
            ],
            [
               60,
               60,
               60,
               60,
               60
            ]
         ],
         "cooldownBurn": "7/6/5/4/3",
         "description": "Akali flourishes her kamas, dealing damage based on her Attack Damage and Ability Power.",
         "name": "Crescent Slash",
         "sanitizedTooltip": "Akali flourishes her kamas, slicing nearby enemy units for {{ e1 }} (+{{ f1 }}) (+{{ a1 }}) physical damage. Triggers Mark of the Assassin on targets affected by it.",
         "key": "AkaliShadowSwipe",
         "costBurn": "60/55/50/45/40",
         "tooltip": "Akali flourishes her kamas, slicing nearby enemy units for {{ e1 }} <span class=\"colorFF8C00\">(+{{ f1 }})<\/span> <span class=\"color99FF99\">(+{{ a1 }})<\/span> physical damage.<br><br>Triggers Mark of the Assassin on targets affected by it."
      },
      {
         "range": [
            800,
            800,
            800
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ f1 }} -> {{ f2 }}",
               "{{ cooldown }} -> {{ cooldownnNL }}"
            ],
            "label": [
               "Damage",
               "Essence Refresh Timer",
               "Cooldown"
            ]
         },
         "resource": "{{ e5 }} Essence of Shadow",
         "maxrank": 3,
         "effectBurn": [
            "",
            "100/175/250",
            "10/20/30",
            "30/22.5/15",
            "3",
            "1"
         ],
         "image": {
            "w": 48,
            "full": "AkaliShadowDance.png",
            "sprite": "spell0.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 192
         },
         "cooldown": [
            2,
            1.5,
            1
         ],
         "cost": [
            0,
            0,
            0
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
                  30,
                  22.5,
                  15
               ],
               "key": "f1"
            },
            {
               "link": "@cooldownchampion",
               "coeff": [
                  22.5,
                  15
               ],
               "key": "f2"
            }
         ],
         "sanitizedDescription": "Akali moves through shadows to quickly strike her target, dealing damage and consuming an Essence of Shadow charge. Akali recharges Essence of Shadow charges both periodically and upon kills and assists, max 3 stacks.",
         "rangeBurn": "800",
         "costType": "EssenceofShadow",
         "effect": [
            "null",
            [
               100,
               175,
               250
            ],
            [
               10,
               20,
               30
            ],
            [
               30,
               22.5,
               15
            ],
            [
               3,
               3,
               3
            ],
            [
               1,
               1,
               1
            ]
         ],
         "cooldownBurn": "2/1.5/1",
         "description": "Akali moves through shadows to quickly strike her target, dealing damage and consuming an Essence of Shadow charge. Akali recharges Essence of Shadow charges both periodically and upon kills and assists, max 3 stacks.",
         "name": "Shadow Dance",
         "sanitizedTooltip": "Akali moves through shadows to quickly strike her target, dealing {{ e1 }} (+{{ a1 }}) Magic Damage. Akali stores an Essence of Shadow on kills and assists as well as every {{ f1 }} seconds up to {{ e4 }} total.",
         "key": "AkaliShadowDance",
         "costBurn": "0",
         "tooltip": "Akali moves through shadows to quickly strike her target, dealing {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> Magic Damage.<br><br>Akali stores an Essence of Shadow on kills and assists as well as every <span class=\"colorFFFFFF\">{{ f1 }}<\/span> seconds up to {{ e4 }} total."
      }
   ],
   "key": "Akali"
}