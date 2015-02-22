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


import itertools
import doctest
import os.path
import random
import sys
import unittest


ONLY_FLAG = "--only"
ROOT_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")


def execute_specs(args):
    setup_displayhook()
    setup_paths()
    install_gettext_in_builtin_namespace()
    disable_monitoring()
    suite = create_suite(create_include_test_function(args))
    all_pass = execute_suite(suite, select_verbosity(args))
    return all_pass


def setup_displayhook():
    # Background why this is needed:
    # http://sheep.art.pl/Gettext%20and%20Doctest%20Together%20in%20Python
    # Current doctest seems to use sys.__displayhook__ instead, so replace both.
    def displayhook_that_does_not_modify_(value):
        if value is not None:
            print(repr(value))
    sys.__displayhook__ = sys.displayhook = displayhook_that_does_not_modify_


def setup_paths():
    sys.path.insert(0, os.path.join(ROOT_DIR, "source"))
    sys.path.insert(0, os.path.join(ROOT_DIR, "test"))
    sys.path.insert(0, os.path.join(ROOT_DIR, "dependencies", "dev", "mock-0.7.2"))
    sys.path.insert(0, os.path.join(ROOT_DIR, "dependencies", "timelinelib", "icalendar-3.2"))
    sys.path.insert(0, os.path.join(ROOT_DIR, "dependencies", "timelinelib", "markdown-2.0.3"))
    sys.path.insert(0, os.path.join(ROOT_DIR, "dependencies", "timelinelib", "pysvg-0.2.1"))
    sys.path.insert(0, os.path.join(ROOT_DIR, "dependencies", "timelinelib", "pytz-2012j"))


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


def create_suite(include_test_function):
    whole_suite = suite_from_modules(find_test_modules())
    filtered_suite = filter_suite(whole_suite, include_test_function)
    return shuffled_suite(filtered_suite)


def suite_from_modules(modules):
    suite = unittest.TestSuite()
    for (test_type, module) in modules:
        {
            "spec": load_test_cases_from_module_name,
            "doctest": load_doc_tests_from_module_name,
        }[test_type](suite, module)
    return suite


def load_test_cases_from_module_name(suite, module_name):
    __import__(module_name)
    module = sys.modules[module_name]
    module_suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    suite.addTest(module_suite)


def load_doc_tests_from_module_name(suite, module_name):
    __import__(module_name)
    module = sys.modules[module_name]
    try:
        module_suite = doctest.DocTestSuite(module)
    except ValueError:
        # No tests found
        pass
    else:
        suite.addTest(module_suite)


def find_test_modules():
    modules = find_specs() + find_doctests()
    random.shuffle(modules)
    return modules


def _find_specs():
    specs = []
    for file in os.listdir(os.path.join(os.path.dirname(__file__), "specs")):
        if file.endswith(".py") and file != "__init__.py":
            module_name = os.path.basename(file)[:-3]
            abs_module_name = "specs.%s" % module_name
            specs.append(("spec", abs_module_name))
    print specs
    return specs


def find_specs():

    def valid(f):
        return f.endswith(".py") and not f.startswith("__")

    def module_name(rpath, filename):
        # This following if-statement is only needed when running from within eclipse!
        # Can't figure out why
        if rpath.startswith("test\\"):
            rpath = rpath[5:]
        return "%s.%s" % (rpath.replace("\\","."), filename.rsplit(".", 1)[0])

    rp = os.path.relpath(os.path.join(os.path.dirname(__file__), "specs"))
    return list(itertools.chain(*[[("spec", module_name(rpath, f))
                                for f in files if valid(f)]
                                for rpath, _, files in os.walk(rp)]))


def find_doctests():
    doctests = []
    timelinelib_dir = os.path.join(ROOT_DIR, "source", "timelinelib")
    for module in find_python_modules(timelinelib_dir):
        doctests.append(("doctest", module))
    return doctests


def find_python_modules(path):
    module_names = []
    files = os.listdir(path)
    if "__init__.py" in files:
        module_names.append("%s" % os.path.basename(path))
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                module_names.append("%s.%s" % (os.path.basename(path), file[:-3]))
            if os.path.isdir(os.path.join(path, file)):
                for x in find_python_modules(os.path.join(path, file)):
                    module_names.append("%s.%s" % (os.path.basename(path), x))
    return module_names


def filter_suite(test, include_test_function):
    new_suite = unittest.TestSuite()
    if isinstance(test, unittest.TestCase):
        if include_test_function(test):
            new_suite.addTest(test)
    else:
        for subtest in test:
            new_suite.addTest(filter_suite(subtest, include_test_function))
    return new_suite


def shuffled_suite(suite):
    test_cases = extract_test_cases(suite)
    random.shuffle(test_cases)
    return unittest.TestSuite(test_cases)


def extract_test_cases(suite):
    if isinstance(suite, unittest.TestCase):
        return [suite]
    else:
        tests = []
        for test in suite:
            tests.extend(extract_test_cases(test))
        return tests


def execute_suite(suite, verbosity):
    res = unittest.TextTestRunner(verbosity=verbosity).run(suite)
    return res.wasSuccessful()


def select_verbosity(args):
    if ONLY_FLAG in args:
        return 2
    else:
        return 1


if __name__ == '__main__':
    all_pass = execute_specs(sys.argv)
    if all_pass:
        sys.exit(0)
    else:
        sys.exit(1)
