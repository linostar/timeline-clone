# Copyright (C) 2009  Rickard Lindberg, Roger Lindberg
#
# This file is part of Timeline.
#
# Timeline is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Timeline is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Timeline.  If not, see <http://www.gnu.org/licenses/>.


"""
Program main entry point.

Responsible for processing command line options and initializing the
application.
"""


from sys import argv
from sys import version as python_version
import platform
from optparse import OptionParser
import logging
from logging import info as loginfo
import gettext

import wx

from gui import MainFrame
from version import get_version
import config
from about import APPLICATION_NAME
from paths import LOCALE_DIR


def setup_gettext():
    """Make sure that the _() is available everywhere."""
    gettext.install(APPLICATION_NAME.lower(), LOCALE_DIR, unicode=True)


def parse_options():
    """Parse command line options using the optparse module."""
    version_string = "%prog " + get_version()
    option_parser = OptionParser(usage="%prog [options] [filename]",
                                 version=version_string)
    option_parser.add_option("-l", "--log-level",
                             type="int", default=100, # Don't log anything
                             help="specify log level (0 to log everything)")
    option_parser.add_option("-f", "--log-file",
                             default=None,
                             help="specify a file to send log messages to")
    # Skip first command line argument since it is the name of the program
    return option_parser.parse_args(argv[1:])


def setup_logging(log_level, filename):
    """
    Setup default logger to log to stderror and possible also to a file.

    The default logger is used like this:

        import logging
        logging.error(...)
    """
    format= "%(asctime)s [%(levelname)s] %(message)s"
    # Setup logging to stderror
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(format))
    console_handler.setLevel(log_level)
    logging.getLogger().addHandler(console_handler)
    # Setup logging to file if filename is specified
    if filename:
        file_handler = logging.FileHandler(filename, "w")
        file_handler.setFormatter(logging.Formatter(format))
        file_handler.setLevel(log_level)
        logging.getLogger().addHandler(file_handler)
    logging.getLogger().setLevel(log_level)
    loginfo("Logging set up with log level=%s, filename=%s", log_level,
            filename)


def log_versions():
    loginfo("Timeline version %s", get_version())
    loginfo("System version %s", ", ".join(platform.uname()))
    loginfo("Python version %s", python_version.replace("\n", ""))
    loginfo("wxPython version %s", wx.version())


def create_wx_app(input_files):
    """Initialize wx and create the main frame."""
    app = wx.PySimpleApp()
    config.read() # Must be called after we have created the wx.App
    main_frame = MainFrame()
    main_frame.Show()
    if len(input_files) == 0:
        ro = config.get_recently_opened()
        if config.get_open_recent_at_startup() and len(ro) > 0:
            main_frame.open_timeline_if_exists(ro[0])
    else:
        for input_file in input_files:
            main_frame.open_timeline(input_file)
    return app


def main():
    """Main entry point."""
    setup_gettext()
    (options, input_files) = parse_options()
    setup_logging(options.log_level, options.log_file)
    log_versions()
    app = create_wx_app(input_files)
    app.MainLoop()