import os
import json
import requests

from functools import partial
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.button import Button as BaseButton
from kivy.uix.dropdown import DropDown
from kivy.core.window import Window
from kivy.modules import inspector
from kivy.properties import ListProperty, StringProperty, DictProperty, NumericProperty
from kivy.clock import Clock

import champion_ids
from items_folder.items_data import ITEMS_IDS_TO_NAMES_MAP


Window.size = (1050, 800)


# ----------------------------------------------------------------------------------------------------------------------
HOST_URL = 'http://localhost:64000'


# ----------------------------------------------------------------------------------------------------------------------
DRAGONTAIL_VERSION = '6.1.1'
PATH_BASE = '/home/black/Downloads/dragontail-{0}/{0}/'.format(DRAGONTAIL_VERSION)
IMAGE_PATH_BASE = PATH_BASE + 'img/'
CHAMPION_IMAGE_PATH_BASE = IMAGE_PATH_BASE + 'champion/'
SPELL_IMAGE_PATH_BASE = IMAGE_PATH_BASE + 'spell/'
ITEM_IMAGE_PATH_BASE = IMAGE_PATH_BASE + 'item/'

CHAMPION_DATA_PATH_BASE = PATH_BASE + 'data/en_US/champion/'


# ----------------------------------------------------------------------------------------------------------------------
PLAYER_AND_ENEMIES_LST = ['player', ]
PLAYER_AND_ENEMIES_LST += ['enemy_{}'.format(i) for i in range(1, 5)]
SPELL_SHORTCUTS = ['q', 'w', 'e', 'r']


# ----------------------------------------------------------------------------------------------------------------------
class Button(BaseButton):
    """
    Removes border from all buttons.
    """

    obj_name = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(border=(0, 0, 0, 0), **kwargs)


# ----------------------------------------------------------------------------------------------------------------------
def spell_icon_path(champion_name, ability_name):
    """
    Returns path of the icon.
    If path is incorrect returns empty string (in order to display a white image in kivy without raising exceptions).
    :param champion_name: (str) e.g. 'Jax', 'KogMaw'
    :param ability_name: (str) 'q', 'w', 'e', 'r'
    :return: (str)
    """
    # (champ name might be given with first letter being lowercase, while the path expects it as uppercase)
    champion_name = champion_name.capitalize()

    try:
        champion_json_path = CHAMPION_DATA_PATH_BASE + champion_name + '.json'
        with open(champion_json_path) as opened_file:
            champ_json_as_str = opened_file.read()

        ability_index = 'qwer'.index(ability_name)
        ability_id = json.loads(champ_json_as_str)['data'][champion_name]['spells'][ability_index]['id']

        return SPELL_IMAGE_PATH_BASE + ability_id + '.png'
    except FileNotFoundError:
        return ''


def item_icon_path(item_id):
    return ITEM_IMAGE_PATH_BASE + item_id + '.png'


def champion_icon_path(champ_name):
    # (champ name starts with uppercase in non-app data)
    return CHAMPION_IMAGE_PATH_BASE + champ_name.capitalize() + '.png'


# ----------------------------------------------------------------------------------------------------------------------
class DropdownButton(Button):

    def __init__(self, **kwargs):
        self.dropdown_instance = DropDown()
        self.var_tracked = None
        self.contents_in_dropdown = []    # List; each element contains the callable widget and its kwargs

        super().__init__(text='default text', **kwargs)
        self.bind(on_release=self.populate_dropdown)
        self.bind(on_release=self.dropdown_instance.open)

    # Abstract
    def populate_dropdown(self, *args):
        raise NotImplemented


class LvlsDropdownButton(DropdownButton):

    min_max = ListProperty(defaultvalue=[0, 0])
    lvl = NumericProperty()

    def __init__(self, **kwargs):
        self.size_hint_y = None
        super().__init__(height=20, width=40, **kwargs)

    def create_contents_in_dropdown(self, *args):
        """
        Creates buttons and their kwargs.
        :return: (None)
        """
        lst = []

        for i in range(int(self.min_max[0]), int(self.min_max[1]) + 1):

            kwargs_dct = {
                'text': str(i),
                'size_hint_y': None,
                'height': 18
            }

            lst.append((Button, kwargs_dct))

        self.contents_in_dropdown = lst

    def on_min_max(self, *args):
        self.text = str(self.min_max[0])

    def populate_dropdown(self, *args):
        self.dropdown_instance.clear_widgets()
        self.create_contents_in_dropdown()

        for widget, kwargs_dict in self.contents_in_dropdown:

            final_kwargs_dct = dict(**kwargs_dict)

            widg = widget(**final_kwargs_dct)

            if isinstance(widg, Button):
                widg.bind(on_release=lambda btn: self.dropdown_instance.dismiss())
                widg.bind(on_release=lambda btn: setattr(self, 'lvl', int(btn.text)))
                widg.bind(on_release=lambda btn: setattr(self, 'text', btn.text))

            self.dropdown_instance.add_widget(widg)

    def on_press(self, *args):
        self.populate_dropdown()


