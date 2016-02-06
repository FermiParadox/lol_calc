from flask import Flask, request, send_file
import copy
import ast
import pprint

import user_instance_settings
import functional_testing.default_config as default_config

app = Flask(__name__)


ALLOWED_PRESET_KEYS = ['selected_champions_dct',
                       'ability_lvls_dct',
                       'champion_lvls_dct',
                       'max_combat_time',
                       'chosen_items_dct',
                       'selected_summoner_spells']


def filled_and_refined_combat_preset(given_dct):
    """
    Completes missing data in order to create a valid combat preset dict.

    Fills whatever is missing in order to create a valid preset dict.Removes empty key-values.

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

    if 'input_as_str' in r:
        input_dct = ast.literal_eval(r['input_as_str'])
        input_dct = filled_and_refined_combat_preset(given_dct=input_dct)
        pprint.pprint(input_dct)
        try:
            im_name = user_instance_settings.UserSession().create_instance_and_return_image_name(input_dct=input_dct)
            return im_name
        except ImportError as err:

            return '{}'.format(err)

    else:
        return ''

if __name__ == '__main__':
    app.run(debug=True, port=64000)
