from __future__ import unicode_literals, print_function
__version__ = '0.0.1'
import kivy
from kivy.app import App
from kivy.properties import (ObjectProperty, ListProperty)
from kivy.uix.widget import Widget
from kivy.graphics import Fbo, Rectangle, Color, RenderContext, ClearColor, ClearBuffers
from numpad import DecimalNumPad, NumPad
from ui_elements import FlatPopup as Popup
from ui_elements import ErrorContent, OptionContent, FlatIconButton, FlatLabel
from utils import get_icon_char, get_rgba_color
from kivy.base import EventLoop
from kivy.uix.effectwidget import EffectWidget, HorizontalBlurEffect, VerticalBlurEffect


def color_default(color_name):
    return (1., 1., 1., 1.)

def icon_default(icon_name):
    return ''

class MyEffectWidget(EffectWidget):
    background_color = ListProperty((1., 1., 1., 1.))

class DropShadowContainer(Widget):
    texture = ObjectProperty(None)
    
    def __init__(self, **kwargs):

        super(DropShadowContainer, self).__init__(**kwargs)
        self.shadow_widget = shadow = Widget(size=self.size, pos=self.pos)
        self.effect_widget = effect_widget = MyEffectWidget(size=self.size, pos=self.pos)
        effect_widget.effects = [HorizontalBlurEffect(size=6.), VerticalBlurEffect(size=6.)]
        with shadow.canvas:
            self.fbo = Fbo(size=self.size, )
            Color(0., 0., 0., .75)
            self.rect = Rectangle(size=self.size, pos=self.pos, texture=self.fbo.texture)
        effect_widget.reg_flag = True
        effect_widget.add_widget(shadow)
        self.add_widget(effect_widget)
        self.content = content = Widget(size=self.size, pos=self.pos)
        content.reg_flag = True
        self.add_widget(content)
        self.bind(size=self.update_fbo, pos=self.update_fbo)
        

    def update_fbo(self, *args):
        self.fbo.size = self.size
        self.content.size = self.size
        self.content.pos = self.pos
        self.effect_widget.pos = self.pos
        self.effect_widget.size = self.size
        self.shadow_widget.size = self.size
        self.shadow_widget.pos = self.pos
        self.rect.size = self.size
        self.rect.pos = self.pos[0] + 5, self.pos[1] - 5
        self.rect.texture = self.fbo.texture
        print(self.rect.size, self.rect.pos)
        print(self.shadow_widget.pos, self.shadow_widget.size)


    def add_widget(self, widget, index=0):
        # Add the widget to our Fbo instead of the normal canvas
        print(self.children)
        if hasattr(widget, 'reg_flag') and widget.reg_flag:
            super(DropShadowContainer, self).add_widget(widget)
        else:
            c = self.canvas
            self.canvas = self.content.canvas
            super(DropShadowContainer, self).add_widget(widget)
            self.canvas = self.fbo
            if index == 0 or len(self.children) == 0:
                self.canvas.add(widget.canvas)
            else:
                canvas = self.canvas
                children = self.children
                if index >= len(children):
                    index = len(children)
                    next_index = 0
                else:
                    next_child = children[index]
                    next_index = canvas.indexof(next_child.canvas)
                    if next_index == -1:
                        next_index = canvas.length()
                    else:
                        next_index += 1
                # we never want to insert widget _before_ canvas.before.
                if next_index == 0 and canvas.has_before:
                    next_index = 1
                canvas.insert(next_index, widget.canvas)
            print(widget.canvas.has_before, widget.canvas.has_after)
            self.canvas.remove(widget.canvas.after)
            self.canvas = c

    def remove_widget(self, widget):
        # Remove the widget from our Fbo instead of the normal canvas
        c = self.canvas
        self.canvas = self.content.canvas
        super(DropShadowContainer, self).remove_widget(widget)
        self.canvas = self.fbo
        self.canvas.remove(widget.canvas)
        self.canvas = c





class FlatApp(App):
    get_color = ObjectProperty(color_default)
    get_icon = ObjectProperty(icon_default)

    def build(self):
        self.get_color = get_rgba_color
        self.get_icon = get_icon_char
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
        print(do_decimal)
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