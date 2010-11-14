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

from timelinelib.time import PyTimeType
from timelinelib.time.typeinterface import TimeType
from timelinelib.db.objects import TimePeriod


class ATime(object):

    def __init__(self, num):
        self.num = num

    def __eq__(self, other):
        return isinstance(other, ATime) and self.num == other.num

    def __ne__(self, ohter):
        return not (self == other)

    def __add__(self, other):
        if isinstance(other, ADelta):
            return ATime(self.num + other.num)
        raise Exception("Only time+delta supported")

    def __sub__(self, other):
        if isinstance(other, ATime):
            return ADelta(self.num - other.num)
        elif isinstance(other, ADelta):
            return ATime(self.num - other.num)
        raise Exception("Only time-time and time-delta supported")

    def __lt__(self, other):
        return self.num < other.num


class ADelta(object):

    def __init__(self, num):
        self.num = num

    def __eq__(self, other):
        return isinstance(other, ADelta) and self.num == other.num

    def __ne__(self, ohter):
        return not (self == other)

    def __div__(self, other):
        if isinstance(other, int):
            return ADelta(int(self.num/other))
        raise Exception("Only delta/int supported")


class ATimeType(TimeType):

    def get_min_time(self):
        return ATime(0)

    def get_max_time(self):
        return ATime(100)

    def get_zero_delta(self):
        return ADelta(0)


class time_period_spec(unittest.TestCase):

    def test_creating_period_with_too_small_start_time_should_fail(self):
        self.assertRaises(ValueError, TimePeriod,
                          ATimeType(), ATime(-1), ATime(5))

    def test_creating_period_with_too_large_end_time_should_fail(self):
        self.assertRaises(ValueError, TimePeriod,
                          ATimeType(), ATime(0), ATime(150))

    def test_creating_period_with_end_before_start_should_fail(self):
        self.assertRaises(ValueError, TimePeriod,
                          ATimeType(), ATime(50), ATime(10))

    def test_delta_should_return_time_specific_delta(self):
        tp = TimePeriod(ATimeType(), ATime(0), ATime(4))
        self.assertEquals(ADelta(4), tp.delta())

    def test_mean_time_should_return_time_specific_time(self):
        tp = TimePeriod(ATimeType(), ATime(0), ATime(4))
        self.assertEquals(ATime(2), tp.mean_time())

    def test_center_should_center_period_around_time(self):
        tp = TimePeriod(ATimeType(), ATime(0), ATime(4))
        tp.center(ATime(5))
        self.assertEquals(
            tp,
            TimePeriod(ATimeType(), ATime(3), ATime(7)))

    def test_center_before_lower_limit_should_make_period_start_there(self):
        tp = TimePeriod(ATimeType(), ATime(10), ATime(14))
        tp.center(ATime(-5))
        self.assertEquals(
            tp,
            TimePeriod(ATimeType(), ATime(0), ATime(4)))

    def test_center_after_upper_limit_should_make_period_end_there(self):
        tp = TimePeriod(ATimeType(), ATime(10), ATime(14))
        tp.center(ATime(200))
        self.assertEquals(
            tp,
            TimePeriod(ATimeType(), ATime(96), ATime(100)))


class TimePeriodSpec(unittest.TestCase):

    def testFormatsPeriodUsingTimeType(self):
        time_period = TimePeriod(PyTimeType(), 
                                 datetime.datetime(2010, 8, 01, 13, 44),
                                 datetime.datetime(2010, 8, 02, 13, 30))
        # TODO: Make month name same on all os and tests
        month = calendar.month_abbr[8]
        self.assertEquals(u"1 %s 2010 13:44 to 2 %s 2010 13:30" % (month, month), 
                          time_period.get_label())
