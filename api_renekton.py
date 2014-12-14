ABILITIES = {
   "id": 58,
   "title": "the Butcher of the Sands",
   "name": "Renekton",
   "spells": [
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
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e2 }} / {{ e3 }} -> {{ e2NL }} / {{ e3NL }}",
               "{{ e4 }} -> {{ e4NL }}"
            ],
            "label": [
               "Damage",
               "Max Health Gain",
               "Fury Damage"
            ]
         },
         "resource": "No Cost or 50 Fury",
         "maxrank": 5,
         "effectBurn": [
            "",
            "60/90/120/150/180",
            "50/75/100/125/150",
            "150/225/300/375/450",
            "90/135/180/225/270"
         ],
         "image": {
            "w": 48,
            "full": "RenektonCleave.png",
            "sprite": "spell8.png",
            "group": "spell",
            "h": 48,
            "y": 48,
            "x": 0
         },
         "cooldown": [
            8,
            8,
            8,
            8,
            8
         ],
         "cost": [
            0,
            0,
            0,
            0,
            0
         ],
         "vars": [
            {
               "link": "bonusattackdamage",
               "coeff": [0.8],
               "key": "f1"
            },
            {
               "link": "bonusattackdamage",
               "coeff": [1.2],
               "key": "f2"
            }
         ],
         "sanitizedDescription": "Renekton swings his blade, dealing moderate physical damage to all targets around him, and heals for a small portion of the damage dealt. If he has more than 50 Fury, his damage and heal are increased.",
         "rangeBurn": "325",
         "costType": "NoCostor50Fury",
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
               50,
               75,
               100,
               125,
               150
            ],
            [
               150,
               225,
               300,
               375,
               450
            ],
            [
               90,
               135,
               180,
               225,
               270
            ]
         ],
         "cooldownBurn": "8",
         "description": "Renekton swings his blade, dealing moderate physical damage to all targets around him, and heals for a small portion of the damage dealt. If he has more than 50 Fury, his damage and heal are increased.",
         "name": "Cull the Meek",
         "sanitizedTooltip": "Renekton swings his blade, dealing {{ e1 }} (+{{ f1 }}) physical damage to nearby enemies and gains 5% of the damage dealt as Health (20% for champions), up to {{ e2 }}. 50 Fury Bonus: Damage increased to {{ e4 }} (+{{ f2 }}). Heal percent increased to 10%, up to {{ e3 }}.",
         "key": "RenektonCleave",
         "costBurn": "0",
         "tooltip": "Renekton swings his blade, dealing {{ e1 }} <span class=\"colorFF8C00\">(+{{ f1 }})<\/span> physical damage to nearby enemies and gains 5% of the damage dealt as Health (20% for champions), up to {{ e2 }}. <br><br><span class=\"colorFF6633\">50 Fury Bonus:<\/span> Damage increased to {{ e4 }} <span class=\"colorFF8C00\">(+{{ f2 }})<\/span>. Heal percent increased to 10%, up to {{ e3 }}. "
      },
      {
         "range": "self",
         "leveltip": {
            "effect": [
               "{{ e3 }} / {{ e4 }} -> {{ e3NL }} / {{ e4NL }}",
               "{{ cooldown }} -> {{ cooldownnNL }}"
            ],
            "label": [
               "Bonus Damage",
               "Cooldown"
            ]
         },
         "resource": "No Cost or 50 Fury",
         "maxrank": 5,
         "effectBurn": [
            "",
            "225",
            "150",
            "10/30/50/70/90",
            "15/45/75/105/135"
         ],
         "image": {
            "w": 48,
            "full": "RenektonPreExecute.png",
            "sprite": "spell8.png",
            "group": "spell",
            "h": 48,
            "y": 48,
            "x": 48
         },
         "cooldown": [
            13,
            12,
            11,
            10,
            9
         ],
         "cost": [
            0,
            0,
            0,
            0,
            0
         ],
         "vars": [
            {
               "link": "attackdamage",
               "coeff": [1.5],
               "key": "f1"
            },
            {
               "link": "attackdamage",
               "coeff": [2.25],
               "key": "f2"
            }
         ],
         "sanitizedDescription": "Renekton slashes his target twice, dealing moderate physical damage and stuns them for 0.75 seconds. If Renekton has more than 50 Fury, he slashes his target three times, dealing high physical damage and stuns them for 1.5 seconds.",
         "rangeBurn": "self",
         "costType": "NoCostor50Fury",
         "effect": [
            "null",
            [
               225,
               225,
               225,
               225,
               225
            ],
            [
               150,
               150,
               150,
               150,
               150
            ],
            [
               10,
               30,
               50,
               70,
               90
            ],
            [
               15,
               45,
               75,
               105,
               135
            ]
         ],
         "cooldownBurn": "13/12/11/10/9",
         "description": "Renekton slashes his target twice, dealing moderate physical damage and stuns them for 0.75 seconds. If Renekton has more than 50 Fury, he slashes his target three times, dealing high physical damage and stuns them for 1.5 seconds.",
         "name": "Ruthless Predator",
         "sanitizedTooltip": "Renekton's next attack strikes twice, dealing {{ f1 }} physical damage ({{ e3 }} + {{ e2 }}% of his Attack Damage) and stuns for 0.75 seconds. Each hit applies on-hit effects. 50 Fury Bonus: Renekton attacks three times, dealing {{ f2 }} physical damage ({{ e4 }} + {{ e1 }}% of his Attack Damage) and stuns his target for 1.5 seconds.",
         "key": "RenektonPreExecute",
         "costBurn": "0",
         "tooltip": "Renekton's next attack strikes twice, dealing <span class=\"colorFF8C00\">{{ f1 }}<\/span> physical damage ({{ e3 }} + {{ e2 }}% of his Attack Damage) and stuns for 0.75 seconds. Each hit applies on-hit effects.<br><br><span class=\"colorFF6633\">50 Fury Bonus:<\/span> Renekton attacks three times, dealing <span class=\"colorFF8C00\">{{ f2 }}<\/span> physical damage ({{ e4 }} + {{ e1 }}% of his Attack Damage) and stuns his target for 1.5 seconds. "
      },
      {
         "range": [
            450,
            450,
            450,
            450,
            450
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e2 }}% -> {{ e2NL }}%",
               "{{ cooldown }} -> {{ cooldownnNL }}"
            ],
            "label": [
               "Bonus Damage",
               "Armor Reduction %",
               "Cooldown"
            ]
         },
         "resource": "No Cost or 50 Fury",
         "maxrank": 5,
         "effectBurn": [
            "",
            "30/60/90/120/150",
            "15/20/25/30/35",
            "45/90/135/180/225"
         ],
         "image": {
            "w": 48,
            "full": "RenektonSliceAndDice.png",
            "sprite": "spell8.png",
            "group": "spell",
            "h": 48,
            "y": 48,
            "x": 96
         },
         "cooldown": [
            18,
            17,
            16,
            15,
            14
         ],
         "cost": [
            0,
            0,
            0,
            0,
            0
         ],
         "vars": [
            {
               "link": "bonusattackdamage",
               "coeff": [0.9],
               "key": "f1"
            },
            {
               "link": "bonusattackdamage",
               "coeff": [1.35],
               "key": "f2"
            }
         ],
         "sanitizedDescription": "Renekton dashes, dealing damage to units along the way. Empowered, Renekton deals bonus damage and reduces the Armor of units hit.",
         "rangeBurn": "450",
         "costType": "NoCostor50Fury",
         "effect": [
            "null",
            [
               30,
               60,
               90,
               120,
               150
            ],
            [
               15,
               20,
               25,
               30,
               35
            ],
            [
               45,
               90,
               135,
               180,
               225
            ]
         ],
         "cooldownBurn": "18/17/16/15/14",
         "description": "Renekton dashes, dealing damage to units along the way. Empowered, Renekton deals bonus damage and reduces the Armor of units hit.",
         "name": "Slice and Dice",
         "sanitizedTooltip": "Slice: Renekton dashes, dealing {{ e1 }} (+{{ f1 }}) physical damage. Hitting an enemy grants the ability to use Dice for 4 seconds. Dice: Renekton dashes, dealing {{ e1 }} (+{{ f1 }}) physical damage. Dice - 50 Fury Bonus: Damage increased to {{ e3 }} (+{{ f2 }}). Enemies hit have {{ e2 }}% reduced Armor for 4 seconds.",
         "key": "RenektonSliceAndDice",
         "costBurn": "0",
         "tooltip": "<span class=\"colorFF6633\">Slice:<\/span> Renekton dashes, dealing {{ e1 }} <span class=\"colorFF8C00\">(+{{ f1 }})<\/span> physical damage. Hitting an enemy grants the ability to use Dice for 4 seconds.<br><br><span class=\"colorFF6633\">Dice:<\/span> Renekton dashes, dealing {{ e1 }} <span class=\"colorFF8C00\">(+{{ f1 }})<\/span> physical damage. <br><br><span class=\"colorFF6633\">Dice - 50 Fury Bonus:<\/span> Damage increased to {{ e3 }} <span class=\"colorFF8C00\">(+{{ f2 }})<\/span>. Enemies hit have {{ e2 }}% reduced Armor for 4 seconds. "
      },
      {
         "range": "self",
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e2 }} -> {{ e2NL }}"
            ],
            "label": [
               "Bonus Health",
               "Periodic Damage"
            ]
         },
         "resource": "No Cost",
         "maxrank": 3,
         "effectBurn": [
            "",
            "200/400/800",
            "30/60/120",
            "7.5"
         ],
         "image": {
            "w": 48,
            "full": "RenektonReignOfTheTyrant.png",
            "sprite": "spell8.png",
            "group": "spell",
            "h": 48,
            "y": 48,
            "x": 144
         },
         "cooldown": [
            120,
            120,
            120
         ],
         "cost": [
            0,
            0,
            0
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.1],
            "key": "a1"
         }],
         "sanitizedDescription": "Renekton transforms into the Tyrant form, gaining bonus Health and dealing damage to enemies around him. While in this form, Renekton gains Fury periodically.",
         "rangeBurn": "self",
         "costType": "NoCost",
         "effect": [
            "null",
            [
               200,
               400,
               800
            ],
            [
               30,
               60,
               120
            ],
            [
               7.5,
               7.5,
               7.5
            ]
         ],
         "cooldownBurn": "120",
         "description": "Renekton transforms into the Tyrant form, gaining bonus Health and dealing damage to enemies around him. While in this form, Renekton gains Fury periodically.",
         "name": "Dominus",
         "sanitizedTooltip": "Renekton surrounds himself with dark energies for 15 seconds, gaining {{ e1 }} Health. While active, he deals {{ e2 }} (+{{ a1 }}) magic damage to nearby enemies and gains 5 Fury per second.",
         "key": "RenektonReignOfTheTyrant",
         "costBurn": "0",
         "tooltip": "Renekton surrounds himself with dark energies for 15 seconds, gaining {{ e1 }} Health. While active, he deals {{ e2 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> magic damage to nearby enemies and gains 5 Fury per second."
      }
   ],
   "key": "Renekton"
}