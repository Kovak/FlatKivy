
from weakref import ref

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import (ObjectProperty, OptionProperty, NumericProperty,
                             ListProperty, StringProperty)
from kivy.metrics import sp
from kivy.animation import Animation
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.graphics import (StencilPush, StencilPop, StencilUse,
                           StencilUnUse, Color, Rectangle)
try:
    from kivy.graphics import (ScissorPush, ScissorPop)
except ImportError:
    _has_scissor_instr = False
else:
    _has_scissor_instr = True

from flat_kivy.utils import construct_data_resource
from flat_kivy.logmanager import LogManager


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
                        print(each, 'not in theme', value[0], value[1], self)
                        continue
                    for propname in theme_def:
                        setattr(self, propname, theme_def[propname])


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


class LogBehavior(object):
    log_manager = LogManager(
        construct_data_resource('logs/'))

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


class LogNoTouchBehavior(object):
    log_manager = LogManager(
        construct_data_resource('logs/'))


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
            self.dispatch(b'on_press')
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


class SliderTouchRippleBehavior(object):
    ripple_rad = NumericProperty(10)
    ripple_pos = ListProperty([0, 0])
    ripple_color = ListProperty((1., 1., 1., 1.))
    ripple_duration_in = NumericProperty(.2)
    ripple_duration_out = NumericProperty(.5)
    fade_to_alpha = NumericProperty(.75)
    ripple_scale = NumericProperty(2.0)
    ripple_func_in = StringProperty('in_cubic')
    ripple_func_out = StringProperty('out_quad')

    def __init__(self, **kwargs):
        super(SliderTouchRippleBehavior, self).__init__(**kwargs)
        self.slider_stencil = None
        self.slider_stencil_unuse = None
        self.slider_line_stencil = None
        self.slider_line_stencil_unuse = None

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
                x,y = self.to_window(*self.pos)
                width, height = self.size

                if self.orientation == 'horizontal':
                    ellipse_pos = (self.value_pos[0] - sp(16), self.center_y - sp(17))
                    stencil_pos = (self.x + self.padding + sp(2), self.center_y - sp(7))
                    stencil_size = (self.width - self.padding * 2 - sp(4), sp(14))
                else:
                    ellipse_pos = (self.center_x - sp(17), self.value_pos[1] - sp(16))
                    stencil_pos = (self.center_x - sp(7), self.y + self.padding + sp(2))
                    stencil_size = (sp(14), self.height - self.padding * 2 - sp(4))

                StencilPush()
                Rectangle(
                    pos=stencil_pos,
                    size=stencil_size)
                self.slider_stencil = Ellipse(
                    pos=ellipse_pos,
                    size=(sp(32), sp(32)))
                StencilUse(op='lequal')
                self.col_instruction = Color(rgba=self.ripple_color)
                self.ellipse = Ellipse(size=(ripple_rad, ripple_rad),
                    pos=(ripple_pos[0] - ripple_rad/2.,
                    ripple_pos[1] - ripple_rad/2.))
                StencilUnUse()
                Rectangle(
                    pos=stencil_pos,
                    size=stencil_size)
                self.slider_stencil_unuse = Ellipse(
                    pos=ellipse_pos,
                    size=(sp(32), sp(32)))

                StencilPop()
            self.bind(ripple_color=self.set_color, ripple_pos=self.set_ellipse,
                ripple_rad=self.set_ellipse)
        return super(SliderTouchRippleBehavior, self).on_touch_down(touch)

    def update_stencil(self):
        if self.orientation == 'horizontal':
            pos = [self.value_pos[0] - sp(16),
                   self.center_y - sp(17)]
            ellipse = [self.value_pos[0] - sp(16),
                       self.center_y - sp(17), sp(32), sp(32)]
        else:
            pos = [self.center_x - sp(17),
                   self.value_pos[1] - sp(16)]
            ellipse = [self.center_x - sp(17),
                       self.value_pos[1] - sp(16), sp(32), sp(32)]

        if self.slider_stencil is not None:
            self.slider_stencil.pos = pos
        if self.slider_stencil_unuse is not None:
            self.slider_stencil_unuse.pos = pos
        if self.slider_line_stencil is not None:
            self.slider_line_stencil.ellipse = ellipse
        if self.slider_line_stencil_unuse is not None:
            self.slider_line_stencil_unuse.ellipse = ellipse

    def on_value_pos(self, instance, value):
        self.update_stencil()

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
        return super(SliderTouchRippleBehavior, self).on_touch_up(touch)

    def anim_complete(self, anim, instance):
        self.ripple_rad = 10
        self.canvas.after.clear()
        self.slider_stencil = None
        self.slider_stencil_unuse = None
