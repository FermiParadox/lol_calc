ABILITIES = {
   "id": 12,
   "title": "the Minotaur",
   "name": "Alistar",
   "spells": [
      {
         "range": [
            365,
            365,
            365,
            365,
            365
         ],
         "leveltip": {
            "effect": [
               "{{ e2 }} -> {{ e2NL }}",
               "{{ cooldown }} -> {{ cooldownnNL }}",
               "{{ cost }} -> {{ costnNL }}"
            ],
            "label": [
               "Damage",
               "Cooldown",
               "Mana Cost"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "70/85/100/115/130",
            "60/105/150/195/240"
         ],
         "image": {
            "w": 48,
            "full": "Pulverize.png",
            "sprite": "spell0.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 432
         },
         "cooldown": [
            17,
            16,
            15,
            14,
            13
         ],
         "cost": [
            65,
            70,
            75,
            80,
            85
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.5],
            "key": "a1"
         }],
         "sanitizedDescription": "Alistar smashes the ground, dealing damage to all nearby enemies and tossing them into the air for 1.5 seconds. On landing, enemies are stunned.",
         "rangeBurn": "365",
         "costType": "Mana",
         "effect": [
            'null',
            [
               70,
               85,
               100,
               115,
               130
            ],
            [
               60,
               105,
               150,
               195,
               240
            ]
         ],
         "cooldownBurn": "17/16/15/14/13",
         "description": "Alistar smashes the ground, dealing damage to all nearby enemies and tossing them into the air for 1.5 seconds. On landing, enemies are stunned.",
         "name": "Pulverize",
         "sanitizedTooltip": "Alistar smashes the ground, dealing {{ e2 }} (+{{ a1 }}) magic damage and tossing all nearby enemy units into the air, stunning them for 1.5 seconds.",
         "key": "Pulverize",
         "costBurn": "65/70/75/80/85",
         "tooltip": "Alistar smashes the ground, dealing {{ e2 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> magic damage and tossing all nearby enemy units into the air, stunning them for 1.5 seconds."
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
               "{{ e2 }} -> {{ e2NL }}",
               "{{ cooldown }} -> {{ cooldownnNL }}",
               "{{ cost }} -> {{ costnNL }}"
            ],
            "label": [
               "Damage",
               "Cooldown",
               "Mana Cost"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "80/90/100/110/120",
            "55/110/165/220/275"
         ],
         "image": {
            "w": 48,
            "full": "Headbutt.png",
            "sprite": "spell0.png",
            "group": "spell",
            "h": 48,
            "y": 144,
            "x": 0
         },
         "cooldown": [
            14,
            13,
            12,
            11,
            10
         ],
         "cost": [
            65,
            70,
            75,
            80,
            85
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.7],
            "key": "a1"
         }],
         "sanitizedDescription": "Alistar rams a target with his head, dealing damage and knocking the target back.",
         "rangeBurn": "650",
         "costType": "Mana",
         "effect": [
            'null',
            [
               80,
               90,
               100,
               110,
               120
            ],
            [
               55,
               110,
               165,
               220,
               275
            ]
         ],
         "cooldownBurn": "14/13/12/11/10",
         "description": "Alistar rams a target with his head, dealing damage and knocking the target back.",
         "name": "Headbutt",
         "sanitizedTooltip": "Alistar charges at an enemy and rams them, dealing {{ e2 }} (+{{ a1 }}) magic damage and stunning them while knocking them back.",
         "key": "Headbutt",
         "costBurn": "65/70/75/80/85",
         "tooltip": "Alistar charges at an enemy and rams them, dealing {{ e2 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> magic damage and stunning them while knocking them back."
      },
      {
         "range": [
            575,
            575,
            575,
            575,
            575
         ],
         "leveltip": {
            "effect": [
               "{{ cost }} -> {{ costnNL }}",
               " {{ e2 }} -> {{ e2NL }}"
            ],
            "label": [
               "Mana Cost",
               "Health Restored"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "2",
            "60/90/120/150/180"
         ],
         "image": {
            "w": 48,
            "full": "TriumphantRoar.png",
            "sprite": "spell0.png",
            "group": "spell",
            "h": 48,
            "y": 144,
            "x": 48
         },
         "cooldown": [
            12,
            12,
            12,
            12,
            12
         ],
         "cost": [
            40,
            50,
            60,
            70,
            80
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.2],
            "key": "a1"
         }],
         "sanitizedDescription": "Alistar lets out a commanding war cry, restoring Health to himself and nearby friendly units for half the amount. Can be cast more often if nearby enemies are dying.",
         "rangeBurn": "575",
         "costType": "Mana",
         "effect": [
            'null',
            [
               2,
               2,
               2,
               2,
               2
            ],
            [
               60,
               90,
               120,
               150,
               180
            ]
         ],
         "cooldownBurn": "12",
         "description": "Alistar lets out a commanding war cry, restoring Health to himself and nearby friendly units for half the amount. Can be cast more often if nearby enemies are dying.",
         "name": "Triumphant Roar",
         "sanitizedTooltip": "Restores {{ e2 }} (+{{ a1 }}) Health to Alistar and half as much to nearby allies. Cooldown is reduced by {{ e1 }} seconds each time a nearby enemy unit dies.",
         "key": "TriumphantRoar",
         "costBurn": "40/50/60/70/80",
         "tooltip": "Restores {{ e2 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> Health to Alistar and half as much to nearby allies. Cooldown is reduced by {{ e1 }} seconds each time a nearby enemy unit dies."
      },
      {
         "range": "self",
         "leveltip": {
            "effect": [
               "{{ e3 }} -> {{ e3NL }}",
               "{{ cooldown }} -> {{ cooldownnNL }}"
            ],
            "label": [
               "Attack Damage",
               "Cooldown"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 3,
         "effectBurn": [
            "",
            "7",
            "120/100/80",
            "60/75/90",
            "70"
         ],
         "image": {
            "w": 48,
            "full": "FerociousHowl.png",
            "sprite": "spell0.png",
            "group": "spell",
            "h": 48,
            "y": 144,
            "x": 96
         },
         "cooldown": [
            120,
            100,
            80
         ],
         "cost": [
            100,
            100,
            100
         ],
         "sanitizedDescription": "Alistar lets out a wild roar, gaining bonus damage, removing all crowd control effects on himself, and reducing incoming physical and magical damage for the duration.",
         "rangeBurn": "self",
         "costType": "Mana",
         "effect": [
            'null',
            [
               7,
               7,
               7
            ],
            [
               120,
               100,
               80
            ],
            [
               60,
               75,
               90
            ],
            [
               70,
               70,
               70
            ]
         ],
         "cooldownBurn": "120/100/80",
         "description": "Alistar lets out a wild roar, gaining bonus damage, removing all crowd control effects on himself, and reducing incoming physical and magical damage for the duration.",
         "name": "Unbreakable Will",
         "sanitizedTooltip": "Removes disables from Alistar, and Alistar gains {{ e3 }} Attack Damage and takes {{ e4 }}% reduced physical and magic damage for {{ e1 }} seconds.",
         "key": "FerociousHowl",
         "costBurn": "100",
         "tooltip": "Removes disables from Alistar, and Alistar gains {{ e3 }} Attack Damage and takes {{ e4 }}% reduced physical and magic damage for {{ e1 }} seconds."
      }
   ],
   "key": "Alistar"
}