
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import (ListProperty, StringProperty, NumericProperty,
                             BooleanProperty)

from flat_kivy.uix.behaviors import (GrabBehavior, ThemeBehavior, LogBehavior,
                                     TouchRippleBehavior, ButtonBehavior)
from flat_kivy.uix.styles import RaisedStyle


class FlatButtonBase(GrabBehavior, LogBehavior, TouchRippleBehavior,
                     ThemeBehavior):
    color = ListProperty([1., 1., 1.])
    color_down = ListProperty([.7, .7, .7])
    border_size = ListProperty([0, 0, 0, 0])
    text = StringProperty('')
    alpha = NumericProperty(1.0)
    style = StringProperty(None, allownone=True)
    color_tuple = ListProperty(['Grey', '500'])
    font_color_tuple = ListProperty(['Grey', '1000'])
    ripple_color_tuple = ListProperty(['Grey', '1000'])
    font_ramp_tuple = ListProperty(None)
    font_size = NumericProperty(12)
    eat_touch = BooleanProperty(False)

    def on_color(self, instance, value):
        self.color_down = [x*.7 for x in value]


class FlatButton(FlatButtonBase, ButtonBehavior, AnchorLayout):
    pass


class RaisedFlatButton(RaisedStyle, FlatButton):
    pass
