import os
import json
import requests
import ast

from pprint import pprint as pp
from functools import partial
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.label import Label
from kivy.uix.button import Button as BaseButton
from kivy.uix.dropdown import DropDown
from kivy.core.window import Window
from kivy.modules import inspector
from kivy.properties import ListProperty, StringProperty, DictProperty, NumericProperty
from kivy.clock import Clock

# ----------------------------------------------------------------------------------------------------------------------
__version__ = '0.0.1'

# ----------------------------------------------------------------------------------------------------------------------

Window.size = (1050, 1000)

# ----------------------------------------------------------------------------------------------------------------------
# SERVER URL

# (removed real addresses)
HOSTS_URLS_DCTS = {
    1: 'http://---------',
    2: 'http://----------',
    3: 'http://-----------'
}

HOST_URL = HOSTS_URLS_DCTS[3]

REQUEST_TIMEOUT = None

print('GUI initiated.')

# ----------------------------------------------------------------------------------------------------------------------
# PATHS

DRAGONTAIL_VERSION = '6.1.1'
DRAGONTAIL_FOLDER = 'dragontail-{}'.format(DRAGONTAIL_VERSION)

FILE_PATH = os.path.dirname(__file__)
PATH_BASE = os.path.join(FILE_PATH, DRAGONTAIL_FOLDER, DRAGONTAIL_VERSION)
IMAGE_PATH_BASE = os.path.join(PATH_BASE, 'img')
CHAMPION_IMAGE_PATH_BASE = os.path.join(IMAGE_PATH_BASE, 'champion')
SPELL_IMAGE_PATH_BASE = os.path.join(IMAGE_PATH_BASE, 'spell')
ITEM_IMAGE_PATH_BASE = os.path.join(IMAGE_PATH_BASE, 'item')
MASTERY_IMAGE_PATH_BASE = os.path.join(IMAGE_PATH_BASE, 'mastery')
MELEE_CREEP_IMAGE_PATH = os.path.join(IMAGE_PATH_BASE, 'profileicon', '15.png')

CHAMPION_DATA_PATH_BASE = os.path.join(PATH_BASE, 'data', 'en_US', 'champion')

MASTERIES_JSON_PATH = os.path.join(PATH_BASE, 'data', 'en_US', 'mastery.json')

# ----------------------------------------------------------------------------------------------------------------------
PLAYER_AND_ENEMIES_LST = ['player', ]
PLAYER_AND_ENEMIES_LST += ['enemy_{}'.format(i) for i in range(1, 5)]
SPELL_SHORTCUTS = ['q', 'w', 'e', 'r']

# ----------------------------------------------------------------------------------------------------------------------
CREATED_CHAMPION_IDS = []
ITEMS_IDS_TO_NAMES_MAP = {}
try:
    r = requests.get(HOST_URL, timeout=REQUEST_TIMEOUT,
                     params={'created_champions_names_and_items_ids_to_names_map': ''})
    print(r)

    dct = ast.literal_eval(r.text)

    CREATED_CHAMPION_IDS = dct['created_champions_ids']
    ITEMS_IDS_TO_NAMES_MAP = dct['items_ids_to_names_map']

    print('SERVER ONLINE')

except requests.ConnectionError:
    print('Server OFFLINE.')


# ----------------------------------------------------------------------------------------------------------------------
class Button(BaseButton):
    """
    Removes border from all buttons.
    """

    obj_name = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(border=(0, 0, 0, 0), **kwargs)


class SquareButton(Button):

    def __init__(self, square_a, **kwargs):
        super().__init__(size_hint=(None, None),
                         width=square_a,
                         height=square_a,
                         **kwargs)


# ----------------------------------------------------------------------------------------------------------------------
def empty_str_on_file_not_found_error(func):
    """
    Decorator that handles FileNotFoundError and returns an empty string instead of raising an error.
    """

    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            return ''

    return wrapped


