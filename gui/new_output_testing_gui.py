from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown


class MainWidget(TabbedPanel):
    pass


class NewSingleInstanceTestApp(App):
    def build(self):
        return MainWidget()


if __name__ == '__main__':
    NewSingleInstanceTestApp().run()