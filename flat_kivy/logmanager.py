
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, BooleanProperty, StringProperty

from flat_kivy.dbinterface import DBInterface


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