# ----------------------------------------------------------------------------------------------------------------------
with open(MASTERIES_JSON_PATH) as masteries_file:
    masteries_as_str = masteries_file.read()

    # (includes tree as well)
    _ALL_MASTERIES_DATA_DCT = json.loads(masteries_as_str)
    # (includes only dicts of each mastery)
    MASTERIES_DCT = _ALL_MASTERIES_DATA_DCT['data']
    MASTERIES_TREE_DCT = _ALL_MASTERIES_DATA_DCT['tree']

MASTERIES_CATEGORIES = ('Ferocity', 'Cunning', 'Resolve')

MAX_MASTERY_TIER = 6
MAX_TOTAL_MASTERIES_POINTS = 30

MASTERIES_TIERS_MAP = {}
for branch_name in MASTERIES_TREE_DCT:
    MASTERIES_TIERS_MAP.update({branch_name: {}})
    for tier_number, tier_lst in enumerate(MASTERIES_TREE_DCT[branch_name], start=1):

        for elem in tier_lst:
            if elem:
                MASTERIES_TIERS_MAP[branch_name].update({elem['masteryId']: tier_number})


# ----------------------------------------------------------------------------------------------------------------------

@empty_str_on_file_not_found_error
def mastery_image_path(mastery_id, gray):
    """
    Returns given mastery's image path.

    :param mastery_id: (str) or (int)
    :param gray: (bool)
    :return: (str) Path in dragontail.
    """

    mastery_id = str(mastery_id)

    if gray:
        mastery_image_file = 'gray_' + mastery_id + '.png'
    else:
        mastery_image_file = mastery_id + '.png'

    return os.path.join(MASTERY_IMAGE_PATH_BASE, mastery_image_file)


# ----------------------------------------------------------------------------------------------------------------------

@empty_str_on_file_not_found_error
def spell_icon_path(champion_name, ability_name):
    """
    Returns path of the icon.

    :param champion_name: (str) e.g. 'jax', 'Jax', 'KogMaw'
    :param ability_name: (str) 'q', 'w', 'e', 'r'
    :return: (str)
    """

    champions_in_path = os.listdir(CHAMPION_DATA_PATH_BASE)
    # Dict with `lower_case: normal_case pairs`, e.g. `'kogmaw': 'KogMaw'`
    # to make the function case-insensitive.
    # (`[:-5]` slices off '.json')
    champions_in_path = {i[:-5].lower(): i[:-5] for i in champions_in_path}

    lower_champ_name = champion_name.lower()
    champ_name_in_api = champions_in_path[lower_champ_name]

    champion_json_path = os.path.join(CHAMPION_DATA_PATH_BASE, champ_name_in_api + '.json')
    with open(champion_json_path) as opened_file:
        champ_json_as_str = opened_file.read()

    ability_index = 'qwer'.index(ability_name)
    ability_id = json.loads(champ_json_as_str)['data'][champ_name_in_api]['spells'][ability_index]['id']
    ability_image_file = ability_id + '.png'

    return os.path.join(SPELL_IMAGE_PATH_BASE, ability_image_file)


def item_icon_path(item_id):
    return os.path.join(ITEM_IMAGE_PATH_BASE, item_id + '.png')


def champion_icon_path(champ_name):
    if champ_name != 'melee_creep':
        # (champ name starts with uppercase in non-app data)
        return os.path.join(CHAMPION_IMAGE_PATH_BASE, champ_name.capitalize() + '.png')
    else:
        return MELEE_CREEP_IMAGE_PATH


