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
Script that runs all automated tests.

All automated tests include the unit tests in this directory tree and the
doctests written in the source code.
"""

import sys
import os.path
import unittest
import gettext

def run_all_tests():
    setup_paths()
    enable_gettext()
    suite = create_test_suite()
    verbosity = get_verbosity_level()
    all_pass = run_suite(suite, verbosity)
    return all_pass

def setup_paths():
    # So that the we can write 'import timelinelib.xxx' and 'import tests.xxx'
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, root_dir)

def enable_gettext():
    # So that the _ function is available
    from timelinelib.about import APPLICATION_NAME
    from timelinelib.paths import LOCALE_DIR
    gettext.install(APPLICATION_NAME.lower(), LOCALE_DIR, unicode=True)

def create_test_suite():
    suite = unittest.TestSuite()
    add_unittests(suite)
    add_doctests(suite)
    return suite

def add_unittests(suite):
    def add_tests_from_module(module_name):
        __import__(module_name)
        module = sys.modules[module_name]
        module_suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        suite.addTest(module_suite)
    add_tests_from_module("tests.time_period")
    add_tests_from_module("tests.file_timeline")
    add_tests_from_module("tests.wildcard_helper")
    add_tests_from_module("tests.category_editor")
    add_tests_from_module("tests.config")
    add_tests_from_module("tests.memorydb")
    add_tests_from_module("tests.dbread.v010")
    add_tests_from_module("tests.duplicateevent")

def add_doctests(suite):
    pass

def get_verbosity_level():
    verbosity = 2
    if len(sys.argv) == 2 and sys.argv[1] == "quiet":
        verbosity = 0
    return verbosity

def run_suite(suite, verbosity):
    res = unittest.TextTestRunner(verbosity=verbosity).run(suite)
    return res.wasSuccessful()

if __name__ == '__main__':
    all_pass = run_all_tests()
    if all_pass:
        sys.exit(0)
    else:
        sys.exit(1)
