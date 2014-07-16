from __future__ import unicode_literals, print_function
from kivy.utils import platform
from kivy.lang import Builder
from utils import (construct_target_file_name, get_metric_conversion, 
    get_next_smallest_style)

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
from kivy.uix.textinput import TextInput

from kivy.graphics import (StencilPush, StencilPop, StencilUse, StencilUnUse, 
    Rectangle, Ellipse, Color)



class TouchRippleBehavior(object):
    ripple_rad = NumericProperty(10)
    ripple_pos = ListProperty([0, 0])
    ripple_color = ListProperty((1., 1., 1., 1.))
    ripple_duration_in = NumericProperty(.4)
    ripple_duration_out = NumericProperty(.5)
    fade_to_alpha = NumericProperty(.75)
    ripple_scale = NumericProperty(2.0)
    ripple_func_in = StringProperty('in_cubic')
    ripple_func_out = StringProperty('out_quad')

    def on_touch_down(self, touch):
        super(TouchRippleBehavior, self).on_touch_down(touch)
        if self.collide_point(touch.x, touch.y):
            self.anim_complete(self, self)
            self.ripple_pos = ripple_pos = (touch.x, touch.y)
            Animation.cancel_all(self, 'ripple_rad', 'ripple_color')
            rc = self.ripple_color

            touch.grab(self)
            ripple_rad = self.ripple_rad
            self.ripple_color = [rc[0], rc[1], rc[2], 1.]
            anim = Animation(
                ripple_rad=max(self.width, self.height) * self.ripple_scale, 
                t=self.ripple_func_in,
                ripple_color=[rc[0], rc[1], rc[2], self.fade_to_alpha], 
                duration=self.ripple_duration_in)
            anim.start(self)
            with self.canvas.after:
                StencilPush()
                Rectangle(size=self.size, pos=self.pos)
                StencilUse()
                self.col_instruction = Color(rgba=self.ripple_color)
                self.ellipse = Ellipse(size=(ripple_rad, ripple_rad),
                    pos=(ripple_pos[0] - ripple_rad/2., 
                    ripple_pos[1] - ripple_rad/2.))
                StencilUnUse()
                StencilPop()
            self.bind(ripple_color=self.set_color, ripple_pos=self.set_ellipse,
                ripple_rad=self.set_ellipse)

    def set_ellipse(self, instance, value):
        ellipse = self.ellipse
        ripple_pos = self.ripple_pos
        ripple_rad = self.ripple_rad
        ellipse.size = (ripple_rad, ripple_rad)
        ellipse.pos = (ripple_pos[0] - ripple_rad/2., 
            ripple_pos[1] - ripple_rad/2.)

    def set_color(self, instance, value):
        self.col_instruction.rgba = value

    def on_touch_up(self, touch):
        super(TouchRippleBehavior, self).on_touch_up(touch)
        if touch.grab_current is self:
            Animation.cancel_all(self, 'ripple_rad', 'ripple_color')
            rc = self.ripple_color
            anim = Animation(ripple_color=[rc[0], rc[1], rc[2], 0.], 
                t=self.ripple_func_out, duration=self.ripple_duration_out)
            anim.bind(on_complete=self.anim_complete)
            anim.start(self)
            touch.ungrab(self)

    def anim_complete(self, anim, instance):
        self.ripple_rad = 10
        self.canvas.after.clear()


class FlatTextInput(TouchRippleBehavior, TextInput):
    ripple_color_name = StringProperty('default_ripple')

    def on_touch_down(self, touch):
        TextInput.on_touch_down(self, touch)
        super(FlatTextInput, self).on_touch_down(touch)



class FlatPopup(Popup):
    popup_color = ListProperty([1., 1., 1., 1.])


class FlatScrollView(ScrollView):

    def scroll_to_top(self):
        self.scroll_y = 1.0

class FlatButton(ButtonBehavior,TouchRippleBehavior,  AnchorLayout):
    color = ListProperty([1., 1., 1.])
    color_down = ListProperty([.7, .7, .7])
    text = StringProperty('')
    style = StringProperty(None, allownone=True)
    color_name = StringProperty('default')
    font_color_name = StringProperty('font_default')
    ripple_color_name = StringProperty('default_ripple')
    font_size = NumericProperty(12)
    
    def on_color(self, instance, value):
        self.color_down = [x*.7 for x in value]

    
class FlatIconButton(ButtonBehavior, TouchRippleBehavior, AnchorLayout):
    color = ListProperty([1., 1., 1.])
    color_down = ListProperty([.7, .7, .7])
    text = StringProperty('')
    icon = StringProperty('')
    style = StringProperty(None, allownone=True)
    color_name = StringProperty('default')
    font_size = NumericProperty(12)
    icon_color_name = StringProperty('font_default')
    font_color_name = StringProperty('font_default')
    ripple_color_name = StringProperty('default_ripple')

    def on_color(self, instance, value):
        self.color_down = [x*.7 for x in value]


class FlatLabel(Label):
    text = StringProperty(None, allownone=True)
    color_name = StringProperty('font_default')
    style = StringProperty(None, allownone=True)
    style_dict = DictProperty(None, allownone=True)

    def on_style_dict(self, instance, value):
        if value is not None:
            self.font_name = 'data/font/' + value['font']
            self.font_size = font_size = get_metric_conversion(
                value['sizings']['mobile'])
            self.color[3] = value['alpha']
            self.shorten = not value['wrap']

    def on_texture(self, instance, value):
        if value is not None and not self.shorten and self.style is not None:
            self.calculate_fit()

    def calculate_fit(self):
        actual_size = self._label._internal_size
        size = self.size
        if actual_size[0] > size[0] or actual_size[1] > size[1]:
            self.style = get_next_smallest_style(self.style)

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


class FlatToggleButton(ToggleButtonBehavior, 
    TouchRippleBehavior, AnchorLayout):
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

class FlatCheckBox(TouchRippleBehavior, CheckBox):
    check = ObjectProperty(None)
    no_interact = BooleanProperty(False)
    check_scale = NumericProperty(.5)
    outline_color_name = StringProperty('black')
    color_name = StringProperty('white')
    outline_size = NumericProperty(5)
    check_color_name = StringProperty('default')
    ripple_color_name = StringProperty('default_ripple')

    def __init__(self, **kwargs):
        super(FlatCheckBox, self).__init__(**kwargs)
        self.check = check = Check(scale=self.check_scale, 
            color_name=self.check_color_name)
        self.bind(pos=check.setter('pos'), size=check.setter('size'),
            check_scale=check.setter('scale'), 
            check_color_name=check.setter('color_name'))

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
    

class CheckBoxListItem(TouchRippleBehavior, BoxLayout):
    text = StringProperty(None)
    group = StringProperty(None)
    outline_color_name = StringProperty('black')
    outline_size = NumericProperty(5)
    check_color_name = StringProperty('default')
    checkbox_color_name = StringProperty('white')
    text_color_name = StringProperty('black')
    ripple_color_name = StringProperty('default_ripple')

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.toggle_checkbox()
        super(CheckBoxListItem, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        super(CheckBoxListItem, self).on_touch_up(touch)

    def toggle_checkbox(self):
        self.ids.checkbox._toggle_active()