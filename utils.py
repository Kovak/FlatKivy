from __future__ import unicode_literals, print_function
from os import path
from kivy.utils import platform
from color_definitions import colors
from fa_icon_definitions import fa_icons
from font_definitions import font_styles, wrap_ids
import kivy.metrics

def get_metric_conversion(metric_tuple):
    return getattr(kivy.metrics, metric_tuple[1])(metric_tuple[0])

def construct_target_file_name(target_file_name, pyfile):
    '''Returns the correct file path relative to the __file__ 
    passed as pyfile'''
    return path.join(path.dirname(path.abspath(pyfile)), target_file_name)

def get_next_smallest_style(style):
    wrap_id = font_styles[style]['wrap_id']
    next_id = str(int(wrap_id)+1)
    try:
        return wrap_ids[next_id]
    except:
        return style


def get_style(style):
    if style is not None:
        try:
            return font_styles[style]
        except:
            print('font style: ' + style + ' not in fa_icons')
            return {}
    else:
        return {}


def get_icon_char(icon):
    if icon != '':
        try:
            return fa_icons[icon]
        except:
            print('icon: ' + icon + ' not in fa_icons')
            return ''
    else:
        return ''

def get_rgba_color(color):
    try:
        return colors[color]
    except:
        print('Error: ' + color + ' not found, set to default')
        return colors['default']
    

