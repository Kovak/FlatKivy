

from __future__ import unicode_literals, print_function
from weakref import ref


from kivy.lang import Builder
from utils import construct_target_file_name, get_metric_conversion

Builder.load_file(construct_target_file_name('ui_elements.kv', __file__))

from kivy.uix.togglebutton import ToggleButton
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import (ObjectProperty, StringProperty, OptionProperty,
    DictProperty, ListProperty, BooleanProperty, NumericProperty, 
    VariableListProperty)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.animation import Animation
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.graphics import Ellipse, Color

try:
    from kivy.graphics import (ScissorPush, ScissorPop)
except ImportError:
    _has_scissor_instr = False
    from kivy.graphics import (StencilPush, StencilPop, StencilUse,
                               StencilUnUse, Color, Rectangle)
else:
    _has_scissor_instr = True

from kivy.event import EventDispatcher
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.app import App

from dbinterface import DBInterface


class GrabBehavior(object):
    last_touch = ObjectProperty(None)

    def on_touch_down(self, touch):
        if touch.is_mouse_scrolling:
            return False
        if self.disabled:
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
        if touch.grab_current is self:
            result = super(GrabBehavior, self).on_touch_up(touch)
            touch.ungrab(self)
            self.last_touch = touch
            return result


class LogManager(EventDispatcher):
    device_id = NumericProperty(None)
    do_logging = BooleanProperty(False)
    do_label_logging = BooleanProperty(False)
    do_image_logging = BooleanProperty(False)
    do_screen_logging = BooleanProperty(False)
    touch_id = NumericProperty(0)
    hour = NumericProperty(None)
    log_path = StringProperty('default_log_dir')

    def __init__(self, log_path, **kwargs):
        super(LogManager, self).__init__(**kwargs)
        self.log_path = log_path
        self.log_interface = log_interface = DBInterface(
            log_path, 'log', do_date=True, do_hour=True)
        touch_id = log_interface.get_entry('touches', 'last_touch_id', 'value')
        if touch_id is None:
            touch_id = 0
        self.touch_id = touch_id

    def on_device_id(self, instance, value):
        print('in on device id', value)


class LogNoTouchBehavior(object):
    log_manager = LogManager(
        construct_target_file_name('data/logs/', __file__))


