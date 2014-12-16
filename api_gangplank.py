ABILITIES = {
   "id": 41,
   "title": "the Saltwater Scourge",
   "name": "Gangplank",
   "spells": [
      {
         "range": [
            625,
            625,
            625,
            625,
            625
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e2 }} -> {{ e2NL }}",
               "{{ cost }} -> {{ costnNL }}"
            ],
            "label": [
               "Base Damage",
               "Extra Gold",
               "Mana Cost"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "20/45/70/95/120",
            "4/5/6/7/8"
         ],
         "image": {
            "w": 48,
            "full": "Parley.png",
            "sprite": "spell3.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 240
         },
         "cooldown": [
            5,
            5,
            5,
            5,
            5
         ],
         "cost": [
            50,
            55,
            60,
            65,
            70
         ],
         "vars": [{
            "link": "attackdamage",
            "coeff": [1],
            "key": "f1"
         }],
         "sanitizedDescription": "Gangplank takes aim and shoots an enemy unit with his pistol. If Parrrley deals a killing blow, he gains extra gold and half the Mana cost is refunded.",
         "rangeBurn": "625",
         "costType": "Mana",
         "effect": [
            "null",
            [
               20,
               45,
               70,
               95,
               120
            ],
            [
               4,
               5,
               6,
               7,
               8
            ]
         ],
         "cooldownBurn": "5",
         "description": "Gangplank takes aim and shoots an enemy unit with his pistol. If Parrrley deals a killing blow, he gains extra gold and half the Mana cost is refunded.",
         "name": "Parrrley",
         "sanitizedTooltip": "Gangplank shoots a target unit for {{ e1 }} (+{{ f1 }}) physical damage. If Parrrley deals a killing blow, Gangplank gains {{ e2 }} extra gold and half the Mana cost is refunded. Parrrley can crit and applies on hit effects as if a melee basic attack. Total Gold Plundered: {{ f2 }} gold.",
         "key": "Parley",
         "costBurn": "50/55/60/65/70",
         "tooltip": "Gangplank shoots a target unit for {{ e1 }} <span class=\"colorFF8C00\">(+{{ f1 }})<\/span> physical damage. If Parrrley deals a killing blow, Gangplank gains {{ e2 }} extra gold and half the Mana cost is refunded.<br><br>Parrrley can crit and applies on hit effects as if a melee basic attack.<br><br><span class=\"colorFF9900\">Total Gold Plundered: <\/span>{{ f2 }} gold."
      },
      {
         "range": "self",
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ cooldown }} -> {{ cooldownnNL }}"
            ],
            "label": [
               "Heal",
               "Cooldown"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "80/150/220/290/360"
         ],
         "image": {
            "w": 48,
            "full": "RemoveScurvy.png",
            "sprite": "spell3.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 288
         },
         "cooldown": [
            22,
            21,
            20,
            19,
            18
         ],
         "cost": [
            65,
            65,
            65,
            65,
            65
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [1],
            "key": "a1"
         }],
         "sanitizedDescription": "Consumes a large quantity of citrus fruit which clears any crowd control effects on him and heals him.",
         "rangeBurn": "self",
         "costType": "Mana",
         "effect": [
            "null",
            [
               80,
               150,
               220,
               290,
               360
            ]
         ],
         "cooldownBurn": "22/21/20/19/18",
         "description": "Consumes a large quantity of citrus fruit which clears any crowd control effects on him and heals him.",
         "name": "Remove Scurvy",
         "sanitizedTooltip": "Consumes a large quantity of citrus fruit which clears any crowd control effects on him and heals him for {{ e1 }} (+{{ a1 }}) Health.",
         "key": "RemoveScurvy",
         "costBurn": "65",
         "tooltip": "Consumes a large quantity of citrus fruit which clears any crowd control effects on him and heals him for {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> Health."
      },
      {
         "range": [
            1300,
            1300,
            1300,
            1300,
            1300
         ],
         "leveltip": {
            "effect": [
               "{{ e3 }} -> {{ e3NL }}",
               "{{ e4 }}% -> {{ e4NL }}%",
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e2 }}% -> {{ e2NL }}%",
               "{{ cost }} -> {{ costnNL }}"
            ],
            "label": [
               "Active Attack Damage",
               "Active Movement Speed",
               "Passive Attack Damage",
               "Passive Movement Speed",
               "Mana Cost"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "8/10/12/14/16",
            "3/4/5/6/7",
            "12/19/26/33/40",
            "8/11/14/17/20"
         ],
         "image": {
            "w": 48,
            "full": "RaiseMorale.png",
            "sprite": "spell3.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 336
         },
         "cooldown": [
            20,
            20,
            20,
            20,
            20
         ],
         "cost": [
            50,
            55,
            60,
            65,
            70
         ],
         "sanitizedDescription": "Gangplank fires a shot into the air, increasing nearby allied champions' Attack Damage and Movement Speed.",
         "rangeBurn": "1300",
         "costType": "Mana",
         "effect": [
            "null",
            [
               8,
               10,
               12,
               14,
               16
            ],
            [
               3,
               4,
               5,
               6,
               7
            ],
            [
               12,
               19,
               26,
               33,
               40
            ],
            [
               8,
               11,
               14,
               17,
               20
            ]
         ],
         "cooldownBurn": "20",
         "description": "Gangplank fires a shot into the air, increasing nearby allied champions' Attack Damage and Movement Speed.",
         "name": "Raise Morale",
         "sanitizedTooltip": "Passive: Gangplank gains {{ e1 }} Attack Damage and {{ e2 }}% Movement Speed. Active: Gangplank fires his pistol into the air, disabling his passive boost but increasing his Attack Damage by {{ e3 }} and Movement Speed by {{ e4 }}% and nearby allied champions' Attack Damage and Movement Speed by half that amount for 7 seconds.",
         "key": "RaiseMorale",
         "costBurn": "50/55/60/65/70",
         "tooltip": "<span class=\"colorFF9900\">Passive: <\/span>Gangplank gains {{ e1 }} Attack Damage and {{ e2 }}% Movement Speed.<br><br><span class=\"colorFF9900\">Active: <\/span>Gangplank fires his pistol into the air, disabling his passive boost but increasing his Attack Damage by {{ e3 }} and Movement Speed by {{ e4 }}% and nearby allied champions' Attack Damage and Movement Speed by half that amount for 7 seconds."
      },
      {
         "range": [
            30000,
            30000,
            30000
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
            "75/120/165",
            "25",
            "7",
            "1"
         ],
         "image": {
            "w": 48,
            "full": "CannonBarrage.png",
            "sprite": "spell3.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 384
         },
         "cooldown": [
            125,
            110,
            95
         ],
         "cost": [
            100,
            100,
            100
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.2],
            "key": "a1"
         }],
         "sanitizedDescription": "Gangplank signals his ship to fire upon an area, slowing enemies and dealing damage within the area.",
         "rangeBurn": "30000",
         "costType": "Mana",
         "effect": [
            "null",
            [
               75,
               120,
               165
            ],
            [
               25,
               25,
               25
            ],
            [
               7,
               7,
               7
            ],
            [
               1,
               1,
               1
            ]
         ],
         "cooldownBurn": "125/110/95",
         "description": "Gangplank signals his ship to fire upon an area, slowing enemies and dealing damage within the area.",
         "name": "Cannon Barrage",
         "sanitizedTooltip": "Signals Gangplank's ship to fire upon an area for {{ e3 }} seconds, slowing enemies in the area by {{ e2 }}%. Waves of cannonballs rain upon the area, dealing {{ e1 }} (+{{ a1 }}) magic damage per second.",
         "key": "CannonBarrage",
         "costBurn": "100",
         "tooltip": "Signals Gangplank's ship to fire upon an area for {{ e3 }} seconds, slowing enemies in the area by {{ e2 }}%. Waves of cannonballs rain upon the area, dealing {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> magic damage per second."
      }
   ],
   "key": "Gangplank"
}