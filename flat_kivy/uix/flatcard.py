
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty

from flat_kivy.uix.behaviors import (GrabBehavior, ThemeBehavior, LogBehavior,
                                     TouchRippleBehavior, ButtonBehavior)


class FlatCard(GrabBehavior, ThemeBehavior, LogBehavior, TouchRippleBehavior,
               ButtonBehavior, BoxLayout):
    image_source = StringProperty(None)
    style = StringProperty(None, allownone=True)
    color_tuple = ListProperty(['Grey', '500'])
    font_color_tuple = ListProperty(['Grey', '1000'])
    font_ramp_tuple = ListProperty(None)
    ripple_color_tuple = ListProperty(['Grey', '1000'])
    text = StringProperty(None)
    color = ListProperty([1., 1., 1.])
    color_down = ListProperty([.7, .7, .7])

    def on_color(self, instance, value):
        self.color_down = [x*.7 for x in value]