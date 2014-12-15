ABILITIES = {
   "id": 254,
   "title": "the Piltover Enforcer",
   "name": "Vi",
   "spells": [
      {
         "range": [
            250,
            250,
            250,
            250,
            250
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e2 }} -> {{ e2NL }}",
               "{{ cooldown }} -> {{ cooldownnNL }}",
               " {{ cost }} -> {{ costnNL }}"
            ],
            "label": [
               "Min Damage",
               "Max Damage",
               "Cooldown",
               "Mana Cost"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "50/75/100/125/150",
            "100/150/200/250/300"
         ],
         "image": {
            "w": 48,
            "full": "ViQ.png",
            "sprite": "spell11.png",
            "group": "spell",
            "h": 48,
            "y": 48,
            "x": 384
         },
         "cooldown": [
            18,
            15.5,
            13,
            10.5,
            8
         ],
         "cost": [
            50,
            60,
            70,
            80,
            90
         ],
         "vars": [
            {
               "link": "bonusattackdamage",
               "coeff": [0.8],
               "key": "a1"
            },
            {
               "link": "bonusattackdamage",
               "coeff": [1.4],
               "key": "f1"
            }
         ],
         "sanitizedDescription": "Vi charges her gauntlets and unleashes a vault shattering punch, carrying her forward. Enemies she hits are knocked back and receive a stack of Denting Blows.",
         "rangeBurn": "250",
         "costType": "Mana",
         "effect": [
            "null",
            [
               50,
               75,
               100,
               125,
               150
            ],
            [
               100,
               150,
               200,
               250,
               300
            ]
         ],
         "cooldownBurn": "18/15.5/13/10.5/8",
         "description": "Vi charges her gauntlets and unleashes a vault shattering punch, carrying her forward. Enemies she hits are knocked back and receive a stack of Denting Blows.",
         "name": "Vault Breaker",
         "sanitizedTooltip": "Charges a powerful punch that carries Vi forward. First Cast: Slows Movement Speed by 15% while increasing damage and dash range over 1.25 seconds. Second Cast: Dashes forward dealing {{ e1 }} (+{{ a1 }}) to {{ e2 }} (+{{ f1 }}) physical damage and applying Denting Blows to all enemies hit (deals 75% damage to minions and monsters). Stops upon colliding with an enemy champion, knocking it back.",
         "key": "ViQ",
         "costBurn": "50/60/70/80/90",
         "tooltip": "Charges a powerful punch that carries Vi forward.<br><br><span class=\"colorFF9900\">First Cast:<\/span> Slows Movement Speed by 15% while increasing damage and dash range over 1.25 seconds.<br><br><span class=\"colorFF9900\">Second Cast:<\/span> Dashes forward dealing {{ e1 }} <span class=\"colorFF8C00\">(+{{ a1 }})<\/span> to {{ e2 }} <span class=\"colorFF8C00\">(+{{ f1 }})<\/span> physical damage and applying Denting Blows to all enemies hit (deals 75% damage to minions and monsters). Stops upon colliding with an enemy champion, knocking it back."
      },
      {
         "range": "self",
         "leveltip": {
            "effect": [
               "{{ e1 }}% -> {{ e1NL }}%",
               "{{ e2 }}% -> {{ e2NL }}%"
            ],
            "label": [
               "Max Health Damage",
               "Attack Speed"
            ]
         },
         "resource": "Passive",
         "maxrank": 5,
         "effectBurn": [
            "",
            "4/5.5/7/8.5/10",
            "30/35/40/45/50",
            "15/17.5/20/22.5/25",
            "30/35/40/45/50"
         ],
         "image": {
            "w": 48,
            "full": "ViW.png",
            "sprite": "spell11.png",
            "group": "spell",
            "h": 48,
            "y": 48,
            "x": 432
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
         "vars": [{
            "link": "@special.viw",
            "coeff": [35],
            "key": "f1"
         }],
         "sanitizedDescription": "Vi's punches break her opponent's Armor, dealing bonus damage and granting her Attack Speed.",
         "rangeBurn": "self",
         "costType": "Passive",
         "effect": [
            "null",
            [
               4,
               5.5,
               7,
               8.5,
               10
            ],
            [
               30,
               35,
               40,
               45,
               50
            ],
            [
               15,
               17.5,
               20,
               22.5,
               25
            ],
            [
               30,
               35,
               40,
               45,
               50
            ]
         ],
         "cooldownBurn": "0",
         "description": "Vi's punches break her opponent's Armor, dealing bonus damage and granting her Attack Speed.",
         "name": "Denting Blows",
         "sanitizedTooltip": "Every 3rd attack on the same target deals an additional {{ e1 }}% (+{{ f1 }}%) of the target's maximum Health as physical damage, reduces its Armor by 20% and grants Vi {{ e2 }}% Attack Speed for 4 seconds (max 300 damage vs. minions and monsters).",
         "key": "ViW",
         "costBurn": "0",
         "tooltip": "Every 3rd attack on the same target deals an additional {{ e1 }}% <span class=\"colorFF8C00\">(+{{ f1 }}%)<\/span> of the target's maximum Health as physical damage, reduces its Armor by 20% and grants Vi {{ e2 }}% Attack Speed for 4 seconds (max 300 damage vs. minions and monsters)."
      },
      {
         "range": "self",
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ f1 }} -> {{ f2 }}"
            ],
            "label": [
               "Damage",
               "Charge Time"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "5/20/35/50/65",
            "110/115/120/125/130",
            "6"
         ],
         "image": {
            "w": 48,
            "full": "ViE.png",
            "sprite": "spell11.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 0
         },
         "cooldown": [
            1,
            1,
            1,
            1,
            1
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
               "link": "attackdamage",
               "coeff": [1.15],
               "key": "f3"
            },
            {
               "link": "spelldamage",
               "coeff": [0.7],
               "key": "a1"
            },
            {
               "link": "@text",
               "coeff": [
                  14,
                  12.5,
                  11,
                  9.5,
                  8
               ],
               "key": "f1"
            }
         ],
         "sanitizedDescription": "Vi's next attack blasts through her target, dealing damage to enemies behind it.",
         "rangeBurn": "self",
         "costType": "Mana",
         "effect": [
            "null",
            [
               5,
               20,
               35,
               50,
               65
            ],
            [
               110,
               115,
               120,
               125,
               130
            ],
            [
               6,
               6,
               6,
               6,
               6
            ]
         ],
         "cooldownBurn": "1",
         "description": "Vi's next attack blasts through her target, dealing damage to enemies behind it.",
         "name": "Excessive Force",
         "sanitizedTooltip": "Causes next basic attack to deal {{ e1 }} (+{{ f3 }}) (+{{ a1 }}) physical damage to the target and enemies behind it. Vi charges a new punch every {{ f1 }} seconds and can hold 2 charges at once.",
         "key": "ViE",
         "costBurn": "60",
         "tooltip": "Causes next basic attack to deal {{ e1 }} <span class=\"colorFF8C00\">(+{{ f3 }})<\/span> <span class=\"color99FF99\">(+{{ a1 }})<\/span> physical damage to the target and enemies behind it.<br><br><\/span>Vi charges a new punch every <span class=\"colorFFFFFF\">{{ f1 }}<\/span> seconds and can hold 2 charges at once."
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
               "{{ cooldown }} -> {{ cooldownnNL }}",
               " {{ cost }} -> {{ costnNL }}"
            ],
            "label": [
               "Total Damage",
               "Cooldown",
               "Mana Cost"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 3,
         "effectBurn": [
            "",
            "200/325/450",
            "200/325/450",
            "30/40/50",
            "4",
            "1/1.5/2"
         ],
         "image": {
            "w": 48,
            "full": "ViR.png",
            "sprite": "spell11.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 48
         },
         "cooldown": [
            150,
            115,
            80
         ],
         "cost": [
            100,
            125,
            150
         ],
         "vars": [{
            "link": "bonusattackdamage",
            "coeff": [1.4],
            "key": "a1"
         }],
         "sanitizedDescription": "Vi runs down an enemy, knocking aside anyone in the way. When she reaches her target she knocks it into the air, jumps after it, and slams it back into the ground.",
         "rangeBurn": "800",
         "costType": "Mana",
         "effect": [
            "null",
            [
               200,
               325,
               450
            ],
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
               4,
               4,
               4
            ],
            [
               1,
               1.5,
               2
            ]
         ],
         "cooldownBurn": "150/115/80",
         "description": "Vi runs down an enemy, knocking aside anyone in the way. When she reaches her target she knocks it into the air, jumps after it, and slams it back into the ground.",
         "name": "Assault and Battery",
         "sanitizedTooltip": "Targets an enemy champion and chases it down, knocking it up for 1.25 seconds, dealing {{ e1 }} (+{{ a1 }}) physical damage. While charging, Vi cannot be stopped and will knock aside enemies in the way, dealing 75% damage to them.",
         "key": "ViR",
         "costBurn": "100/125/150",
         "tooltip": "Targets an enemy champion and chases it down, knocking it up for 1.25 seconds, dealing {{ e1 }} <span class=\"colorFF8C00\">(+{{ a1 }})<\/span> physical damage.<br><br>While charging, Vi cannot be stopped and will knock aside enemies in the way, dealing 75% damage to them."
      }
   ],
   "key": "Vi"
}