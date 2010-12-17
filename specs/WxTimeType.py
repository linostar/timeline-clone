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
import calendar

import wx
from mock import Mock

from timelinelib.time import WxTimeType
from timelinelib.db.objects import TimePeriod


class WxTimeTypeSpec(unittest.TestCase):

    def setUp(self):
        self.time_type = WxTimeType()

    def testConvertsTimeToString(self):
        self.assertEquals(
            u"2010-08-31 13:44:00",
            self.time_type.time_string(wx.DateTimeFromDMY(31, 7, 2010, 13, 44)))

    def testParsesTimeFromString(self):
        tm1 = wx.DateTimeFromDMY(31, 7, 2010, 13, 44)
        tm2 = self.time_type.parse_time("2010-08-31 13:44:00")
        self.assertEquals(tm1, tm2)

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
                                 wx.DateTimeFromDMY(1, 7, 2010, 13, 44),
                                 wx.DateTimeFromDMY(2, 7, 2010, 13, 30))
        self.assertEquals(
            u"01 %s 2010 13:44 to 02 %s 2010 13:30" % (_("Aug"), _("Aug")),
            self.time_type.format_period(time_period))

    def testReturnsMinTime(self):
        tm1 = wx.DateTimeFromDMY(1, 0, -4700)
        tm2 = self.time_type.get_min_time()[0]
        self.assertEquals(tm1, tm2) 

    def testReturnsMaxTime(self):
        tm1 = wx.DateTimeFromDMY(1, 0, 120000)
        tm2 = self.time_type.get_max_time()[0]
        self.assertEquals(tm1, tm2) 

    def testReturnsMarginDelta(self):
        delta = wx.TimeSpan.Days(days=48)
        margin_delta = self.time_type.margin_delta(delta)
        self.assertEquals(wx.TimeSpan.Days(2), margin_delta) 
        
    def testReturnsHalfDelta(self):
        delta = wx.TimeSpan.Days(100 * 365)
        half_delta = self.time_type.half_delta(delta)
        self.assertEquals(wx.TimeSpan.Days(50 * 365).GetMilliseconds(), 
                          half_delta.GetMilliseconds()) 
