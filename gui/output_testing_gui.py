import functional_testing.default_config as default_config

from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label


ALL_DATA = default_config.ALL_DATA




class VerticalBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'


class SmallButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (50,50)
        self.size_hint = (None, None)

# ----------------------------------------------------------------------------------------------------------------------


class ChampionLvlLabel(Label):
    def __init__(self, champ, **kwargs):
        # ('player', 'enemy_1', ..)
        self.champ = champ

        super().__init__(**kwargs)
        self.font_size = 24
        self.text_size = self.size
        self.halign = 'left'
        self.text = self.__label_text()

    def __label_text(self):

        champ_name = str(ALL_DATA['selected_champions_dct'][self.champ].capitalize())
        champ_lvl = str(ALL_DATA['champion_lvls_dct'][self.champ])

        msg = '{} {}'.format(champ_name, champ_lvl)

        return msg




class GeneralTab(TabbedPanel):
    pass


class SingleInstanceTest(App):

    def build(self):
        return GeneralTab()


if __name__ == '__main__':
    SingleInstanceTest().run()