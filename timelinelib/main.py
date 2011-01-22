# Copyright (C) 2009, 2010  Rickard Lindberg, Roger Lindberg
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


import sys
from sys import argv
from sys import version as python_version
import platform
from optparse import OptionParser
import gettext

import wx

from timelinelib.gui.dialogs.mainframe import MainFrame
from timelinelib.unhandledex import unhandled_exception_hook
from version import get_version
import config
from about import APPLICATION_NAME
from paths import LOCALE_DIR


def setup_gettext():
    """Make sure that the _() is available everywhere."""
    if platform.system() == "Windows":
        # The appropriate environment variables are set on other systems
        import locale
        import os
        language, encoding = locale.getdefaultlocale()
        os.environ['LANG'] = language
    gettext.install(APPLICATION_NAME.lower(), LOCALE_DIR, unicode=True)


def parse_options():
    """Parse command line options using the optparse module."""
    version_string = "%prog " + get_version()
    option_parser = OptionParser(usage="%prog [options] [filename]",
                                 version=version_string)
    # Skip first command line argument since it is the name of the program
    return option_parser.parse_args(argv[1:])


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
    # Customize the handling of top-level exceptions
    app = create_wx_app(input_files)
    sys.excepthook = unhandled_exception_hook
    app.MainLoop()

