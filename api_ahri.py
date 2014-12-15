ABILITIES = {
   "id": 103,
   "title": "the Nine-Tailed Fox",
   "name": "Ahri",
   "spells": [
      {
         "range": [
            880,
            880,
            880,
            880,
            880
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "  {{ cost }} -> {{ costnNL }}"
            ],
            "label": [
               "Damage",
               "Mana Cost"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "40/65/90/115/140"
         ],
         "image": {
            "w": 48,
            "full": "AhriOrbofDeception.png",
            "sprite": "spell0.png",
            "group": "spell",
            "h": 48,
            "y": 48,
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
            55,
            60,
            65,
            70,
            75
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.35],
            "key": "a1"
         }],
         "sanitizedDescription": "Ahri sends out and pulls back her orb, dealing magic damage on the way out and true damage on the way back.",
         "rangeBurn": "880",
         "costType": "Mana",
         "effect": [
            "null",
            [
               40,
               65,
               90,
               115,
               140
            ]
         ],
         "cooldownBurn": "7",
         "description": "Ahri sends out and pulls back her orb, dealing magic damage on the way out and true damage on the way back.",
         "name": "Orb of Deception",
         "sanitizedTooltip": "Deals {{ e1 }} (+{{ a1 }}) magic damage on the way out, and {{ e1 }} (+{{ a1 }}) true damage on the way back.",
         "key": "AhriOrbofDeception",
         "costBurn": "55/60/65/70/75",
         "tooltip": "Deals {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> magic damage on the way out, and {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> true damage on the way back."
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
               "{{ e1 }} -> {{ e1NL }}",
               " {{ cooldown }} -> {{ cooldownnNL }}"
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
            "40/65/90/115/140",
            "12/19.5/27/34.5/42",
            "64/104/144/184/224"
         ],
         "image": {
            "w": 48,
            "full": "AhriFoxFire.png",
            "sprite": "spell0.png",
            "group": "spell",
            "h": 48,
            "y": 48,
            "x": 384
         },
         "cooldown": [
            9,
            8,
            7,
            6,
            5
         ],
         "cost": [
            50,
            50,
            50,
            50,
            50
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.4],
            "key": "a1"
         }],
         "sanitizedDescription": "Ahri releases three fox-fires, that lock onto and attack nearby enemies.",
         "rangeBurn": "800",
         "costType": "Mana",
         "effect": [
            "null",
            [
               40,
               65,
               90,
               115,
               140
            ],
            [
               12,
               19.5,
               27,
               34.5,
               42
            ],
            [
               64,
               104,
               144,
               184,
               224
            ]
         ],
         "cooldownBurn": "9/8/7/6/5",
         "description": "Ahri releases three fox-fires, that lock onto and attack nearby enemies.",
         "name": "Fox-Fire",
         "sanitizedTooltip": "Releases three fox-fires that lock on to nearby enemies (prioritizes Champions) dealing {{ e1 }} (+{{ a1 }}) magic damage. Enemies hit with multiple fox-fires take 30% damage from each additional fox-fire beyond the first, for a maximum of {{ f1 }} damage to a single enemy.",
         "key": "AhriFoxFire",
         "costBurn": "50",
         "tooltip": "Releases three fox-fires that lock on to nearby enemies (prioritizes Champions) dealing {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> magic damage.<br><br>Enemies hit with multiple fox-fires take 30% damage from each additional fox-fire beyond the first, for a maximum of {{ f1 }} damage to a single enemy."
      },
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
               " {{ e2 }} -> {{ e2NL }}"
            ],
            "label": [
               "Damage",
               "Duration"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "60/90/120/150/180",
            "1/1.25/1.5/1.75/2"
         ],
         "image": {
            "w": 48,
            "full": "AhriSeduce.png",
            "sprite": "spell0.png",
            "group": "spell",
            "h": 48,
            "y": 48,
            "x": 432
         },
         "cooldown": [
            12,
            12,
            12,
            12,
            12
         ],
         "cost": [
            85,
            85,
            85,
            85,
            85
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.35],
            "key": "a1"
         }],
         "sanitizedDescription": "Ahri blows a kiss that damages and charms an enemy it encounters, causing them to walk harmlessly towards her. Ahri deals additional damage to recently charmed enemies.",
         "rangeBurn": "975",
         "costType": "Mana",
         "effect": [
            "null",
            [
               60,
               90,
               120,
               150,
               180
            ],
            [
               1,
               1.25,
               1.5,
               1.75,
               2
            ]
         ],
         "cooldownBurn": "12",
         "description": "Ahri blows a kiss that damages and charms an enemy it encounters, causing them to walk harmlessly towards her. Ahri deals additional damage to recently charmed enemies.",
         "name": "Charm",
         "sanitizedTooltip": "Blows a kiss dealing {{ e1 }} (+{{ a1 }}) magic damage and charms an enemy causing them to walk harmlessly towards Ahri for {{ e2 }} second(s). Enemies hit by Charm take 20% more magic damage from Ahri for 6 seconds. Orb of Deception's true damage is also increased by this effect.",
         "key": "AhriSeduce",
         "costBurn": "85",
         "tooltip": "Blows a kiss dealing {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> magic damage and charms an enemy causing them to walk harmlessly towards Ahri for {{ e2 }} second(s).<br><br>Enemies hit by Charm take 20% more magic damage from Ahri for 6 seconds. Orb of Deception's true damage is also increased by this effect."
      },
      {
         "range": [
            450,
            450,
            450
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
            "70/110/150",
            "10/20/30",
            "28/23/18",
            "2",
            "1"
         ],
         "image": {
            "w": 48,
            "full": "AhriTumble.png",
            "sprite": "spell0.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 0
         },
         "cooldown": [
            110,
            95,
            80
         ],
         "cost": [
            100,
            100,
            100
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.3],
            "key": "a1"
         }],
         "sanitizedDescription": "Ahri dashes forward and fires essence bolts, damaging 3 nearby enemies (prioritizes Champions). Spirit Rush can be cast up to three times before going on cooldown.",
         "rangeBurn": "450",
         "costType": "Mana",
         "effect": [
            "null",
            [
               70,
               110,
               150
            ],
            [
               10,
               20,
               30
            ],
            [
               28,
               23,
               18
            ],
            [
               2,
               2,
               2
            ],
            [
               1,
               1,
               1
            ]
         ],
         "cooldownBurn": "110/95/80",
         "description": "Ahri dashes forward and fires essence bolts, damaging 3 nearby enemies (prioritizes Champions). Spirit Rush can be cast up to three times before going on cooldown.",
         "name": "Spirit Rush",
         "sanitizedTooltip": "Nimbly dashes forward firing 3 essence bolts at nearby enemies (prioritizes Champions) dealing {{ e1 }} (+{{ a1 }}) magic damage. Can be cast up to three times within 10 seconds before going on cooldown.",
         "key": "AhriTumble",
         "costBurn": "100",
         "tooltip": "Nimbly dashes forward firing 3 essence bolts at nearby enemies (prioritizes Champions) dealing {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> magic damage. Can be cast up to three times within 10 seconds before going on cooldown."
      }
   ],
   "key": "Ahri"
}