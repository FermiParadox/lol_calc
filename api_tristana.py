ABILITIES = {
   "id": 18,
   "title": "the Megling Gunner",
   "name": "Tristana",
   "spells": [
      {
         "range": "self",
         "leveltip": {
            "effect": [" {{ e1 }} -> {{ e1NL }}%"],
            "label": ["Attack Speed % "]
         },
         "resource": "No Cost",
         "maxrank": 5,
         "effectBurn": [
            "",
            "30/50/70/90/110"
         ],
         "image": {
            "w": 48,
            "full": "RapidFire.png",
            "sprite": "spell10.png",
            "group": "spell",
            "h": 48,
            "y": 48,
            "x": 192
         },
         "cooldown": [
            20,
            20,
            20,
            20,
            20
         ],
         "cost": [
            0,
            0,
            0,
            0,
            0
         ],
         "sanitizedDescription": "Tristana fires her weapon rapidly, increasing her Attack Speed for a short time.",
         "rangeBurn": "self",
         "costType": "NoCost",
         "effect": [
            "null",
            [
               30,
               50,
               70,
               90,
               110
            ]
         ],
         "cooldownBurn": "20",
         "description": "Tristana fires her weapon rapidly, increasing her Attack Speed for a short time.",
         "name": "Rapid Fire",
         "sanitizedTooltip": "Increases Tristana's Attack Speed by {{ e1 }}% for 5 seconds.",
         "key": "RapidFire",
         "costBurn": "0",
         "tooltip": "Increases Tristana's Attack Speed by {{ e1 }}% for 5 seconds."
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
               "{{ e3 }} -> {{ e3NL }}",
               "{{ cooldown }} -> {{ cooldownnNL }}"
            ],
            "label": [
               "Damage",
               "Slow Duration",
               "Cooldown"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "70/115/160/205/250",
            "22/20/18/16/14",
            "1/1.5/2/2.5/3"
         ],
         "image": {
            "w": 48,
            "full": "RocketJump.png",
            "sprite": "spell10.png",
            "group": "spell",
            "h": 48,
            "y": 48,
            "x": 240
         },
         "cooldown": [
            22,
            20,
            18,
            16,
            14
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
            "coeff": [0.8],
            "key": "a1"
         }],
         "sanitizedDescription": "Tristana fires at the ground to propel herself to a distant location, dealing damage and slowing surrounding units for 3 seconds where she lands.",
         "rangeBurn": "900",
         "costType": "Mana",
         "effect": [
            "null",
            [
               70,
               115,
               160,
               205,
               250
            ],
            [
               22,
               20,
               18,
               16,
               14
            ],
            [
               1,
               1.5,
               2,
               2.5,
               3
            ]
         ],
         "cooldownBurn": "22/20/18/16/14",
         "description": "Tristana fires at the ground to propel herself to a distant location, dealing damage and slowing surrounding units for 3 seconds where she lands.",
         "name": "Rocket Jump",
         "sanitizedTooltip": "Tristana fires at the ground to propel herself to target location, dealing {{ e1 }} (+{{ a1 }}) Magic Damage and slowing surrounding units by 60% for {{ e3 }} seconds when she lands. On a champion kill or assist, Rocket Jump's cooldown resets.",
         "key": "RocketJump",
         "costBurn": "60",
         "tooltip": "Tristana fires at the ground to propel herself to target location, dealing {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> Magic Damage and slowing surrounding units by 60% for {{ e3 }} seconds when she lands.<br>On a champion kill or assist, Rocket Jump's cooldown resets."
      },
      {
         "range": [
            550,
            550,
            550,
            550,
            550
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e3 }} -> {{ e3NL }}",
               "{{ cost }} -> {{ costnNL }}"
            ],
            "label": [
               "Explosion Damage",
               "Debuff Damage",
               "Mana Cost"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "50/75/100/125/150",
            "4/5/6/7/8",
            "80/125/170/215/260"
         ],
         "image": {
            "w": 48,
            "full": "DetonatingShot.png",
            "sprite": "spell10.png",
            "group": "spell",
            "h": 48,
            "y": 48,
            "x": 288
         },
         "cooldown": [
            16,
            16,
            16,
            16,
            16
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
               "link": "spelldamage",
               "coeff": [0.25],
               "key": "a2"
            },
            {
               "link": "spelldamage",
               "coeff": [1],
               "key": "a1"
            }
         ],
         "sanitizedDescription": "When Tristana kills a unit, her cannonballs burst into shrapnel, dealing damage to surrounding enemies. Can be activated to deal damage to target unit over time, and reduce healing received.",
         "rangeBurn": "550",
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
               4,
               5,
               6,
               7,
               8
            ],
            [
               80,
               125,
               170,
               215,
               260
            ]
         ],
         "cooldownBurn": "16",
         "description": "When Tristana kills a unit, her cannonballs burst into shrapnel, dealing damage to surrounding enemies. Can be activated to deal damage to target unit over time, and reduce healing received.",
         "name": "Explosive Shot",
         "sanitizedTooltip": "Passive: Enemies explode when slain by Tristana's basic attacks, dealing {{ e1 }} (+{{ a2 }}) Magic Damage to nearby enemies. Active: Rends target enemy, reducing healing and health regeneration by 50% and dealing {{ e3 }} (+{{ a1 }}) Magic Damage over 5 seconds.",
         "key": "DetonatingShot",
         "costBurn": "50/60/70/80/90",
         "tooltip": "<span class=\"colorFF9900\">Passive: <\/span>Enemies explode when slain by Tristana's basic attacks, dealing {{ e1 }} <span class=\"color99FF99\">(+{{ a2 }})<\/span> Magic Damage to nearby enemies.<br><br><span class=\"colorFF9900\">Active: <\/span>Rends target enemy, reducing healing and health regeneration by 50% and dealing {{ e3 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> Magic Damage over 5 seconds."
      },
      {
         "range": [
            550,
            550,
            550
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               " {{ e2 }} -> {{ e2NL }}",
               "{{ cooldown }} -> {{ cooldownnNL }}"
            ],
            "label": [
               "Damage",
               "Knockback Distance",
               "Cooldown"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 3,
         "effectBurn": [
            "",
            "300/400/500",
            "600/800/1000",
            "90/75/60"
         ],
         "image": {
            "w": 48,
            "full": "BusterShot.png",
            "sprite": "spell10.png",
            "group": "spell",
            "h": 48,
            "y": 48,
            "x": 336
         },
         "cooldown": [
            100,
            85,
            70
         ],
         "cost": [
            100,
            100,
            100
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [1.5],
            "key": "a1"
         }],
         "sanitizedDescription": "Tristana loads a massive cannonball into her weapon and fires it at an enemy unit. This deals Magic Damage and knocks the target back.",
         "rangeBurn": "550",
         "costType": "Mana",
         "effect": [
            "null" ,
            [
               300,
               400,
               500
            ],
            [
               600,
               800,
               1000
            ],
            [
               90,
               75,
               60
            ]
         ],
         "cooldownBurn": "100/85/70",
         "description": "Tristana loads a massive cannonball into her weapon and fires it at an enemy unit. This deals Magic Damage and knocks the target back.",
         "name": "Buster Shot",
         "sanitizedTooltip": "Tristana fires a massive cannonball at an enemy unit. This deals {{ e1 }} (+{{ a1 }}) Magic Damage and knocks surrounding units back {{ e2 }} distance.",
         "key": "BusterShot",
         "costBurn": "100",
         "tooltip": "Tristana fires a massive cannonball at an enemy unit. This deals {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> Magic Damage and knocks surrounding units back {{ e2 }} distance."
      }
   ],
   "key": "Tristana"
}