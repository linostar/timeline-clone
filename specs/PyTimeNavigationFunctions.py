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
from timelinelib.db.objects import TimePeriod
from timelinelib.time.pytime import fit_day_fn


class PyTimeNavigationFunctionsSpec(unittest.TestCase):

    def _call_fn_with_period(self, fn, start, end):
        self.time_period = TimePeriod(PyTimeType(), start, end)
        fn(None, self.time_period, self._nav_fn)

    def _nav_fn(self, fn):
        fn(self.time_period)

    def _assertTimePeriodEquals(self, start, end):
        self.assertEquals(start, self.time_period.start_time)
        self.assertEquals(end, self.time_period.end_time)

    def testFitDayShouldDisplayTheDayThatIsInTheCenter(self):
        self._call_fn_with_period(
            fit_day_fn, 
            datetime.datetime(2010, 1, 1, 0, 0, 0),
            datetime.datetime(2010, 1, 2, 12, 0, 0))
        self._assertTimePeriodEquals(
            datetime.datetime(2010, 1, 1, 0, 0, 0),
            datetime.datetime(2010, 1, 2, 0, 0, 0))
