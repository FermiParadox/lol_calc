import champions.jax as jax_mod
import champions.vayne as vayne_mod
import items_folder.items_data as items_mod


import pprint as pp
import copy


def merged_dicts(given_effects):

    new_d = {}

    for ability_name in given_effects:



        if given_effects[ability_name]:

            new_d.update({ability_name:
                              {'passives':{}, 'actives': {}}})

            enemy_d = given_effects[ability_name]['enemy']

            player_d = given_effects[ability_name]['player']
        else:
            new_d.update({ability_name: {}})
            continue

        for application_type in ('passives', 'actives'):
            if application_type in enemy_d:
                for effect_cat_name in enemy_d[application_type]:

                    player_cat_contents = player_d[application_type][effect_cat_name]
                    enemy_cat_contents = enemy_d[application_type][effect_cat_name]

                    try:
                        new_contents = player_cat_contents + enemy_cat_contents
                    except TypeError:
                        new_contents = copy.deepcopy(enemy_cat_contents)
                        new_contents.update(player_cat_contents)

                    new_d[ability_name][application_type].update({effect_cat_name: new_contents})

    return new_d


pp.pprint(merged_dicts(items_mod.ITEMS_EFFECTS))