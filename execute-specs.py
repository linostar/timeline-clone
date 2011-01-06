#!/usr/bin/env python
#
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

import sys
import os.path
import unittest
import doctest

def execute_all_specs():
    setup_paths()
    install_gettext_in_builtin_namespace()
    suite = create_suite()
    all_pass = execute_suite(suite)
    return all_pass

def setup_paths():
    # So that the we can write 'import timelinelib.xxx' and 'import specs.xxx'
    root_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.insert(0, root_dir)

def install_gettext_in_builtin_namespace():
    def _(message):
        return "#%s#" % message
    import __builtin__
    __builtin__.__dict__["_"] = _

def create_suite():
    suite = unittest.TestSuite()
    add_specs(suite)
    add_unittests(suite)
    add_doctests(suite)
    return suite

def execute_suite(suite):
    res = unittest.TextTestRunner(verbosity=1).run(suite)
    return res.wasSuccessful()

def add_specs(suite):
    for file in os.listdir(os.path.join(os.path.dirname(__file__), "specs")):
        if file.endswith(".py") and file != "__init__.py":
            module_name = os.path.basename(file)[:-3]
            abs_module_name = "specs.%s" % module_name
            load_test_cases_from_module_name(suite, abs_module_name)

def add_unittests(suite):
    load_test_cases_from_module_name(suite, "tests.unit.db.backends.file")
    load_test_cases_from_module_name(suite, "tests.unit.db.backends.memory")
    load_test_cases_from_module_name(suite, "tests.integration.read_010_file")
    load_test_cases_from_module_name(suite, "tests.integration.read_090_file")
    load_test_cases_from_module_name(suite, "tests.integration.read_0100_file")
    load_test_cases_from_module_name(suite, "tests.unit.db.backends.xmlparser")
    load_test_cases_from_module_name(suite, "tests.integration.read_write_xml")
    load_test_cases_from_module_name(suite, "tests.integration.write_xml")

def add_doctests(suite):
    load_doc_test_from_module_name(suite, "timelinelib.db.backends.xmlparser")
    load_doc_test_from_module_name(suite, "timelinelib.utils")

def load_test_cases_from_module_name(suite, module_name):
    __import__(module_name)
    module = sys.modules[module_name]
    module_suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    suite.addTest(module_suite)

def load_doc_test_from_module_name(suite, module_name):
    __import__(module_name)
    module = sys.modules[module_name]
    module_suite = doctest.DocTestSuite(module)
    suite.addTest(module_suite)

if __name__ == '__main__':
    all_pass = execute_all_specs()
    if all_pass:
        sys.exit(0)
    else:
        sys.exit(1)
