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

from timelinelib.time.timeline import TimelineDelta
import timelinelib.time.timeline as timeline


class TimeSpec(unittest.TestCase):

    def test_can_return_time_of_day(self):
        dt = timeline.Time(0, 0)
        self.assertEqual(dt.get_time_of_day(), (0, 0, 0))

        dt = timeline.Time(0, 1)
        self.assertEqual(dt.get_time_of_day(), (0, 0, 1))

        dt = timeline.Time(0, 61)
        self.assertEqual(dt.get_time_of_day(), (0, 1, 1))

        dt = timeline.Time(0, 60 * 60 * 2 + 60 * 3 + 5)
        self.assertEqual(dt.get_time_of_day(), (2, 3, 5))

    def test_add(self):
        self.assertEqual(timeline.Time(10, 61) + TimelineDelta(9),
                timeline.Time(10, 70))
        self.assertEqual(timeline.Time(10, 61) + TimelineDelta(24 * 60 * 60),
                timeline.Time(11, 61))

    def test_sub(self):
        self.assertEqual(timeline.Time(10, 61) - TimelineDelta(1),
                         timeline.Time(10, 60))
        self.assertEqual(timeline.Time(10, 0) - TimelineDelta(1),
                         timeline.Time(9, 24 * 60 * 60 - 1))
        self.assertEqual(timeline.Time(10, 0) - timeline.Time(5, 0),
                         TimelineDelta(5 * 24 * 60 * 60))
        self.assertEqual(timeline.Time(10, 5) - timeline.Time(5, 0),
                         TimelineDelta(5 * 24 * 60 * 60 + 5))
        self.assertEqual(timeline.Time(10, 5) - timeline.Time(5, 10),
                         TimelineDelta(4 * 24 * 60 * 60 + (24 * 60 * 60 - 5)))

    def test_rejects_invalid_times(self):
        self.assertRaises(ValueError, timeline.Time, -1, 0)
        self.assertRaises(ValueError, timeline.Time, 0, -1)
        self.assertRaises(ValueError, timeline.Time, 0, 24*60*60)


class TimelineDeltaSpec(unittest.TestCase):

    def test_div(self):
        self.assertEqual(2.5, TimelineDelta(5) / TimelineDelta(2))

    def test_sub(self):
        self.assertEqual(TimelineDelta(2) - TimelineDelta(1), TimelineDelta(1))

    def test_mul(self):
        self.assertEqual(TimelineDelta(2), TimelineDelta(5) * 0.5)
        self.assertEqual(TimelineDelta(2), 0.5 * TimelineDelta(5))

    def test_negate(self):
        self.assertEqual(TimelineDelta(-2), -TimelineDelta(2))
