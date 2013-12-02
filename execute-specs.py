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


import sys
import os.path
import unittest
import doctest


ONLY_FLAG = "--only"


def execute_specs(args):
    setup_paths()
    install_gettext_in_builtin_namespace()
    disable_monitoring()
    suite = create_suite(create_include_test_function(args))
    all_pass = execute_suite(suite, select_verbosity(args))
    return all_pass


def setup_paths():
    root_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.insert(0, os.path.join(root_dir, "libs", "dev", "mock-0.7.2"))
    sys.path.insert(0, os.path.join(root_dir, "libs", "dependencies", "icalendar-3.2"))
    sys.path.insert(0, os.path.join(root_dir, "libs", "dependencies", "pytz-2012j"))


def install_gettext_in_builtin_namespace():
    def _(message):
        return "#%s#" % message
    import __builtin__
    __builtin__.__dict__["_"] = _


def disable_monitoring():
    from timelinelib.monitoring import monitoring
    monitoring.IS_ENABLED = False


def create_include_test_function(args):
    if ONLY_FLAG in args:
        patterns = args[args.index(ONLY_FLAG)+1:]
        return lambda test: any([pattern in test.id() for pattern in patterns])
    else:
        return lambda test: True


def select_verbosity(args):
    if ONLY_FLAG in args:
        return 2
    else:
        return 1


def create_suite(include_test_function):
    suite = unittest.TestSuite()
    add_specs(suite, include_test_function)
    add_doctests(suite, include_test_function)
    return suite


def add_specs(suite, include_test_function):
    for file in os.listdir(os.path.join(os.path.dirname(__file__), "specs")):
        if file.endswith(".py") and file != "__init__.py":
            module_name = os.path.basename(file)[:-3]
            abs_module_name = "specs.%s" % module_name
            load_test_cases_from_module_name(suite, abs_module_name,
                                             include_test_function)


def load_test_cases_from_module_name(suite, module_name, include_test_function):
    __import__(module_name)
    module = sys.modules[module_name]
    module_suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    filtered = filter_suite(module_suite, include_test_function)
    suite.addTest(filtered)


def add_doctests(suite, include_test_function):
    for module in [
                    "timelinelib.xml.parser",
                    "timelinelib.utils"
                  ]:
        load_doc_test_from_module_name(suite, module, include_test_function)


def load_doc_test_from_module_name(suite, module_name, include_test_function):
    __import__(module_name)
    module = sys.modules[module_name]
    module_suite = doctest.DocTestSuite(module)
    filtered = filter_suite(module_suite, include_test_function)
    suite.addTest(filtered)


def filter_suite(test, include_test_function):
    new_suite = unittest.TestSuite()
    if isinstance(test, unittest.TestCase):
        if include_test_function(test):
            new_suite.addTest(test)
    else:
        for subtest in test:
            new_suite.addTest(filter_suite(subtest, include_test_function))
    return new_suite


def execute_suite(suite, verbosity):
    res = unittest.TextTestRunner(verbosity=verbosity).run(suite)
    return res.wasSuccessful()


if __name__ == '__main__':
    all_pass = execute_specs(sys.argv)
    if all_pass:
        sys.exit(0)
    else:
        sys.exit(1)
