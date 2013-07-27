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


import datetime
import unittest

import timelinelib.calendar.gregorian as gregorian
import timelinelib.time.timeline as timeline


class GregorianSpec(unittest.TestCase):

    def test_rejects_invalid_dates(self):
        self.assertRaises(ValueError, gregorian.Gregorian, 2013, 0, 1, 0, 0, 0)

    def test_can_replace(self):
        g = gregorian.Gregorian(2013, 7, 12, 10, 16, 12)
        self.assertEquals(g.replace(year=1990),
                          gregorian.Gregorian(1990, 7, 12, 10, 16, 12))
        self.assertEquals(g.replace(month=6),
                          gregorian.Gregorian(2013, 6, 12, 10, 16, 12))
        self.assertEquals(g.replace(year=1990, month=6),
                          gregorian.Gregorian(1990, 6, 12, 10, 16, 12))
        self.assertRaises(ValueError, g.replace, month=13)


class GregorianConversionsSpec(unittest.TestCase):

    def test_can_convert_from_timeline_time_to_gregorian(self):
        self.assertEquals(
            gregorian.from_time(timeline.Time(julian_day=0, seconds=0)),
            gregorian.Gregorian(-4713, 11, 24, 0, 0, 0))
        self.assertEquals(
            gregorian.from_time(timeline.Time(julian_day=1, seconds=0)),
            gregorian.Gregorian(-4713, 11, 25, 0, 0, 0))

    def test_can_convert_from_gregorian_to_timeline_time(self):
        self.assertEquals(
            gregorian.Gregorian(-4713, 11, 24, 0, 0, 0).to_time(),
            timeline.Time(julian_day=0, seconds=0))
        self.assertEquals(
            gregorian.Gregorian(-4713, 11, 25, 0, 0, 0).to_time(),
            timeline.Time(julian_day=1, seconds=0))

    def test_roundtrip_julian_day_conversions(self):
        for julian_day in range(100):
            (year, month, day) = gregorian.from_julian_day(julian_day)
            roundtrip = gregorian.to_julian_day(year, month, day)
            self.assertEquals(roundtrip, julian_day)

    def test_roundtrip_gregorian_dates_conversions(self):
        dates = [
            (2013, 1, 1),
            (2013, 1, 31),
        ]
        for gregorian_date in dates:
            (year, month, day) = gregorian_date
            julian_day = gregorian.to_julian_day(year, month, day)
            roundtrip = gregorian.from_julian_day(julian_day)
            self.assertEquals(roundtrip, gregorian_date)

    def test_works_same_as_python_date(self):
        py_date = datetime.date(1900, 1, 1)
        jd = gregorian.to_julian_day(1900, 1, 1)
        for i in range(365*200):
            (y, m, d) = gregorian.from_julian_day(jd)
            self.assertEquals(py_date, datetime.date(y, m, d))
            py_date += datetime.timedelta(days=1)
            jd += 1


class GregorianPrimitivesSpec(unittest.TestCase):

    def test_is_valid(self):
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

    def test_is_leap_year(self):
        self.assertFalse(gregorian.is_leap_year(2013))
        self.assertFalse(gregorian.is_leap_year(1900))
        self.assertTrue(gregorian.is_leap_year(2016))
        self.assertTrue(gregorian.is_leap_year(2000))
