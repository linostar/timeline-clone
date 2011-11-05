#!/usr/bin/env python
#
# Copyright (C) 2009, 2010, 2011  Rickard Lindberg, Roger Lindberg
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

import gettext
import locale
import os
import platform
import sys

# Make sure that we can import timelinelib
sys.path.insert(0, os.path.dirname(__file__))
# Make sure that we can import pysvg
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs", "dependencies", "pysvg-0.2.1"))
# Make sure that we can import icalendar
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs", "dependencies", "icalendar-2.1"))
# Make sure that we can import markdown
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs", "dependencies", "markdown-2.0.3"))

from timelinelib.config.arguments import ApplicationArguments
from timelinelib.config.paths import LOCALE_DIR
from timelinelib.meta.about import APPLICATION_NAME
from timelinelib.wxgui.setup import start_wx_application

if platform.system() == "Windows":
    # The appropriate environment variables are set on other systems
    language, encoding = locale.getdefaultlocale()
    os.environ['LANG'] = language

gettext.install(APPLICATION_NAME.lower(), LOCALE_DIR, unicode=True)

application_arguments = ApplicationArguments()
application_arguments.parse_from(sys.argv[1:])

start_wx_application(application_arguments)
