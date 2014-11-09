"""
ABBREVIATIONS:
- dmg: damage
- AA: auto attack
- resist: resistance
- dot: damage over time
- percent: percentage
- lvl: level
- inn: innate
- cooldown reduction: cdr


GENERAL:
- Dmg types are: true, physical, magic, AA
- Percentages must be converted to floats before given to functions (e.g. 5% -> 0.05)
- Caution when dividing (e.g. 1/2=0)
- Actions: item active spells, AA, Q, W, E, R, ignite, exhaust
- dmg: permanent change (unlike buffs) to hp, mana, energy, etc.
- ?? Effects: dmg, dots
        (exceptions): Varus, Volibear. effects: dmg, buff_end, dots
-Buff's duration: When not set, it's considered unlimited.

PERIODIC EVENTS:
-An accompanying buff is required that will finish slightly after the last tick occurs
(to ensure the last tick is created).
-name of buff must be: 'name' + '_dot_buff'


ASSUMPTIONS:
- AA have a fixed cast time (and therefor an 'AA_COOLDOWN')
    In reality their cd is based on att_speed with an unknown formula.


TODO:
- Care with functions requiring ability_lvl. It should be converted to ability_lvl-1.
- Trinity,LB must trigger at ability start to ensure it's applied to Ez and Gp Q.
        (exceptions): Fizz Q
- find actual period of regeneration (assumed 0.5)
-check if cost exceeds resource. if it does modify action_lst.

(minor)
- perhaps add travel time.


PERFORMANCE:
- check if modify_buffs_on_death should remove current buffs or not.
- change mana_restore (and similar) to a set value depending on period chosen instead of calculating the value each time
(e.g. mana_restore=total_stats[...]['mana_per_period])

(dict structure)
- champion_abilities_dct['q']['enemy']['actives']['buffs']
- on_hit_buffs_dct[target]      # contains buffs triggered by AA
- item_actives[name]
- available_buffs[buff_name]['max_stacks']
- item_actives[action_name][target_type]['actives']['buffs']

"""