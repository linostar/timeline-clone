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


import unittest
import wx

from timelinelib.time.timeline import Time
import timelinelib.calendar.gregorian as gregorian


class MonthNamesSpec(unittest.TestCase):

    def test_time_creation(self):
        STOP = 10
        STEP = 10000
        for i in range(0, STOP, STEP):
            tm1 = Time(i, 0)
            gt = gregorian.from_time(tm1)
            wt = wx.DateTime().SetJDN(i) 
            ws = "%d-%02d-%02d" % (wt.Year, wt.Month + 1, wt.Day)
            gs = "%d-%02d-%02d" % (gt.year, gt.month, gt.day)
            self.assertEqual(ws, gs)
            tm2 = gt.to_time()
            self.assertEqual(tm1, tm2)
