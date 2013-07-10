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

from timelinelib.time.timeline import TimelineDateTime


class TimelineDateTimeSpec(unittest.TestCase):

    def test_can_return_time_of_day(self):
        dt = TimelineDateTime(0, 0)
        self.assertEqual(dt.get_time_of_day(), (0, 0, 0))
        
        dt = TimelineDateTime(0, 1)
        self.assertEqual(dt.get_time_of_day(), (0, 0, 1))

        dt = TimelineDateTime(0, 61)
        self.assertEqual(dt.get_time_of_day(), (0, 1, 1))

        dt = TimelineDateTime(0, 60 * 60 * 2 + 60 * 3 + 5)
        self.assertEqual(dt.get_time_of_day(), (2, 3, 5))
