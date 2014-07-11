from __future__ import unicode_literals, print_function
from kivy.utils import platform
from kivy.lang import Builder
from utils import construct_target_file_name

Builder.load_file(construct_target_file_name('ui_elements.kv', __file__))

from kivy.uix.togglebutton import ToggleButton
from kivy.uix.checkbox import CheckBox
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import (ObjectProperty, StringProperty, 
    DictProperty, ListProperty, BooleanProperty, NumericProperty)
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.anchorlayout import AnchorLayout
from kivy.animation import Animation
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup


class FlatPopup(Popup):
    popup_color = ListProperty([1., 1., 1., 1.])


class FlatScrollView(ScrollView):

    def scroll_to_top(self):
        self.scroll_y = 1.0

class FlatButton(ButtonBehavior, AnchorLayout):
    color = ListProperty([1., 1., 1.])
    color_down = ListProperty([.7, .7, .7])
    text = StringProperty('')
    color_name = StringProperty('default')
    font_color_name = StringProperty('font_default')
    touch_rad = NumericProperty(10)
    touch_pos = ListProperty([0, 0])
    touch_color = ListProperty((1., 0., 0., 1.))

    def on_color(self, instance, value):
        self.color_down = [x*.7 for x in value]

    def on_touch_down(self, touch):
        super(FlatButton, self).on_touch_down(touch)
        if self.collide_point(touch.x, touch.y):
            self.touch_pos = (touch.x, touch.y)
            Animation.cancel_all(self)
            tc = self.touch_color
            self.touch_color = [tc[0], tc[1], tc[2], 1.]
            anim = Animation(touch_rad=self.width*2, t='in_cubic',
                touch_color=[tc[0], tc[1], tc[2], .75], duration=.3)
            anim.start(self)

    def on_touch_up(self, touch):
        super(FlatButton, self).on_touch_up(touch)
        Animation.cancel_all(self)
        tc = self.touch_color
        anim = Animation(touch_color=[tc[0], tc[1], tc[2], 0.], 
            t='out_quad', duration=.3)
        anim.bind(on_complete=self.anim_complete)
        anim.start(self)

    def anim_complete(self, anim, instance):
        self.touch_rad = 10
        




class FlatIconButton(ButtonBehavior, AnchorLayout):
    color = ListProperty([1., 1., 1.])
    color_down = ListProperty([.7, .7, .7])
    text = StringProperty('')
    icon = StringProperty('')
    color_name = StringProperty('default')
    icon_color_name = StringProperty('font_default')
    font_color_name = StringProperty('font_default')

    def on_color(self, instance, value):
        self.color_down = [x*.7 for x in value]

class FlatLabel(Label):
    text = StringProperty(None, allownone=True)
    color_name = StringProperty('font_default')

class FlatIcon(FlatLabel):
    color_name = StringProperty('default')
    icon = StringProperty('')

class Check(FlatIcon):
    scale = NumericProperty(1.0)


class OptionButton(ToggleButton):
    key = StringProperty(None)


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


class FlatToggleButton(ToggleButtonBehavior, AnchorLayout):
    color = ListProperty([1., 1., 1.])
    color_down = ListProperty([.7, .7, .7])
    text = StringProperty('')
    color_name = StringProperty('default')
    font_color_name = StringProperty('font_default')
    no_up = BooleanProperty(False)

    def on_color(self, instance, value):
        self.color_down = [x*.7 for x in value]

    def on_touch_down(self, touch):
        if self.no_up:
            if self.collide_point(touch.x, touch.y) and self.state == 'normal':
                super(FlatToggleButton, self).on_touch_down(touch)
        else:
            super(FlatToggleButton, self).on_touch_down(touch)

class FlatCheckBox(CheckBox):
    check = ObjectProperty(None)
    no_interact = BooleanProperty(False)
    check_scale = NumericProperty(.5)
    outline_color_name = StringProperty('black')
    color_name = StringProperty('white')
    outline_size = NumericProperty(5)
    check_color_name = StringProperty('default')

    def __init__(self, **kwargs):
        super(FlatCheckBox, self).__init__(**kwargs)
        self.check = check = Check(scale=self.check_scale, 
            color_name=self.check_color_name)
        self.bind(pos=check.setter('pos'), size=check.setter('size'),
            check_scale=check.setter('scale'), check_color_name=check.setter('color_name'))

    def on_active(self, instance, value):
        check = self.check
        if value and check not in self.children:
            self.add_widget(check)
        elif not value and check in self.children:
            self.remove_widget(check)

    def on_touch_down(self, touch):
        if self.no_interact:
            if self.collide_point(touch.x, touch.y):
                return False
        else:
            super(FlatCheckBox, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.no_interact:
            if self.collide_point(touch.x, touch.y):
                return False
        else:
            super(FlatCheckBox, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.no_interact:
            if self.collide_point(touch.x, touch.y):
                return False
        else:
            super(FlatCheckBox, self).on_touch_up(touch)


class TextInputFocus(StackLayout):
    close_callback = ObjectProperty(None)
    text = StringProperty(None, allownone=True)
    outline_color_name = StringProperty('black')
    outline_size = NumericProperty(5)
    check_color_name = StringProperty('default')
    checkbox_color_name = StringProperty('white')


class CheckBoxListItem(BoxLayout):
    answer_text = StringProperty(None)
    group = StringProperty(None)

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            checkbox = self.ids.checkbox
            checkbox._toggle_active()

    def toggle_checkbox(self):
        self.ids.checkbox._toggle_active()