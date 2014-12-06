ABILITIES = {
   "id": 10,
   "title": "The Judicator",
   "name": "Kayle",
   "spells": [
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
               "{{ e2 }}% -> {{ e2NL }}%",
               "{{ cost }}  ->  {{ costnNL }}"
            ],
            "label": [
               "Damage",
               "Slow %",
               "Mana Cost"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "60/110/160/210/260",
            "35/40/45/50/55",
            "3"
         ],
         "image": {
            "w": 48,
            "full": "JudicatorReckoning.png",
            "sprite": "spell4.png",
            "group": "spell",
            "h": 48,
            "y": 144,
            "x": 144
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
            75,
            80,
            85,
            90
         ],
         "vars": [
            {
               "link": "bonusattackdamage",
               "coeff": [1],
               "key": "a2"
            },
            {
               "link": "spelldamage",
               "coeff": [0.6],
               "key": "a1"
            }
         ],
         "sanitizedDescription": "Blasts an enemy unit with angelic force, dealing damage, slowing Movement Speed, and applying Holy Fervor.",
         "rangeBurn": "650",
         "costType": "Mana",
         "effect": [
            "null",
            [
               60,
               110,
               160,
               210,
               260
            ],
            [
               35,
               40,
               45,
               50,
               55
            ],
            [
               3,
               3,
               3,
               3,
               3
            ]
         ],
         "cooldownBurn": "8",
         "description": "Blasts an enemy unit with angelic force, dealing damage, slowing Movement Speed, and applying Holy Fervor.",
         "name": "Reckoning",
         "sanitizedTooltip": "Blasts a target, dealing {{ e1 }} (+{{ a2 }}) (+{{ a1 }}) magic damage, slowing their Movement Speed by {{ e2 }}% for {{ e3 }} seconds, and applying a stack of Holy Fervor.",
         "key": "JudicatorReckoning",
         "costBurn": "70/75/80/85/90",
         "tooltip": "Blasts a target, dealing {{ e1 }} <span class=\"colorFF8C00\">(+{{ a2 }})<\/span> <span class=\"color99FF99\">(+{{ a1 }})<\/span> magic damage, slowing their Movement Speed by {{ e2 }}% for {{ e3 }} seconds, and applying a stack of Holy Fervor."
      },
      {
         "range": [
            900,
            900,
            900,
            900,
            900
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e2 }}% -> {{ e2NL }}%",
               "{{ cost }} -> {{ costnNL }}"
            ],
            "label": [
               "Health Restoration",
               "Move Speed Bonus",
               "Mana Cost"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "60/105/150/195/240",
            "18/21/24/27/30",
            "3"
         ],
         "image": {
            "w": 48,
            "full": "JudicatorDivineBlessing.png",
            "sprite": "spell4.png",
            "group": "spell",
            "h": 48,
            "y": 144,
            "x": 192
         },
         "cooldown": [
            15,
            15,
            15,
            15,
            15
         ],
         "cost": [
            60,
            70,
            80,
            90,
            100
         ],
         "vars": [
            {
               "link": "spelldamage",
               "coeff": [0.07],
               "key": "a2"
            },
            {
               "link": "spelldamage",
               "coeff": [0.45],
               "key": "a1"
            }
         ],
         "sanitizedDescription": "Blesses a target friendly champion, granting them increased Movement Speed and healing them.",
         "rangeBurn": "900",
         "costType": "Mana",
         "effect": [
            "null",
            [
               60,
               105,
               150,
               195,
               240
            ],
            [
               18,
               21,
               24,
               27,
               30
            ],
            [
               3,
               3,
               3,
               3,
               3
            ]
         ],
         "cooldownBurn": "15",
         "description": "Blesses a target friendly champion, granting them increased Movement Speed and healing them.",
         "name": "Divine Blessing",
         "sanitizedTooltip": "Blesses an allied champion, increasing their Movement Speed by {{ e2 }}% (+{{ a2 }}%) for {{ e3 }} seconds and healing them for {{ e1 }} (+{{ a1 }}) Health.",
         "key": "JudicatorDivineBlessing",
         "costBurn": "60/70/80/90/100",
         "tooltip": "Blesses an allied champion, increasing their Movement Speed by {{ e2 }}% <span class=\"color99FF99\">(+{{ a2 }}%)<\/span> for {{ e3 }} seconds and healing them for {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> Health."
      },
      {
         "range": "self",
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e3 }} -> {{ e3NL }}"
            ],
            "label": [
               "Base Damage",
               "Splash Attack Damage Ratio "
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "20/30/40/50/60",
            "20/25/30/35/40",
            "0.2/0.25/0.3/0.35/0.4"
         ],
         "image": {
            "w": 48,
            "full": "JudicatorRighteousFury.png",
            "sprite": "spell4.png",
            "group": "spell",
            "h": 48,
            "y": 144,
            "x": 240
         },
         "cooldown": [
            16,
            16,
            16,
            16,
            16
         ],
         "cost": [
            45,
            45,
            45,
            45,
            45
         ],
         "vars": [
            {
               "link": "spelldamage",
               "coeff": [0.25],
               "key": "a1"
            },
            {
               "link": "attackdamage",
               "coeff": [
                  0.2,
                  0.25,
                  0.3,
                  0.35,
                  0.4
               ],
               "key": "f2"
            }
         ],
         "sanitizedDescription": "Ignites Kayle's sword with a holy flame, granting Kayle a ranged splash attack and bonus magic damage.",
         "rangeBurn": "self",
         "costType": "Mana",
         "effect": [
            "null",
            [
               20,
               30,
               40,
               50,
               60
            ],
            [
               20,
               25,
               30,
               35,
               40
            ],
            [
               0.2,
               0.25,
               0.3,
               0.35,
               0.4
            ]
         ],
         "cooldownBurn": "16",
         "description": "Ignites Kayle's sword with a holy flame, granting Kayle a ranged splash attack and bonus magic damage.",
         "name": "Righteous Fury",
         "sanitizedTooltip": "Kayle increases her Attack Range by 400 for 10 seconds and her basic attack deals an additional {{ e1 }} (+{{ a1 }}) magic damage on hit. In addition, enemies near her target take {{ e1 }} (+{{ f2 }}) (+{{ a1 }}) magic damage on attack.",
         "key": "JudicatorRighteousFury",
         "costBurn": "45",
         "tooltip": "Kayle increases her Attack Range by 400 for 10 seconds and her basic attack deals an additional {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> magic damage on hit.<br><br>In addition, enemies near her target take {{ e1 }} <span class=\"colorFF8C00\">(+{{ f2 }})<\/span> <span class=\"color99FF99\">(+{{ a1 }})<\/span> magic damage on attack."
      },
      {
         "range": [
            900,
            900,
            900
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ cooldown }} -> {{ cooldownnNL }}"
            ],
            "label": [
               "Duration",
               "Cooldown"
            ]
         },
         "resource": "No Cost",
         "maxrank": 3,
         "effectBurn": [
            "",
            "2/2.5/3"
         ],
         "image": {
            "w": 48,
            "full": "JudicatorIntervention.png",
            "sprite": "spell4.png",
            "group": "spell",
            "h": 48,
            "y": 144,
            "x": 288
         },
         "cooldown": [
            100,
            90,
            80
         ],
         "cost": [
            0,
            0,
            0
         ],
         "sanitizedDescription": "Shields Kayle or an ally for a short time, causing them to be immune to damage.",
         "rangeBurn": "900",
         "costType": "NoCost",
         "effect": [
            "null",
            [
               2,
               2.5,
               3
            ]
         ],
         "cooldownBurn": "100/90/80",
         "description": "Shields Kayle or an ally for a short time, causing them to be immune to damage.",
         "name": "Intervention",
         "sanitizedTooltip": "Bathes Kayle's target in a holy light, rendering them immune to all damage for {{ e1 }} seconds.",
         "key": "JudicatorIntervention",
         "costBurn": "0",
         "tooltip": "Bathes Kayle's target in a holy light, rendering them immune to all damage for {{ e1 }} seconds."
      }
   ],
   "key": "Kayle"
}