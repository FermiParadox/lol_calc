ABILITIES = {
   "id": 68,
   "title": "the Mechanized Menace",
   "name": "Rumble",
   "spells": [
      {
         "range": [
            600,
            600,
            600,
            600,
            600
         ],
         "leveltip": {
            "effect": ["{{ e1 }} -> {{ e1NL }}"],
            "label": ["Damage"]
         },
         "resource": "{{ e2 }} Heat",
         "maxrank": 5,
         "effectBurn": [
            "",
            "75/135/195/255/315",
            "20",
            "35/30/25/20/15"
         ],
         "image": {
            "w": 48,
            "full": "RumbleFlameThrower.png",
            "sprite": "spell8.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 96
         },
         "cooldown": [
            6,
            6,
            6,
            6,
            6
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
            "coeff": [1],
            "key": "a1"
         }],
         "sanitizedDescription": "Rumble torches opponents in front of him, dealing magic damage in a cone for 3 seconds. While in Danger Zone this damage is increased.",
         "rangeBurn": "600",
         "costType": "Heat",
         "effect": [
            "null",
            [
               75,
               135,
               195,
               255,
               315
            ],
            [
               20,
               20,
               20,
               20,
               20
            ],
            [
               35,
               30,
               25,
               20,
               15
            ]
         ],
         "cooldownBurn": "6",
         "description": "Rumble torches opponents in front of him, dealing magic damage in a cone for 3 seconds. While in Danger Zone this damage is increased. ",
         "name": "Flamespitter",
         "sanitizedTooltip": "Rumble torches his opponents, dealing {{ e1 }} (+{{ a1 }}) magic damage in a cone over 3 seconds. This spell deals half damage to minions and neutral monsters. Danger Zone Bonus: Deals 50% bonus damage.",
         "key": "RumbleFlameThrower",
         "costBurn": "0",
         "tooltip": "Rumble torches his opponents, dealing {{ e1 }}<span class=\"color99FF99\"> (+{{ a1 }})<\/span> magic damage in a cone over 3 seconds. This spell deals half damage to minions and neutral monsters.<br><br><span class=\"colorFFFF00\">Danger Zone Bonus:<\/span> Deals 50% bonus damage."
      },
      {
         "range": "self",
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e2 }}% -> {{ e2NL }}%"
            ],
            "label": [
               "Damage Absorption",
               "Movement Speed Bonus"
            ]
         },
         "resource": "{{ e3 }} Heat",
         "maxrank": 5,
         "effectBurn": [
            "",
            "50/80/110/140/170",
            "10/15/20/25/30",
            "20",
            "13/19/26/32/39"
         ],
         "image": {
            "w": 48,
            "full": "RumbleShield.png",
            "sprite": "spell8.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 144
         },
         "cooldown": [
            6,
            6,
            6,
            6,
            6
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
            "coeff": [0.4],
            "key": "a1"
         }],
         "sanitizedDescription": "Rumble pulls up a shield, protecting him from damage and granting him a quick burst of speed. While in Danger Zone, the shield strength and speed bonus is increased.",
         "rangeBurn": "self",
         "costType": "Heat",
         "effect": [
            "null",
            [
               50,
               80,
               110,
               140,
               170
            ],
            [
               10,
               15,
               20,
               25,
               30
            ],
            [
               20,
               20,
               20,
               20,
               20
            ],
            [
               13,
               19,
               26,
               32,
               39
            ]
         ],
         "cooldownBurn": "6",
         "description": "Rumble pulls up a shield, protecting him from damage and granting him a quick burst of speed. While in Danger Zone, the shield strength and speed bonus is increased. ",
         "name": "Scrap Shield",
         "sanitizedTooltip": "Rumble tosses up a shield for 2 seconds that absorbs {{ e1 }} (+{{ a1 }}) damage. Rumble also gains an additional {{ e2 }}% Movement Speed for 1 second. Danger Zone Bonus: 50% increase in shield health and Movement Speed.",
         "key": "RumbleShield",
         "costBurn": "0",
         "tooltip": "Rumble tosses up a shield for 2 seconds that absorbs {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> damage. Rumble also gains an additional {{ e2 }}% Movement Speed for 1 second. <\/span><br><br><span class=\"colorFFFF00\">Danger Zone Bonus:<\/span> 50% increase in shield health and Movement Speed."
      },
      {
         "range": [
            850,
            850,
            850,
            850,
            850
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e2 }}% -> {{ e2NL }}%"
            ],
            "label": [
               "Damage",
               "Slow Amount"
            ]
         },
         "resource": "{{ e3 }} Heat",
         "maxrank": 5,
         "effectBurn": [
            "",
            "45/70/95/120/145",
            "15/20/25/30/35",
            "20",
            "20/26/33/39/45",
            "20/15/15/10/10"
         ],
         "image": {
            "w": 48,
            "full": "RumbleGrenade.png",
            "sprite": "spell8.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 192
         },
         "cooldown": [
            0.5,
            0.5,
            0.5,
            0.5,
            0.5
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
            "coeff": [0.4],
            "key": "a1"
         }],
         "sanitizedDescription": "Rumble launches a taser, electrocuting his target with magic damage and slowing their Movement Speed. A second shot can be fired within 3 seconds. While in Danger Zone the damage and slow percentage is increased.",
         "rangeBurn": "850",
         "costType": "Heat",
         "effect": [
            "null",
            [
               45,
               70,
               95,
               120,
               145
            ],
            [
               15,
               20,
               25,
               30,
               35
            ],
            [
               20,
               20,
               20,
               20,
               20
            ],
            [
               20,
               26,
               33,
               39,
               45
            ],
            [
               20,
               15,
               15,
               10,
               10
            ]
         ],
         "cooldownBurn": "0.5",
         "description": "Rumble launches a taser, electrocuting his target with magic damage and slowing their Movement Speed. A second shot can be fired within 3 seconds. While in Danger Zone the damage and slow percentage is increased.  ",
         "name": "Electro Harpoon",
         "sanitizedTooltip": "Rumble shoots his opponent with up to 2 tasers, dealing {{ e1 }} (+{{ a1 }}) magic damage and applying a stacking slow of {{ e2 }}% for 3 seconds. Danger Zone Bonus: Damage and slow percentage increased by 50%. After using this ability you may cast it a second time at no cost within 3 seconds.",
         "key": "RumbleGrenade",
         "costBurn": "0",
         "tooltip": "Rumble shoots his opponent with up to 2 tasers, dealing {{ e1 }}<span class=\"color99FF99\"> (+{{ a1 }})<\/span> magic damage and applying a stacking slow of {{ e2 }}% for 3 seconds.<br><br><span class=\"colorFFFF00\">Danger Zone Bonus:<\/span> Damage and slow percentage increased by 50%.<br><br><span class=\"color99FF99\">After using this ability you may cast it a second time at no cost within 3 seconds.<\/span>"
      },
      {
         "range": [
            1750,
            1750,
            1750
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ cooldown }} -> {{ cooldownnNL }}"
            ],
            "label": [
               "Damage Per Second",
               "Cooldown"
            ]
         },
         "resource": "No Cost",
         "maxrank": 3,
         "effectBurn": [
            "",
            "130/185/240",
            "150/225/300",
            "35"
         ],
         "image": {
            "w": 48,
            "full": "RumbleCarpetBomb.png",
            "sprite": "spell8.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 240
         },
         "cooldown": [
            105,
            90,
            75
         ],
         "cost": [
            0,
            0,
            0
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.3],
            "key": "a2"
         }],
         "sanitizedDescription": "Rumble fires off a group of rockets, creating a wall of flames that damages and slows enemies.",
         "rangeBurn": "1750",
         "costType": "NoCost",
         "effect": [
            "null",
            [
               130,
               185,
               240
            ],
            [
               150,
               225,
               300
            ],
            [
               35,
               35,
               35
            ]
         ],
         "cooldownBurn": "105/90/75",
         "description": "Rumble fires off a group of rockets, creating a wall of flames that damages and slows enemies. ",
         "name": "The Equalizer",
         "sanitizedTooltip": "Rumble launches a line of rockets that creates a burning trail for 5 seconds. Enemies in the area have their Movement Speed slowed by {{ e3 }}% and take {{ e1 }} (+{{ a2 }}) magic damage each second. You can control the placement of this attack by clicking and dragging your mouse in a line.",
         "key": "RumbleCarpetBomb",
         "costBurn": "0",
         "tooltip": "Rumble launches a line of rockets that creates a burning trail for 5 seconds. Enemies in the area have their Movement Speed slowed by {{ e3 }}% and take {{ e1 }}<span class=\"color99FF99\"> (+{{ a2 }})<\/span> magic damage each second.<br><br><span class=\"color99FF99\">You can control the placement of this attack by clicking and dragging your mouse in a line.<\/span>"
      }
   ],
   "key": "Rumble"
}