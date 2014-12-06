ABILITIES = {
   "id": 36,
   "title": "the Madman of Zaun",
   "name": "Dr. Mundo",
   "spells": [
      {
         "range": [
            975,
            975,
            975,
            975,
            975
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e2 }}% -> {{ e2NL }}%",
               "{{ e3 }} -> {{ e3NL }}"
            ],
            "label": [
               "Minimum Damage",
               "Damage Percent",
               "Health Cost"
            ]
         },
         "resource": "{{ e3 }} Health",
         "maxrank": 5,
         "effectBurn": [
            "",
            "80/130/180/230/280",
            "15/18/21/23/25",
            "50/60/70/80/90",
            "40",
            "2"
         ],
         "image": {
            "w": 48,
            "full": "InfectedCleaverMissileCast.png",
            "sprite": "spell2.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 240
         },
         "cooldown": [
            4,
            4,
            4,
            4,
            4
         ],
         "cost": [
            0,
            0,
            0,
            0,
            0
         ],
         "sanitizedDescription": "Dr. Mundo hurls his cleaver, dealing damage equal to a portion of his target's current Health and slowing them for a short time. Dr. Mundo delights in the suffering of others, so he is returned half of the Health cost when he successfully lands a cleaver.",
         "rangeBurn": "975",
         "costType": "Health",
         "effect": [
            "null",
            [
               80,
               130,
               180,
               230,
               280
            ],
            [
               15,
               18,
               21,
               23,
               25
            ],
            [
               50,
               60,
               70,
               80,
               90
            ],
            [
               40,
               40,
               40,
               40,
               40
            ],
            [
               2,
               2,
               2,
               2,
               2
            ]
         ],
         "cooldownBurn": "4",
         "description": "Dr. Mundo hurls his cleaver, dealing damage equal to a portion of his target's current Health and slowing them for a short time. Dr. Mundo delights in the suffering of others, so he is returned half of the Health cost when he successfully lands a cleaver.",
         "name": "Infected Cleaver",
         "sanitizedTooltip": "Dr. Mundo hurls his cleaver, dealing magic damage equal to {{ e2 }}% of the target's current Health ({{ e1 }} damage minimum) and slowing them by {{ e4 }}% for {{ e5 }} seconds. Half of the Health cost is refunded if the cleaver hits a target.",
         "key": "InfectedCleaverMissileCast",
         "costBurn": "0",
         "tooltip": "Dr. Mundo hurls his cleaver, dealing magic damage equal to {{ e2 }}% of the target's current Health ({{ e1 }} damage minimum) and slowing them by {{ e4 }}% for {{ e5 }} seconds.<br><br>Half of the Health cost is refunded if the cleaver hits a target."
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
               " {{ e3 }} -> {{ e3NL }}",
               "{{ e2 }}% -> {{ e2NL }}%",
               "{{ e1 }} -> {{ e1NL }}"
            ],
            "label": [
               "Damage Per Second",
               "Crowd Control Reduction",
               "Health Cost"
            ]
         },
         "resource": "{{ e1 }} Health Per Sec",
         "maxrank": 5,
         "effectBurn": [
            "",
            "10/15/20/25/30",
            "10/15/20/25/30",
            "35/50/65/80/95"
         ],
         "image": {
            "w": 48,
            "full": "BurningAgony.png",
            "sprite": "spell2.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 288
         },
         "cooldown": [
            4,
            4,
            4,
            4,
            4
         ],
         "cost": [
            0,
            0,
            0,
            0,
            0
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.2],
            "key": "a1"
         }],
         "sanitizedDescription": "Dr. Mundo drains his Health to reduce the duration of disables and deal continual damage to nearby enemies.",
         "rangeBurn": "325",
         "costType": "HealthPerSec",
         "effect": [
            "null",
            [
               10,
               15,
               20,
               25,
               30
            ],
            [
               10,
               15,
               20,
               25,
               30
            ],
            [
               35,
               50,
               65,
               80,
               95
            ]
         ],
         "cooldownBurn": "4",
         "description": "Dr. Mundo drains his Health to reduce the duration of disables and deal continual damage to nearby enemies.",
         "name": "Burning Agony",
         "sanitizedTooltip": "Toggle: Dr. Mundo deals {{ e3 }} (+{{ a1 }}) magic damage to nearby enemies, and reduces the duration of disables on Dr. Mundo by {{ e2 }}%.",
         "key": "BurningAgony",
         "costBurn": "0",
         "tooltip": "<span class=\"colorFF9900\">Toggle: <\/span>Dr. Mundo deals {{ e3 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> magic damage to nearby enemies, and reduces the duration of disables on Dr. Mundo by {{ e2 }}%."
      },
      {
         "range": "self",
         "leveltip": {
            "effect": [
               " {{ e1 }} -> {{ e1NL }}",
               "{{ e3 }} -> {{ e3NL }}",
               "{{ e2 }} -> {{ e2NL }}"
            ],
            "label": [
               "Attack Damage Bonus",
               "Bonus Factor",
               "Health Cost"
            ]
         },
         "resource": "{{ e2 }} Health",
         "maxrank": 5,
         "effectBurn": [
            "",
            "40/55/70/85/100",
            "25/35/45/55/65",
            "0.4/0.55/0.7/0.85/1",
            "5"
         ],
         "image": {
            "w": 48,
            "full": "Masochism.png",
            "sprite": "spell2.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 336
         },
         "cooldown": [
            7,
            7,
            7,
            7,
            7
         ],
         "cost": [
            0,
            0,
            0,
            0,
            0
         ],
         "sanitizedDescription": "Masochism increases Dr. Mundo's Attack Damage by a flat amount for 5 seconds. In addition, Dr. Mundo also gains an additional amount of Attack Damage for each percentage of Health he is missing.",
         "rangeBurn": "self",
         "costType": "Health",
         "effect": [
            "null",
            [
               40,
               55,
               70,
               85,
               100
            ],
            [
               25,
               35,
               45,
               55,
               65
            ],
            [
               0.4,
               0.55,
               0.7,
               0.85,
               1
            ],
            [
               5,
               5,
               5,
               5,
               5
            ]
         ],
         "cooldownBurn": "7",
         "description": "Masochism increases Dr. Mundo's Attack Damage by a flat amount for 5 seconds. In addition, Dr. Mundo also gains an additional amount of Attack Damage for each percentage of Health he is missing.",
         "name": "Masochism",
         "sanitizedTooltip": "Increases Attack Damage by {{ e1 }} for {{ e4 }} seconds. Dr. Mundo gains an additional +{{ e3 }} Attack Damage for each percentage of Health he is missing.",
         "key": "Masochism",
         "costBurn": "0",
         "tooltip": "Increases Attack Damage by {{ e1 }} for {{ e4 }} seconds. Dr. Mundo gains an additional +{{ e3 }} Attack Damage for each percentage of Health he is missing."
      },
      {
         "range": "self",
         "leveltip": {
            "effect": [
               "{{ e1 }}% -> {{ e1NL }}%",
               "{{ e3 }}% -> {{ e3NL }}%"
            ],
            "label": [
               "Heal Amount",
               "Movement Speed Bonus"
            ]
         },
         "resource": "{{ e4 }}% of Current Health",
         "maxrank": 3,
         "effectBurn": [
            "",
            "40/50/60",
            "12",
            "15/25/35",
            "20"
         ],
         "image": {
            "w": 48,
            "full": "Sadism.png",
            "sprite": "spell2.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 384
         },
         "cooldown": [
            75,
            75,
            75
         ],
         "cost": [
            0,
            0,
            0
         ],
         "sanitizedDescription": "Dr. Mundo sacrifices a portion of his Health for increased Movement Speed and drastically increased Health Regeneration.",
         "rangeBurn": "self",
         "costType": "pofCurrentHealth",
         "effect": [
            "null",
            [
               40,
               50,
               60
            ],
            [
               12,
               12,
               12
            ],
            [
               15,
               25,
               35
            ],
            [
               20,
               20,
               20
            ]
         ],
         "cooldownBurn": "75",
         "description": "Dr. Mundo sacrifices a portion of his Health for increased Movement Speed and drastically increased Health Regeneration.",
         "name": "Sadism",
         "sanitizedTooltip": "Dr. Mundo regenerates {{ e1 }}% of his maximum Health over {{ e2 }} seconds. Additionally, he gains {{ e3 }}% Movement Speed.",
         "key": "Sadism",
         "costBurn": "0",
         "tooltip": "Dr. Mundo regenerates {{ e1 }}% of his maximum Health over {{ e2 }} seconds. Additionally, he gains {{ e3 }}% Movement Speed."
      }
   ],
   "key": "DrMundo"
}