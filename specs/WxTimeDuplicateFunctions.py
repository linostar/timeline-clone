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
from timelinelib.time import WxTimeType
from timelinelib.time.wxtime import move_period_num_days
from timelinelib.time.wxtime import move_period_num_months
from timelinelib.time.wxtime import move_period_num_weeks
from timelinelib.time.wxtime import move_period_num_years


class WxTimeDuplicateFunctionsSpec(unittest.TestCase):

    def test_move_period_num_days_adds_given_number_of_days(self):
        new_period = move_period_num_days(
            period(start(2010, 1, 1), end(2010, 1, 30)),
            6)
        self.assertEquals(
            period(start(2010, 1, 7), end(2010, 2, 5)),
            new_period)

    def test_move_period_num_weeks_adds_given_number_of_weeks(self):
        new_period = move_period_num_weeks(
            period(start(2010, 12, 20), end(2010, 12, 31)),
            -3)
        self.assertEquals(
            period(start(2010, 11, 29), end(2010, 12, 10)),
            new_period)

    def test_move_period_num_months_adds_given_number_of_months(self):
        new_period = move_period_num_months(
            period(start(2010, 1, 1), end(2010, 1, 5)),
            2)
        self.assertEquals(
            period(start(2010, 3, 1), end(2010, 3, 5)),
            new_period)

    def test_move_period_num_months_can_handle_year_boundries(self):
        new_period = move_period_num_months(
            period(start(2010, 1, 1), end(2010, 1, 5)),
            -2)
        self.assertEquals(
            period(start(2009, 11, 1), end(2009, 11, 5)),
            new_period)

    def test_move_period_num_months_returns_none_if_day_does_not_exist(self):
        new_period = move_period_num_months(
            period(start(2010, 1, 31), end(2010, 3, 15)),
            1)
        self.assertEquals(None, new_period)

    def test_move_period_num_years_adds_given_number_of_years(self):
        new_period = move_period_num_years(
            period(start(2010, 1, 1), end(2010, 1, 5)),
            1)
        self.assertEquals(
            period(start(2011, 1, 1), end(2011, 1, 5)),
            new_period)

    def test_move_period_num_years_returns_none_if_day_does_not_exist(self):
        new_period = move_period_num_years(
            period(start(2012, 2, 29), end(2012, 3, 5)),
            1)
        self.assertEquals(None, new_period)


def period(start, end):
    return TimePeriod(WxTimeType(), start, end)

def time(year, month, day, hour=15, minute=30, second=5):
    return wx.DateTimeFromDMY(day, month-1, year, hour, minute, second)

start = time

end = time
