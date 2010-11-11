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
from timelinelib.db.objects import TimePeriod


class TimePeriodSpec(unittest.TestCase):

    def testFormatsPeriodUsingTimeType(self):
        time_period = TimePeriod(PyTimeType(), 
                                 datetime.datetime(2010, 8, 01, 13, 44),
                                 datetime.datetime(2010, 8, 02, 13, 30))
        # TODO: Make month name same on all os and tests
        month = calendar.month_abbr[8]
        self.assertEquals(u"1 %s 2010 13:44 to 2 %s 2010 13:30" % (month, month), 
                          time_period.get_label())
