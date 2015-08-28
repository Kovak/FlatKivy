
from kivy.uix.gridlayout import GridLayout
from kivy.properties import (ListProperty, DictProperty, StringProperty,
                             ObjectProperty, NumericProperty)
from kivy.lang import Builder

from flat_kivy.utils import construct_data_resource


Builder.load_file(
    construct_data_resource('ui_elements.kv'))


class ErrorContent(GridLayout):
    error_text = StringProperty('Default Error Text')


class OptionContent(GridLayout):
    option_text = StringProperty('Default Option Text')
    options_dict = DictProperty(None)
    callback = ObjectProperty(None)
    dismiss_func = ObjectProperty(None)

    def __init__(self, options_dict, **kwargs):
        super(OptionContent, self).__init__(**kwargs)
        self.options_dict = options_dict
        self.populate_options(options_dict)

    def populate_options(self, options_dict):
        rem_wid = self.remove_widget
        add_wid = self.add_widget
        for child in self.children:
            if isinstance(child, OptionButton):
                rem_wid(child)
        for key in options_dict:
            button = OptionButton(key=key, text=options_dict[key],
                                  on_release=self.option_callback)
            add_wid(button)

    def option_callback(self, instance):
        callback = self.callback
        if callback is not None:
            self.callback(instance.key)
        self.dismiss_func()


# Fake a number of modules that have a small amount of code.

import sys

from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from flat_kivy.uix.behaviors import GrabBehavior, LogNoTouchBehavior


class FlatPopup(Popup):
    popup_color = ListProperty([1., 1., 1., 1.])
    title_color_tuple = ListProperty(['Gray', '0000'])


class FlatScreen(GrabBehavior, LogNoTouchBehavior, Screen):

    def on_enter(self, *args):
        super(FlatScreen, self).on_enter(*args)
        print('in enter screen')
        log_manager = self.log_manager
        if log_manager.do_screen_logging:
            print('logging screen')
            log_manager.log_interface.set_entry('events', 'screen_events',
                'enter', self.name, do_history=True)

    def on_leave(self, *args):
        super(FlatScreen, self).on_leave(*args)
        log_manager = self.log_manager
        if log_manager.do_screen_logging:
            log_manager.log_interface.set_entry('events', 'screen_events',
                'exit', self.name, do_history=True)


class FlatScrollView(ScrollView):

    def scroll_to_top(self):
        self.scroll_y = 1.0


class flatpopup(object):
    FlatPopup = FlatPopup


class flatscreemanager(object):
    FlatScreen = FlatScreen


class flatscrollview(object):
    FlatScrollView = FlatScrollView


sys.modules['flat_kivy.uix.flatpopup'] = flatpopup
sys.modules['flat_kivy.uix.flatscreemanager'] = flatscreemanager
sys.modules['flat_kivy.uix.flatscrollview'] = flatscrollview
