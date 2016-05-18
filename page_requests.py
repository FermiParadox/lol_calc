import copy

import champion_ids
import functional_testing.default_config as default_config
import user_instance_settings
import abilities
import items_folder.items_data as items_data_module


# Created items and champions
CREATED_CHAMPIONS_IDS = abilities.CREATED_CHAMPIONS_IDS
CREATED_ITEMS_IDS_TO_NAMES_MAP = items_data_module.ITEMS_IDS_TO_NAMES_MAP


def fixed_dict(given_dct):
    """
    Converts given dict to expected format and converts contents from ids to names.
    E.g. 'player_champion' is inserted in the expected 'selected_champions' dict.

    :param given_dct: (dict)
    :return: (dict)
    """

    dct = copy.deepcopy(default_config.EMPTY_DATA)

    selected_player_champ = champion_ids.CHAMPION_IDS[given_dct['player_champion']]
    dct['selected_champions_dct'].update({'player': selected_player_champ})

    dct['champion_lvls_dct'].update({'player': given_dct['champion_lvls_dct']['player']})

    selected_items = [items_data_module.ITEMS_IDS_TO_NAMES_MAP[i] for i in given_dct['player_items']]
    dct['chosen_items_dct'].update(player=selected_items)

    dct['ability_lvls_dct'] = given_dct['ability_lvls_dct']


def results_image_name(given_dct):
    return user_instance_settings.UserSession().create_instance_and_return_image_name(input_dct=given_dct)



