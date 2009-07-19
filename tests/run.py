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

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, src_dir)

import time_period

if __name__ == '__main__':
    loader = unittest.TestLoader()
    test_modules = [time_period]
    test_suites = [loader.loadTestsFromModule(x) for x in test_modules]
    the_suite = unittest.TestSuite(test_suites)
    unittest.TextTestRunner(verbosity=2).run(the_suite)