# ----------------------------------------------------------------------------------------------------------------------
class DropdownButton(Button):

    def __init__(self, **kwargs):
        self.dropdown_instance = DropDown()
        self.var_tracked = None
        self.contents_in_dropdown = []  # List; each element contains the callable widget and its kwargs

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
class PopupGridlayoutButton(SquareButton):
    obj_name = StringProperty()

    def __init__(self,
                 title,
                 grid_contents,
                 square_a,
                 **kwargs):

        self.popup_instance = Popup(title=title, size_hint=(.8, .8))
        self.gridlayout_instance = GridLayout(cols=15, spacing=3, )
        self.popup_instance.add_widget(self.gridlayout_instance)
        self.grid_contents = grid_contents  # List; each element contains the callable widget and its kwargs
        super().__init__(square_a=square_a, **kwargs)

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

            widg = widget(**kwargs_dict)

            if isinstance(widg, Button):
                widg.bind(on_release=lambda btn: self.popup_instance.dismiss())
                widg.bind(on_release=self.set_button_image_and_text)

            self.gridlayout_instance.add_widget(widg)


class ChampionButton(PopupGridlayoutButton):
    initial_champion = StringProperty()
    square_a = NumericProperty(50)

    def __init__(self, **kwargs):
        super().__init__(square_a=self.square_a,
                         grid_contents=self.champion_buttons_and_kwargs(),
                         title='click a champion',
                         **kwargs)

    def on_initial_champion(self, *args):
        self.background_normal = champion_icon_path(champ_name=self.initial_champion)
        self.text = self.initial_champion

    def champion_buttons_and_kwargs(self):
        """
        Creates the grid buttons that are used to select a champion.
        :return:
        """
        lst = []

        for champ_name in sorted(CREATED_CHAMPION_IDS):
            kwargs_dct = {
                'text': champ_name,
                'square_a': self.square_a
            }

            button_background_path = champion_icon_path(champ_name=champ_name)
            kwargs_dct.update({
                'background_normal': button_background_path,
            })

            lst.append([SquareButton, kwargs_dct])

        return lst


class ItemButton(PopupGridlayoutButton):
    UPDATE_MAIN_TEXT_TO_SELECTED_BUTTON_TEXT = False
    square_a = NumericProperty(50)

    def __init__(self, **kwargs):

        super().__init__(text='select \nitem',
                         update_root_button_text=False,
                         disable_selection_buttons_text=True,
                         grid_contents=self.item_buttons_and_kwargs(),
                         title="click an item (TODO white items; avoid using them)",
                         square_a=self.square_a,
                         **kwargs)

    def item_buttons_and_kwargs(self):
        """
        Creates the grid buttons that are used to select a champion.
        :return:
        """

        # (no-item button)
        lst = [(SquareButton, {'text': 'select\nitem', 'square_a': self.square_a})]

        for item_id in sorted(ITEMS_IDS_TO_NAMES_MAP):
            kwargs = {'square_a': self.square_a}
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

            lst.append([SquareButton, kwargs])

        return lst


# ----------------------------------------------------------------------------------------------------------------------
class Tooltip(Label):
    pass


