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

import wx

from timelinelib.db.objects import TimePeriod
from timelinelib.monthnames import ABBREVIATED_ENGLISH_MONTH_NAMES
from timelinelib.time import WxTimeType
from timelinelib.time.wxtime import move_period_num_days
from timelinelib.time.wxtime import move_period_num_months
from timelinelib.time.wxtime import move_period_num_weeks
from timelinelib.time.wxtime import move_period_num_years


class WxTimeDuplicateFunctionsSpec(unittest.TestCase):

    def test_move_period_num_days_adds_given_number_of_days(self):
        a_period = period("1 Jan 2010", "30 Jan 2010")
        new_period = move_period_num_days(a_period, 6)
        self.assertEquals(period("7 Jan 2010", "5 Feb 2010"), new_period)

    def test_move_period_num_weeks_adds_given_number_of_weeks(self):
        a_period = period("20 Dec 2010", "31 Dec 2010")
        new_period = move_period_num_weeks(a_period, -3)
        self.assertEquals(period("29 Nov 2010", "10 Dec 2010"), new_period)

    def test_move_period_num_months_adds_given_number_of_months(self):
        a_period = period("1 Jan 2010", "5 Jan 2010")
        new_period = move_period_num_months(a_period, 2)
        self.assertEquals(period("1 Mar 2010", "5 Mar 2010"), new_period)

    def test_move_period_num_months_can_handle_year_boundries(self):
        a_period = period("1 Jan 2010", "5 Jan 2010")
        new_period = move_period_num_months(a_period, -2)
        self.assertEquals(period("1 Nov 2009", "5 Nov 2009"), new_period)

    def test_move_period_num_months_returns_none_if_day_does_not_exist(self):
        a_period = period("31 Jan 2010", "15 Mar 2010")
        new_period = move_period_num_months(a_period, 1)
        self.assertEquals(None, new_period)

    def test_move_period_num_years_adds_given_number_of_years(self):
        a_period = period("1 Jan 2010", "5 Jan 2010")
        new_period = move_period_num_years(a_period, 1)
        self.assertEquals(period("1 Jan 2011", "5 Jan 2011"), new_period)

    def test_move_period_num_years_returns_none_if_day_does_not_exist(self):
        a_period = period("29 Feb 2012", "5 Mar 2012")
        new_period = move_period_num_years(a_period, 1)
        self.assertEquals(None, new_period)


def period(start, end):
    return TimePeriod(WxTimeType(), human_to_wx(start), human_to_wx(end))

def human_to_wx(human_time):
    day_part, month_part, year_part = human_time.split(" ")
    day = int(day_part)
    month = ABBREVIATED_ENGLISH_MONTH_NAMES.index(month_part) + 1
    year = int(year_part)
    return wx_time(year, month, day)

def wx_time(year, month, day, hour=15, minute=30, second=5):
    return wx.DateTimeFromDMY(day, month-1, year, hour, minute, second)
