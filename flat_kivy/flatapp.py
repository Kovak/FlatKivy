from __future__ import unicode_literals, print_function
from kivy.app import App
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty
from kivy.clock import Clock

from flat_kivy.uix.behaviors import LogBehavior
from flat_kivy.uix.flatbutton import FlatButton, RaisedFlatButton
from flat_kivy.uix.flattogglebutton import (FlatToggleButton,
                                            RaisedFlatToggleButton)
from flat_kivy.uix.flatpopup import FlatPopup
from flat_kivy.uix import ErrorContent, OptionContent
from flat_kivy.uix.flaticonbutton import FlatIconButton
from flat_kivy.uix.flatcheckbox import FlatCheckBox, FlatCheckBoxListItem
from flat_kivy.uix.flatlabel import FlatLabel
from flat_kivy.uix.flatslider import FlatSlider
from flat_kivy.uix.flatcard import FlatCard
from flat_kivy.uix.flattextinput import FlatTextInput

from numpad import DecimalNumPad, NumPad
from utils import get_icon_char, get_rgba_color, construct_target_file_name
from font_definitions import get_font_ramp_group, get_style, style_manager
from dbinterface import DBInterface


def style_default(style_name):
    return None

def color_default(color_tuple):
    return (1., 1., 1., 1.)

def icon_default(icon_name):
    return ''

def ramp_default(ramp_group_tuple):
    return None


