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

from timelinelib.time.timeline import *


class TimeSpec(unittest.TestCase):

    def test_can_return_time_of_day(self):
        self.assertEqual(
            Time(0, 0).get_time_of_day(),
            (0, 0, 0))
        self.assertEqual(
            Time(0, 1).get_time_of_day(),
            (0, 0, 1))
        self.assertEqual(
            Time(0, 61).get_time_of_day(),
            (0, 1, 1))
        self.assertEqual(
            Time(0, 60 * 60 * 2 + 60 * 3 + 5).get_time_of_day(),
            (2, 3, 5))

    def test_add(self):
        self.assertEqual(
            Time(10, 61) + delta_from_seconds(9),
            Time(10, 70))
        self.assertEqual(
            Time(10, 61) + delta_from_days(1),
            Time(11, 61))

    def test_sub(self):
        self.assertEqual(
            Time(10, 61) - delta_from_seconds(1),
            Time(10, 60))
        self.assertEqual(
            Time(10, 0) - delta_from_seconds(1),
            Time(9, 24 * 60 * 60 - 1))
        self.assertEqual(
            Time(10, 0) - Time(5, 0),
            delta_from_seconds(5 * 24 * 60 * 60))
        self.assertEqual(
            Time(10, 5) - Time(5, 0),
            delta_from_seconds(5 * 24 * 60 * 60 + 5))
        self.assertEqual(
            Time(10, 5) - Time(5, 10),
            delta_from_seconds(4 * 24 * 60 * 60 + (24 * 60 * 60 - 5)))

    def test_rejects_invalid_times(self):
        self.assertRaises(ValueError, Time, -1, 0)
        self.assertRaises(ValueError, Time, 0, -1)
        self.assertRaises(ValueError, Time, 0, 24*60*60)


class TimeDeltaSpec(unittest.TestCase):

    def test_can_create(self):
        self.assertEqual(delta_from_seconds(5), TimeDelta(5))
        self.assertEqual(delta_from_days(5), TimeDelta(5*24*60*60))

    def test_div(self):
        self.assertEqual(2.5, TimeDelta(5) / TimeDelta(2))

    def test_sub(self):
        self.assertEqual(TimeDelta(2) - TimeDelta(1), TimeDelta(1))

    def test_mul(self):
        self.assertEqual(TimeDelta(2), TimeDelta(5) * 0.5)
        self.assertEqual(TimeDelta(2), 0.5 * TimeDelta(5))

    def test_negate(self):
        self.assertEqual(TimeDelta(-2), -TimeDelta(2))
