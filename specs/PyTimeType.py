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
import calendar

from mock import Mock

from timelinelib.time import PyTimeType
from timelinelib.db.objects import TimePeriod


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

    def testFormatsPeriodToString(self):
        time_period = TimePeriod(self.time_type, 
                                 datetime.datetime(2010, 8, 01, 13, 44),
                                 datetime.datetime(2010, 8, 02, 13, 30))
        # TODO: Make month name same on all os and tests
        month = calendar.month_abbr[8]
        self.assertEquals(
            u"1 %s 2010 13:44 to 2 %s 2010 13:30" % (month, month),
            self.time_type.format_period(time_period))

    def testReturnsMinTime(self):
        self.assertEquals(datetime.datetime(10, 1, 1), 
                          self.time_type.get_min_time())

    def testReturnsMaxTime(self):
        self.assertEquals(datetime.datetime(9990, 1, 1), 
                          self.time_type.get_max_time())
