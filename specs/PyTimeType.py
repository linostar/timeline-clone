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


import unittest
import datetime

from mock import Mock

from timelinelib.time import PyTimeType


class PyTimeTypeSpec(unittest.TestCase):

    def setUp(self):
        self.time_type = PyTimeType()

    def testConvertsTimeToString(self):
        self.assertEquals(
            "2010-8-31 13:44:0",
            self.time_type.time_string(datetime.datetime(2010, 8, 31, 13, 44)))

    def testParsesTimeFromString(self):
        self.assertEquals(
            datetime.datetime(2010, 8, 31, 13, 44),
            self.time_type.parse_time("2010-8-31 13:44:0"))

    def testRaisesValueErrorWhenParsingInvalidTime(self):
        self.assertRaises(
            ValueError,
            self.time_type.parse_time, "2010-31-31 0:0:0")

    def testRaisesValueErrorWhenParsingBadlyFormattedTime(self):
        self.assertRaises(
            ValueError,
            self.time_type.parse_time, "2010-31-hello 0:0:0")
