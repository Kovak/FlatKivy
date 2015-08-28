

from kivy.uix.slider import Slider
from kivy.properties import ListProperty

from behaviors import GrabBehavior, SliderTouchRippleBehavior, ThemeBehavior


class FlatSlider(GrabBehavior, SliderTouchRippleBehavior, ThemeBehavior,
                 Slider):
    color_tuple = ListProperty(['Blue', '500'])
    slider_color_tuple = ListProperty(['Orange', '300'])
    outline_color_tuple = ListProperty(['Blue', '600'])
    slider_outline_color_tuple = ListProperty(['Orange', '500'])
    ripple_color_tuple = ListProperty(['Grey', '0000'])
