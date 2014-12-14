ABILITIES = {
   "id": 24,
   "title": "Grandmaster at Arms",
   "name": "Jax",
   "spells": [
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
               "{{ e1 }} -> {{ e1NL }}",
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
            "70/110/150/190/230"
         ],
         "image": {
            "w": 48,
            "full": "JaxLeapStrike.png",
            "sprite": "spell4.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 240
         },
         "cooldown": [
            10,
            9,
            8,
            7,
            6
         ],
         "cost": [
            65,
            65,
            65,
            65,
            65
         ],
         "vars": [
            {
               "link": "bonusattackdamage",
               "coeff": [1],
               "key": "f1"
            },
            {
               "link": "spelldamage",
               "coeff": [0.6],
               "key": "a1"
            }
         ],
         "sanitizedDescription": "Jax leaps toward a unit. If they are an enemy, he strikes them with his weapon.",
         "rangeBurn": "700",
         "costType": "Mana",
         "effect": [
            "null",
            [
               70,
               110,
               150,
               190,
               230
            ]
         ],
         "cooldownBurn": "10/9/8/7/6",
         "description": "Jax leaps toward a unit. If they are an enemy, he strikes them with his weapon.",
         "name": "Leap Strike",
         "sanitizedTooltip": "Jax leaps to a target unit, dealing {{ e1 }} (+{{ f1 }}) (+{{ a1 }}) physical damage if it is an enemy.",
         "key": "JaxLeapStrike",
         "costBurn": "65",
         "tooltip": "Jax leaps to a target unit, dealing {{ e1 }} <span class=\"colorFF8C00\">(+{{ f1 }})<\/span> <span class=\"color99FF99\">(+{{ a1 }})<\/span> physical damage if it is an enemy."
      },
      {
         "range": "self",
         "leveltip": {
            "effect": [
               " {{ e1 }} -> {{ e1NL }}",
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
            "40/75/110/145/180"
         ],
         "image": {
            "w": 48,
            "full": "JaxEmpowerTwo.png",
            "sprite": "spell4.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 288
         },
         "cooldown": [
            7,
            6,
            5,
            4,
            3
         ],
         "cost": [
            30,
            30,
            30,
            30,
            30
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.6],
            "key": "a1"
         }],
         "sanitizedDescription": "Jax charges his weapon with energy, causing his next attack to deal additional damage.",
         "rangeBurn": "self",
         "costType": "Mana",
         "effect": [
            "null",
            [
               40,
               75,
               110,
               145,
               180
            ]
         ],
         "cooldownBurn": "7/6/5/4/3",
         "description": "Jax charges his weapon with energy, causing his next attack to deal additional damage.",
         "name": "Empower",
         "sanitizedTooltip": "Jax charges his weapon with energy, causing his next basic attack or Leap Strike to deal an additional {{ e1 }} (+{{ a1 }}) Magic Damage.",
         "key": "JaxEmpowerTwo",
         "costBurn": "30",
         "tooltip": "Jax charges his weapon with energy, causing his next basic attack or Leap Strike to deal an additional {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }}) <\/span>Magic Damage."
      },
      {
         "range": "self",
         "leveltip": {
            "effect": [
               "{{ cooldown }} -> {{ cooldownnNL }}",
               "{{ e1 }} -> {{ e1NL }}",
               "{{ cost }} -> {{ costnNL }} "
            ],
            "label": [
               "Cooldown",
               "Damage",
               "Mana Cost"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "50/75/100/125/150",
            "1",
            "25",
            "100",
            "20"
         ],
         "image": {
            "w": 48,
            "full": "JaxCounterStrike.png",
            "sprite": "spell4.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 336
         },
         "cooldown": [
            16,
            14,
            12,
            10,
            8
         ],
         "cost": [
            70,
            75,
            80,
            85,
            90
         ],
         "vars": [{
            "link": "bonusattackdamage",
            "coeff": [0.5],
            "key": "f2"
         }],
         "sanitizedDescription": "Jax's combat prowess allows him to dodge all incoming attacks for a short duration and then quickly counterattack, stunning all surrounding enemies.",
         "rangeBurn": "self",
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
               1,
               1,
               1,
               1,
               1
            ],
            [
               25,
               25,
               25,
               25,
               25
            ],
            [
               100,
               100,
               100,
               100,
               100
            ],
            [
               20,
               20,
               20,
               20,
               20
            ]
         ],
         "cooldownBurn": "16/14/12/10/8",
         "description": "Jax's combat prowess allows him to dodge all incoming attacks for a short duration and then quickly counterattack, stunning all surrounding enemies.",
         "name": "Counter Strike",
         "sanitizedTooltip": "Jax enters a defensive stance for up to 2 seconds, dodging all incoming basic attacks and taking {{ e3 }}% less damage from area of effect abilities. After 2 seconds or if activated again, Jax stuns surrounding enemies for {{ e2 }} second and deals {{ e1 }} (+{{ f2 }}) physical damage to them. Counter Strike deals {{ e5 }}% more damage for each attack Jax dodged (max: {{ e4 }}% increased damage).",
         "key": "JaxCounterStrike",
         "costBurn": "70/75/80/85/90",
         "tooltip": "Jax enters a defensive stance for up to 2 seconds, dodging all incoming basic attacks and taking {{ e3 }}% less damage from area of effect abilities.<br><br>After 2 seconds or if activated again, Jax stuns surrounding enemies for {{ e2 }} second and deals {{ e1 }} <span class=\"colorFF8C00\">(+{{ f2 }})<\/span> physical damage to them.<br><br><span class=\"color99FF99\">Counter Strike deals {{ e5 }}% more damage for each attack Jax dodged (max: {{ e4 }}% increased damage).<\/span>"
      },
      {
         "range": "self",
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e3 }} -> {{ e3NL }}",
               "{{ e3 }} -> {{ e3NL }}"
            ],
            "label": [
               "Passive Damage",
               "Armor Bonus",
               "Magic Resist Bonus"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 3,
         "effectBurn": [
            "",
            "100/160/220",
            "3",
            "20/35/50",
            "6/8/10",
            "8",
            "50",
            "20"
         ],
         "image": {
            "w": 48,
            "full": "JaxRelentlessAssault.png",
            "sprite": "spell4.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 384
         },
         "cooldown": [
            80,
            80,
            80
         ],
         "cost": [
            100,
            100,
            100
         ],
         "vars": [
            {
               "link": "spelldamage",
               "coeff": [0.7],
               "key": "a1"
            },
            {
               "link": "@special.jaxrarmor",
               "coeff": [0.3],
               "key": "f2"
            },
            {
               "link": "@special.jaxrmr",
               "coeff": [0.2],
               "key": "f1"
            }
         ],
         "sanitizedDescription": "Every third consecutive attack deals additional Magic Damage. Additionally, Jax can activate this ability to strengthen his resolve, increasing his Armor and Magic Resist for a short duration.",
         "rangeBurn": "self",
         "costType": "Mana",
         "effect": [
            "null",
            [
               100,
               160,
               220
            ],
            [
               3,
               3,
               3
            ],
            [
               20,
               35,
               50
            ],
            [
               6,
               8,
               10
            ],
            [
               8,
               8,
               8
            ],
            [
               50,
               50,
               50
            ],
            [
               20,
               20,
               20
            ]
         ],
         "cooldownBurn": "80",
         "description": "Every third consecutive attack deals additional Magic Damage. Additionally, Jax can activate this ability to strengthen his resolve, increasing his Armor and Magic Resist for a short duration.",
         "name": "Grandmaster's Might",
         "sanitizedTooltip": "Passive: Every third consecutive strike Jax deals {{ e1 }} (+{{ a1 }}) additional Magic Damage. Active: Jax strengthens his resolve, granting him {{ f2 }} Armor and {{ f1 }} Magic Resist for {{ e5 }} seconds. Armor bonus is equal to {{ e3 }} + {{ e6 }}% bonus Attack Damage. Magic Resist bonus is equal to {{ e3 }} + {{ e7 }}% Ability Power.",
         "key": "JaxRelentlessAssault",
         "costBurn": "100",
         "tooltip": "<span class=\"colorFF9900\">Passive:<\/span> Every third consecutive strike Jax deals {{ e1 }}<span class=\"color99FF99\"> (+{{ a1 }}) <\/span>additional Magic Damage.<br><br><span class=\"colorFF9900\">Active:<\/span> Jax strengthens his resolve, granting him <span class=\"colorFF8C00\">{{ f2 }}<\/span> Armor and <span class=\"color99FF99\">{{ f1 }}<\/span> Magic Resist for {{ e5 }} seconds.<span class=\"colorFF8C00\"><br><br>Armor bonus is equal to {{ e3 }} + {{ e6 }}% bonus Attack Damage.<\/span><span class=\"color99FF99\"><br>Magic Resist bonus is equal to {{ e3 }} + {{ e7 }}% Ability Power.<\/span>"
      }
   ],
   "key": "Jax"
}