# Copyright (C) 2009  Rickard Lindberg, Roger Lindberg
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

from datetime import datetime as dt
from datetime import timedelta

from timelinelib.db.objects import TimePeriod


class TestTimePeriod(unittest.TestCase):

    def setUp(self):
        self.lower = dt(10, 1, 1)
        self.upper = dt(9990, 1, 1)

    def testDelta(self):
        tp = TimePeriod(dt(2009, 8, 25), dt(2009, 8, 30))
        self.assertEquals(tp.delta(), timedelta(days=5))

    def testMeanTime(self):
        tp = TimePeriod(dt(2009, 8, 25), dt(2009, 8, 29))
        self.assertEquals(tp.mean_time(), dt(2009, 8, 27))

    def testLowerLimit(self):
        below_lower = self.lower - timedelta(microseconds=1)
        TimePeriod(self.lower, self.lower)
        self.assertRaises(ValueError, TimePeriod, below_lower, below_lower)

    def testUpperLimit(self):
        above_upper = self.upper + timedelta(microseconds=1)
        TimePeriod(self.upper, self.upper)
        self.assertRaises(ValueError, TimePeriod, above_upper, above_upper)

    def testCenter(self):
        tp = TimePeriod(dt(2009, 8, 30), dt(2009, 8, 31))
        tp.center(dt(2009, 8, 31, 12, 0, 0))
        self.assertEquals(tp.start_time, dt(2009, 8, 31))
        self.assertEquals(tp.end_time, dt(2009, 9, 1))

    def testCenterBeyondLower(self):
        end_time = self.lower + timedelta(days=1)
        tp = TimePeriod(self.lower, self.lower + timedelta(days=1))
        tp.center(self.lower)
        self.assertEquals(tp.start_time, self.lower)
        self.assertEquals(tp.end_time, end_time)

    def testCenterBeyondUpper(self):
        start_time = self.upper - timedelta(days=1)
        tp = TimePeriod(start_time, self.upper)
        tp.center(self.upper)
        self.assertEquals(tp.start_time, start_time)
        self.assertEquals(tp.end_time, self.upper)
