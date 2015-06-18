
from kivy.properties import ListProperty, StringProperty

from flat_kivy.uix.flatlabel import FlatLabel


class FlatIcon(FlatLabel):
    color_tuple = ListProperty(['Grey', '0000'])
    icon = StringProperty('')

