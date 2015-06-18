
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import (ListProperty, StringProperty,
                             VariableListProperty, NumericProperty)

from flat_kivy.uix.behaviors import (GrabBehavior, LogBehavior,
                                     ButtonBehavior, TouchRippleBehavior,
                                     ThemeBehavior)


class FlatIconButton(GrabBehavior, LogBehavior, ButtonBehavior,
                     TouchRippleBehavior, ThemeBehavior, AnchorLayout):
    color = ListProperty([1., 1., 1.])
    color_down = ListProperty([.7, .7, .7])
    text = StringProperty('')
    icon = StringProperty('')
    style = StringProperty(None, allownone=True)
    font_size = NumericProperty(12)
    icon_color_tuple = ListProperty(['Grey', '1000'])
    color_tuple = ListProperty(['Blue', '500'])
    font_color_tuple = ListProperty(['Grey', '1000'])
    font_ramp_tuple = ListProperty(None)
    ripple_color_tuple = ListProperty(['Grey', '1000'])
    content_padding = VariableListProperty([0., 0., 0., 0.])
    content_spacing = VariableListProperty([0., 0.], length=2)

    def on_color(self, instance, value):
        self.color_down = [x*.7 for x in value]


class FlatIconButtonLeft(FlatIconButton):
    pass
