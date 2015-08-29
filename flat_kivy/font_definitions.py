from __future__ import unicode_literals, print_function
from kivy.uix.label import Label
from kivy.event import EventDispatcher
from flat_kivy.uix.flatlabel import FlatLabel
from kivy.clock import Clock
from kivy.properties import ListProperty
import operator


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
    ignore_list = ListProperty(['default'])

    def __init__(self, font_ramp, name, **kwargs):
        super(RampGroup, self).__init__(**kwargs)
        self.tracked_labels = []
        self.font_ramp = font_ramp
        self.name = name
        self.current_style = font_ramp[-1]
        self._test_label = FlatLabel()
        self._cache = {}
        self.max_iterations = 5
        self.trigger_fit_check = Clock.create_trigger(
            self.check_fit_for_all_labels)

    def copy_label_to_test_label(self, label, style):
        test_label = self._test_label
        test_label.size = label.size
        test_label.style = style
        test_label.text = label.text
        test_label.halign = label.halign
        test_label.valign = label.valign
        test_label.max_lines = label.max_lines
        test_label.texture_update()
        return test_label

    def check_fit_for_all_labels(self, dt):
        if self.name in self.ignore_list:
            return
        tracked_labels = self.tracked_labels
        font_ramp = self.font_ramp
        return_counts = {}
        
        for each in font_ramp:
            return_counts[each] = {'fit_count': 0, 'big_count': 0, 
                'small_count': 0}
        for label in tracked_labels:
            for style in font_ramp:
                return_count = return_counts[style]
                
                fit = self.get_fit(label, style)
                if fit == 'fits':
                    return_count['fit_count'] += 1
                elif fit == 'toobig':
                    return_count['big_count'] += 1
                elif fit =='toosmall':
                    return_count['small_count'] += 1
        fit_counts = []
        fit_a = fit_counts.append
        for style in return_counts:
            if return_counts[style]['big_count'] == 0:
                fit_a((
                    style, return_counts[style]['fit_count'],
                    return_counts[style]['big_count'],
                    return_counts[style]['small_count'],
                    font_ramp.index(style)))
        sorted_fit = sorted(fit_counts, key=lambda x: (
            x[1], -x[2], -x[3], -x[4]))
        if len(sorted_fit) > 0:
            last = sorted_fit[-1]
        else:
            last = [font_ramp[-1], 0, 0, 0]
        if last[2] > 0 and last[1] == 0 and last[3] == 0:
            style = font_ramp[-1]
        else:
            style = last[0]
        self.set_style(style)

    def set_style(self, style):
        for tracked_label in self.tracked_labels:
            tracked_label._do_check_adjustments = True
            tracked_label.style = style

    def reset_track_adjustments(self, dt):
        for tracked_label in self.tracked_labels:
            tracked_label._do_check_adjustments = True
            
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

    def get_fit(self, label, style):
        key = (label.text, (label.width, label.height), style)
        if key not in self._cache:
            test_label = self.copy_label_to_test_label(label, style)
            self._cache[key] = self.calculate_fit(test_label)
        return self._cache[key]

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



