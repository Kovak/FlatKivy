
from kivy.uix.label import Label
from kivy.properties import (BooleanProperty, ListProperty, StringProperty,
                             ObjectProperty)

from flat_kivy.uix.behaviors import (GrabBehavior, ThemeBehavior, LogBehavior)
from flat_kivy.utils import construct_data_resource, get_metric_conversion


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
            self.font_name = construct_data_resource(
                'font/' + value.font_file)
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