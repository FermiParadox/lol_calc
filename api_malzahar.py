ABILITIES = {
   "id": 90,
   "title": "the Prophet of the Void",
   "name": "Malzahar",
   "spells": [
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
               "{{ e2 }} -> {{ e2NL }}",
               "{{ cost }} -> {{ costnNL }}"
            ],
            "label": [
               "Damage",
               "Silence Duration",
               "Mana Cost"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "80/135/190/245/300",
            "1.4/1.8/2.2/2.6/3"
         ],
         "image": {
            "w": 48,
            "full": "AlZaharCalloftheVoid.png",
            "sprite": "spell6.png",
            "group": "spell",
            "h": 48,
            "y": 48,
            "x": 0
         },
         "cooldown": [
            9,
            9,
            9,
            9,
            9
         ],
         "cost": [
            80,
            85,
            90,
            95,
            100
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.8],
            "key": "a1"
         }],
         "sanitizedDescription": "Malzahar opens up two portals to the Void. After a short delay, they fire projectiles that deal Magic Damage and silence enemy champions.",
         "rangeBurn": "900",
         "costType": "Mana",
         "effect": [
            "null",
            [
               80,
               135,
               190,
               245,
               300
            ],
            [
               1.4,
               1.8,
               2.2,
               2.6,
               3
            ]
         ],
         "cooldownBurn": "9",
         "description": "Malzahar opens up two portals to the Void. After a short delay, they fire projectiles that deal Magic Damage and silence enemy champions.",
         "name": "Call of the Void",
         "sanitizedTooltip": "Malzahar opens two portals to the Void. After a short delay, they fire projectiles that deal {{ e1 }} (+{{ a1 }}) Magic Damage and silence champions for {{ e2 }} seconds.",
         "key": "AlZaharCalloftheVoid",
         "costBurn": "80/85/90/95/100",
         "tooltip": "Malzahar opens two portals to the Void. After a short delay, they fire projectiles that deal {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> Magic Damage and silence champions for {{ e2 }} seconds."
      },
      {
         "range": [
            800,
            800,
            800,
            800,
            800
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }}% -> {{ e1NL }}%",
               "{{ cost }} -> {{ costnNL }}"
            ],
            "label": [
               "Damage %",
               "Mana Cost"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "4/5/6/7/8",
            "25/35/45/55/65",
            "5",
            "120"
         ],
         "image": {
            "w": 48,
            "full": "AlZaharNullZone.png",
            "sprite": "spell6.png",
            "group": "spell",
            "h": 48,
            "y": 48,
            "x": 48
         },
         "cooldown": [
            14,
            14,
            14,
            14,
            14
         ],
         "cost": [
            90,
            95,
            100,
            105,
            110
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.01],
            "key": "a1"
         }],
         "sanitizedDescription": "Malzahar creates a zone of negative energy which damages enemies that stand in it.",
         "rangeBurn": "800",
         "costType": "Mana",
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
               25,
               35,
               45,
               55,
               65
            ],
            [
               5,
               5,
               5,
               5,
               5
            ],
            [
               120,
               120,
               120,
               120,
               120
            ]
         ],
         "cooldownBurn": "14",
         "description": "Malzahar creates a zone of negative energy which damages enemies that stand in it.",
         "name": "Null Zone",
         "sanitizedTooltip": "Malzahar creates a zone of negative energy for {{ e3 }} seconds. The zone damages nearby enemies for {{ e1 }}% (+{{ a1 }}%) of their max Health each second (damage to monsters is capped at {{ e4 }} damage per second).",
         "key": "AlZaharNullZone",
         "costBurn": "90/95/100/105/110",
         "tooltip": "Malzahar creates a zone of negative energy for {{ e3 }} seconds. The zone damages nearby enemies for {{ e1 }}% <span class=\"color99FF99\">(+{{ a1 }}%)<\/span> of their max Health each second (damage to monsters is capped at {{ e4 }} damage per second)."
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
               " {{ cooldown }} -> {{ cooldownnNL }}",
               " {{ cost }} -> {{ costnNL }}"
            ],
            "label": [
               "Damage",
               "Mana Restore",
               "Cooldown",
               "Mana Cost"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "80/140/200/260/320",
            "10/14/18/22/26"
         ],
         "image": {
            "w": 48,
            "full": "AlZaharMaleficVisions.png",
            "sprite": "spell6.png",
            "group": "spell",
            "h": 48,
            "y": 48,
            "x": 96
         },
         "cooldown": [
            15,
            13,
            11,
            9,
            7
         ],
         "cost": [
            60,
            75,
            90,
            105,
            120
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.8],
            "key": "a1"
         }],
         "sanitizedDescription": "Malzahar infects his target's mind with cruel visions of their demise, dealing damage each second. If the target dies while afflicted by the visions, they pass on to a nearby enemy unit and Malzahar gains Mana. Malzahar's Voidlings are attracted to affected units.",
         "rangeBurn": "650",
         "costType": "Mana",
         "effect": [
            "null",
            [
               80,
               140,
               200,
               260,
               320
            ],
            [
               10,
               14,
               18,
               22,
               26
            ]
         ],
         "cooldownBurn": "15/13/11/9/7",
         "description": "Malzahar infects his target's mind with cruel visions of their demise, dealing damage each second. If the target dies while afflicted by the visions, they pass on to a nearby enemy unit and Malzahar gains Mana. Malzahar's Voidlings are attracted to affected units.",
         "name": "Malefic Visions",
         "sanitizedTooltip": "Malzahar infects his target's mind, dealing {{ e1 }} (+{{ a1 }}) Magic Damage over 4 seconds. If the target dies during this time, the visions pass to a nearby enemy and Malzahar gains {{ e2 }} Mana. Malzahar's Voidlings are attracted to affected units.",
         "key": "AlZaharMaleficVisions",
         "costBurn": "60/75/90/105/120",
         "tooltip": "Malzahar infects his target's mind, dealing {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> Magic Damage over 4 seconds.<br><br>If the target dies during this time, the visions pass to a nearby enemy and Malzahar gains {{ e2 }} Mana.<br><br>Malzahar's Voidlings are attracted to affected units."
      },
      {
         "range": [
            700,
            700,
            700
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               " {{ cooldown }} -> {{ cooldownnNL }}"
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
            "250/400/550"
         ],
         "image": {
            "w": 48,
            "full": "AlZaharNetherGrasp.png",
            "sprite": "spell6.png",
            "group": "spell",
            "h": 48,
            "y": 48,
            "x": 144
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
         "vars": [{
            "link": "spelldamage",
            "coeff": [1.3],
            "key": "a1"
         }],
         "sanitizedDescription": "Malzahar channels the essence of the Void to suppress an enemy champion and deal damage each second.",
         "rangeBurn": "700",
         "costType": "Mana",
         "effect": [
            "null",
            [
               250,
               400,
               550
            ]
         ],
         "cooldownBurn": "120/100/80",
         "description": "Malzahar channels the essence of the Void to suppress an enemy champion and deal damage each second.",
         "name": "Nether Grasp",
         "sanitizedTooltip": "Malzahar channels the essence of the Void to suppress target champion, dealing {{ e1 }} (+{{ a1 }}) Magic Damage over 2.5 seconds.",
         "key": "AlZaharNetherGrasp",
         "costBurn": "100",
         "tooltip": "Malzahar channels the essence of the Void to suppress target champion, dealing {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> Magic Damage over 2.5 seconds."
      }
   ],
   "key": "Malzahar"
}