class SingleMasteryWidget(SquareButton):
    mastery_lvl = NumericProperty(0)

    def __init__(self, mastery_id, masteries_lvls, **kwargs):
        self.mastery_id = mastery_id
        self.normal_image_path = mastery_image_path(mastery_id=mastery_id, gray=False)
        self.gray_image_path = mastery_image_path(mastery_id=mastery_id, gray=True)
        self.masteries_lvls = masteries_lvls
        self.masteries_lvls.update({self.mastery_id: 0})
        self.max_lvl = self.mastery_max_lvl(mastery_id=self.mastery_id)
        self.mastery_app_name = MASTERIES_DCT[self.mastery_id]['name']
        self.mastery_description_pieces = MASTERIES_DCT[self.mastery_id]['description']
        self.mastery_branch, self.mastery_tier = self.mastery_branch_and_tier(mastery_id=self.mastery_id)

        square_a = 50
        super().__init__(square_a=square_a, **kwargs)
        self.text_size = self.size[0], self.size[1] + 30
        self.text = str(self.mastery_lvl)

        self.update_mastery_image()

        self.tooltip = Tooltip()
        Window.bind(mouse_pos=self.on_mouse_pos)

    def update_mastery_description(self):
        # (description on 0 lvl is the same as 1 lvl)
        description_index = max(self.mastery_lvl - 1, 0)

        description = self.mastery_app_name + '\n\n'
        description += self.mastery_description_pieces[description_index]
        description = description.replace('<br><br>', '\n')

        self.tooltip.text = description

    def on_mouse_pos(self, *args):
        mouse_pos = Window.mouse_pos
        self.tooltip.pos = mouse_pos[0] + self.width, mouse_pos[1] + self.height
        self.remove_widget(self.tooltip)

        if self.collide_point(*self.to_widget(*mouse_pos)):
            self.update_mastery_description()
            self.add_widget(self.tooltip)

    def on_mastery_lvl(self, *args):
        self.masteries_lvls[self.mastery_id] = self.mastery_lvl
        self.text = str(self.mastery_lvl)

        self.on_mouse_pos()

    @staticmethod
    def mastery_max_lvl(mastery_id):
        mastery_id = str(mastery_id)

        return MASTERIES_DCT[mastery_id]['ranks']

    @staticmethod
    def mastery_branch_and_tier(mastery_id):
        """
        Returns a both branch and tier of a mastery.

        :param mastery_id:
        :return: (tuple) Contains branch and tier.
        """
        for branch_name in MASTERIES_TREE_DCT:
            for tier_num, tier_lst in enumerate(MASTERIES_TREE_DCT[branch_name], start=1):

                for elem in tier_lst:
                    if elem:

                        if elem['masteryId'] == mastery_id:
                            return branch_name, tier_num

        else:
            raise KeyError('Non existent mastery id: {}'.format(mastery_id))

    @staticmethod
    def tier_max_lvl(tier):
        if tier % 2 == 0:
            return 1
        else:
            return 5

    def previous_tier_max_lvl(self, tier):
        return self.tier_max_lvl(tier=tier - 1)

    def previous_tier_lvls(self):
        tot_lvls = 0
        previous_tier = self.mastery_tier - 1

        for mast_id, tier_n in MASTERIES_TIERS_MAP[self.mastery_branch].items():
            if tier_n == previous_tier:
                tot_lvls += self.masteries_lvls[mast_id]

        return tot_lvls

    def current_tier_lvls(self):
        tot_lvls = 0
        for mast_id, tier_n in MASTERIES_TIERS_MAP[self.mastery_branch].items():
            if tier_n == self.mastery_tier:
                tot_lvls += self.masteries_lvls[mast_id]

        return tot_lvls

    def current_total_masteries_points(self):

        tot_lvls = 0
        for branch_name in MASTERIES_TIERS_MAP:
            for mastery_id in MASTERIES_TIERS_MAP[branch_name]:
                tot_lvls += self.masteries_lvls[mastery_id]

        return tot_lvls

    def reset_current_tier(self):
        for mast_id, tier_n in MASTERIES_TIERS_MAP[self.mastery_branch].items():
            if tier_n == self.mastery_tier:
                self.masteries_lvls[mast_id] = 0

    def previous_tiers_filled(self):
        # Tier 1 masteries have no previous requirements.
        if self.mastery_tier == 1:
            return True

        else:
            if self.previous_tier_max_lvl(tier=self.mastery_tier) == self.previous_tier_lvls():
                return True
            else:
                return False

    def current_tier_filled(self):
        if self.current_tier_lvls() == self.max_lvl:
            return True
        else:
            return False

    def following_tier_has_contents(self):
        if self.mastery_tier == MAX_MASTERY_TIER:
            return False

        else:
            following_tier = self.mastery_tier + 1

            for mast_id, tier_n in MASTERIES_TIERS_MAP[self.mastery_branch].items():
                if tier_n == following_tier:
                    if self.masteries_lvls[mast_id]:
                        return True

            else:
                return False

    def update_mastery_image(self):
        if self.mastery_lvl:
            path = self.normal_image_path
        else:
            path = self.gray_image_path

        self.background_normal = path

    def on_release(self):
        """
        Increases lvl of mastery based on its current value, up to its maximum value.

        :return: (None)
        """

        # Disables button functionality if masteries' points requirements aren't met.
        if self.previous_tiers_filled():
            if not self.current_tier_filled():
                if self.current_total_masteries_points() < MAX_TOTAL_MASTERIES_POINTS:

                    current_mastery_lvl = self.mastery_lvl
                    if current_mastery_lvl < self.max_lvl:
                        self.mastery_lvl = current_mastery_lvl + 1
                        self.update_mastery_image()