# ----------------------------------------------------------------------------------------------------------------------
class PopupGridlayoutButton(Button):

    obj_name = StringProperty()

    def __init__(self,
                 grid_contents,
                 square_a=None,
                 **kwargs):

        self.popup_instance = Popup(size_hint=(.8, .8), title='click a champion')
        self.gridlayout_instance = GridLayout(cols=15, spacing=3, )
        self.popup_instance.add_widget(self.gridlayout_instance)
        self.square_a = square_a    # Square side length
        self.grid_contents = grid_contents    # List; each element contains the callable widget and its kwargs
        super().__init__(**kwargs)
        self.size_hint = (None, None)

        self.insert_widgets_in_grid()

        self.bind(on_release=self.popup_instance.open)

    def set_button_image_and_text(self, widg):
        self.background_normal = widg.background_normal
        self.text = widg.text
        self.obj_name = widg.obj_name

    def insert_widgets_in_grid(self):
        """
        Inserts all widgets in the dropdown menu
        and binds whichever are buttons into displaying their image and text as "selected".

        Kwargs that normally aren't present in a widget are to start with "_". They are added after the normal kwargs.

        :return:
        """
        for widget, kwargs_dict in self.grid_contents:

            final_kwargs_dct = dict(size_hint_y=None,
                                    **kwargs_dict)

            if self.square_a:
                # Makes buttons square
                final_kwargs_dct.update(size_hint_x=None,)
                final_kwargs_dct.update(height=self.square_a,
                                        width=self.square_a)

            widg = widget(**final_kwargs_dct)

            if isinstance(widg, Button):
                widg.bind(on_release=lambda btn: self.popup_instance.dismiss())
                widg.bind(on_release=self.set_button_image_and_text)

            self.gridlayout_instance.add_widget(widg)


class ChampionButton(PopupGridlayoutButton):

    initial_champion = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(square_a=60,
                         grid_contents=self.champion_buttons_and_kwargs(),
                         **kwargs)
        self.height = self.width = 70

    def on_initial_champion(self, *args):
        self.background_normal = champion_icon_path(champ_name=self.initial_champion)

    @staticmethod
    def champion_buttons_and_kwargs():
        """
        Creates the grid buttons that are used to select a champion.
        :return:
        """
        lst = []

        for champ_name in sorted(champion_ids.CHAMPION_IDS.values()):
            kwargs_dct = {
                'text': champ_name,
                }

            # Buttons are added only if the champion has been created in the app.
            if champ_name.lower() + '.py' in os.listdir('/home/black/Dev/PycharmProjects/WhiteProject/champions'):
                button_background_path = champion_icon_path(champ_name=champ_name)

                kwargs_dct.update({
                    'background_normal': button_background_path,
                })

                lst.append([Button, kwargs_dct])

        return lst


class ItemButton(PopupGridlayoutButton):
    UPDATE_MAIN_TEXT_TO_SELECTED_BUTTON_TEXT = False

    def __init__(self,  **kwargs):

        super().__init__(text='select \nitem',
                         size_hint=(None, None),
                         height=50,
                         width=50,
                         square_a=50,
                         update_root_button_text=False,
                         disable_selection_buttons_text=True,
                         grid_contents=self.item_buttons_and_kwargs(),
                         **kwargs)

    def item_buttons_and_kwargs(self):
        """
        Creates the grid buttons that are used to select a champion.
        :return:
        """

        # (no-item button)
        lst = [(Button, {'text': 'select\nitem', })]

        for item_id in sorted(ITEMS_IDS_TO_NAMES_MAP):
            kwargs = {}
            item_name = ITEMS_IDS_TO_NAMES_MAP[item_id]

            if self.UPDATE_MAIN_TEXT_TO_SELECTED_BUTTON_TEXT:
                kwargs.update({
                    'text': item_name
                })

            button_background_path = item_icon_path(item_id=item_id)
            kwargs.update({
                'background_normal': button_background_path,
                'obj_name': item_name
            })

            lst.append([Button, kwargs])

        return lst


# ----------------------------------------------------------------------------------------------------------------------
class MasteriesWidget(BoxLayout):
    pass


# ----------------------------------------------------------------------------------------------------------------------
class MainWidget(TabbedPanel):

    server_status = StringProperty()

    def all_preset_params(self):
        return {
            'selected_champions_dct': self.selected_champions_dct,
            'ability_lvls_dct': self.ability_lvls_dct,
            'champion_lvls_dct': self.champion_lvls_dct,
            'max_combat_time': self.max_combat_time,
            'chosen_items_dct': self.chosen_items_dct,
            'selected_summoner_spells': self.selected_summoner_spells,
            'rotation_lst': self.rotation_lst,
        }

    def preset_dct_as_str(self):
        """
        Converts dict to be sent through request's "params" to a string.

        :return: (str)
        """
        return str(self.all_preset_params())

    def __init__(self, **kwargs):
        self.results = ''
        super().__init__(**kwargs)
        self.refresh_server_status()
        Clock.schedule_interval(self.refresh_server_status, 10)

    def refresh_server_status(self, *args):
        try:
            requests.get(HOST_URL)
            self.server_status = 'online'
        except requests.ConnectionError:
            self.server_status = 'offline'

    def request_results(self, params_dct):
        self.refresh_server_status()
        if self.server_status == 'online':
            r = requests.get(HOST_URL, params=params_dct).text
            self.results = r
            print(type(r))
            print(r)
            self.ids.server_message_label.text = "There ya go!"
            self.ids.server_message_label.color = (0,1,0,1)
        else:
            self.ids.server_message_label.text = "Can't bro, server is offline."
            self.ids.server_message_label.color = (1,0,0,1)




class NewSingleInstanceTestApp(App):

    def build(self):
        main_widg = MainWidget()
        return main_widg


if __name__ == '__main__':
    NewSingleInstanceTestApp().run()




