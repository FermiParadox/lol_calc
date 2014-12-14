ABILITIES = {
   "id": 32,
   "title": "the Sad Mummy",
   "name": "Amumu",
   "spells": [
      {
         "range": [
            1100,
            1100,
            1100,
            1100,
            1100
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               " {{ cooldown }} -> {{ cooldownnNL }}",
               "{{ cost }} -> {{ costnNL }}"
            ],
            "label": [
               "Damage",
               "Cooldown",
               "Mana"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "80/130/180/230/280"
         ],
         "image": {
            "w": 48,
            "full": "BandageToss.png",
            "sprite": "spell0.png",
            "group": "spell",
            "h": 48,
            "y": 96,
            "x": 432
         },
         "cooldown": [
            16,
            14,
            12,
            10,
            8
         ],
         "cost": [
            80,
            90,
            100,
            110,
            120
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.7],
            "key": "a1"
         }],
         "sanitizedDescription": "Amumu tosses a sticky bandage at a target, stunning and damaging the target while he pulls himself to them.",
         "rangeBurn": "1100",
         "costType": "Mana",
         "effect": [
            "null",
            [
               80,
               130,
               180,
               230,
               280
            ]
         ],
         "cooldownBurn": "16/14/12/10/8",
         "description": "Amumu tosses a sticky bandage at a target, stunning and damaging the target while he pulls himself to them.",
         "name": "Bandage Toss",
         "sanitizedTooltip": "Throws a bandage to target location. If it hits an enemy unit, Amumu will pull himself to the enemy, stun them for 1 second, and deal {{ e1 }} (+{{ a1 }}) magic damage.",
         "key": "BandageToss",
         "costBurn": "80/90/100/110/120",
         "tooltip": "Throws a bandage to target location. If it hits an enemy unit, Amumu will pull himself to the enemy, stun them for 1 second, and deal {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> magic damage. "
      },
      {
         "range": [
            300,
            300,
            300,
            300,
            300
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }}% -> {{ e1NL }}%",
               "{{ e2 }} -> {{ e2NL }}"
            ],
            "label": [
               "Percent Health Damaged",
               "Base Damage"
            ]
         },
         "resource": "{{ cost }} Mana per Second",
         "maxrank": 5,
         "effectBurn": [
            "",
            "1/1.5/2/2.5/3",
            "8/12/16/20/24"
         ],
         "image": {
            "w": 48,
            "full": "AuraofDespair.png",
            "sprite": "spell0.png",
            "group": "spell",
            "h": 48,
            "y": 144,
            "x": 0
         },
         "cooldown": [
            1,
            1,
            1,
            1,
            1
         ],
         "cost": [
            8,
            8,
            8,
            8,
            8
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.01],
            "key": "a1"
         }],
         "sanitizedDescription": "Overcome by anguish, nearby enemies lose a percentage of their maximum Health each second.",
         "rangeBurn": "300",
         "costType": "ManaperSecond",
         "effect": [
            "null",
            [
               1,
               1.5,
               2,
               2.5,
               3
            ],
            [
               8,
               12,
               16,
               20,
               24
            ]
         ],
         "cooldownBurn": "1",
         "description": "Overcome by anguish, nearby enemies lose a percentage of their maximum Health each second.",
         "name": "Despair",
         "sanitizedTooltip": "Toggle: Nearby enemies take {{ e2 }} magic damage plus {{ e1 }} (+{{ a1 }})% of their maximum Health each second.",
         "key": "AuraofDespair",
         "costBurn": "8",
         "tooltip": "<span class=\"colorFF9900\">Toggle: <\/span>Nearby enemies take {{ e2 }} magic damage plus {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span>% of their maximum Health each second."
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
               " {{ cooldown }} -> {{ cooldownnNL }}",
               "{{ e2 }} -> {{ e2NL }}"
            ],
            "label": [
               "Damage Reduced",
               "Cooldown",
               "Damage"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 5,
         "effectBurn": [
            "",
            "2/4/6/8/10",
            "75/100/125/150/175"
         ],
         "image": {
            "w": 48,
            "full": "Tantrum.png",
            "sprite": "spell0.png",
            "group": "spell",
            "h": 48,
            "y": 144,
            "x": 48
         },
         "cooldown": [
            10,
            9,
            8,
            7,
            6
         ],
         "cost": [
            35,
            35,
            35,
            35,
            35
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.5],
            "key": "a1"
         }],
         "sanitizedDescription": "Permanently reduces the physical damage Amumu would take. Amumu can unleash his rage, dealing damage to surrounding enemies. Each time Amumu is hit, the cooldown on Tantrum is reduced by 0.5 seconds.",
         "rangeBurn": "350",
         "costType": "Mana",
         "effect": [
            "null",
            [
               2,
               4,
               6,
               8,
               10
            ],
            [
               75,
               100,
               125,
               150,
               175
            ]
         ],
         "cooldownBurn": "10/9/8/7/6",
         "description": "Permanently reduces the physical damage Amumu would take. Amumu can unleash his rage, dealing damage to surrounding enemies. Each time Amumu is hit, the cooldown on Tantrum is reduced by 0.5 seconds.",
         "name": "Tantrum",
         "sanitizedTooltip": "Passive: Amumu takes {{ e1 }} reduced damage from physical attacks. Active: Amumu deals {{ e2 }} (+{{ a1 }}) magic damage to surrounding units. Each time Amumu is hit, the cooldown on Tantrum is reduced by 0.5 seconds.",
         "key": "Tantrum",
         "costBurn": "35",
         "tooltip": "<span class=\"colorFF9900\">Passive: <\/span>Amumu takes {{ e1 }} reduced damage from physical attacks.<br><br><span class=\"colorFF9900\">Active: <\/span>Amumu deals {{ e2 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> magic damage to surrounding units.  Each time Amumu is hit, the cooldown on Tantrum is reduced by 0.5 seconds."
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
               "{{ cost }} -> {{ costnNL }}",
               "{{ cooldown }} -> {{ cooldownnNL }}"
            ],
            "label": [
               "Damage Dealt",
               "Mana Cost",
               "Cooldown"
            ]
         },
         "resource": "{{ cost }} Mana",
         "maxrank": 3,
         "effectBurn": [
            "",
            "150/250/350"
         ],
         "image": {
            "w": 48,
            "full": "CurseoftheSadMummy.png",
            "sprite": "spell0.png",
            "group": "spell",
            "h": 48,
            "y": 144,
            "x": 96
         },
         "cooldown": [
            150,
            130,
            110
         ],
         "cost": [
            100,
            150,
            200
         ],
         "vars": [{
            "link": "spelldamage",
            "coeff": [0.8],
            "key": "a1"
         }],
         "sanitizedDescription": "Amumu entangles surrounding enemy units in bandages, damaging them and rendering them unable to attack or move.",
         "rangeBurn": "550",
         "costType": "Mana",
         "effect": [
            "null",
            [
               150,
               250,
               350
            ]
         ],
         "cooldownBurn": "150/130/110",
         "description": "Amumu entangles surrounding enemy units in bandages, damaging them and rendering them unable to attack or move.",
         "name": "Curse of the Sad Mummy",
         "sanitizedTooltip": "Amumu entangles surrounding enemy units, dealing {{ e1 }} (+{{ a1 }}) magic damage and preventing attacks and movement for 2 seconds.",
         "key": "CurseoftheSadMummy",
         "costBurn": "100/150/200",
         "tooltip": "Amumu entangles surrounding enemy units, dealing {{ e1 }} <span class=\"color99FF99\">(+{{ a1 }})<\/span> magic damage and preventing attacks and movement for 2 seconds."
      }
   ],
   "key": "Amumu"
}