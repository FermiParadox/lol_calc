from flask import Flask, abort, request, jsonify, send_file

import abilities
import user_instance_settings
import functional_testing.default_config as default_config

app = Flask(__name__)


def combat_preset_data(given_dct):
    """
    Completes missing data in order to create a valid combat preset dict.

    :param given_dct:
    :return: (dict)
    """







@app.route('/', methods=['GET'])
def index():
    r = request.args.to_dict()

    if 'player_champion' in r:
        im_name = user_instance_settings.UserSession().create_instance_and_return_image_name(default_config.ALL_DATA)
        return send_file(im_name)

    else:
        return ''

if __name__ == '__main__':
    app.run(debug=True, port=64000)
