from kivy.uix.listview import ListView
from kivy.base import runTouchApp


class MainView(ListView):
    def __init__(self, **kwargs):
        super(MainView, self).__init__(
            item_strings=[str(index) for index in range(100)])

if __name__ == '__main__':
    runTouchApp(MainView())