from __future__ import unicode_literals, print_function
from kivy.uix.widget import Widget
from kivy.properties import (StringProperty, 
    NumericProperty, ObjectProperty)
from kivy.lang import Builder

from utils import construct_target_file_name

Builder.load_file(construct_target_file_name('numpad.kv', __file__))


class NumPad(Widget):
    display_text = StringProperty("0")
    display_value = NumericProperty(0)
    init_value = NumericProperty(100)
    maximum_value = NumericProperty(None, allownone=True)
    minimum_value = NumericProperty(None, allownone=True)
    return_callback = ObjectProperty(None, allownone=True)
    units = StringProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super(NumPad, self).__init__(**kwargs)

    def check_minimum_value(self):
        if self.minimum_value != None:
            if self.display_value < self.minimum_value:
                self.display_text = str(self.minimum_value)

    def button_callback(self, button_str):
        if button_str in [str(x) for x in range(10)]:
            if self.display_text == '0':
                self.display_text = button_str 
            else:
                self.display_text = self.display_text + button_str
            maximum_value = self.maximum_value
            if maximum_value != None:
                if self.display_value > maximum_value: 
                    self.display_value = maximum_value
        elif button_str == 'del':
            self.display_text = self.display_text[:-1]
        elif button_str == 'ret':
            self.check_minimum_value()
            self.return_callback(self.display_value, True)

    def on_display_text(self, instance, value):
        if value == '':
            self.display_text = '0'
            return
        if int(value) > self.maximum_value and self.maximum_value != None:
            self.display_text = str(self.maximum_value)
            return
        self.display_value = int(value)
        if self.return_callback is not None:
            self.return_callback(self.display_value, False)


class DecimalNumPad(NumPad):

    def button_callback(self, button_str):
        if button_str in [str(x) for x in range(10)] or button_str == '.' and \
            '.' not in self.display_text:
            if self.display_text == '0':
                self.display_text = button_str 
            else:
                self.display_text = self.display_text + button_str
            maximum_value = self.maximum_value
            if maximum_value != None:
                if self.display_value > maximum_value: 
                    self.display_value = maximum_value
        elif button_str == 'del':
            self.display_text = self.display_text[:-1]
        elif button_str == 'ret':
            self.check_minimum_value()
            self.return_callback(self.display_value, True)

    def on_display_text(self, instance, value):
        if value == '':
            self.display_text = '0'
            return
        if value == '.':
            self.display_text = '0.'
            return
        if float(value) > self.maximum_value and self.maximum_value != None:
            self.display_text = str(self.maximum_value)
            return
        self.display_value = float(value)
        if self.return_callback is not None:
            self.return_callback(self.display_value, False)
