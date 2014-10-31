from __future__ import unicode_literals, print_function
from kivy.uix.label import Label
from kivy.event import EventDispatcher
from ui_elements import FlatLabel
from kivy.clock import Clock


def get_style(style):
    if style is not None:
        try:
            return style_manager.styles[style]
        except:
            print('font style: ' + style + ' not defined.')
            return None
    else:
        return None

def get_font_ramp_group(font_ramp_tuple):
    if font_ramp_tuple != []:
        group_name, ramp_name = font_ramp_tuple
        font_ramp = style_manager.get_font_ramp(ramp_name)
        if style_manager.check_ramp_group_exists(group_name):
            return style_manager.get_ramp_group(group_name)
        else:
            return style_manager.create_ramp_group(group_name, font_ramp)

class FontStyle(object):

    def __init__(self, font_file, name, size_mobile, size_desktop, alpha,
        **kwargs):
        super(FontStyle, self).__init__(**kwargs)
        self.font_file = font_file
        self.name = name
        self.size_mobile = size_mobile
        self.size_desktop = size_desktop
        self.alpha = alpha

class RampGroup(EventDispatcher):

    def __init__(self, font_ramp, name, **kwargs):
        super(RampGroup, self).__init__(**kwargs)
        self.tracked_labels = []
        self.font_ramp = font_ramp
        self.name = name
        self.current_style = font_ramp[0]
        self._test_label = FlatLabel()
        self.max_iterations = 2

    def copy_label_to_test_label(self, label, style):
        test_label = self._test_label
        test_label.size = label.size
        test_label.style = style
        test_label.text = label.text
        test_label.halign = label.halign
        test_label.valign = label.valign
        test_label.text_size = label.text_size
        test_label._label.render()
        return test_label

    def check_fit_for_all_labels(self, style, iterations):
        tracked_labels = self.tracked_labels
        returns = set()
        r_add = returns.add
        max_iterations = self.max_iterations
        copy_label_to_test_label = self.copy_label_to_test_label
        calculate_fit = self.calculate_fit
        
        if self.name in ['default', 'question_default']:
            return
        for tracked_label in tracked_labels:
            if tracked_label.width <= 0 or tracked_label.height <= 0:
                continue
            test_label = copy_label_to_test_label(tracked_label, style)

            check_fit = calculate_fit(test_label)
            print(tracked_label.size, tracked_label.text, check_fit)
            r_add(check_fit)
        print(returns, iterations, max_iterations)
        if 'toobig' in returns and iterations < max_iterations:
            self.current_style = style = self.get_next_smallest_style(style)
            self.check_fit_for_all_labels(style, iterations+1)
        elif 'toosmall' in returns and iterations < max_iterations:
            self.current_style = style = self.get_next_largest_style(style)
            self.check_fit_for_all_labels(style, iterations+1)
        else:
            self.set_style(style)

    def set_style(self, style):
        for tracked_label in self.tracked_labels:
            tracked_label._do_check_adjustments = False
            tracked_label.style = style
        Clock.schedule_once(self.reset_track_adjustments, 1.)

    def reset_track_adjustments(self, dt):
        for tracked_label in self.tracked_labels:
            tracked_label._do_check_adjustments = True
            


    def get_next_smallest_style(self, style):
        font_ramp = self.font_ramp
        current_ind = font_ramp.index(style)
        next_ind = current_ind+1
        try:
            return font_ramp[next_ind]
        except:
            return style

    def get_next_largest_style(self, style):
        font_ramp = self.font_ramp
        current_ind = font_ramp.index(style)
        next_ind = current_ind-1
        try:
            return font_ramp[next_ind]
        except:
            return style

    def calculate_fit(self, label):
        actual_size = label._label._internal_size
        size = label.size
        style = label.style
        status = 'fits'
        if actual_size[0] > size[0] or actual_size[1] > size[1]:
            status = 'toobig'
        elif actual_size[0] < size[0]*.5 and actual_size[1] < size[1] *.5:
            status = 'toosmall'
        return status

    def add_label(self, label):
        tracked_labels = self.tracked_labels
        if label not in tracked_labels and isinstance(label, Label):
            tracked_labels.append(label)
            label.style = self.current_style
        else:
            print('Label already added or not instance of Label')

    def remove_widget(self, label):
        try:
            self.tracked_labels.remove(label)
        except:
            print('widget not removed, maybe it is not there')


class StyleManager(object):

    def __init__(self, **kwargs):
        super(StyleManager, self).__init__(**kwargs)
        self.styles = {}
        self.ramp_groups = {}
        self.font_ramps = {}

    def add_style(self, font_file, name, size_mobile, size_desktop, alpha):
        style = FontStyle(font_file, name, size_mobile, size_desktop, alpha)
        self.styles[name] = style

    def add_font_ramp(self, name, ramp):
        styles = self.styles
        for style in ramp:
            assert(style in styles)
        self.font_ramps[name] = ramp

    def create_ramp_group(self, name, ramp):
        ramp_group = RampGroup(ramp, name)
        self.ramp_groups[name] = ramp_group
        return ramp_group

    def check_ramp_group_exists(self, name):
        return name in self.ramp_groups

    def get_font_ramp(self, ramp_name):
        return self.font_ramps[ramp_name]

    def get_ramp_group(self, group_name):
        return self.ramp_groups[group_name]

style_manager = StyleManager()



