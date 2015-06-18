
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (BooleanProperty, ListProperty, StringProperty,
                             NumericProperty, ObjectProperty)

from flat_kivy.uix.behaviors import (ToggleButtonBehavior, GrabBehavior,
                                     ThemeBehavior, TouchRippleBehavior,
                                     LogBehavior)
from flat_kivy.uix.flaticon import FlatIcon


class Check(FlatIcon):
    scale = NumericProperty(1.0)


class CheckBox(ToggleButtonBehavior, Widget):
    '''CheckBox class, see module documentation for more information.
    '''

    active = BooleanProperty(False)
    '''Indicates if the switch is active or inactive.

    :attr:`active` is a :class:`~kivy.properties.BooleanProperty` and defaults
    to False.
    '''

    def __init__(self, **kwargs):
        self._previous_group = None
        super(CheckBox, self).__init__(**kwargs)

    def on_state(self, instance, value):
        if value == 'down':
            self.active = True
        else:
            self.active = False

    def _toggle_active(self):
        self._do_press()


class FlatCheckBox(GrabBehavior, TouchRippleBehavior,
                   LogBehavior, ThemeBehavior, CheckBox):
    check = ObjectProperty(None)
    no_interact = BooleanProperty(False)
    check_scale = NumericProperty(.5)
    outline_size = NumericProperty(5)
    color_tuple = ListProperty(['Grey', '0000'])
    check_color_tuple = ListProperty(['Grey', '1000'])
    outline_color_tuple = ListProperty(['Grey', '1000'])
    ripple_color_tuple = ListProperty(['Grey', '1000'])

    def __init__(self, **kwargs):
        super(FlatCheckBox, self).__init__(**kwargs)
        self.check = check = Check(scale=self.check_scale,
                                   color_tuple=self.check_color_tuple)
        self.bind(pos=check.setter('pos'),
                  size=check.setter('size'),
                  check_scale=check.setter('scale'),
                  check_color_tuple=check.setter('color_tuple'))

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


class FlatCheckBoxListItem(GrabBehavior, TouchRippleBehavior,
                           ThemeBehavior, BoxLayout):
    text = StringProperty(None)
    group = StringProperty(None)
    outline_size = NumericProperty(5)
    style = StringProperty(None, allownone=True)
    check_scale = NumericProperty(.7)
    font_color_tuple = ListProperty(['Grey', '1000'])
    color_tuple = ListProperty(['Grey', '500'])
    check_color_tuple = ListProperty(['Grey', '1000'])
    checkbox_color_tuple = ListProperty(['Grey', '0000'])
    outline_color_tuple = ListProperty(['Grey', '1000'])
    ripple_color_tuple = ListProperty(['Grey', '1000'])
    font_ramp_tuple = ListProperty(['default', '1'])
    halign = StringProperty('left')
    valign = StringProperty('bottom')
    alpha = NumericProperty(None, allownone=True)

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.toggle_checkbox()
        super(FlatCheckBoxListItem, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        super(FlatCheckBoxListItem, self).on_touch_up(touch)

    def toggle_checkbox(self):
        self.ids.checkbox._toggle_active()
