
from kivy.properties import StringProperty

from flat_kivy.uix.flattogglebutton import FlatToggleButton


class FlatOptionButton(FlatToggleButton):
    key = StringProperty(None)