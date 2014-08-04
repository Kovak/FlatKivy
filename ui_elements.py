from __future__ import unicode_literals, print_function
from kivy.utils import platform
from kivy.lang import Builder
from utils import (construct_target_file_name, get_metric_conversion, 
    get_next_smallest_style, get_next_largest_style)

Builder.load_file(construct_target_file_name('ui_elements.kv', __file__))

from kivy.uix.togglebutton import ToggleButton
#from kivy.uix.checkbox import CheckBox
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import (ObjectProperty, StringProperty, OptionProperty,
    DictProperty, ListProperty, BooleanProperty, NumericProperty, VariableListProperty)
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.animation import Animation
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.app import App
from weakref import ref
from kivy.graphics import (StencilPush, StencilPop, StencilUse, StencilUnUse, 
    Rectangle, Ellipse, Color)


class GrabBehavior(object):
    last_touch = ObjectProperty(None)

    def on_touch_down(self, touch):
        if touch.is_mouse_scrolling:
            return False
        if not self.collide_point(touch.x, touch.y):
            return False
        if self in touch.ud:
            return False
        touch.grab(self)
        touch.ud[self] = True
        self.last_touch = touch
        return super(GrabBehavior, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if super(GrabBehavior, self).on_touch_move(touch):
            return True
        if touch.grab_current is self:
            return True 
        return self in touch.ud

    def on_touch_up(self, touch):
        result = super(GrabBehavior, self).on_touch_up(touch)
        touch.ungrab(self)
        self.last_touch = touch
        return result


class ButtonBehavior(object):
    '''Button behavior.

    :Events:
        `on_press`
            Fired when the button is pressed.
        `on_release`
            Fired when the button is released (i.e. the touch/click that
            pressed the button goes away).
    '''

    state = OptionProperty('normal', options=('normal', 'down'))
    '''State of the button, must be one of 'normal' or 'down'.
    The state is 'down' only when the button is currently touched/clicked,
    otherwise 'normal'.

    :attr:`state` is an :class:`~kivy.properties.OptionProperty`.
    '''


    def __init__(self, **kwargs):
        self.register_event_type(b'on_press')
        self.register_event_type(b'on_release')
        super(ButtonBehavior, self).__init__(**kwargs)

    def _do_press(self):
        self.state = 'down'

    def _do_release(self):
        self.state = 'normal'

    def on_touch_down(self, touch):
        if self in touch.ud:
            self._do_press()
            self.dispatch(b'on_press')
        return super(ButtonBehavior, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        return super(ButtonBehavior, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self in touch.ud:
            self._do_release()
            self.dispatch(b'on_release')
        return super(ButtonBehavior, self).on_touch_up(touch)

    def on_press(self):
        pass

    def on_release(self):
        pass

    def trigger_action(self, duration=0.1):
        '''Trigger whatever action(s) have been bound to the button by calling
        both the on_press and on_release callbacks.

        This simulates a quick button press without using any touch events.

        Duration is the length of the press in seconds. Pass 0 if you want
        the action to happen instantly.

        .. versionadded:: 1.8.0
        '''
        self._do_press()
        self.dispatch('on_press')

        def trigger_release(dt):
            self._do_release()
            self.dispatch('on_release')
        if not duration:
            trigger_release(0)
        else:
            Clock.schedule_once(trigger_release, duration)


class ToggleButtonBehavior(ButtonBehavior):
    '''ToggleButton behavior, see ToggleButton module documentation for more
    information.

    .. versionadded:: 1.8.0
    '''

    __groups = {}

    group = ObjectProperty(None, allownone=True)
    '''Group of the button. If None, no group will be used (button is
    independent). If specified, :attr:`group` must be a hashable object, like
    a string. Only one button in a group can be in 'down' state.

    :attr:`group` is a :class:`~kivy.properties.ObjectProperty`
    '''

    def __init__(self, **kwargs):
        self._previous_group = None
        super(ToggleButtonBehavior, self).__init__(**kwargs)

    def on_group(self, *largs):
        groups = ToggleButtonBehavior.__groups
        if self._previous_group:
            group = groups[self._previous_group]
            for item in group[:]:
                if item() is self:
                    group.remove(item)
                    break
        group = self._previous_group = self.group
        if group not in groups:
            groups[group] = []
        r = ref(self, ToggleButtonBehavior._clear_groups)
        groups[group].append(r)

    def _release_group(self, current):
        if self.group is None:
            return
        group = self.__groups[self.group]
        for item in group[:]:
            widget = item()
            if widget is None:
                group.remove(item)
            if widget is current:
                continue
            widget.state = 'normal'

    def _do_press(self):
        self._release_group(self)
        self.state = 'normal' if self.state == 'down' else 'down'

    def _do_release(self):
        pass

    @staticmethod
    def _clear_groups(wk):
        # auto flush the element when the weak reference have been deleted
        groups = ToggleButtonBehavior.__groups
        for group in list(groups.values()):
            if wk in group:
                group.remove(wk)
                break

    @staticmethod
    def get_widgets(groupname):
        '''Return the widgets contained in a specific group. If the group
        doesn't exist, an empty list will be returned.

        .. important::

            Always release the result of this method! In doubt, do::

                l = ToggleButtonBehavior.get_widgets('mygroup')
                # do your job
                del l

        .. warning::

            It's possible that some widgets that you have previously
            deleted are still in the list. Garbage collector might need
            more elements before flushing it. The return of this method
            is informative, you've been warned!
        '''
        groups = ToggleButtonBehavior.__groups
        if groupname not in groups:
            return []
        return [x() for x in groups[groupname] if x()][:]


class ThemeBehavior(object):
    theme = ListProperty([])

    def on_theme(self, instance, value):
        if value != []:
            app = App.get_running_app()
            theme = app.theme_manager.get_theme(value[0], value[1])
            types = app.theme_manager.get_theme_types()
            for each in types:
                if isinstance(self, types[each]):
                    try:
                        theme_def = theme[each]
                    except:
                        print(each, 'not in theme', value[0], value[1])
                        continue
                    for propname in theme_def:
                        setattr(self, propname, theme_def[propname])




class TouchRippleBehavior(object):
    ripple_rad = NumericProperty(10)
    ripple_pos = ListProperty([0, 0])
    ripple_color = ListProperty((1., 1., 1., 1.))
    ripple_duration_in = NumericProperty(.2)
    ripple_duration_out = NumericProperty(.5)
    fade_to_alpha = NumericProperty(.75)
    ripple_scale = NumericProperty(2.0)
    ripple_func_in = StringProperty('in_cubic')
    ripple_func_out = StringProperty('out_quad')

    def on_touch_down(self, touch):
        if self in touch.ud:
            self.anim_complete(self, self)
            self.ripple_pos = ripple_pos = (touch.x, touch.y)
            Animation.cancel_all(self, 'ripple_rad', 'ripple_color')
            rc = self.ripple_color
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
        return super(TouchRippleBehavior, self).on_touch_down(touch)

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
        if self in touch.ud:
            Animation.cancel_all(self, 'ripple_rad', 'ripple_color')
            rc = self.ripple_color
            anim = Animation(ripple_color=[rc[0], rc[1], rc[2], 0.], 
                t=self.ripple_func_out, duration=self.ripple_duration_out)
            anim.bind(on_complete=self.anim_complete)
            anim.start(self)
        return super(TouchRippleBehavior, self).on_touch_up(touch)

    def anim_complete(self, anim, instance):
        self.ripple_rad = 10
        self.canvas.after.clear()

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


class FlatTextInput(GrabBehavior, TouchRippleBehavior, TextInput):
    ripple_color_tuple = ListProperty(['Grey', '0000'])

    def on_touch_down(self, touch):
        TextInput.on_touch_down(self, touch)
        super(FlatTextInput, self).on_touch_down(touch)



class FlatPopup(Popup):
    popup_color = ListProperty([1., 1., 1., 1.])


class FlatScrollView(ScrollView):

    def scroll_to_top(self):
        self.scroll_y = 1.0

class FlatButton(GrabBehavior, TouchRippleBehavior, 
    ThemeBehavior, ButtonBehavior, AnchorLayout):
    color = ListProperty([1., 1., 1.])
    color_down = ListProperty([.7, .7, .7])
    text = StringProperty('')
    style = StringProperty(None, allownone=True)
    color_tuple = ListProperty(['Blue', '500'])
    font_color_tuple = ListProperty(['Grey', '1000'])
    ripple_color_tuple = ListProperty(['Grey', '0000'])
    font_size = NumericProperty(12)
    
    def on_color(self, instance, value):
        self.color_down = [x*.7 for x in value]

    
class FlatIconButton(GrabBehavior, ButtonBehavior, TouchRippleBehavior, 
    ThemeBehavior, AnchorLayout):
    color = ListProperty([1., 1., 1.])
    color_down = ListProperty([.7, .7, .7])
    text = StringProperty('')
    icon = StringProperty('')
    style = StringProperty(None, allownone=True)
    font_size = NumericProperty(12)
    icon_color_tuple = ListProperty(['Grey', '1000'])
    color_tuple = ListProperty(['Blue', '500'])
    font_color_tuple = ListProperty(['Grey', '1000'])
    ripple_color_tuple = ListProperty(['Grey', '0000'])
    content_padding = VariableListProperty([0., 0., 0., 0.])
    content_spacing = VariableListProperty([0., 0.], length=2)

    def on_color(self, instance, value):
        self.color_down = [x*.7 for x in value]


class FlatIconButtonLeft(FlatIconButton):
    pass


class FlatLabel(ThemeBehavior, Label):
    text = StringProperty(None, allownone=True)
    color_tuple = ListProperty(['Grey', '0000'])
    style = StringProperty(None, allownone=True)
    style_dict = DictProperty(None, allownone=True)
    do_resize = BooleanProperty(True)

    def on_style_dict(self, instance, value):
        if value != {}:
            self.font_name = construct_target_file_name(
                'data/font/' + value['font'], __file__)
            self.font_size = font_size = get_metric_conversion(
                value['sizings']['mobile'])
            self.color[3] = value['alpha']
            self.shorten = not value['wrap']

    def on_texture(self, instance, value):
        if value is not None and not self.shorten and self.style is not None and self.do_resize:
            self.calculate_fit()

    def on_size(self, instance, value):
        if not self.shorten and self.style is not None and self.do_resize:
            self.calculate_fit()

    def calculate_fit(self):
        actual_size = self._label._internal_size
        size = self.size
        style = self.style
        if actual_size[0] > size[0] or actual_size[1] > size[1]:
            self.style = None
            self.style = get_next_smallest_style(style)
        elif actual_size[0] < size[0]*.5 and actual_size[1] < size[1] *.5:
            self.style = None
            self.style = get_next_largest_style(style)



class FlatIcon(FlatLabel):
    color_tuple = ListProperty(['Grey', '0000'])
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


class FlatToggleButton(GrabBehavior, ToggleButtonBehavior, 
    TouchRippleBehavior, ThemeBehavior, AnchorLayout):
    color = ListProperty([1., 1., 1.])
    color_down = ListProperty([.7, .7, .7])
    text = StringProperty('')
    color_tuple = ListProperty(['Blue', '500'])
    font_color_tuple = ListProperty(['Grey', '1000'])
    ripple_color_tuple = ListProperty(['Grey', '0000'])
    no_up = BooleanProperty(False)
    style = StringProperty(None, allownone=True)

    def on_color(self, instance, value):
        self.color_down = [x*.7 for x in value]

    def on_touch_down(self, touch):
        if self.no_up:
            if self.collide_point(touch.x, touch.y) and self.state == 'normal':
                super(FlatToggleButton, self).on_touch_down(touch)
        else:
            super(FlatToggleButton, self).on_touch_down(touch)

class FlatCheckBox(GrabBehavior, TouchRippleBehavior, ThemeBehavior, CheckBox):
    check = ObjectProperty(None)
    no_interact = BooleanProperty(False)
    check_scale = NumericProperty(.5)
    outline_size = NumericProperty(5)
    color_tuple = ListProperty(['Grey', '0000'])
    check_color_tuple = ListProperty(['Grey', '1000'])
    outline_color_tuple = ListProperty(['Grey', '1000'])
    ripple_color_tuple = ListProperty(['Grey', '0000'])

    def __init__(self, **kwargs):
        super(FlatCheckBox, self).__init__(**kwargs)
        self.check = check = Check(scale=self.check_scale, 
            color_tuple=self.check_color_tuple)
        self.bind(pos=check.setter('pos'), size=check.setter('size'),
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


class TextInputFocus(StackLayout):
    close_callback = ObjectProperty(None)
    text = StringProperty(None, allownone=True)
    

class CheckBoxListItem(GrabBehavior, TouchRippleBehavior, 
    ThemeBehavior, BoxLayout):
    text = StringProperty(None)
    group = StringProperty(None)
    outline_size = NumericProperty(5)
    style = StringProperty(None, allownone=True)
    check_scale = NumericProperty(.7)
    font_color_tuple = ListProperty(['Grey', '1000'])
    color_tuple = ListProperty(['Blue', '500'])
    check_color_tuple = ListProperty(['Grey', '1000'])
    checkbox_color_tuple = ListProperty(['Grey', '0000'])
    outline_color_tuple = ListProperty(['Grey', '1000'])
    ripple_color_tuple = ListProperty(['Grey', '0000'])
    font_color_tuple = ListProperty(['Grey', '1000'])

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.toggle_checkbox()
        super(CheckBoxListItem, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        super(CheckBoxListItem, self).on_touch_up(touch)

    def toggle_checkbox(self):
        self.ids.checkbox._toggle_active()