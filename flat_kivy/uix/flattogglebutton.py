
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import BooleanProperty

from flat_kivy.uix.behaviors import ToggleButtonBehavior
from flat_kivy.uix.flatbutton import FlatButtonBase
from flat_kivy.uix.styles import RaisedStyle


class FlatToggleButton(FlatButtonBase, ToggleButtonBehavior, AnchorLayout):
    no_up = BooleanProperty(False)

    def on_touch_down(self, touch):
        if self.no_up:
            if self.collide_point(touch.x, touch.y) and self.state == 'normal':
                super(FlatToggleButton, self).on_touch_down(touch)
        else:
            super(FlatToggleButton, self).on_touch_down(touch)


class RaisedFlatToggleButton(RaisedStyle, FlatToggleButton):
    pass