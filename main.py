from __future__ import unicode_literals, print_function
__version__ = '0.0.1'
import kivy
from kivy.app import App
from kivy.properties import (ObjectProperty, ListProperty)
from numpad import DecimalNumPad, NumPad
from ui_elements import FlatPopup as Popup
from ui_elements import ErrorContent, OptionContent, FlatIconButton, FlatLabel
from utils import get_icon_char, get_rgba_color, get_style

def style_default(style_name):
    return {}

def color_default(color_tuple):
    return (1., 1., 1., 1.)

def icon_default(icon_name):
    return ''


class FlatApp(App):
    get_color = ObjectProperty(color_default)
    get_icon = ObjectProperty(icon_default)
    get_style = ObjectProperty(style_default)

    def build(self):
        self.get_color = get_rgba_color
        self.get_icon = get_icon_char
        self.get_style = get_style
        super(FlatApp, self).build()

    def raise_error(self, error_title, error_text):
        error_content = ErrorContent()
        error_popup = Popup(
            content=error_content, size_hint=(.6, .4))
        error_content.error_text = error_text
        error_popup.title = error_title
        dismiss_button = error_content.dismiss_button
        dismiss_button.bind(on_release=error_popup.dismiss)
        error_popup.open()

    def raise_option_dialogue(self, option_title, option_text, options, 
            callback):
        option_content = OptionContent(options, option_text=option_text, 
            callback=callback)
        option_popup = Popup(content=option_content, size_hint=(.6,.4))
        option_popup.title = option_title
        option_content.dismiss_func = option_popup.dismiss
        option_popup.open()

    def raise_numpad(self, numpad_title, callback, units=None,
        minimum=None, maximum=None, do_decimal=False):
        if do_decimal:
            numpad = DecimalNumPad(units=units, minimum_value=minimum, 
                maximum_value=maximum)
        else:
            numpad = NumPad(units=units, minimum_value=minimum, 
                maximum_value=maximum)     
        numpad_popup = Popup(
            title=numpad_title, content=numpad, size_hint=(.8, .8))
        def return_callback(value, is_return):
            if callback is not None:
                callback(value, is_return)
            if is_return:
                numpad_popup.dismiss()
        numpad.return_callback = return_callback
        numpad_popup.open()


if __name__ == '__main__':
    FlatApp().run()