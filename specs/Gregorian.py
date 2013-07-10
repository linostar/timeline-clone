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
import timelinelib.time.gregorian as gregorian


class GregorianSpec(unittest.TestCase):

    def test_can_convert_from_timeline_date_time_to_gregorian(self):
        timeline_date_time = TimelineDateTime(julian_day=0, seconds=0)
        gregorian = timeline_date_time_to_gregorian(timeline_date_time)
        self.assertEquals(gregorian.to_tuple(), (-4713, 11, 24, 0, 0, 0))

        timeline_date_time = TimelineDateTime(julian_day=1, seconds=0)
        gregorian = timeline_date_time_to_gregorian(timeline_date_time)
        self.assertEquals(gregorian.to_tuple(), (-4713, 11, 25, 0, 0, 0))

    def test_gregorian_valid(self):
        self.assertTrue(gregorian.is_valid(2013, 1, 1))
        self.assertFalse(gregorian.is_valid(2013, 0, 1))
        self.assertFalse(gregorian.is_valid(2013, 13, 1))
        self.assertFalse(gregorian.is_valid(2013, 1, 0))
        self.assertFalse(gregorian.is_valid(2013, 1, 32))
        self.assertFalse(gregorian.is_valid(2013, 2, 30))

    def test_days_in_month(self):
        self.assertEqual(31, gregorian.days_in_month(2013, 1))
        self.assertEqual(28, gregorian.days_in_month(2013, 2))
        self.assertEqual(31, gregorian.days_in_month(2013, 3))
        self.assertEqual(30, gregorian.days_in_month(2013, 4))
        self.assertEqual(31, gregorian.days_in_month(2013, 5))
        self.assertEqual(30, gregorian.days_in_month(2013, 6))
        self.assertEqual(31, gregorian.days_in_month(2013, 7))
        self.assertEqual(31, gregorian.days_in_month(2013, 8))
        self.assertEqual(30, gregorian.days_in_month(2013, 9))
        self.assertEqual(31, gregorian.days_in_month(2013, 10))
        self.assertEqual(30, gregorian.days_in_month(2013, 11))
        self.assertEqual(31, gregorian.days_in_month(2013, 12))
        self.assertEqual(29, gregorian.days_in_month(2016, 2))

    def test_leap_year(self):
        self.assertFalse(gregorian.is_leap_year(2013))
        self.assertFalse(gregorian.is_leap_year(1900))
        self.assertTrue(gregorian.is_leap_year(2016))
        self.assertTrue(gregorian.is_leap_year(2000))
        
        