class _MasteriesTierWidget(BoxLayout):
    reset_signal = NumericProperty()

    def __init__(self, masteries_in_tier_lst, masteries_lvls, **kwargs):
        self.masteries_in_tier_lst = masteries_in_tier_lst
        self.masteries_lvls = masteries_lvls
        super().__init__(orientation='horizontal', **kwargs)
        self.populate_widg()

    def populate_widg(self):
        self.add_widget(Label())
        for elem in self.masteries_in_tier_lst:
            if elem:
                mastery_id = elem['masteryId']
                single_mastery_widg = SingleMasteryWidget(mastery_id=mastery_id, masteries_lvls=self.masteries_lvls)
                self.add_widget(single_mastery_widg)

            else:
                self.add_widget(Label())
        self.add_widget(Label())


class _MasteriesBranch(BoxLayout):

    def __init__(self, branch_name, masteries_lvls, **kwargs):
        self.branch_name = branch_name
        self.masteries_lvls = masteries_lvls

        super().__init__(orientation='vertical', **kwargs)
        self.populate_branch()

    def populate_branch(self):
        branch_contents_lst = MASTERIES_TREE_DCT[self.branch_name]

        for tier_lst in branch_contents_lst:
            tier_widg = _MasteriesTierWidget(masteries_in_tier_lst=tier_lst, masteries_lvls=self.masteries_lvls)
            self.add_widget(tier_widg)


class MasteriesWidget(BoxLayout):
    masteries_lvls = DictProperty()

    def __init__(self, **kwargs):
        super().__init__(orientation='horizontal', **kwargs)
        self.repopulate_masteries_widget()

    def repopulate_masteries_widget(self):
        self.clear_widgets()
        for branch_name in MASTERIES_CATEGORIES:
            self.add_widget(_MasteriesBranch(branch_name=branch_name, masteries_lvls=self.masteries_lvls))

    def reset_masteries_lvls(self, *args):
        for i in self.masteries_lvls:
            self.masteries_lvls[i] = 0

        self.repopulate_masteries_widget()


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
        super().__init__(**kwargs)
        self.refresh_server_status()
        # Server periodic refreshing switch.
        if 0:
            Clock.schedule_interval(self.refresh_server_status, 300)

    def refresh_server_status(self, *args):

        try:
            requests.get(HOST_URL, timeout=REQUEST_TIMEOUT)
            self.server_status = 'online'

        except requests.ConnectionError:
            self.server_status = 'offline'

    def request_results(self, params_dct):
        self.refresh_server_status()
        if self.server_status == 'online':
            image_name = requests.get(HOST_URL, timeout=REQUEST_TIMEOUT, params=params_dct).text
            self.ids.server_message_label.text = "There ya go!"
            self.ids.server_message_label.color = (0, 1, 0, 1)
            self.ids.results_image.source = os.path.join(HOST_URL, 'img', image_name)
        else:
            self.ids.server_message_label.text = "Can't bro, server is offline."
            self.ids.server_message_label.color = (1, 0, 0, 1)


class MainGUIApp(App):

    def build(self):
        main_widg = MainWidget()
        return main_widg


if __name__ == '__main__':
    MainGUIApp().run()
