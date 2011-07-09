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
#sys.path.insert(0, os.path.dirname(__file__))
exepath = os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding()))
sys.path.insert(0, exepath)

from timelinelib.about import APPLICATION_NAME
from timelinelib.arguments import ApplicationArguments
from timelinelib.gui.setup import start_wx_application
from timelinelib.paths import LOCALE_DIR

if platform.system() == "Windows":
    # The appropriate environment variables are set on other systems
    language, encoding = locale.getdefaultlocale()
    os.environ['LANG'] = language

gettext.install(APPLICATION_NAME.lower(), LOCALE_DIR, unicode=True)

application_arguments = ApplicationArguments()
application_arguments.parse_from(sys.argv[1:])

start_wx_application(application_arguments)

