import api_champion_database as all_data

def new_dct(old_dct):

    dct = {}

    for key_name in old_dct:

        dct.update({key_name.lower(): old_dct[key_name]})

    return dct


def change_file():

    with open('api_champion_database.py', 'w') as edited_module:
        s = new_dct(all_data.ALL_CHAMPIONS_ATTR)
        s = 'ALL_CHAMPIONS_ATTR = '+str(s)
        edited_module.write(s)

if __name__ == '__main__':
    change_file()
    print(all_data.ALL_CHAMPIONS_ATTR.keys())