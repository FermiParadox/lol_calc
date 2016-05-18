from flask import Flask, request, send_file
import copy
import ast
import pprint
import os

import user_instance_settings
import palette
import champion_ids
import functional_testing.default_config as default_config
from items_folder.items_data import ITEMS_IDS_TO_NAMES_MAP


app = Flask(__name__)


CHAMPION_IDS = champion_ids.CHAMPION_IDS.values()


# TODO remove below; code exists in abilities.py
CHAMPIONS_FILES_NAMES = os.listdir(palette.PROJECT_PATH + '/champions')
CREATED_CHAMPIONS_IDS = []
for champ_name in CHAMPION_IDS:
    if champ_name.lower() + '.py' in CHAMPIONS_FILES_NAMES:
        # TODO fix below; it doesn't contain IDs.
        CREATED_CHAMPIONS_IDS.append(champ_name)

CREATED_CHAMPIONS_NAMES_AND_ITEMS_IDS_TO_NAMES_MAP = {
    'created_champions_ids': CREATED_CHAMPIONS_IDS,
    'items_ids_to_names_map': ITEMS_IDS_TO_NAMES_MAP,
}


ALLOWED_PRESET_KEYS = ['selected_champions_dct',
                       'ability_lvls_dct',
                       'champion_lvls_dct',
                       'max_combat_time',
                       'chosen_items_dct',
                       'selected_summoner_spells']


def filled_and_refined_combat_preset(given_dct):
    """
    Completes missing data in order to create a valid combat preset dict.

    Fills whatever is missing in order to create a valid preset dict. Removes empty key-values.

    :param given_dct:
    :return: (dict)
    """

    dct = copy.deepcopy(given_dct)

    for k, v in default_config.EMPTY_DATA.items():
        if k not in dct:
            dct.update({k: v})

    return dct


@app.route('/', methods=['GET'])
def index():
    r = request.args.to_dict()

    if 'input_as_str' in r.keys():
        input_dct = ast.literal_eval(r['input_as_str'])
        input_dct = filled_and_refined_combat_preset(given_dct=input_dct)
        try:
            im_name = user_instance_settings.UserSession().create_instance_and_return_image_name(input_dct=input_dct)
            return im_name
        except ImportError as err:

            return '{}'.format(err)

    elif 'created_champions_names_and_items_ids_to_names_map' in r.keys():
        return str(CREATED_CHAMPIONS_NAMES_AND_ITEMS_IDS_TO_NAMES_MAP)

    else:
        return ''

if __name__ == '__main__':
    app.run(debug=True, port=64000)