class ThemeManager(object):

    types_to_theme = {
        'FlatButton': FlatButton, 'FlatIconButton': FlatIconButton,
        'FlatToggleButton': FlatToggleButton,
        'RaisedFlatButton': RaisedFlatButton,
        'RaisedFlatToggleButton': RaisedFlatToggleButton,
        'FlatLabel': FlatLabel,
        'FlatCheckBox': FlatCheckBox,
        'FlatCheckBoxListItem': FlatCheckBoxListItem,
        'FlatSlider': FlatSlider,
        'FlatCard': FlatCard,
        }

    themes = {}

    def get_theme(self, theme_name, variant_name):
        try:
            return self.themes[theme_name][variant_name]
        except KeyError:
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
    get_ramp_group = ObjectProperty()
    device_id = NumericProperty(None)
    do_device_id = BooleanProperty(True)

    def __init__(self, **kwargs):
        self.theme_manager = ThemeManager()
        self.setup_font_ramps()
        self.get_color = get_rgba_color
        self.get_icon = get_icon_char
        self.get_style = get_style
        self.get_ramp_group = get_font_ramp_group
        super(FlatApp, self).__init__(**kwargs)
        self.setup_themes()
        self.numpads = numpads = {}
        numpads['decimal'] = DecimalNumPad()
        numpads['regular'] = NumPad()
        if self.do_device_id:
            log_behavior = LogBehavior()
            self.log_manager = log_manager = log_behavior.log_manager
            self.settings_interface = settings_interface = DBInterface(
                construct_target_file_name('', __file__), 'settings')
            self.device_id = device_id = settings_interface.get_entry(
                'settings', 'device_id', 'value')

            self.bind(device_id=log_manager.setter('device_id'))
            if device_id is None:
                Clock.schedule_once(self.register_device_id)

    def _register_device_id(self, value, is_return):
        if is_return:
            self.device_id = value
            self.settings_interface.set_entry('settings', 'device_id', 'value',
                value)

    def register_device_id(self, dt):
        self.raise_numpad('Enter Device ID', self._register_device_id,
            auto_dismiss=False)

    def get_font(self, font_file):
        return construct_target_file_name(font_file, None)

    def raise_error(self, error_title, error_text, auto_dismiss=True, timeout=None):
        error_content = ErrorContent()
        error_popup = FlatPopup(
            content=error_content, size_hint=(.6, .4),
            auto_dismiss=auto_dismiss)
        error_content.error_text = error_text
        error_popup.title = error_title
        dismiss_button = error_content.dismiss_button
        dismiss_button.bind(on_release=error_popup.dismiss)
        error_popup.open()
        if timeout is not None:
            def close_popup(dt):
                error_popup.dismiss()
            Clock.schedule_once(close_popup, timeout)

    def raise_option_dialogue(self, option_title, option_text, options,
            callback, auto_dismiss=True):
        option_content = OptionContent(options, option_text=option_text,
            callback=callback)
        option_popup = FlatPopup(content=option_content, size_hint=(.6,.4),
            auto_dismiss=auto_dismiss)
        option_popup.title = option_title
        option_content.dismiss_func = option_popup.dismiss
        option_popup.open()

    def raise_numpad(self, numpad_title, callback, units=None,
        minimum=None, maximum=None, do_decimal=False, auto_dismiss=True):
        if do_decimal:
            numpad = self.numpads['decimal']
        else:
            numpad = self.numpads['regular']
        numpad.units = units
        numpad.minimum_value = minimum
        numpad.maximum_value = maximum
        if numpad.parent is not None:
            numpad.parent.remove_widget(numpad)
        numpad_popup = FlatPopup(
            title=numpad_title, content=numpad, size_hint=(.8, .8),
            auto_dismiss=auto_dismiss)
        def return_callback(value, is_return):
            if callback is not None:
                callback(value, is_return)
            if is_return:
                numpad_popup.dismiss(force=True)
                numpad_popup.ids.container.remove_widget(numpad)
                numpad.return_callback = None
                numpad.display_text = '0'
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
            'FlatCheckBoxListItem':{
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

    def setup_font_ramps(self):
        font_styles = {
            'Display 4': {
                'font': 'Roboto-Light.ttf',
                'sizings': {'mobile': (112, 'sp'), 'desktop': (112, 'sp')},
                'alpha': .65,
                'wrap': False,
                },
            'Display 3': {
                'font': 'Roboto-Regular.ttf',
                'sizings': {'mobile': (56, 'sp'), 'desktop': (56, 'sp')},
                'alpha': .65,
                'wrap': False,
                },
            'Display 2': {
                'font': 'Roboto-Regular.ttf',
                'sizings': {'mobile': (45, 'sp'), 'desktop': (45, 'sp')},
                'alpha': .65,
                'wrap': True,
                'wrap_id': '1',
                'leading': (48, 'pt'),
                },
            'Display 1': {
                'font': 'Roboto-Regular.ttf',
                'sizings': {'mobile': (34, 'sp'), 'desktop': (34, 'sp')},
                'alpha': .65,
                'wrap': True,
                'wrap_id': '2',
                'leading': (40, 'pt'),
                },
            'Headline': {
                'font': 'Roboto-Regular.ttf',
                'sizings': {'mobile': (24, 'sp'), 'desktop': (24, 'sp')},
                'alpha': .87,
                'wrap': True,
                'wrap_id': '3',
                'leading': (32, 'pt'),
                },
            'Title': {
                'font': 'Roboto-Medium.ttf',
                'sizings': {'mobile': (20, 'sp'), 'desktop': (20, 'sp')},
                'alpha': .87,
                'wrap': False,
                },
            'Subhead': {
                'font': 'Roboto-Regular.ttf',
                'sizings': {'mobile': (16, 'sp'), 'desktop': (15, 'sp')},
                'alpha': .87,
                'wrap': True,
                'wrap_id': '4',
                'leading': (28, 'pt'),
                },
            'Body 2': {
                'font': 'Roboto-Medium.ttf',
                'sizings': {'mobile': (14, 'sp'), 'desktop': (13, 'sp')},
                'alpha': .87,
                'wrap': True,
                'wrap_id': '5',
                'leading': (24, 'pt'),
                },
            'Body 1': {
                'font': 'Roboto-Regular.ttf',
                'sizings': {'mobile': (14, 'sp'), 'desktop': (13, 'sp')},
                'alpha': .87,
                'wrap': True,
                'wrap_id': '6',
                'leading': (20, 'pt'),
                },
            'Caption': {
                'font': 'Roboto-Regular.ttf',
                'sizings': {'mobile': (12, 'sp'), 'desktop': (12, 'sp')},
                'alpha': .65,
                'wrap': False,
                },
            'Menu': {
                'font': 'Roboto-Medium.ttf',
                'sizings': {'mobile': (14, 'sp'), 'desktop': (13, 'sp')},
                'alpha': .87,
                'wrap': False,
                },
            'Button': {
                'font': 'Roboto-Medium.ttf',
                'sizings': {'mobile': (14, 'sp'), 'desktop': (14, 'sp')},
                'alpha': .87,
                'wrap': False,
                },
            }
        for each in font_styles:
            style = font_styles[each]
            sizings = style['sizings']
            style_manager.add_style(style['font'], each, sizings['mobile'],
                sizings['desktop'], style['alpha'])

        style_manager.add_font_ramp('1', ['Display 2', 'Display 1',
            'Headline', 'Subhead', 'Body 2', 'Body 1'])


if __name__ == '__main__':
    FlatApp().run()