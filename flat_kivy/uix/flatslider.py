
from kivy.uix.slider import Slider
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.graphics import Color, Rectangle

from flat_kivy.utils import construct_data_resource, get_metric_conversion
from flat_kivy.uix.behaviors import ThemeBehavior


class FlatSlider(Slider, ThemeBehavior):
    bar_color = ListProperty((.5, .5, .5, 1.))
    bar_fill_color = ListProperty((.8, .8, .8, 1.))
    handle_accent_color = ListProperty((1., 1., 1., 1.))
    handle_size = NumericProperty('28sp')
    handle_image_normal = StringProperty(
        construct_data_resource('images/slider_handle_normal.png'))
    handle_image_disabled = StringProperty(
        construct_data_resource('images/slider_handle_disabled.png'))

    bar_color_tuple = ListProperty(('Gray', '800'))
    bar_fill_color_tuple = ListProperty(('Blue', '500'))
    handle_accent_color_tuple = ListProperty(('Gray', '0000'))

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
        hac = self.handle_accent_color[:]
        if self.disabled:
            bc = [i * .6 for i in bc]
            bfc = [i * .6 for i in bfc]
            hac = [i * .6 for i in hac]

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
            Color(*hac)
            self._handle = Rectangle(size=(hs, hs),
                                     source=source)

        self.update()

    def update(self, *ar):
        den = float(self.max - self.min)
        per = 0.0 if den == 0.0 else (self.value - self.min) / den
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
