from __future__ import unicode_literals, print_function
from os import path
from kivy.utils import platform, get_color_from_hex
from color_definitions import colors
from fa_icon_definitions import fa_icons
import kivy.metrics

def get_metric_conversion(metric_tuple):
    return getattr(kivy.metrics, metric_tuple[1])(metric_tuple[0])


def construct_target_file_name(target_file_name, pyfile):
    '''Returns the correct file path relative to the __file__ 
    passed as pyfile'''
    if pyfile is None:
        pyfile = __file__
    return path.join(path.dirname(path.abspath(pyfile)), target_file_name)


def construct_data_resource(res_path):
    path_to_this_file = path.abspath(__file__)
    data_path = path.join(path.dirname(path_to_this_file),
                          'data')
    return path.join(data_path, res_path)


def get_icon_char(icon):
    if icon != '':
        try:
            return fa_icons[icon]
        except:
            print('icon: ' + icon + ' not in fa_icons')
            return ''
    else:
        return ''


def get_rgba_color(color_tuple, control_alpha=None):
    color, weight = color_tuple
    try:
        color = get_color_from_hex(colors[color][weight])
    except:
        print('Error: ' + color + weight + ' not found, set to default')
        return (1., 1., 1., 1.)
    if control_alpha is None:
        return color
    else:
        color[3] = control_alpha
        return color
    

