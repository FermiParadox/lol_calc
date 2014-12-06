ABILITIES = {
   "id": 1,
   "title": "the Dark Child",
   "name": "Annie",
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
               " {{ cost }} -> {{ costnNL }}"
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
            "80/115/150/185/220"
         ],
         "image": {
            "w": 48,
            "full": "Disintegrate.png",
            "sprite": "spell1.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 48
         },
         "cooldown": [
            4,
            4,
            4,
            4,
            4
         ],
         "cost": [
            60,
            65,
            70,
            75,
            80
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.8],
            "key": "a1"
         }],
         "sanitizedDescription": "Annie hurls a Mana infused fireball, dealing damage and refunding the Mana cost if it destroys the target.",
         "rangeBurn": "625",
         "costType": "Mana",
         "effect": [
            "null",
            [
               80,
               115,
               150,
               185,
               220
            ]
         ],
         "cooldownBurn": "4",
         "description": "Annie hurls a Mana infused fireball, dealing damage and refunding the Mana cost if it destroys the target.",
         "name": "Disintegrate",
         "sanitizedTooltip": "Deals {{ e1 }} (+{{ a1 }}) magic damage. Mana cost and half the cooldown are refunded if Disintegrate kills the target.",
         "key": "Disintegrate",
         "costBurn": "60/65/70/75/80",
         "tooltip": "Deals {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> magic damage. Mana cost and half the cooldown are refunded if Disintegrate kills the target."
      },
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
               " {{ cost }} -> {{ costnNL }}"
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
            "70/115/160/205/250"
         ],
         "image": {
            "w": 48,
            "full": "Incinerate.png",
            "sprite": "spell1.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 96
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
            80,
            90,
            100,
            110
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.85],
            "key": "a1"
         }],
         "sanitizedDescription": "Annie casts a blazing cone of fire, dealing damage to all enemies in the area.",
         "rangeBurn": "625",
         "costType": "Mana",
         "effect": [
            "null",
            [
               70,
               115,
               160,
               205,
               250
            ]
         ],
         "cooldownBurn": "8",
         "description": "Annie casts a blazing cone of fire, dealing damage to all enemies in the area.",
         "name": "Incinerate",
         "sanitizedTooltip": "Casts a cone of fire dealing {{ e1 }} (+{{ a1 }}) magic damage to all enemies in the area.",
         "key": "Incinerate",
         "costBurn": "70/80/90/100/110",
         "tooltip": "Casts a cone of fire dealing {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> magic damage to all enemies in the area."
      },
      {
         "range": "self",
         "leveltip": {
            "effect": [
               "{{ e2 }} -> {{ e2NL }}",
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e1 }} -> {{ e1NL }}"
            ],
            "label": [
               "Damage",
               "Armor Bonus",
               "Magic Resist Bonus"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "20/30/40/50/60",
            "20/30/40/50/60",
            "5"
         ],
         "image": {
            "w": 48,
            "full": "MoltenShield.png",
            "sprite": "spell1.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 144
         },
         "cooldown": [
            10,
            10,
            10,
            10,
            10
         ],
         "cost": [
            20,
            20,
            20,
            20,
            20
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.2],
            "key": "a1"
         }],
         "sanitizedDescription": "Increases Annie's Armor and Magic Resist and damages enemies who hit Annie with basic attacks.",
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
               30,
               40,
               50,
               60
            ],
            [
               5,
               5,
               5,
               5,
               5
            ]
         ],
         "cooldownBurn": "10",
         "description": "Increases Annie's Armor and Magic Resist and damages enemies who hit Annie with basic attacks.",
         "name": "Molten Shield",
         "sanitizedTooltip": "Increases Armor and Magic Resist by {{ e1 }} for {{ e3 }} seconds. Deals {{ e2 }} (+{{ a1 }}) magic damage to enemies who attack Annie with basic attacks.",
         "key": "MoltenShield",
         "costBurn": "20",
         "tooltip": "Increases Armor and Magic Resist by {{ e1 }} for {{ e3 }} seconds. Deals {{ e2 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> magic damage to enemies who attack Annie with basic attacks."
      },
      {
         "altimages": [{
            "w": 48,
            "full": "InfernalGuardian0.png",
            "sprite": "spell12.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 144
         }],
         "range": [
            600,
            600,
            600
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e2 }} -> {{ e2NL }}",
               "{{ e5 }} -> {{ e5NL }}",
               "{{ e3 }} -> {{ e3NL }}",
               "{{ cooldown }} -> {{ cooldownnNL }}"
            ],
            "label": [
               "Damage",
               "Tibbers Health",
               "Tibbers Armor and Magic Resist",
               "Tibbers Attack Damage",
               "Cooldown"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 3,
         "effectBurn": [
            "",
            "175/300/425",
            "1200/2100/3000",
            "80/105/130",
            "35",
            "30/50/70",
            "45"
         ],
         "image": {
            "w": 48,
            "full": "InfernalGuardian.png",
            "sprite": "spell1.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 192
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
         "vars": [
            {
               "link": "spelldamage",
               "coeff": [0.8],
               "key": "a1"
            },
            {
               "link": "spelldamage",
               "coeff": [0.2],
               "key": "a2"
            }
         ],
         "sanitizedDescription": "Annie wills her bear Tibbers to life, dealing damage to units in the area. Tibbers can attack and also burns enemies that stand near him.",
         "rangeBurn": "600",
         "costType": "Mana",
         "effect": [
            "null",
            [
               175,
               300,
               425
            ],
            [
               1200,
               2100,
               3000
            ],
            [
               80,
               105,
               130
            ],
            [
               35,
               35,
               35
            ],
            [
               30,
               50,
               70
            ],
            [
               45,
               45,
               45
            ]
         ],
         "cooldownBurn": "120/100/80",
         "description": "Annie wills her bear Tibbers to life, dealing damage to units in the area. Tibbers can attack and also burns enemies that stand near him.",
         "name": "Summon: Tibbers",
         "sanitizedTooltip": "Tibbers appears in a burst of flame dealing {{ e1 }} (+{{ a1 }}) magic damage to enemies in the target area. For the next {{ e6 }} seconds, Tibbers chases down enemies and deals {{ e4 }} (+{{ a2 }}) magic damage each second to nearby foes. Tibbers can be controlled by holding the alt key and using the right mouse button or by reactivating this ability.",
         "key": "InfernalGuardian",
         "costBurn": "100",
         "tooltip": "Tibbers appears in a burst of flame dealing {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> magic damage to enemies in the target area.<br><br>For the next {{ e6 }} seconds, Tibbers chases down enemies and deals {{ e4 }}<span class=\"color99FF99\"> (+{{ a2 }})<\/span> magic damage each second to nearby foes.<br><br><span class=\"color99FF99\">Tibbers can be controlled by holding the alt key and using the right mouse button or by reactivating this ability.<\/span>"
      }
   ],
   "key": "Annie"
}