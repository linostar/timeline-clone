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
import mock

from timelinelib.db.objects import TimePeriod
from timelinelib.time import GregorianTimeType
from timelinelib.time.timeline import TimelineDateTime
from timelinelib.time.timeline import TimelineDelta
from timelinelib.time.gregorian import Gregorian
from timelinelib.time.gregorian import gregorian_to_timeline_date_time
from timelinelib.time.gregoriantime import StripWeek
from timelinelib.time.gregoriantime import StripYear
from timelinelib.time.gregoriantime import StripDecade
from timelinelib.time.gregoriantime import StripMonth
from timelinelib.time.gregoriantime import StripDay


class GregorianTimeTypeSpec(unittest.TestCase):

    def setUp(self):
        self.time_type = GregorianTimeType()

    def test_converts_time_to_string(self):
        self.assertEquals(
            "-4713-11-24 00:00:00",
            self.time_type.time_string(TimelineDateTime(julian_day=0, seconds=0)))

    def test_parses_time_from_string(self):
        self.assertEquals(
            TimelineDateTime(julian_day=0, seconds=0),
            self.time_type.parse_time("-4713-11-24 00:00:00"))

    def test_raises_ValueError_when_parsing_invalid_time(self):
        self.assertRaises(
            ValueError,
            self.time_type.parse_time, "2010-31-31 0:0:0")

    def test_raises_ValueError_when_parsing_badly_formatted_time(self):
        self.assertRaises(
            ValueError,
            self.time_type.parse_time, "2010-31-hello 0:0:0")

    def test_formats_period_to_string(self):
        time_period = TimePeriod(self.time_type,
                                 self.time_type.parse_time("2010-08-01 13:44:00"),
                                 self.time_type.parse_time("2010-08-02 13:30:00"))
        self.assertEquals(
            u"1 %s 2010 13:44 to 2 %s 2010 13:30" % (_("Aug"), _("Aug")),
            self.time_type.format_period(time_period))

    def test_returns_min_time(self):
        self.assertEquals(TimelineDateTime(0, 0), self.time_type.get_min_time()[0])

    def test_returns_max_time(self):
        self.assertEquals(self.time_type.parse_time("9990-01-01 00:00:00"),
                          self.time_type.get_max_time()[0])

    def test_returns_half_delta(self):
        delta = TimelineDelta(4)
        half_delta = self.time_type.half_delta(delta)
        self.assertEquals(TimelineDelta(2), half_delta)

    def test_returns_margin_delta(self):
        delta = TimelineDelta(48)
        margin_delta = self.time_type.margin_delta(delta)
        self.assertEquals(TimelineDelta(2), margin_delta)

    def test_event_date_string_method(self):
        self.assertEquals(
            "2010-08-01",
            self.time_type.event_date_string(self.time_type.parse_time("2010-08-01 13:44:22")))

    def test_event_time_string_method(self):
        self.assertEquals(
            "13:44",
            self.time_type.event_time_string(self.time_type.parse_time("2010-08-01 13:44:22")))

    def test_eventtimes_equals_method_when_equals(self):
        self.assertTrue(
            self.time_type.eventtimes_equals(self.time_type.parse_time("2010-08-01 13:44:22"),
                                             self.time_type.parse_time("2010-08-01 13:44:00")))

    def test_eventtimes_equals_method_when_not_equals(self):
        self.assertFalse(
            self.time_type.eventtimes_equals(self.time_type.parse_time("2010-08-01 13:44:22"),
                                             self.time_type.parse_time("2010-07-01 13:44:22")))

    def test_div_deltas(self):
        result = self.time_type.div_timedeltas(TimelineDelta(5), TimelineDelta(2))
        self.assertEqual(2.5, result)

    def test_get_time_at_x(self):
        time_period = TimePeriod(self.time_type,
                                 self.time_type.parse_time("2010-08-01 00:00:00"),
                                 self.time_type.parse_time("2010-08-02 00:00:00"))
        dt = self.time_type.get_time_at_x(time_period, 0.5)
        self.assertEqual(dt, self.time_type.parse_time("2010-08-01 12:00:00"))

    def test_get_weekday(self):
        dt = self.time_type.parse_time("2013-07-10 00:00:00")
        self.assertEqual(2, dt.get_day_of_week())


