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
Script that prints a specification of the program from the tests.

Usage:

    python print_spec.py
    python print_spec.py timelinelib.gui.components.timelineview.DrawingAreaController
"""


import re
import sys
import unittest
from datetime import datetime

from mock import Mock


class SuiteMetadataTest(unittest.TestCase):

    def setUp(self):
        self.meta = SuiteMetadata()

    def testExtractsNoMetadataFromEmptySuite(self):
        self.meta.extract_from_suite(unittest.TestSuite())
        self.assertEquals([], self.meta.get_modules())
        self.assertEquals([], self.meta.get_ill_formed_tests())

    def testExtractsWellFormedTestToModulesList(self):
        suite = unittest.TestSuite([
            self.createTestCaseWithGivenIdString("tests.unit.bar.BarTest.testReturnsOneAfterInit")
        ])
        self.meta.extract_from_suite(suite)
        self.assertEquals(["timelinelib.bar"], self.meta.get_modules())
        self.assertEquals(["Bar"], self.meta.get_classes("timelinelib.bar"))
        self.assertEquals(["returns one after init"], self.meta.get_test_stories("timelinelib.bar", "Bar"))

    def testExtractsIllFormedTestToIllFormedTestsList(self):
        test = self.createTestCaseWithGivenIdString("timelinelib.bar.BarTest.foo_bar_test")
        self.meta.extract_from_suite(unittest.TestSuite([test]))
        self.assertEquals([], self.meta.get_modules())
        self.assertEquals(["timelinelib.bar.BarTest.foo_bar_test"], self.meta.get_ill_formed_tests())

    def testHandlesSuitesInSuites(self):
        suite = unittest.TestSuite([
            unittest.TestSuite([
                self.createTestCaseWithGivenIdString("tests.unit.bar.BarTest.testAlwaysFails")
            ]),
            self.createTestCaseWithGivenIdString("tests.unit.foo.FooTest.testAlwaysFails")
        ])
        self.meta.extract_from_suite(suite)
        self.assertEquals(["timelinelib.bar", "timelinelib.foo"], self.meta.get_modules())

    def createTestCaseWithGivenIdString(self, id_str):
        test_case = Mock()
        test_case.id.return_value = id_str
        return test_case


class SuiteMetadata(object):

    def __init__(self):
        self.modules = {}
        self.ill_formed_tests = []

    def extract_from_suite(self, suite):
        for item in suite:
            if isinstance(item, unittest.TestSuite):
                self.extract_from_suite(item)
            else:
                self._extract_from_test(item)

    def get_modules(self):
        tmp_modules = self.modules.keys()[:]
        tmp_modules.sort()
        return tmp_modules

    def get_classes(self, module):
        tmp_classes = self.modules[module].keys()[:]
        tmp_classes.sort()
        return tmp_classes

    def get_test_stories(self, module, test_class):
        return self.modules[module][test_class]

    def get_ill_formed_tests(self):
        return self.ill_formed_tests

    def _extract_from_test(self, test):
        def is_well_formed(test_id):
            split = test_id.split(".")
            if split[0] != "tests":
                return False
            if split[1] != "unit":
                return False
            if not split[-1].startswith("test"):
                return False
            if not (split[-2].startswith("Test") or split[-2].endswith("Test")):
                return False
            return True
        if is_well_formed(test.id()):
            module_name = "timelinelib." + ".".join(test.id().split(".")[2:-2])
            class_name = test.id().split(".")[-2].replace("Test", "")
            test_desc = self._storify_test_name(test.id())
            if not module_name in self.modules:
                self.modules[module_name] = {}
            if not class_name in self.modules[module_name]:
                self.modules[module_name][class_name] = []
            self.modules[module_name][class_name].append(test_desc)
        else:
            self.ill_formed_tests.append(test.id())

    def _storify_test_name(self, test_name):
        compact_description = test_name.split(".")[-1]
        split = re.split(r"([A-Z][a-z]+)", compact_description)
        clean_split = [x.lower() for x in split if x != ""][1:]
        return " ".join(clean_split)


def print_story(suite_metadata):
    if len(sys.argv) > 1:
        module = ".".join(sys.argv[1].split(".")[:-1])
        test_class = sys.argv[1].split(".")[-1]
        try:
            test_stories = suite_metadata.get_test_stories(module, test_class)
        except Exception:
            print "Unable to find %s" % sys.argv[1]
        else:
            print "%s:" % sys.argv[1]
            print
            for test in test_stories:
                print "  * %s" % test
    else:
        print "TIMELINE SPECIFICATION".center(79)
        print datetime.now().strftime("%d %B %Y").center(79)
        for module in suite_metadata.get_modules():
            print
            print "%s:" % module
            for test_class in suite_metadata.get_classes(module):
                print
                print "  %s:" % test_class
                print
                for test in suite_metadata.get_test_stories(module, test_class):
                    print "    * %s" % test
        print
        print "Ill-formed tests:"
        print
        for test in suite_metadata.get_ill_formed_tests():
            print "  * %s" % test


if __name__ == "__main__":
    if "--test" in sys.argv:
        sys.argv.remove("--test")
        unittest.main()
    else:
        from run import create_test_suite
        suite_metadata = SuiteMetadata()
        suite_metadata.extract_from_suite(create_test_suite())
        print_story(suite_metadata)