class LogBehavior(object):
    log_manager = LogManager(
        construct_target_file_name('data/logs/', __file__))

    def on_touch_down(self, touch):
        log_manager = self.log_manager
        if self in touch.ud and log_manager.do_logging:
            print(self, 'in on touch dwon')
            coords = (touch.x, touch.y)
            log_interface = log_manager.log_interface
            touch_id = log_manager.touch_id
            touch.ud['log_id'] = touch_id
            log_interface.set_entry(
                'touches', touch_id, 'touch_down_at', coords, 
                do_timestamp=True)
            log_manager.touch_id += 1
            log_interface.set_entry(
                'touches', 'last_touch_id', 'value', touch_id)
        return super(LogBehavior, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        log_manager = self.log_manager
        if self in touch.ud and log_manager.do_logging:
            coords = (touch.x, touch.y)
            touch_id = touch.ud['log_id']
            log_manager.log_interface.append_entry('touches', touch_id, 
                'touch_moves_at', coords, do_timestamp=True)
        return super(LogBehavior, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        log_manager = self.log_manager
        if self in touch.ud and log_manager.do_logging:
            coords = (touch.x, touch.y)
            touch_id = touch.ud['log_id']
            log_manager.log_interface.set_entry(
                'touches', touch_id, 'touch_up_at', coords, do_timestamp=True)
        return super(LogBehavior, self).on_touch_up(touch)


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

    pressed_time = NumericProperty(0.085)
    '''The minimum amount of time (in seconds) the button will be in the down
    state. On faster machines, the button can be pressed and released so
    quickly that the user cannot see the button in the down state. Set this
    parameter to non-zero to delay the release to provide better feedback.

    :attr:`state` is an :class:`~kivy.properties.NumericProperty`.
    '''

    def __init__(self, **kwargs):
        self.register_event_type(b'on_press')
        self.register_event_type(b'on_release')
        super(ButtonBehavior, self).__init__(**kwargs)
        self._pressed_at_time = 0

    def _do_press(self):
        self.state = 'down'
        self._pressed_at_time = Clock.time()
        self.dispatch(b'on_press')

    def _do_release(self):
        # If the button has not been pressed for pressed_time seconds,
        # instead of releasing it right away schedule the release.
        delta = Clock.time() - self._pressed_at_time

        if delta > self.pressed_time:
            self._do_release_actual()
        else:
            Clock.schedule_once(self._do_release_actual,
                                self.pressed_time - delta)

    def _do_release_actual(self, *ar):
        self.state = 'normal'
        self.dispatch(b'on_release')

    def on_touch_down(self, touch):
        if self in touch.ud:
            if isinstance(self, LogBehavior):
                log_manager = self.log_manager
                if log_manager.do_logging:
                    if isinstance(self, CheckBox):
                        touch_id = touch.ud['log_id']
                        log_manager.log_interface.set_entry(
                            'touches', touch_id, 
                            'checkbox_pressed_down', self.state, 
                            do_timestamp=True)
                    else:
                        touch_id = touch.ud['log_id']
                        log_manager.log_interface.set_entry(
                            'touches', touch_id, 
                            'button_pressed', self.text, do_timestamp=True)
            self._do_press()
        return super(ButtonBehavior, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        return super(ButtonBehavior, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self in touch.ud:  
            if isinstance(self, LogBehavior):
                log_manager = self.log_manager
                if log_manager.do_logging:
                    if isinstance(self, CheckBox):
                        touch_id = touch.ud['log_id']
                        log_manager.log_interface.set_entry(
                            'touches', touch_id, 
                            'checkbox_released', self.state, 
                            do_timestamp=True)
                    else:
                        touch_id = touch.ud['log_id']
                        log_manager.log_interface.set_entry(
                            'touches', touch_id, 'button_released', 
                            self.text, do_timestamp=True)
            self._do_release()
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

        def trigger_release(self, dt):
            saved_pressed_time = self.pressed_time
            self.pressed_time = 0.0
            self._do_release()
            self.pressed_time = saved_pressed_time

        if not duration:
            trigger_release(0)
        else:
            Clock.schedule_once(self.trigger_release, duration)


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
    ripple_color = ListProperty((0., 0., 0., 1.))
    ripple_duration_in = NumericProperty(.7)
    ripple_duration_out = NumericProperty(.3)
    fade_to_alpha = NumericProperty(.12)
    ripple_scale = NumericProperty(4.0)
    ripple_func_in = StringProperty('in_cubic')
    ripple_func_out = StringProperty('out_quad')

    def on_touch_down(self, touch):
        if self in touch.ud:
            self.anim_complete(self, self)
            self.ripple_pos = ripple_pos = (touch.x, touch.y)
            Animation.cancel_all(self, 'ripple_rad', 'ripple_color')
            rc = self.ripple_color
            ripple_rad = self.ripple_rad
            self.ripple_color = [rc[0], rc[1], rc[2], .16]
            anim = Animation(
                ripple_rad=max(self.width, self.height) * self.ripple_scale, 
                t=self.ripple_func_in,
                ripple_color=[rc[0], rc[1], rc[2], self.fade_to_alpha],
                duration=self.ripple_duration_in)
            anim.start(self)
            with self.canvas.after:
                x,y = self.to_window(*self.pos)
                width, height = self.size
                #In python 3 the int cast will be unnecessary
                pos = (int(round(x)), int(round(y)))
                size = (int(round(width)), int(round(height)))

                if _has_scissor_instr:
                    ScissorPush(x=pos[0], y=pos[1],
                                width=size[0], height=size[1])
                else:
                    StencilPush()
                    Rectangle(pos=(int(round(x)), int(round(y))),
                              size=(int(round(width)), int(round(height))))

                    StencilUse()

                self.col_instruction = Color(rgba=self.ripple_color)
                self.ellipse = Ellipse(size=(ripple_rad, ripple_rad),
                                       pos=(ripple_pos[0] - ripple_rad/2.,
                                            ripple_pos[1] - ripple_rad/2.))

                if _has_scissor_instr:
                    ScissorPop()
                else:
                    StencilUnUse()
                    Rectangle(pos=(int(round(x)), int(round(y))),
                              size=(int(round(width)), int(round(height))))
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
    ripple_color_tuple = ListProperty(['Grey', '1000'])

    def on_touch_down(self, touch):
        TextInput.on_touch_down(self, touch)
        super(FlatTextInput, self).on_touch_down(touch)

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

class FlatPopup(Popup):
    popup_color = ListProperty([1., 1., 1., 1.])


class FlatScrollView(ScrollView):

    def scroll_to_top(self):
        self.scroll_y = 1.0


class FlatButton(GrabBehavior, LogBehavior, TouchRippleBehavior, 
    ThemeBehavior, ButtonBehavior, AnchorLayout):
    color = ListProperty([1., 1., 1.])
    color_down = ListProperty([.7, .7, .7])
    text = StringProperty('')
    style = StringProperty(None, allownone=True)
    color_tuple = ListProperty(['Blue', '500'])
    font_color_tuple = ListProperty(['Grey', '1000'])
    ripple_color_tuple = ListProperty(['Grey', '1000'])
    font_ramp_tuple = ListProperty(None)
    font_size = NumericProperty(12)
    
    def on_color(self, instance, value):
        self.color_down = [x*.7 for x in value]


class FlatImageButton(GrabBehavior, LogBehavior, ButtonBehavior,
    TouchRippleBehavior, ThemeBehavior, AnchorLayout):
    color = ListProperty([1., 1., 1.])
    color_down = ListProperty([.7, .7, .7])
    text = StringProperty('')
    icon_source = StringProperty('')
    style = StringProperty(None, allownone=True)
    font_size = NumericProperty(12)
    image_color_tuple = ListProperty(['Grey', '1000'])
    color_tuple = ListProperty(['Blue', '500'])
    font_color_tuple = ListProperty(['Grey', '1000'])
    font_ramp_tuple = ListProperty(None)
    ripple_color_tuple = ListProperty(['Grey', '1000'])
    content_padding = VariableListProperty([0., 0., 0., 0.])
    content_spacing = VariableListProperty([0., 0.], length=2)

    def on_color(self, instance, value):
        self.color_down = [x*.7 for x in value]

class FlatImageButtonLeft(FlatImageButton):
    pass

class FlatIconButton(GrabBehavior, LogBehavior, ButtonBehavior, 
    TouchRippleBehavior, ThemeBehavior, AnchorLayout):
    color = ListProperty([1., 1., 1.])
    color_down = ListProperty([.7, .7, .7])
    text = StringProperty('')
    icon = StringProperty('')
    style = StringProperty(None, allownone=True)
    font_size = NumericProperty(12)
    icon_color_tuple = ListProperty(['Grey', '1000'])
    color_tuple = ListProperty(['Blue', '500'])
    font_color_tuple = ListProperty(['Grey', '1000'])
    font_ramp_tuple = ListProperty(None)
    ripple_color_tuple = ListProperty(['Grey', '1000'])
    content_padding = VariableListProperty([0., 0., 0., 0.])
    content_spacing = VariableListProperty([0., 0.], length=2)

    def on_color(self, instance, value):
        self.color_down = [x*.7 for x in value]


class FlatIconButtonLeft(FlatIconButton):
    pass

class FlatCard(GrabBehavior, ThemeBehavior, LogBehavior, TouchRippleBehavior,
    ButtonBehavior, BoxLayout):
    image_source = StringProperty(None)
    style = StringProperty(None, allownone=True)
    color_tuple = ListProperty(['Blue', '500'])
    font_color_tuple = ListProperty(['Grey', '1000'])
    font_ramp_tuple = ListProperty(None)
    ripple_color_tuple = ListProperty(['Grey', '1000'])
    text = StringProperty(None)
    color = ListProperty([1., 1., 1.])
    color_down = ListProperty([.7, .7, .7])

    def on_color(self, instance, value):
        self.color_down = [x*.7 for x in value]


class FlatLabel(GrabBehavior, ThemeBehavior, LogBehavior, Label):
    text = StringProperty(None, allownone=True)
    color_tuple = ListProperty(['Grey', '0000'])
    style = StringProperty(None, allownone=True)
    style_dict = ObjectProperty(None, allownone=True)
    do_resize = BooleanProperty(True)
    ramp_group = ObjectProperty(None, allownone=True)
    font_ramp_tuple = ListProperty(None)

    def __init__(self, **kwargs):
        self._do_check_adjustments = True
        super(FlatLabel, self).__init__(**kwargs)

    def on_style_dict(self, instance, value):
        if value is not None:
            self.font_name = construct_target_file_name(
                'data/font/' + value.font_file, __file__)
            self.font_size = font_size = get_metric_conversion(
                value.size_mobile)
            self.color[3] = value.alpha
            #self.shorten = not value['wrap']

    def on_font_ramp_tuple(self, instance, value):
        if self.ramp_group is not None:
            self.ramp_group.remove_widget(self)

    def on_ramp_group(self, instance, value):
        if value is not None:
            value.add_label(self)
            value.trigger_fit_check()

    def on_touch_down(self, touch):
        log_manager = self.log_manager
        if log_manager.do_label_logging:
            super(FlatLabel, self).on_touch_down(touch)
            if self in touch.ud:
                touch_id = touch.ud['log_id']
                log_manager.log_interface.set_entry(
                    'touches', touch_id, 'label_touched', self.text, 
                    do_timestamp=True)

    def on_texture(self, instance, value):
        ramp_group = self.ramp_group
        if ramp_group is not None and self._do_check_adjustments:
            ramp_group.trigger_fit_check()

    def on_size(self, instance, value):
        ramp_group = self.ramp_group
        if ramp_group is not None and self._do_check_adjustments:
            ramp_group.trigger_fit_check()


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
    ripple_color_tuple = ListProperty(['Grey', '1000'])
    font_ramp_tuple = ListProperty(None)
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
    ripple_color_tuple = ListProperty(['Grey', '1000'])
    font_ramp_tuple = ListProperty(['default', '1'])
    halign = StringProperty('left')
    valign = StringProperty('bottom')
    alpha = NumericProperty(None, allownone=True)

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.toggle_checkbox()
        super(CheckBoxListItem, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        super(CheckBoxListItem, self).on_touch_up(touch)

    def toggle_checkbox(self):
        self.ids.checkbox._toggle_active()


class FlatSlider(Slider):
    bar_color = ListProperty((.5, .5, .5, 1.))
    bar_fill_color = ListProperty((.8, .8, .8, 1.))
    handle_size = NumericProperty('28sp')
    handle_image_normal = StringProperty(
        construct_target_file_name('data/images/slider_handle_normal.png',
        __file__))
    handle_image_disabled = StringProperty(
        construct_target_file_name('data/images/slider_handle_disabled.png',
        __file__))

    bar_color_tuple = ListProperty(('Gray', '800'))
    bar_fill_color_tuple = ListProperty(('Blue', '500'))

    def __init__(self, **kw):
        super(FlatSlider, self).__init__(**kw)
        self.bind(size=self.redraw, pos=self.redraw, orientation=self.redraw,
                  bar_color=self.redraw, bar_fill_color=self.redraw,
                  handle_image_normal=self.redraw,
                  handle_image_disabled=self.redraw, handle_size=self.redraw,
                  disabled=self.redraw)
        self.bind(value=self.update, min=self.update, max=self.update)

    def redraw(self, *ar):
        self.canvas.clear()
        bc = self.bar_color[:]
        bfc = self.bar_fill_color[:]
        if self.disabled:
            bc = [i * .6 for i in bc]
            bfc = [i * .6 for i in bfc]

        bw = get_metric_conversion((4, 'sp'))
        hs = self.handle_size

        with self.canvas:
            if self.orientation == 'horizontal':
                Color(*bc)
                Rectangle(pos=(self.x + self.padding, self.center_y - bw / 2.),
                          size=(self.width - self.padding * 2, bw))
                Color(*bfc)
                self._fill_bar = Rectangle(pos=(self.x + self.padding,
                                                self.center_y - bw / 2.),
                                           size=(0, bw))
            else:
                Color(*bc)
                Rectangle(pos=(self.center_x - bw / 2., self.y + self.padding),
                          size=(bw, self.height - self.padding * 2))
                Color(*bfc)
                self._fill_bar = Rectangle(pos=(self.center_x - bw / 2.,
                                                self.y + self.padding),
                                           size=(bw, 0))

            source = (self.handle_image_disabled if self.disabled else self.handle_image_normal)
            self._handle = Rectangle(size=(hs, hs),
                                     source=source)

        self.update()

    def update(self, *ar):
        per = self.value / float(self.max - self.min)
        hs = self.handle_size

        if self.orientation == 'horizontal':
            full = self.width - self.padding * 2
            self._fill_bar.size = (full * per, self._fill_bar.size[1])
            self._handle.pos = (self.x + self.padding + full * per - hs / 2.,
                                self.center_y - hs / 2.)
        else:
            full = self.height - self.padding * 2
            self._fill_bar.size = (self._fill_bar.size[0], full * per)
            self._handle.pos = (self.center_x - hs / 2.,
                                self.y + self.padding + full * per - hs / 2.)
