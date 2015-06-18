
from kivy.uix.textinput import TextInput
from kivy.uix.stacklayout import StackLayout
from kivy.properties import ListProperty, ObjectProperty, StringProperty

from flat_kivy.uix.behaviors import (GrabBehavior, TouchRippleBehavior)


class FlatTextInput(GrabBehavior, TouchRippleBehavior, TextInput):
    ripple_color_tuple = ListProperty(['Grey', '1000'])

    def on_touch_down(self, touch):
        TextInput.on_touch_down(self, touch)
        super(FlatTextInput, self).on_touch_down(touch)


class TextInputFocus(StackLayout):
    close_callback = ObjectProperty(None)
    text = StringProperty(None, allownone=True)
