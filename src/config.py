"""
Handle application configuration.

This module is global and can be used by all modules. Before accessing
configurations, the read function should be called. To save the current
configuration back to file, call the write method.
"""


from ConfigParser import ConfigParser
from ConfigParser import DEFAULTSECT
import os.path
from logging import error as logerror


PATH = os.path.expanduser("~/.thetimelineproj.cfg")
WINDOW_WIDTH = "window_width"
WINDOW_HEIGHT = "window_height"
WINDOW_MAXIMIZED = "window_maximized"
SHOW_SIDEBAR = "show_sidebar"
SIDEBAR_WIDTH = "sidebar_width"
DEFAULTS = {
    WINDOW_WIDTH: "900",
    WINDOW_HEIGHT: "500",
    WINDOW_MAXIMIZED: "False",
    SHOW_SIDEBAR: "True",
    SIDEBAR_WIDTH: "200"
}


config = None


def read():
    global config
    config = ConfigParser(DEFAULTS)
    config.read(PATH)


def write():
    try:
        f = open(PATH, "w")
    except IOError, e:
        logerror("Unable to write configuration file to %s" % PATH)
    else:
        config.write(f)
        f.close()


def get_window_size():
    return (config.getint(DEFAULTSECT, WINDOW_WIDTH),
            config.getint(DEFAULTSECT, WINDOW_HEIGHT))


def set_window_size(size):
    width, height = size
    config.set(DEFAULTSECT, WINDOW_WIDTH, str(width))
    config.set(DEFAULTSECT, WINDOW_HEIGHT, str(height))


def get_window_maximized():
    return config.getboolean(DEFAULTSECT, WINDOW_MAXIMIZED)


def set_window_maximized(maximized):
    config.set(DEFAULTSECT, WINDOW_MAXIMIZED, str(maximized))


def get_show_sidebar():
    return config.getboolean(DEFAULTSECT, SHOW_SIDEBAR)


def set_show_sidebar(show):
    config.set(DEFAULTSECT, SHOW_SIDEBAR, str(show))


def get_sidebar_width():
    return config.getint(DEFAULTSECT, SIDEBAR_WIDTH)


def set_sidebar_width(width):
    config.set(DEFAULTSECT, SIDEBAR_WIDTH, str(width))
