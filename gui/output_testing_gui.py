import os
import json
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.button import Button as BaseButton
from kivy.uix.dropdown import DropDown
from kivy.core.window import Window
from kivy.properties import NumericProperty

import champion_ids
from items_folder.items_data import ITEMS_IDS_TO_NAMES_MAP


Window.size = (1000, 700)

# ----------------------------------------------------------------------------------------------------------------------
PATH_BASE = '/home/black/Downloads/dragontail-5.24.2/5.24.2/'
IMAGE_PATH_BASE = PATH_BASE + 'img/'
CHAMPION_IMAGE_PATH_BASE = IMAGE_PATH_BASE + 'champion/'
SPELL_IMAGE_PATH_BASE = IMAGE_PATH_BASE + 'spell/'
ITEM_IMAGE_PATH_BASE = IMAGE_PATH_BASE + 'item/'

CHAMPION_DATA_PATH_BASE = PATH_BASE + 'data/en_US/champion/'


# ----------------------------------------------------------------------------------------------------------------------
selected_champion = 'Jax'
selected_spell_lvls = {'q': 0, 'w': 0, 'e': 0, 'r': 0}


# ----------------------------------------------------------------------------------------------------------------------
class Button(BaseButton):
    def __init__(self, **kwargs):
        super().__init__(border=(0, 0, 0, 0), **kwargs)


# ----------------------------------------------------------------------------------------------------------------------
def spell_icon_path(champion_name, ability_name):

    champion_json_path = CHAMPION_DATA_PATH_BASE + champion_name + '.json'
    with open(champion_json_path) as opened_file:
        champ_json_as_str = opened_file.read()

    ability_index = 'qwer'.index(ability_name)
    ability_id = json.loads(champ_json_as_str)['data'][champion_name]['spells'][ability_index]['id']

    return SPELL_IMAGE_PATH_BASE + ability_id + '.png'


# ----------------------------------------------------------------------------------------------------------------------
class DropDownList(Button):

    initial_text = 'Default text'

    def __init__(self, list_contents, **kwargs):
        self.text = self.initial_text
        self.dropdown_instance = DropDown()
        self.list_contents = list_contents    # List; each element contains the callable widget and its kwargs
        super().__init__(**kwargs)
        self.size_hint = (None, None)

        self.insert_widgets_in_dropdown()

        self.bind(on_release=self.dropdown_instance.open)
        self.dropdown_instance.bind(on_select=lambda instance, x: setattr(self, 'text', x))

    def set_button_image(self, widg):
        self.text = widg.text

    def insert_widgets_in_dropdown(self):

        for widget, kwargs_dict in self.list_contents:

            final_kwargs_dct = dict(**kwargs_dict)

            widg = widget(**final_kwargs_dct)

            if isinstance(widg, Button):
                widg.bind(on_release=lambda btn: self.dropdown_instance.dismiss())
                widg.bind(on_release=self.set_button_image)

            self.dropdown_instance.add_widget(widg)


class LvlsDropDownList(DropDownList):

    min_lvl = NumericProperty()
    max_lvl = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(text=str(self.min_lvl), list_contents=self.list_contents(), size_hint=(None, None), height=15, width=50, **kwargs)

    def list_contents(self):
        """
        Creates buttons and their kwargs.
        :return: (list) Contains pairs of buttons-kwargs.
        """
        lst = []

        for i in range(self.min_lvl, self.max_lvl + 1):

            kwargs_dct = {
                'text': str(i),
                'size_hint_y': None,
                'height': 18
            }

            lst.append((Button, kwargs_dct))

        return lst


class ChampionLvlsDropDownList(LvlsDropDownList):
    min_lvl = 1
    max_lvl = 18

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class NonUltimateAbilityLvlsDropDownList(LvlsDropDownList):
    min_lvl = 0
    max_lvl = 5


class UltimateAbilityLvlsDropDownList(LvlsDropDownList):
    min_lvl = 0
    max_lvl = 3


# ----------------------------------------------------------------------------------------------------------------------
class PopupGridlayoutButton(Button):

    def __init__(self, grid_contents,
                 square_a=None,
                 update_root_button_text=True,
                 **kwargs):

        self.update_root_button_text = update_root_button_text
        self.popup_instance = Popup(size_hint=(.8, .8), title='click a champion')
        self.gridlayout_instance = GridLayout(cols=15, spacing=3, )
        self.popup_instance.add_widget(self.gridlayout_instance)
        self.square_a = square_a    # Square side length
        self.grid_contents = grid_contents    # List; each element contains the callable widget and its kwargs
        super().__init__(**kwargs)
        self.size_hint = (None, None)

        self.insert_widgets_in_grid()

        self.bind(on_release=self.popup_instance.open)
        self.popup_instance.bind(on_select=lambda instance, x: setattr(self, 'text', x))

    def set_button_image_and_text(self, widg):
        self.background_normal = widg.background_normal
        if self.update_root_button_text:
            self.text = widg.text
        else:
            self.text = ''

    def insert_widgets_in_grid(self):
        """
        Inserts all widgets in the dropdown menu
        and binds whichever are buttons into displaying their image and text as "selected".

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

    def __init__(self, **kwargs):
        super().__init__(text=selected_champion,
                         background_normal=CHAMPION_IMAGE_PATH_BASE + '/' + selected_champion + '.png',
                         square_a=60,
                         grid_contents=self.champion_buttons_and_kwargs(),
                         **kwargs)

    @staticmethod
    def champion_buttons_and_kwargs():
        """
        Creates the grid buttons that are used to select a champion.
        :return:
        """
        lst = []

        for champ_name in sorted(champion_ids.CHAMPION_IDS.values()):
            kwargs = {
                'text': champ_name,
                }

            # Buttons are added only if the champion has been created in the app.
            if champ_name.lower() + '.py' in os.listdir('/home/black/Dev/PycharmProjects/WhiteProject/champions'):
                button_background_path = CHAMPION_IMAGE_PATH_BASE + champ_name + '.png'

                kwargs.update({
                    'background_normal': button_background_path,
                })

                lst.append([Button, kwargs])

        return lst


class ItemButton(PopupGridlayoutButton):
    UPDATE_MAIN_TEXT_TO_SELECTED_BUTTON_TEXT = False

    def __init__(self, update_main_text_to_selected_button_text=False, **kwargs):

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
        lst = []

        for item_id in sorted(ITEMS_IDS_TO_NAMES_MAP):
            kwargs = {}
            if self.UPDATE_MAIN_TEXT_TO_SELECTED_BUTTON_TEXT:
                kwargs.update({
                    'text': ITEMS_IDS_TO_NAMES_MAP[item_id],
                })

            button_background_path = ITEM_IMAGE_PATH_BASE + item_id + '.png'
            kwargs.update({
                'background_normal': button_background_path,
            })

            lst.append([Button, kwargs])

        return lst





class MainWidget(TabbedPanel):
    pass


class NewSingleInstanceTestApp(App):
    def build(self):
        main_widg = MainWidget()
        return main_widg


if __name__ == '__main__':
    NewSingleInstanceTestApp().run()
