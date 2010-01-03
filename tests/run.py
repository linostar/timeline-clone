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
Script that runs all unit tests.
"""

import sys
import os.path
import unittest
import gettext

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)

import time_period
import file_timeline
import wildcard_helper
import category_editor
from timelinelib.about import APPLICATION_NAME
from timelinelib.paths import LOCALE_DIR

if __name__ == '__main__':
    verbosity = 2
    if len(sys.argv) == 2 and sys.argv[1] == "quiet":
        verbosity = 0
    gettext.install(APPLICATION_NAME.lower(), LOCALE_DIR, unicode=True)
    loader = unittest.TestLoader()
    test_modules = [time_period, file_timeline, wildcard_helper,
                    category_editor]
    test_suites = [loader.loadTestsFromModule(x) for x in test_modules]
    the_suite = unittest.TestSuite(test_suites)
    res = unittest.TextTestRunner(verbosity=verbosity).run(the_suite)
    if res.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)