class GregorianStripWeekSpec(unittest.TestCase):

    def setUp(self):
        self.time_type = GregorianTimeType()
        self.config = mock.Mock()
        self.strip = StripWeek(self.config)

    def test_start(self):
        self.config.week_start = "sunday"
        self.assertEqual(
            self.strip.start(self.time_type.parse_time("2013-07-10 00:00:00")),
            self.time_type.parse_time("2013-07-07 00:00:00"))
        self.config.week_start = "monday"
        self.assertEqual(
            self.strip.start(self.time_type.parse_time("2013-07-10 00:00:00")),
            self.time_type.parse_time("2013-07-08 00:00:00"))

    def test_increment(self):
        self.assertEqual(
            self.strip.increment(self.time_type.parse_time("2013-07-07 00:00:00")),
            self.time_type.parse_time("2013-07-14 00:00:00"))

    def test_label(self):
        self.config.week_start = "sunday"
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 00:00:00")),
            "")
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 00:00:00"), True),
            "7-13 %s 2013" % _("Jul"))
        self.config.week_start = "monday"
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 00:00:00"), True),
            "%s 27 (1-7 %s 2013)" % (_("Week"), _("Jul")))


class GregorianStripDaySpec(unittest.TestCase):

    def setUp(self):
        self.time_type = GregorianTimeType()
        self.strip = StripDay()

    def test_start(self):
        self.assertEqual(
            self.strip.start(self.time_type.parse_time("2013-07-10 12:33:15")),
            self.time_type.parse_time("2013-07-10 00:00:00"))

    def test_increment(self):
        self.assertEqual(
            self.strip.increment(self.time_type.parse_time("2013-07-10 00:00:00")),
            self.time_type.parse_time("2013-07-11 00:00:00"))

    def test_label(self):
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 00:00:00")),
            "7")
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 00:00:00"), True),
            "7 %s 2013" % _("Jul"))


class GregorianStripMonthSpec(unittest.TestCase):

    def setUp(self):
        self.time_type = GregorianTimeType()
        self.strip = StripMonth()

    def test_start(self):
        self.assertEqual(
            self.strip.start(self.time_type.parse_time("2013-07-10 12:33:15")),
            self.time_type.parse_time("2013-07-01 00:00:00"))

    def test_increment(self):
        self.assertEqual(
            self.strip.increment(self.time_type.parse_time("2013-07-01 00:00:00")),
            self.time_type.parse_time("2013-08-01 00:00:00"))

    def test_label(self):
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 00:00:00")),
            _("Jul"))
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 00:00:00"), True),
            "%s 2013" % _("Jul"))


class GregorianStripYearSpec(unittest.TestCase):

    def setUp(self):
        self.time_type = GregorianTimeType()
        self.strip = StripYear()

    def test_start(self):
        self.assertEqual(
            self.strip.start(self.time_type.parse_time("2013-07-10 12:33:15")),
            self.time_type.parse_time("2013-01-01 00:00:00"))

    def test_increment(self):
        self.assertEqual(
            self.strip.increment(self.time_type.parse_time("2013-01-01 00:00:00")),
            self.time_type.parse_time("2014-01-01 00:00:00"))

    def test_label(self):
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 00:00:00")),
            "2013")
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 00:00:00"), True),
            "2013")


class GregorianStripDecadeSpec(unittest.TestCase):

    def setUp(self):
        self.time_type = GregorianTimeType()
        self.strip = StripDecade()

    def test_start(self):
        self.assertEqual(
            self.strip.start(self.time_type.parse_time("2013-07-10 12:33:15")),
            self.time_type.parse_time("2010-01-01 00:00:00"))

    def test_increment(self):
        self.assertEqual(
            self.strip.increment(self.time_type.parse_time("2010-01-01 00:00:00")),
            self.time_type.parse_time("2020-01-01 00:00:00"))

    def test_label(self):
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 00:00:00")),
            "2010s")


