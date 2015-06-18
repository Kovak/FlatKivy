
from kivy.properties import ListProperty, StringProperty

from flat_kivy.utils import construct_target_file_name


class RaisedStyle(object):
    border = ListProperty([16, 16, 16, 16])
    border_size = ListProperty([2, 3, 4, 3])
    border_image = StringProperty(
        construct_target_file_name('../data/images/button_raised.png', __file__))
