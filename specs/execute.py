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
Script that executes all specifications.
"""

import sys
import os.path
import unittest
import gettext
import doctest

def execute_all_specs():
    setup_paths()
    enable_gettext()
    suite = create_suite()
    all_pass = execute_suite(suite)
    return all_pass

def setup_paths():
    # So that the we can write 'import timelinelib.xxx' and 'import specs.xxx'
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, root_dir)

def enable_gettext():
    # So that the _ function is available
    from timelinelib.about import APPLICATION_NAME
    from timelinelib.paths import LOCALE_DIR
    gettext.install(APPLICATION_NAME.lower(), LOCALE_DIR, unicode=True)

def create_suite():
    def add_spec_from_module(suite, module_name):
        __import__(module_name)
        module = sys.modules[module_name]
        module_suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        suite.addTest(module_suite)
    suite = unittest.TestSuite()
    for file in os.listdir(os.path.dirname(__file__)):
        if file != os.path.basename(__file__) and file.endswith(".py"):
            module_name = os.path.basename(file)[:-3]
            abs_module_name = "specs.%s" % module_name
            add_spec_from_module(suite, abs_module_name)
    return suite

def execute_suite(suite):
    res = unittest.TextTestRunner(verbosity=1).run(suite)
    return res.wasSuccessful()

if __name__ == '__main__':
    all_pass = execute_all_specs()
    if all_pass:
        sys.exit(0)
    else:
        sys.exit(1)
