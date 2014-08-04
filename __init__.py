from __future__ import unicode_literals, print_function
__version__ = '0.0.1'
import kivy
from kivy.app import App
from kivy.properties import (ObjectProperty, ListProperty)
from numpad import DecimalNumPad, NumPad
from ui_elements import FlatPopup as Popup
from ui_elements import (ErrorContent, OptionContent, FlatIconButton, 
    FlatLabel, FlatButton, FlatToggleButton, FlatCheckBox, CheckBoxListItem,)
from utils import get_icon_char, get_rgba_color, get_style, construct_target_file_name
from kivy.uix.effectwidget import EffectWidget, HorizontalBlurEffect, VerticalBlurEffect

def style_default(style_name):
    return {}

def color_default(color_tuple):
    return (1., 1., 1., 1.)

def icon_default(icon_name):
    return ''


class ThemeManager(object):

    types_to_theme = {
        'FlatButton': FlatButton, 'FlatIconButton': FlatIconButton, 
        'FlatLabel': FlatLabel, 'FlatToggleButton': FlatToggleButton,
        'FlatCheckBox': FlatCheckBox, 'CheckBoxListItem': CheckBoxListItem,
        }

    themes = {}

    def get_theme(self, theme_name, variant_name):
        try:
            return self.themes[theme_name][variant_name]
        except: 
            print(theme_name, variant_name, 'not in theme')
            return None

    def get_theme_types(self):
        return self.types_to_theme

    def add_theme_type(self, type_name, theme_type):
        self.types_to_theme[type_name] = theme_type

    def add_theme(self, theme, variant, theme_dict):
        themes = self.themes
        if theme not in themes:
            themes[theme] = {}
        if variant not in themes[theme]:
            themes[theme][variant] = {}
        self.themes[theme][variant] = theme_dict

class FlatApp(App):
    get_color = ObjectProperty(color_default)
    get_icon = ObjectProperty(icon_default)
    get_style = ObjectProperty(style_default)


    def __init__(self, **kwargs):
        self.theme_manager = ThemeManager()
        self.get_color = get_rgba_color
        self.get_icon = get_icon_char
        self.get_style = get_style
        super(FlatApp, self).__init__(**kwargs)
        self.setup_themes()

    def get_font(self, font_file):
        return construct_target_file_name(font_file, None)

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

    def setup_themes(self):
        variant_1 = {
            'FlatButton':{
                'color_tuple': ('LightBlue', '500'),
                'ripple_color_tuple': ('Cyan', '100'),
                'font_color_tuple': ('Gray', '1000'),
                'style': 'Display 2',
                'ripple_scale': 2.0,
                },
            'FlatIconButton':{
                'color_tuple': ('LightBlue', '500'),
                'ripple_color_tuple': ('Cyan', '100'),
                'font_color_tuple': ('Gray', '1000'),
                'style': 'Display 2',
                'ripple_scale': 2.0,
                'icon_color_tuple': ('Gray', '1000')
                },
            'FlatToggleButton':{
                'color_tuple': ('LightBlue', '500'),
                'ripple_color_tuple': ('Cyan', '100'),
                'font_color_tuple': ('Gray', '1000'),
                'style': 'Display 2',
                'ripple_scale': 2.0,
                },
            'FlatCheckBox':{
                'color_tuple': ('Gray', '0000'),
                'ripple_color_tuple': ('Cyan', '100'),
                'check_color_tuple': ('LightBlue', '500'),
                'outline_color_tuple': ('Gray', '1000'),
                'style': 'Display 2',
                'ripple_scale': 2.0,
                'check_scale': .7,
                'outline_size': '10dp',
                },
            'CheckBoxListItem':{
                'color_tuple': ('Gray', '0000'),
                'ripple_color_tuple': ('Cyan', '100'),
                'check_color_tuple': ('LightBlue', '500'),
                'outline_color_tuple': ('Gray', '1000'),
                'style': 'Display 2',
                'ripple_scale': 2.0,
                'check_scale': .7,
                'outline_size': '10dp',
                },
            }

        variant_2 = {
            'FlatButton':{
                'color_tuple': ('Green', '500'),
                'ripple_color_tuple': ('Cyan', '100'),
                'font_color_tuple': ('Gray', '1000'),
                'style': 'Display 2',
                'ripple_scale': 2.0,
                },
            'FlatIconButton':{
                'color_tuple': ('Green', '500'),
                'ripple_color_tuple': ('Cyan', '100'),
                'font_color_tuple': ('Gray', '1000'),
                'style': 'Display 2',
                'ripple_scale': 2.0,
                'icon_color_tuple': ('Gray', '1000')
                },
            }

        self.theme_manager.add_theme('blue', 'variant_1', variant_1)
        self.theme_manager.add_theme('blue', 'variant_2', variant_2)


if __name__ == '__main__':
    FlatApp().run()