class GregorianTimeTypeDeltaFormattingSpec(unittest.TestCase):

    def setUp(self):
        self.time_type = GregorianTimeType()

    def test_format_delta_method(self):
        time_period1 = TimePeriod(self.time_type,
                                  self.time_type.parse_time("2010-08-01 13:44:00"),
                                  self.time_type.parse_time("2010-08-01 13:44:00"))
        time_period2 = TimePeriod(self.time_type,
                                  self.time_type.parse_time("2010-08-02 13:44:00"),
                                  self.time_type.parse_time("2010-08-02 13:44:00"))
        delta = time_period2.start_time - time_period1.start_time
        self.assertEquals(u"1 %s" % _("day"), self.time_type.format_delta(delta))

    def test_format_one_minute_delta(self):
        delta = self.get_days_delta(days=0, hours=0, minutes=1)
        self.assertEquals(u"1 %s" % _("minute"), self.time_type.format_delta(delta))

    def test_format_two_minutes_delta(self):
        delta = self.get_days_delta(days=0, hours=0, minutes=2)
        self.assertEquals(u"2 %s" % _("minutes"), self.time_type.format_delta(delta))

    def test_format_one_hour_delta(self):
        delta = self.get_days_delta(days=0, hours=1, minutes=0)
        self.assertEquals(u"1 %s" % _("hour"), self.time_type.format_delta(delta))

    def test_format_two_hour_delta(self):
        delta = self.get_days_delta(days=0, hours=2, minutes=0)
        self.assertEquals(u"2 %s" % _("hours"), self.time_type.format_delta(delta))

    def test_format_one_day_delta(self):
        delta = self.get_days_delta(days=1, hours=0, minutes=0)
        self.assertEquals(u"1 %s" % _("day"), self.time_type.format_delta(delta))

    def test_format_two_days_delta(self):
        delta = self.get_days_delta(days=2, hours=0, minutes=0)
        self.assertEquals(u"2 %s" % _("days"), self.time_type.format_delta(delta))

    def test_format_one_hour_one_minute_delta(self):
        delta = self.get_days_delta(days=0, hours=1, minutes=1)
        self.assertEquals(u"1 %s 1 %s" % (_("hour"), _("minute")), self.time_type.format_delta(delta))

    def test_format_one_hour_two_minutes_delta(self):
        delta = self.get_days_delta(days=0, hours=1, minutes=2)
        self.assertEquals(u"1 %s 2 %s" % (_("hour"), _("minutes")), self.time_type.format_delta(delta))

    def test_format_one_day_one_hour_delta(self):
        delta = self.get_days_delta(days=1, hours=1, minutes=0)
        self.assertEquals(u"1 %s 1 %s" % (_("day"), _("hour")), self.time_type.format_delta(delta))

    def test_format_one_day_two_hour_delta(self):
        delta = self.get_days_delta(days=1, hours=2, minutes=0)
        self.assertEquals(u"1 %s 2 %s" % (_("day"), _("hours")), self.time_type.format_delta(delta))

    def test_format_two_days_two_hour_delta(self):
        delta = self.get_days_delta(days=2, hours=2, minutes=0)
        self.assertEquals(u"2 %s 2 %s" % (_("days"), _("hours")), self.time_type.format_delta(delta))

    def test_format_two_days_two_hour_one_minute_delta(self):
        delta = self.get_days_delta(days=2, hours=2, minutes=1)
        self.assertEquals(u"2 %s 2 %s 1 %s" % (_("days"), _("hours"), _("minute")), self.time_type.format_delta(delta))

    def test_format_two_days_two_hour_two_minutes_delta(self):
        delta = self.get_days_delta(days=2, hours=2, minutes=2)
        self.assertEquals(u"2 %s 2 %s 2 %s" % (_("days"), _("hours"), _("minutes")), self.time_type.format_delta(delta))

    def test_format_hundred_days_one_minute_delta(self):
        delta = self.get_days_delta(days=100, hours=0, minutes=0)
        self.assertEquals(u"100 %s" % _("days"), self.time_type.format_delta(delta))

    def test_format_2_years_2_months(self):
        time_period1 = self.create_point_period(1, 1, 1999, 0, 0)
        time_period2 = self.create_point_period(1, 3, 2001, 0, 0)
        delta = time_period2.start_time - time_period1.start_time
        self.assertEquals(u"790 %s" % _("days"), self.time_type.format_delta(delta))

    def test_format_overlapping_events(self):
        time_period1 = TimePeriod(self.time_type,
                                  self.time_type.parse_time("2010-08-01 13:44:00"),
                                  self.time_type.parse_time("2010-08-03 13:44:00"))
        time_period2 = TimePeriod(self.time_type,
                                  self.time_type.parse_time("2010-08-01 13:44:00"),
                                  self.time_type.parse_time("2010-08-03 13:44:00"))
        delta = time_period2.start_time - time_period1.end_time
        self.assertEquals("0", self.time_type.format_delta(delta))

    def create_point_period(self, day, month, year, hour, minute):
        dt = gregorian_to_timeline_date_time(Gregorian(year, month, day, hour, minute, 0))
        return TimePeriod(self.time_type, dt, dt)

    def get_days_delta(self, days=0, hours=0, minutes=0):
        return TimelineDelta(days * 24 * 60 *60 + hours * 60 * 60 + minutes * 60)
