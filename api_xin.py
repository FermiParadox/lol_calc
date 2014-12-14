ABILITIES = {
   "id": 5,
   "title": "the Seneschal of Demacia",
   "name": "Xin Zhao",
   "spells": [
      {
         "range": "self",
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
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
            "15/30/45/60/75",
            "10/20/30/40/50",
            "30/60/90/120/150"
         ],
         "image": {
            "w": 48,
            "full": "XenZhaoComboTarget.png",
            "sprite": "spell12.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 96
         },
         "cooldown": [
            9,
            8,
            7,
            6,
            5
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
            "coeff": [1.25],
            "key": "f1"
         }],
         "sanitizedDescription": "Xin Zhao's next 3 standard attacks deal increased damage that reduce his other ability cooldowns, with the third attack knocking an opponent into the air.",
         "rangeBurn": "self",
         "costType": "Mana",
         "effect": [
            "null",
            [
               15,
               30,
               45,
               60,
               75
            ],
            [
               10,
               20,
               30,
               40,
               50
            ],
            [
               30,
               60,
               90,
               120,
               150
            ]
         ],
         "cooldownBurn": "9/8/7/6/5",
         "description": "Xin Zhao's next 3 standard attacks deal increased damage that reduce his other ability cooldowns, with the third attack knocking an opponent into the air.",
         "name": "Three Talon Strike",
         "sanitizedTooltip": "Xin Zhao's next 3 basic attacks deal {{ e1 }} (+{{ f1 }}) bonus physical damage and reduce his other abilities' cooldowns by 1 second. The final strike also knocks the target into the air.",
         "key": "XenZhaoComboTarget",
         "costBurn": "30",
         "tooltip": "Xin Zhao's next 3 basic attacks deal {{ e1 }} <span class=\"colorFF8C00\">(+{{ f1 }})<\/span> bonus physical damage and reduce his other abilities' cooldowns by 1 second. The final strike also knocks the target into the air."
      },
      {
         "range": "self",
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e2 }} -> {{ e2NL }}",
               "{{ cooldown }} -> {{ cooldownnNL }}"
            ],
            "label": [
               "Passive Heal",
               "Active Attack Speed %",
               "Cooldown"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "26/32/38/44/50",
            "40/50/60/70/80",
            "5"
         ],
         "image": {
            "w": 48,
            "full": "XenZhaoBattleCry.png",
            "sprite": "spell12.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 144
         },
         "cooldown": [
            16,
            15,
            14,
            13,
            12
         ],
         "cost": [
            40,
            40,
            40,
            40,
            40
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.7],
            "key": "a1"
         }],
         "sanitizedDescription": "Xin Zhao passively heals every 3 attacks and can activate this ability to attack faster.",
         "rangeBurn": "self",
         "costType": "Mana",
         "effect": [
            "null",
            [
               26,
               32,
               38,
               44,
               50
            ],
            [
               40,
               50,
               60,
               70,
               80
            ],
            [
               5,
               5,
               5,
               5,
               5
            ]
         ],
         "cooldownBurn": "16/15/14/13/12",
         "description": "Xin Zhao passively heals every 3 attacks and can activate this ability to attack faster.",
         "name": "Battle Cry",
         "sanitizedTooltip": "Passive: Xin Zhao heals himself for {{ e1 }} (+{{ a1 }}) every third basic attack. Active: Xin Zhao unleashes a battle cry, increasing his Attack Speed by {{ e2 }}% for {{ e3 }} seconds.",
         "key": "XenZhaoBattleCry",
         "costBurn": "40",
         "tooltip": "<span class=\"colorFF9900\">Passive: <\/span>Xin Zhao heals himself for {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> every third basic attack.<br><br><span class=\"colorFF9900\">Active: <\/span>Xin Zhao unleashes a battle cry, increasing his Attack Speed by {{ e2 }}% for {{ e3 }} seconds."
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
               "{{ e2 }} -> {{ e2NL }}",
               "{{ cooldown }} -> {{ cooldownnNL }}"
            ],
            "label": [
               "Damage",
               "Slow %",
               "Cooldown"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "70/105/140/175/210",
            "25/30/35/40/45",
            "650/750/850/950/1050",
            "2"
         ],
         "image": {
            "w": 48,
            "full": "XenZhaoSweep.png",
            "sprite": "spell12.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 192
         },
         "cooldown": [
            14,
            13,
            12,
            11,
            10
         ],
         "cost": [
            60,
            60,
            60,
            60,
            60
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.6],
            "key": "a1"
         }],
         "sanitizedDescription": "Xin Zhao charges an enemy, dealing damage and slowing all enemies in the area.",
         "rangeBurn": "650",
         "costType": "Mana",
         "effect": [
            "null",
            [
               70,
               105,
               140,
               175,
               210
            ],
            [
               25,
               30,
               35,
               40,
               45
            ],
            [
               650,
               750,
               850,
               950,
               1050
            ],
            [
               2,
               2,
               2,
               2,
               2
            ]
         ],
         "cooldownBurn": "14/13/12/11/10",
         "description": "Xin Zhao charges an enemy, dealing damage and slowing all enemies in the area.",
         "name": "Audacious Charge",
         "sanitizedTooltip": "Xin Zhao charges and challenges an enemy. The charge deals {{ e1 }} (+{{ a1 }}) magic damage to all nearby enemies and slows them by {{ e2 }}% for 2 seconds.",
         "key": "XenZhaoSweep",
         "costBurn": "60",
         "tooltip": "Xin Zhao charges and challenges an enemy. The charge deals {{ e1 }}<span class=\"color99FF99\"> (+{{ a1 }})<\/span> magic damage to all nearby enemies and slows them by {{ e2 }}% for 2 seconds. "
      },
      {
         "range": [
            500,
            500,
            500
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e3 }} -> {{ e3NL }}",
               "{{ cooldown }} -> {{ cooldownnNL }}"
            ],
            "label": [
               "Bonus Damage",
               "Resistance Per Target",
               "Cooldown"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 3,
         "effectBurn": [
            "",
            "75/175/275",
            "15",
            "15/20/25",
            "7/10/13"
         ],
         "image": {
            "w": 48,
            "full": "XenZhaoParry.png",
            "sprite": "spell12.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 240
         },
         "cooldown": [
            120,
            110,
            100
         ],
         "cost": [
            100,
            100,
            100
         ],
         "vars": [{
            "link": "bonusattackdamage",
            "coeff": [1],
            "key": "f1"
         }],
         "sanitizedDescription": "Xin Zhao deals damage to nearby enemies based on their current Health and knocks non-challenged targets back. Xin Zhao gains bonus Armor and Magic Resist based on number of champions hit.",
         "rangeBurn": "500",
         "costType": "Mana",
         "effect": [
            "null",
            [
               75,
               175,
               275
            ],
            [
               15,
               15,
               15
            ],
            [
               15,
               20,
               25
            ],
            [
               7,
               10,
               13
            ]
         ],
         "cooldownBurn": "120/110/100",
         "description": "Xin Zhao deals damage to nearby enemies based on their current Health and knocks non-challenged targets back. Xin Zhao gains bonus Armor and Magic Resist based on number of champions hit.",
         "name": "Crescent Sweep",
         "sanitizedTooltip": "Xin Zhao unleashes a sweep around him that deals {{ e1 }} (+{{ f1 }}) plus 15% of target's current Health in physical damage and knocks enemies back (max 600 vs minions and monsters). Xin Zhao gains {{ e3 }} Armor and Magic Resist for 6 seconds for each champion hit. Challenge: If a challenged target is hit by the sweep, it is unaffected by the knockback.",
         "key": "XenZhaoParry",
         "costBurn": "100",
         "tooltip": "Xin Zhao unleashes a sweep around him that deals {{ e1 }}<span class=\"colorFF8C00\"> (+{{ f1 }})<\/span> plus 15% of target's current Health in physical damage and knocks enemies back (max 600 vs minions and monsters). Xin Zhao gains {{ e3 }} Armor and Magic Resist for 6 seconds for each champion hit.<br><br><span class=\"colorDDDD77\">Challenge:<\/span> If a challenged target is hit by the sweep, it is unaffected by the knockback."
      }
   ],
   "key": "XinZhao"
}