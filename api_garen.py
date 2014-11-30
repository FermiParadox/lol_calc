ABILITIES = {
   "id": 86,
   "title": "The Might of Demacia",
   "name": "Garen",
   "spells": [
      {
      "sanitizedDescription": "If Garen has not been struck by damage or enemy abilities for the last 10 seconds, Garen regenerates 0.4% of his maximum Health each second. Minion damage does not stop Perseverance.",
      "description": "If Garen has not been struck by damage or enemy abilities for the last 10 seconds, Garen regenerates 0.4% of his maximum Health each second. Minion damage does not stop Perseverance. ",
      "name": "Perseverance",
      "image": {
         "w": 48,
         "full": "Garen_Passive.png",
         "sprite": "passive0.png",
         "group": "passive",
         "h": 48,
         "y": 96,
         "x": 288
      }
      },
      {
         "range": "self",
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e5 }} -> {{ e5NL }}",
               "{{ e3 }} -> {{ e3NL }}"
            ],
            "label": [
               "Bonus Damage",
               "Movement Speed Duration",
               "Silence Duration"
            ]
         },
         "resource": "No Cost",
         "maxrank": 5,
         "effectBurn": [
            "",
            "30/55/80/105/130",
            "35",
            "1.5/1.75/2/2.25/2.5",
            "1.5/1.75/2/2.25/2.5",
            "1.5/2.25/3/3.75/4.5",
            "4.5"
         ],
         "image": {
            "w": 48,
            "full": "GarenQ.png",
            "sprite": "spell3.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 48
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
         "vars": [{
            "link": "attackdamage",
            "coeff": [1.4],
            "key": "a1"
         }],
         "sanitizedDescription": "Garen gains a burst of Movement Speed, breaking free of all slows affecting him and his next attack strikes a vital area of his foe, dealing bonus damage and silencing them.",
         "rangeBurn": "self",
         "costType": "NoCost",
         "effect": [
            'null',
            [
               30,
               55,
               80,
               105,
               130
            ],
            [
               35,
               35,
               35,
               35,
               35
            ],
            [
               1.5,
               1.75,
               2,
               2.25,
               2.5
            ],
            [
               1.5,
               1.75,
               2,
               2.25,
               2.5
            ],
            [
               1.5,
               2.25,
               3,
               3.75,
               4.5
            ],
            [
               4.5,
               4.5,
               4.5,
               4.5,
               4.5
            ]
         ],
         "cooldownBurn": "8",
         "description": "Garen gains a burst of Movement Speed, breaking free of all slows affecting him and his next attack strikes a vital area of his foe, dealing bonus damage and silencing them.",
         "name": "Decisive Strike",
         "sanitizedTooltip": "Garen breaks free from all slows affecting him and gains {{ e2 }}% Movement Speed for {{ e5 }} seconds. His next basic attack within {{ e6 }} seconds deals {{ e1 }} (+{{ a1 }}) physical damage and silences his target for {{ e3 }} seconds.",
         "key": "GarenQ",
         "costBurn": "0",
         "tooltip": "Garen breaks free from all slows affecting him and gains {{ e2 }}% Movement Speed for {{ e5 }} seconds.<br><br>His next basic attack within {{ e6 }} seconds deals {{ e1 }} <span class=\"colorFF8C00\">(+{{ a1 }})<\/span> physical damage and silences his target for {{ e3 }} seconds."
      },
      {
         "range": "self",
         "leveltip": {
            "effect": [
               "{{ e4 }} -> {{ e4NL }}",
               "{{ cooldown }} -> {{ cooldownnNL }}"
            ],
            "label": [
               "Active Duration",
               "Cooldown"
            ]
         },
         "resource": "No Cost",
         "maxrank": 5,
         "effectBurn": [
            "",
            "20",
            "30",
            "75",
            "2/3/4/5/6",
            "20"
         ],
         "image": {
            "w": 48,
            "full": "GarenW.png",
            "sprite": "spell3.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 96
         },
         "cooldown": [
            24,
            23,
            22,
            21,
            20
         ],
         "cost": [
            0,
            0,
            0,
            0,
            0
         ],
         "sanitizedDescription": "Garen passively increases his Armor and Magic Resist. He may also activate this ability to grant himself a shield that reduces incoming damage and crowd control durations for a short time.",
         "rangeBurn": "self",
         "costType": "NoCost",
         "effect": [
            'null',
            [
               20,
               20,
               20,
               20,
               20
            ],
            [
               30,
               30,
               30,
               30,
               30
            ],
            [
               75,
               75,
               75,
               75,
               75
            ],
            [
               2,
               3,
               4,
               5,
               6
            ],
            [
               20,
               20,
               20,
               20,
               20
            ]
         ],
         "cooldownBurn": "24/23/22/21/20",
         "description": "Garen passively increases his Armor and Magic Resist. He may also activate this ability to grant himself a shield that reduces incoming damage and crowd control durations for a short time.",
         "name": "Courage",
         "sanitizedTooltip": "Passive: Garen gains an additional 20% value from bonus Armor and Magic Resist. Active: Garen gains a defensive shield for {{ e4 }} seconds, reducing incoming damage by {{ e2 }}% and granting 30% crowd control duration reduction.",
         "key": "GarenW",
         "costBurn": "0",
         "tooltip": "<span class=\"colorFF9900\">Passive:<\/span> Garen gains an additional 20% value from bonus Armor and Magic Resist.<br><br><span class=\"colorFF9900\">Active: <\/span>Garen gains a defensive shield for {{ e4 }} seconds, reducing incoming damage by {{ e2 }}% and granting 30% crowd control duration reduction."
      },
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
               "{{ e3 }}% -> {{ e3NL }}%",
               "{{ cooldown }} -> {{ cooldownnNL }}"
            ],
            "label": [
               "Base Damage per Second",
               "Total Attack Damage Ratio",
               "Cooldown"
            ]
         },
         "resource": "No Cost",
         "maxrank": 5,
         "effectBurn": [
            "",
            "20/45/70/95/120",
            "3",
            "70/80/90/100/110",
            "75"
         ],
         "image": {
            "w": 48,
            "full": "GarenE.png",
            "sprite": "spell3.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 144
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
         "sanitizedDescription": "Garen performs a dance of death with his sword, dealing damage around him for the duration.",
         "rangeBurn": "325",
         "costType": "NoCost",
         "effect": [
            'null',
            [
               20,
               45,
               70,
               95,
               120
            ],
            [
               3,
               3,
               3,
               3,
               3
            ],
            [
               70,
               80,
               90,
               100,
               110
            ],
            [
               75,
               75,
               75,
               75,
               75
            ]
         ],
         "cooldownBurn": "13/12/11/10/9",
         "description": "Garen performs a dance of death with his sword, dealing damage around him for the duration.",
         "name": "Judgment",
         "sanitizedTooltip": "Garen rapidly spins his sword around his body for {{ e2 }} seconds, dealing {{ e1 }} plus {{ e3 }}% of his attack (+{{ f1 }}) as physical damage to nearby enemies every second. Garen can move through units while spinning but moves 20% slower when travelling through minions and monsters. Judgment can critically strike dealing bonus damage. Judgment deals 25% less damage to minions.",
         "key": "GarenE",
         "costBurn": "0",
         "tooltip": "Garen rapidly spins his sword around his body for {{ e2 }} seconds, dealing {{ e1 }} plus {{ e3 }}% of his attack <span class=\"colorFF8C00\">(+{{ f1 }})<\/span> as physical damage to nearby enemies every second. Garen can move through units while spinning but moves 20% slower when travelling through minions and monsters.<br><br><span class=\"color99FF99\">Judgment can critically strike dealing bonus damage.<br>Judgment deals 25% less damage to minions.<\/span>"
      },
      {
         "range": [
            400,
            400,
            400
         ],
         "leveltip": {
            "effect": [
               "{{ e1 }} -> {{ e1NL }}",
               "{{ e2 }} -> {{ e2NL }}",
               "{{ cooldown }} -> {{ cooldownnNL }}"
            ],
            "label": [
               "Damage",
               "Missing Health Damage",
               "Cooldown"
            ]
         },
         "resource": "No Cost",
         "maxrank": 3,
         "effectBurn": [
            "",
            "175/350/525",
            "3.5/3/2.5"
         ],
         "image": {
            "w": 48,
            "full": "GarenR.png",
            "sprite": "spell3.png",
            "group": "spell",
            "h": 48,
            "y": 0,
            "x": 192
         },
         "cooldown": [
            160,
            120,
            80
         ],
         "cost": [
            0,
            0,
            0
         ],
         "sanitizedDescription": "Garen calls upon the might of Demacia to deal a finishing blow to an enemy champion that deals damage based upon how much Health his target has missing.",
         "rangeBurn": "400",
         "costType": "NoCost",
         "effect": [
            'null',
            [
               175,
               350,
               525
            ],
            [
               3.5,
               3,
               2.5
            ]
         ],
         "cooldownBurn": "160/120/80",
         "description": "Garen calls upon the might of Demacia to deal a finishing blow to an enemy champion that deals damage based upon how much Health his target has missing.",
         "name": "Demacian Justice",
         "sanitizedTooltip": "Garen calls upon the might of Demacia to attempt to execute an enemy champion, dealing {{ e1 }} magic damage plus 1 damage for every {{ e2 }} Health the target is missing.",
         "key": "GarenR",
         "costBurn": "0",
         "tooltip": "Garen calls upon the might of Demacia to attempt to execute an enemy champion, dealing {{ e1 }} magic damage plus 1 damage for every {{ e2 }} Health the target is missing."
      }
   ],
   "key": "Garen"
}