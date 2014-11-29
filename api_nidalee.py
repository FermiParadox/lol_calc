NIDALEE_ABILITIES = {
   "id": 76,
   "title": "the Bestial Huntress",
   "name": "Nidalee",
   "spells": [
      {
         "altimages": [{
            "w": 48,
            "full": "JavelinToss0.png",
            "sprite": "spell13.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 48
         }],
         "range": [
            1500,
            1500,
            1500,
            1500,
            1500
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e2 }} -> {{ e2NL }}",
               "{{ e3 }} -> {{ e3NL }}"
            ],
            "label": [
               "Javelin Minimum Damage",
               "Javelin Maximum Damage",
               "Javelin Mana Cost"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "50/75/100/125/150",
            "150/225/300/375/450",
            "50/60/70/80/90",
            "6",
            "",
            "1.2"
         ],
         "image": {
            "w": 48,
            "full": "JavelinToss.png",
            "sprite": "spell6.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 240
         },
         "cooldown": [
            6,
            6,
            6,
            6,
            6
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
               "coeff": [0.4],
               "key": "a2"
            },
            {
               "link": "spelldamage",
               "coeff": [1.2],
               "key": "a1"
            }
         ],
         "sanitizedDescription": "In human form, Nidalee throws a spiked javelin at her target that gains damage as it flies. As a cougar, her next attack will attempt to fatally wound her target, dealing more damage the less life they have.",
         "rangeBurn": "1500",
         "costType": "Mana",
         "effect": [
            'null',
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
               50,
               60,
               70,
               80,
               90
            ],
            [
               6,
               6,
               6,
               6,
               6
            ],
            'null',
            [
               1.2,
               1.2,
               1.2,
               1.2,
               1.2
            ]
         ],
         "cooldownBurn": "6",
         "description": "In human form, Nidalee throws a spiked javelin at her target that gains damage as it flies.  As a cougar, her next attack will attempt to fatally wound her target, dealing more damage the less life they have.",
         "name": "Javelin Toss / Takedown",
         "sanitizedTooltip": "Human: Nidalee tosses her javelin, dealing {{ e1 }} (+{{ a2 }}) magic damage. If it exceeds her basic attack range, it gains damage based on distance flown, up to a potential {{ e2 }} (+{{ a1 }}) total damage. Cougar: Nidalee's next attack deals additional damage, greatly increased on low health targets.",
         "key": "JavelinToss",
         "costBurn": "50/60/70/80/90",
         "tooltip": "<span class=\"size18 colorFF9900\">Human: <\/span>Nidalee tosses her javelin, dealing {{ e1 }} <span class=\"color99FF99\">(+{{ a2 }})<\/span> magic damage. If it exceeds her basic attack range, it gains damage based on distance flown, up to a potential {{ e2 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> total damage.<br><br><span class=\"size18 colorFF9900\">Cougar: <\/span>Nidalee's next attack deals additional damage, greatly increased on low health targets."
      },
      {
         "altimages": [{
            "w": 48,
            "full": "Bushwhack0.png",
            "sprite": "spell13.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 96
         }],
         "range": [
            900,
            900,
            900,
            900,
            900
         ],
         "leveltip": {
            "effect": [
               "{{ e7 }} -> {{ e7NL }}",
               "{{ e8 }}% -> {{ e8NL }}%",
               "{{ e4 }} -> {{ e4NL }}",
               "{{ e1 }} -> {{ e1NL }}"
            ],
            "label": [
               "Trap Total Flat Damage",
               "Trap Total Percent Damage",
               "Trap Cooldown",
               "Trap Mana Cost"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "40/45/50/55/60",
            "0.025/0.03/0.035/0.04/0.045",
            "0.005",
            "13/12/11/10/9",
            "5/10/15/20/25",
            "2.5/3/3.5/4/4.5",
            "20/40/60/80/100",
            "10/12/14/16/18"
         ],
         "image": {
            "w": 48,
            "full": "Bushwhack.png",
            "sprite": "spell6.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 288
         },
         "cooldown": [
            13,
            12,
            11,
            10,
            9
         ],
         "cost": [
            40,
            45,
            50,
            55,
            60
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.02],
            "key": "a2"
         }],
         "sanitizedDescription": "In human form, Nidalee lays a trap for unwary opponents that, when sprung, damages and reveals its target. As a cougar, she jumps in a direction, dealing damage in an area where she lands.",
         "rangeBurn": "900",
         "costType": "Mana",
         "effect": [
            'null',
            [
               40,
               45,
               50,
               55,
               60
            ],
            [
               0.025,
               0.03,
               0.035,
               0.04,
               0.045
            ],
            [
               0.005,
               0.005,
               0.005,
               0.005,
               0.005
            ],
            [
               13,
               12,
               11,
               10,
               9
            ],
            [
               5,
               10,
               15,
               20,
               25
            ],
            [
               2.5,
               3,
               3.5,
               4,
               4.5
            ],
            [
               20,
               40,
               60,
               80,
               100
            ],
            [
               10,
               12,
               14,
               16,
               18
            ]
         ],
         "cooldownBurn": "13/12/11/10/9",
         "description": "In human form, Nidalee lays a trap for unwary opponents that, when sprung, damages and reveals its target. As a cougar, she jumps in a direction, dealing damage in an area where she lands.",
         "name": "Bushwhack / Pounce",
         "sanitizedTooltip": "Human: Nidalee lays a Bushwhack trap lasting up to 2 minutes. When sprung by an enemy, it is revealed and takes {{ e7 }} plus {{ e8 }}(+{{ a2 }})% of its current Health as magic damage over 4 seconds. Cougar: Nidalee lunges toward a target area, dealing damage to nearby enemies.",
         "key": "Bushwhack",
         "costBurn": "40/45/50/55/60",
         "tooltip": "<span class=\"size18 colorFF9900\">Human: <\/span>Nidalee lays a Bushwhack trap lasting up to 2 minutes. When sprung by an enemy, it is revealed and takes {{ e7 }} plus {{ e8 }}<span class=\"color99FF99\">(+{{ a2 }})<\/span>% of its current Health as magic damage over 4 seconds.<br><br><span class=\"size18 colorFF9900\">Cougar: <\/span>Nidalee lunges toward a target area, dealing damage to nearby enemies."
      },
      {
         "altimages": [{
            "w": 48,
            "full": "PrimalSurge0.png",
            "sprite": "spell13.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 144
         }],
         "range": [
            600,
            600,
            600,
            600,
            600
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e4 }}% -> {{ e4NL }}%",
               "{{ e3 }} -> {{ e3NL }}"
            ],
            "label": [
               "Primal Surge Base Heal",
               "Primal Surge Attack Speed",
               "Primal Surge Mana Cost"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "45/85/125/165/205",
            "",
            "60/75/90/105/120",
            "20/30/40/50/60",
            "0.2/0.3/0.4/0.5/0.6"
         ],
         "image": {
            "w": 48,
            "full": "PrimalSurge.png",
            "sprite": "spell6.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 336
         },
         "cooldown": [
            12,
            12,
            12,
            12,
            12
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
            "coeff": [0.5],
            "key": "a2"
         }],
         "sanitizedDescription": "In human form, Nidalee channels the spirit of the cougar to heal her allies and imbue them with Attack Speed for a short duration. As a cougar, she claws in a direction, dealing damage to enemies in front of her.",
         "rangeBurn": "600",
         "costType": "Mana",
         "effect": [
            'null',
            [
               45,
               85,
               125,
               165,
               205
            ],
            'null',
            [
               60,
               75,
               90,
               105,
               120
            ],
            [
               20,
               30,
               40,
               50,
               60
            ],
            [
               0.2,
               0.3,
               0.4,
               0.5,
               0.6
            ]
         ],
         "cooldownBurn": "12",
         "description": "In human form, Nidalee channels the spirit of the cougar to heal her allies and imbue them with Attack Speed for a short duration. As a cougar, she claws in a direction, dealing damage to enemies in front of her.",
         "name": "Primal Surge / Swipe",
         "sanitizedTooltip": "Human: Nidalee heals a target ally champion for {{ e1 }} (+{{ a2 }}) and grants them {{ e4 }}% Attack Speed for 7 seconds. Cougar: Nidalee claws at enemies in a target direction.",
         "key": "PrimalSurge",
         "costBurn": "60/75/90/105/120",
         "tooltip": "<span class=\"size18 colorFF9900\">Human: <\/span>Nidalee heals a target ally champion for {{ e1 }} <span class=\"color99FF99\">(+{{ a2 }})<\/span> and grants them {{ e4 }}% Attack Speed for 7 seconds.<br><br><span class=\"size18 colorFF9900\">Cougar: <\/span>Nidalee claws at enemies in a target direction."
      },
      {
         "altimages": [{
            "w": 48,
            "full": "AspectOfTheCougar0.png",
            "sprite": "spell13.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 192
         }],
         "range": "self",
         "leveltip": {
            "effect": [
               "{{ e3 }} -> {{ e3NL }}",
               "{{ e4 }} -> {{ e4NL }}",
               "{{ e2 }} -> {{ e2NL }}",
               "{{ e1 }} -> {{ e1NL }}"
            ],
            "label": [
               "Takedown Minimum Base Damage",
               "Takedown Maximum Base Damage",
               "Pounce Damage",
               "Swipe Damage"
            ]
         },
         "resource": "No Cost ",
         "maxrank": 4,
         "effectBurn": [
            "",
            "70/130/190/250",
            "50/100/150/200",
            "4/20/50/90",
            "10/50/125/225",
            "750",
            "6",
            "1.5",
            "10",
            "5/10/15/20"
         ],
         "image": {
            "w": 48,
            "full": "AspectOfTheCougar.png",
            "sprite": "spell6.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 384
         },
         "cooldown": [
            3,
            3,
            3,
            3
         ],
         "cost": [
            0,
            0,
            0,
            0
         ],
         "sanitizedDescription": "Nidalee transforms into a cougar, gaining new abilities.",
         "rangeBurn": "self",
         "costType": "NoCost",
         "effect": [
            'null',
            [
               70,
               130,
               190,
               250
            ],
            [
               50,
               100,
               150,
               200
            ],
            [
               4,
               20,
               50,
               90
            ],
            [
               10,
               50,
               125,
               225
            ],
            [
               750,
               750,
               750,
               750
            ],
            [
               6,
               6,
               6,
               6
            ],
            [
               1.5,
               1.5,
               1.5,
               1.5
            ],
            [
               10,
               10,
               10,
               10
            ],
            [
               5,
               10,
               15,
               20
            ]
         ],
         "cooldownBurn": "3",
         "description": "Nidalee transforms into a cougar, gaining new abilities.",
         "name": "Aspect Of The Cougar",
         "sanitizedTooltip": "Human: Nidalee transforms into a vicious cougar with the basic abilities Takedown, Pounce, and Swipe. While in human form, triggering a Hunt resets the cooldown of Aspect of the Cougar. Cougar: Nidalee transforms back into human form.",
         "key": "AspectOfTheCougar",
         "costBurn": "0",
         "tooltip": "<span class=\"size18 colorFF9900\">Human: <\/span>Nidalee transforms into a vicious cougar with the basic abilities Takedown, Pounce, and Swipe.<br><br>While in human form, triggering a <span class=\"colorFFF673\">Hunt<\/span> resets the cooldown of Aspect of the Cougar.<br><br><span class=\"size18 colorFF9900\">Cougar: <\/span>Nidalee transforms back into human form."
      },
      {
         "range": "self",
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e2 }} -> {{ e2NL }}",
               "{{ e3 }} -> {{ e3NL }}"
            ],
            "label": [
               "Javelin Minimum Damage",
               "Javelin Maximum Damage",
               "Javelin Mana Cost"
            ]
         },
         "resource": "No Cost",
         "maxrank": 5,
         "effectBurn": [
            "",
            "50/75/100/125/150",
            "150/225/300/375/450",
            "50/60/70/80/90",
            "6",
            "",
            "0.9"
         ],
         "image": {
            "w": 48,
            "full": "Takedown.png",
            "sprite": "spell14.png",
            "group": "spell",
            "h": 48,
            "y": 48,
            "x": 384
         },
         "cooldown": [
            5,
            5,
            5,
            5,
            5
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
               "link": "spelldamage",
               "coeff": [0.36],
               "key": "a2"
            },
            {
               "link": "spelldamage",
               "coeff": [0.9],
               "key": "a1"
            }
         ],
         "sanitizedDescription": "Nidalee executes a powerful attack that deals increased damage to low Health and Hunted targets.",
         "rangeBurn": "self",
         "costType": "NoCost",
         "effect": [
            'null',
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
               50,
               60,
               70,
               80,
               90
            ],
            [
               6,
               6,
               6,
               6,
               6
            ],
            'null',
            [
               0.9,
               0.9,
               0.9,
               0.9,
               0.9
            ]
         ],
         "cooldownBurn": "5",
         "description": "Nidalee executes a powerful attack that deals increased damage to low Health and Hunted targets.",
         "name": "Takedown",
         "sanitizedTooltip": "Cougar: Nidalee's next attack deals {{ f2 }} (+{{ f3 }}) (+{{ a2 }}) magic damage. Takedown deals 2.5% additional damage for each 1% Health the target is missing, up to {{ f4 }} (+{{ f1 }}) (+{{ a1 }}) (250% total damage). Hunted targets take 33% additional damage from Takedown. Human: Nidalee tosses her javelin, dealing increased damage the farther the enemy hit is from Nidalee.",
         "key": "Takedown",
         "costBurn": "0",
         "tooltip": "<span class=\"size18 colorFF9900\">Cougar:<\/span> Nidalee's next attack deals {{ f2 }} <span class=\"colorFF8C00\">(+{{ f3 }})<\/span> <span class=\"color99FF99\">(+{{ a2 }})<\/span> magic damage. Takedown deals 2.5% additional damage for each 1% Health the target is missing, up to {{ f4 }} <span class=\"colorFF8C00\">(+{{ f1 }})<\/span> <span class=\"color99FF99\">(+{{ a1 }})<\/span> (250% total damage).<br><br><span class=\"colorFFF673\">Hunted<\/span> targets take 33% additional damage from Takedown.<br><br><span class=\"size18 colorFF9900\">Human: <\/span>Nidalee tosses her javelin, dealing increased damage the farther the enemy hit is from Nidalee."
      },
      {
         "range": [
            350,
            350,
            350,
            350,
            350
         ],
         "leveltip": {
            "effect": [
               "{{ e7 }} -> {{ e7NL }}",
               "{{ e8 }}% -> {{ e8NL }}%",
               "{{ e4 }} -> {{ e4NL }}",
               "{{ e1 }} -> {{ e1NL }}"
            ],
            "label": [
               "Trap Total Flat Damage",
               "Trap Total Percent Damage",
               "Trap Cooldown",
               "Trap Mana Cost"
            ]
         },
         "resource": "No Cost ",
         "maxrank": 5,
         "effectBurn": [
            "",
            "40/45/50/55/60",
            "0.025/0.03/0.035/0.04/0.045",
            "0.005",
            "13/12/11/10/9",
            "5/10/15/20/25",
            "2.5/3/3.5/4/4.5",
            "20/40/60/80/100",
            "10/12/14/16/18"
         ],
         "image": {
            "w": 48,
            "full": "Pounce.png",
            "sprite": "spell14.png",
            "group": "spell",
            "h": 48,
            "y": 48,
            "x": 432
         },
         "cooldown": [
            5,
            5,
            5,
            5,
            5
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
            "coeff": [0.3],
            "key": "a1"
         }],
         "sanitizedDescription": "Nidalee jumps in a direction, dealing damage in an area where she lands.",
         "rangeBurn": "350",
         "costType": "NoCost",
         "effect": [
            'null',
            [
               40,
               45,
               50,
               55,
               60
            ],
            [
               0.025,
               0.03,
               0.035,
               0.04,
               0.045
            ],
            [
               0.005,
               0.005,
               0.005,
               0.005,
               0.005
            ],
            [
               13,
               12,
               11,
               10,
               9
            ],
            [
               5,
               10,
               15,
               20,
               25
            ],
            [
               2.5,
               3,
               3.5,
               4,
               4.5
            ],
            [
               20,
               40,
               60,
               80,
               100
            ],
            [
               10,
               12,
               14,
               16,
               18
            ]
         ],
         "cooldownBurn": "5",
         "description": "Nidalee jumps in a direction, dealing damage in an area where she lands.",
         "name": "Pounce",
         "sanitizedTooltip": "Cougar: Nidalee lunges forward a short distance dealing {{ f1 }} (+{{ a1 }}) magic damage to enemies in the area. Killing a unit in Cougar form reduces Pounce's cooldown to {{ f2 }} second(s). Hunted targets can be Pounced to at up to double the normal range, and the first Pounce to a Hunted target causes it to only incur a {{ f2 }} second cooldown. Human: Nidalee lays a trap that damages and reveals an enemy.",
         "key": "Pounce",
         "costBurn": "0",
         "tooltip": "<span class=\"size18 colorFF9900\">Cougar: <\/span>Nidalee lunges forward a short distance dealing {{ f1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> magic damage to enemies in the area. Killing a unit in Cougar form reduces Pounce's cooldown to <span class=\"colorFFFFFF\">{{ f2 }}<\/span> second(s).<br><br><span class=\"colorFFF673\">Hunted<\/span> targets can be Pounced to at up to double the normal range, and the first Pounce to a <span class=\"colorFFF673\">Hunted<\/span> target causes it to only incur a <span class=\"colorFFFFFF\">{{ f2 }}<\/span> second cooldown.<br><br><span class=\"size18 colorFF9900\">Human: <\/span>Nidalee lays a trap that damages and reveals an enemy."
      },
      {
         "range": [
            350,
            350,
            350,
            350,
            350
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e4 }}% -> {{ e4NL }}%",
               "{{ e3 }} -> {{ e3NL }}"
            ],
            "label": [
               "Primal Surge Base Heal",
               "Primal Surge Attack Speed",
               "Primal Surge Mana Cost"
            ]
         },
         "resource": "No Cost",
         "maxrank": 5,
         "effectBurn": [
            "",
            "55/95/135/175/215",
            "",
            "60/75/90/105/120",
            "20/30/40/50/60",
            "0.2/0.3/0.4/0.5/0.6"
         ],
         "image": {
            "w": 48,
            "full": "Swipe.png",
            "sprite": "spell14.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 0
         },
         "cooldown": [
            5,
            5,
            5,
            5,
            5
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
            "coeff": [0.45],
            "key": "a2"
         }],
         "sanitizedDescription": "Nidalee claws in a direction, dealing damage to enemies in front of her.",
         "rangeBurn": "350",
         "costType": "NoCost",
         "effect": [
            'null',
            [
               55,
               95,
               135,
               175,
               215
            ],
            'null',
            [
               60,
               75,
               90,
               105,
               120
            ],
            [
               20,
               30,
               40,
               50,
               60
            ],
            [
               0.2,
               0.3,
               0.4,
               0.5,
               0.6
            ]
         ],
         "cooldownBurn": "5",
         "description": "Nidalee claws in a direction, dealing damage to enemies in front of her.",
         "name": "Swipe",
         "sanitizedTooltip": "Cougar: Nidalee claws at enemies in front of her, dealing {{ f1 }} (+{{ a2 }}) magic damage. Human: Nidalee heals an ally and grants them an Attack Speed bonus.",
         "key": "Swipe",
         "costBurn": "0",
         "tooltip": "<span class=\"size18 colorFF9900\">Cougar: <\/span>Nidalee claws at enemies in front of her, dealing {{ f1 }} <span class=\"color99FF99\">(+{{ a2 }})<\/span> magic damage.<br><br><span class=\"size18 colorFF9900\">Human: <\/span>Nidalee heals an ally and grants them an Attack Speed bonus."
      }
   ],
   "key": "Nidalee"
}