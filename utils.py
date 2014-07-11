from __future__ import unicode_literals, print_function
from os import path
from kivy.utils import platform
from color_definitions import colors
from fa_icon_definitions import fa_icons


def construct_target_file_name(target_file_name, pyfile):
    '''Returns the correct file path relative to the __file__ 
    passed as pyfile'''
    return path.join(path.dirname(path.abspath(pyfile)), target_file_name)


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
    

