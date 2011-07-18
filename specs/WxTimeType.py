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


import platform

import unittest

import wx

from timelinelib.time import WxTimeType
from timelinelib.time import try_to_create_wx_date_time_from_dmy
from timelinelib.db.objects import TimePeriod


class WxTimeTypeSpec(unittest.TestCase):

    def setUp(self):
        self.time_type = WxTimeType()

    def test_time_string_method(self):
        self.assertEquals(
            "2010-08-31 13:44:00",
            self.time_type.time_string(wx.DateTimeFromDMY(31, 7, 2010, 13, 44)))

    def test_event_date_string_method(self):
        self.assertEquals(
            "2010-08-31",
            self.time_type.event_date_string(wx.DateTimeFromDMY(31, 7, 2010, 13, 44, 22)))

    def test_event_time_string_method(self):
        self.assertEquals(
            "13:44",
            self.time_type.event_time_string(wx.DateTimeFromDMY(31, 7, 2010, 13, 44, 22)))

    def test_eventtimes_equals_method_when_equals(self):
        self.assertTrue(
            self.time_type.eventtimes_equals(wx.DateTimeFromDMY(31, 7, 2010, 13, 44, 22),
                                             wx.DateTimeFromDMY(31, 7, 2010, 13, 44, 00)))

    def test_eventtimes_equals_method_when_not_equals(self):
        self.assertFalse(
            self.time_type.eventtimes_equals(wx.DateTimeFromDMY(31, 7, 2010, 13, 44, 22),
                                             wx.DateTimeFromDMY(31, 6, 2010, 13, 44, 22)))
        
    def test_parse_time_method(self):
        self.assertEquals(
            wx.DateTimeFromDMY(31, 7, 2010, 13, 44),
            self.time_type.parse_time("2010-08-31 13:44:00"))

    def test_raises_ValueError_when_parsing_invalid_time(self):
        # This test don't run in windows
        if platform.system() != "Windows":
            self.assertRaises(
                ValueError,
                self.time_type.parse_time, "2010-31-31 0:0:0")

    def test_raises_ValueError_when_parsing_badly_formatted_time(self):
        self.assertRaises(
            ValueError,
            self.time_type.parse_time, "2010-31-hello 0:0:0")

    def test_format_period_method(self):
        time_period = TimePeriod(self.time_type, 
                                 wx.DateTimeFromDMY(1, 7, 2010, 13, 44),
                                 wx.DateTimeFromDMY(2, 7, 2010, 13, 30))
        self.assertEquals(
            u"01 %s 2010 13:44 to 02 %s 2010 13:30" % (_("Aug"), _("Aug")),
            self.time_type.format_period(time_period))

    def test_returns_year_4700_bc_as_min_time(self):
        self.assertEquals(
            wx.DateTimeFromDMY(1, 0, -4700),
            self.time_type.get_min_time()[0])

    def test_returns_year_120000_as_max_time(self):
        self.assertEquals(
            wx.DateTimeFromDMY(1, 0, 120000),
            self.time_type.get_max_time()[0])

    def test_returns_margin_delta(self):
        delta = wx.TimeSpan.Days(days=48)
        margin_delta = self.time_type.margin_delta(delta)
        self.assertEquals(wx.TimeSpan.Days(2), margin_delta) 
        
    def test_returns_half_delta(self):
        delta = wx.TimeSpan.Days(100 * 365)
        half_delta = self.time_type.half_delta(delta)
        self.assertEquals(wx.TimeSpan.Days(50 * 365).GetMilliseconds(), 
                          half_delta.GetMilliseconds()) 


class WxDateTimeConstructorSpec(unittest.TestCase):

    def testCreatesWxDateTimeIfDateIsValid(self):
        self.assertEquals(
            wx.DateTimeFromDMY(20, 7, 2010, 13, 44, 2),
            try_to_create_wx_date_time_from_dmy(20, 7, 2010, 13, 44, 2))

    def testDefaultsHourMinuteAndSecondToZero(self):
        self.assertEquals(
            wx.DateTimeFromDMY(20, 7, 2010, 0, 0, 0),
            try_to_create_wx_date_time_from_dmy(20, 7, 2010))
    
    def testRaisesValueErrorIfDateIsInvalid(self):
        # This test don't run in windows
        if platform.system() != "Windows":
            self.assertRaises(
                ValueError,
                try_to_create_wx_date_time_from_dmy, 40, 8, 2010)
