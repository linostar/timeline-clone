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
from timelinelib.time.gregorian import timeline_date_time_to_gregorian


class GregorianSpec(unittest.TestCase):

    def test_can_convert_from_timeline_date_time_to_gregorian(self):
        timeline_date_time = TimelineDateTime(julian_day=0, seconds=0)
        gregorian = timeline_date_time_to_gregorian(timeline_date_time)
        self.assertEquals(gregorian.to_tuple(), (-4713, 11, 24, 0, 0, 0))

        timeline_date_time = TimelineDateTime(julian_day=1, seconds=0)
        gregorian = timeline_date_time_to_gregorian(timeline_date_time)
        self.assertEquals(gregorian.to_tuple(), (-4713, 11, 25, 0, 0, 0))
        
        
