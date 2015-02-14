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

from specs.utils import gregorian_period
from timelinelib.calendar.gregorian import Gregorian
from timelinelib.data import TimePeriod
from timelinelib.time.gregoriantime import backward_fn
from timelinelib.time.gregoriantime import backward_one_month_fn
from timelinelib.time.gregoriantime import backward_one_week_fn
from timelinelib.time.gregoriantime import backward_one_year_fn
from timelinelib.time.gregoriantime import fit_century_fn
from timelinelib.time.gregoriantime import fit_day_fn
from timelinelib.time.gregoriantime import fit_decade_fn
from timelinelib.time.gregoriantime import fit_millennium_fn
from timelinelib.time.gregoriantime import fit_month_fn
from timelinelib.time.gregoriantime import fit_week_fn
from timelinelib.time.gregoriantime import fit_year_fn
from timelinelib.time.gregoriantime import forward_fn
from timelinelib.time.gregoriantime import forward_one_month_fn
from timelinelib.time.gregoriantime import forward_one_week_fn
from timelinelib.time.gregoriantime import forward_one_year_fn
from timelinelib.time.gregoriantime import GregorianTimeType
from timelinelib.time.gregoriantime import move_period_num_days
from timelinelib.time.gregoriantime import move_period_num_months
from timelinelib.time.gregoriantime import move_period_num_weeks
from timelinelib.time.gregoriantime import move_period_num_years
from timelinelib.time.gregoriantime import StripCentury
from timelinelib.time.gregoriantime import StripDay
from timelinelib.time.gregoriantime import StripDecade
from timelinelib.time.gregoriantime import StripHour
from timelinelib.time.gregoriantime import StripMonth
from timelinelib.time.gregoriantime import StripWeek
from timelinelib.time.gregoriantime import StripWeekday
from timelinelib.time.gregoriantime import StripYear
from timelinelib.time.gregoriantime import TimeOutOfRangeLeftError
from timelinelib.time.gregoriantime import TimeOutOfRangeRightError
from timelinelib.wxgui.dialogs.mainframe import MainFrame
import timelinelib.time.timeline as timeline


class GregorianTimeTypeSpec(unittest.TestCase):

    def setUp(self):
        self.time_type = GregorianTimeType()

    def test_converts_time_to_string(self):
        self.assertEqual(
            "-4713-11-24 00:00:00",
            self.time_type.time_string(timeline.Time(julian_day=0, seconds=0)))

    def test_parses_time_from_string(self):
        self.assertEqual(
            timeline.Time(julian_day=0, seconds=0),
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
        self.assertEqual(
            u"1 %s 2010 13:44 to 2 %s 2010 13:30" % (_("Aug"), _("Aug")),
            self.time_type.format_period(time_period))

    def test_returns_min_time(self):
        self.assertEqual(timeline.Time(0, 0), self.time_type.get_min_time()[0])

    def test_returns_max_time(self):
        self.assertEqual(self.time_type.parse_time("9990-01-01 00:00:00"),
                          self.time_type.get_max_time()[0])

    def test_returns_half_delta(self):
        self.assertEqual(
            self.time_type.half_delta(timeline.TimeDelta(4)),
            timeline.TimeDelta(2))

    def test_returns_margin_delta(self):
        self.assertEqual(
            self.time_type.margin_delta(timeline.TimeDelta(48)),
            timeline.TimeDelta(2))

    def test_event_date_string_method(self):
        self.assertEqual(
            "2010-08-01",
            self.time_type.event_date_string(self.time_type.parse_time("2010-08-01 13:44:22")))

    def test_event_time_string_method(self):
        self.assertEqual(
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
        self.assertEqual(
            self.time_type.div_timedeltas(timeline.TimeDelta(5), timeline.TimeDelta(2)),
            2.5)

    def test_get_time_at_x(self):
        time_period = TimePeriod(self.time_type,
                                 self.time_type.parse_time("2010-08-01 00:00:00"),
                                 self.time_type.parse_time("2010-08-02 00:00:00"))
        dt = self.time_type.get_time_at_x(time_period, 0.5)
        self.assertEqual(dt, self.time_type.parse_time("2010-08-01 12:00:00"))

    def test_get_weekday(self):
        dt = self.time_type.parse_time("2013-07-10 00:00:00")
        self.assertEqual(2, dt.get_day_of_week())

    def test_get_min_zoom_delta(self):
        self.assertEqual(timeline.TimeDelta(60), self.time_type.get_min_zoom_delta()[0])


class GregorianStripWeekSpec(unittest.TestCase):

    def test_start_when_week_starts_on_sunday(self):
        self.config.week_start = "sunday"
        self.assertEqual(
            self.strip.start(self.time_type.parse_time("2013-07-10 11:00:00")),
            self.time_type.parse_time("2013-07-07 00:00:00"))

    def test_start_when_week_starts_on_monday(self):
        self.config.week_start = "monday"
        self.assertEqual(
            self.strip.start(self.time_type.parse_time("2013-07-10 11:00:00")),
            self.time_type.parse_time("2013-07-08 00:00:00"))

    def test_increments_7_days(self):
        self.assertEqual(
            self.strip.increment(self.time_type.parse_time("2013-07-07 00:00:00")),
            self.time_type.parse_time("2013-07-14 00:00:00"))

    def test_label_minor(self):
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 00:00:00")),
            "")

    def test_label_major_has_no_week_when_week_starts_on_sunday(self):
        self.config.week_start = "sunday"
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 00:00:00"), True),
            "7-13 #Jul# 2013")

    def test_label_major_when_week_starts_on_monday(self):
        self.config.week_start = "monday"
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 00:00:00"), True),
            "#Week# 27 (1-7 #Jul# 2013)")
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("-4-07-07 00:00:00"), True),
            "#Week# 27 (1-7 #Jul# 5 BC)")
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-11-25 00:00:00"), True),
            "#Week# 48 (25 #Nov#-1 #Dec# 2013)")
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("-4-11-25 00:00:00"), True),
            "#Week# 48 (25 #Nov#-1 #Dec# 5 BC)")
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-12-30 00:00:00"), True),
            "#Week# 1 (30 #Dec# 2013-5 #Jan# 2014)")
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("-4-12-30 00:00:00"), True),
            "#Week# 1 (30 #Dec# 5 BC-5 #Jan# 4 BC)")

    def setUp(self):
        self.time_type = GregorianTimeType()
        self.config = mock.Mock()
        self.strip = StripWeek(self.config)


class GregorianStripWeekdaySpec(unittest.TestCase):

    def test_start(self):
        self.assertEqual(
            self.strip.start(self.time_type.parse_time("2013-07-10 12:13:14")),
            self.time_type.parse_time("2013-07-10 00:00:00"))

    def test_increment(self):
        self.assertEqual(
            self.strip.increment(self.time_type.parse_time("2013-07-07 00:00:00")),
            self.time_type.parse_time("2013-07-08 00:00:00"))

    def test_label_minor(self):
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 00:00:00")),
            "#Sun# 7")

    def test_label_major(self):
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 00:00:00"), True),
            "#Sun# 7 #Jul# 2013")
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("-5-07-07 00:00:00"), True),
            "#Fri# 7 #Jul# 6 BC")

    def setUp(self):
        self.time_type = GregorianTimeType()
        self.strip = StripWeekday()


class GregorianStripHourSpec(unittest.TestCase):

    def test_start(self):
        self.assertEqual(
            self.strip.start(self.time_type.parse_time("2013-07-10 12:13:14")),
            self.time_type.parse_time("2013-07-10 12:00:00"))

    def test_increment(self):
        self.assertEqual(
            self.strip.increment(self.time_type.parse_time("2013-07-07 12:00:00")),
            self.time_type.parse_time("2013-07-07 13:00:00"))

    def test_label_minor(self):
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 12:00:00")),
            "12")

    def test_label_major(self):
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 12:00:00"), True),
            "7 #Jul# 2013: 12h")
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("-5-07-07 12:00:00"), True),
            "7 #Jul# 6 BC: 12h")

    def setUp(self):
        self.time_type = GregorianTimeType()
        self.strip = StripHour()


class GregorianStripCenturySpec(unittest.TestCase):

    def test_start(self):
        self.assertEqual(
            self.strip.start(self.time_type.parse_time("2013-07-10 12:33:15")),
            self.time_type.parse_time("2000-01-01 00:00:00"))
        self.assertEqual(
            self.strip.start(self.time_type.parse_time("1013-07-10 12:33:15")),
            self.time_type.parse_time("1000-01-01 00:00:00"))
        self.assertEqual(
            self.strip.start(self.time_type.parse_time("13-07-10 12:33:15")),
            self.time_type.parse_time("0-01-01 00:00:00"))
        self.assertEqual(
            self.strip.start(self.time_type.parse_time("-33-07-10 12:33:15")),
            self.time_type.parse_time("-100-01-01 00:00:00"))

    def test_increment(self):
        self.assertEqual(
            self.strip.increment(self.time_type.parse_time("2000-01-01 00:00:00")),
            self.time_type.parse_time("2100-01-01 00:00:00"))

    def test_label_minor(self):
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 00:00:00")),
            "")

    def test_label_major(self):
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 00:00:00"), True),
            "21 century")

    def setUp(self):
        self.time_type = GregorianTimeType()
        self.strip = StripCentury()


class GregorianStripDaySpec(unittest.TestCase):

    def test_start(self):
        self.assertEqual(
            self.strip.start(self.time_type.parse_time("2013-07-10 12:33:15")),
            self.time_type.parse_time("2013-07-10 00:00:00"))

    def test_increment(self):
        self.assertEqual(
            self.strip.increment(self.time_type.parse_time("2013-07-10 00:00:00")),
            self.time_type.parse_time("2013-07-11 00:00:00"))

    def test_label_minor(self):
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 00:00:00")),
            "7")

    def test_label_major(self):
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 00:00:00"), True),
            "7 #Jul# 2013")
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("-5-07-07 00:00:00"), True),
            "7 #Jul# 6 BC")

    def setUp(self):
        self.time_type = GregorianTimeType()
        self.strip = StripDay()


class GregorianStripMonthSpec(unittest.TestCase):

    def test_start(self):
        self.assertEqual(
            self.strip.start(self.time_type.parse_time("2013-07-10 12:33:15")),
            self.time_type.parse_time("2013-07-01 00:00:00"))

    def test_increment(self):
        self.assertEqual(
            self.strip.increment(self.time_type.parse_time("2013-07-01 00:00:00")),
            self.time_type.parse_time("2013-08-01 00:00:00"))

    def test_label_minor(self):
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 00:00:00")),
            _("Jul"))

    def test_label_major(self):
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 00:00:00"), True),
            "#Jul# 2013")
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("-5-07-07 00:00:00"), True),
            "#Jul# 6 BC")

    def setUp(self):
        self.time_type = GregorianTimeType()
        self.strip = StripMonth()


class GregorianStripYearSpec(unittest.TestCase):

    def test_start(self):
        self.assertEqual(
            self.strip.start(self.time_type.parse_time("2013-07-10 12:33:15")),
            self.time_type.parse_time("2013-01-01 00:00:00"))

    def test_increment(self):
        self.assertEqual(
            self.strip.increment(self.time_type.parse_time("2013-01-01 00:00:00")),
            self.time_type.parse_time("2014-01-01 00:00:00"))

    def test_label_minor(self):
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 00:00:00")),
            "2013")
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("-5-07-07 00:00:00")),
            "6 BC")

    def test_label_major(self):
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 00:00:00"), True),
            "2013")
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("-5-07-07 00:00:00"), True),
            "6 BC")

    def setUp(self):
        self.time_type = GregorianTimeType()
        self.strip = StripYear()


class GregorianStripDecadeSpec(unittest.TestCase):

    def test_start(self):
        self.assertEqual(
            self.strip.start(self.time_type.parse_time("2013-07-10 12:33:15")),
            self.time_type.parse_time("2000-01-01 00:00:00"))
        self.assertEqual(
            self.strip.start(self.time_type.parse_time("5-07-10 12:33:15")),
            self.time_type.parse_time("-10-01-01 00:00:00"))
        self.assertEqual(
            self.strip.start(self.time_type.parse_time("-5-07-10 12:33:15")),
            self.time_type.parse_time("-20-01-01 00:00:00"))
        self.assertEqual(
            self.strip.start(self.time_type.parse_time("-11-07-10 12:33:15")),
            self.time_type.parse_time("-30-01-01 00:00:00"))

    def test_increment(self):
        self.assertEqual(
            self.strip.increment(self.time_type.parse_time("2010-01-01 00:00:00")),
            self.time_type.parse_time("2020-01-01 00:00:00"))

    def test_label(self):
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("2013-07-07 00:00:00")),
            "2010s")
        self.assertEqual(
            self.strip.label(self.time_type.parse_time("-5-07-07 00:00:00")),
            "0s BC")

    def setUp(self):
        self.time_type = GregorianTimeType()
        self.strip = StripDecade()


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
        self.assertEqual(u"1 %s" % _("day"), self.time_type.format_delta(delta))

    def test_format_one_minute_delta(self):
        delta = self.get_days_delta(days=0, hours=0, minutes=1)
        self.assertEqual(u"1 %s" % _("minute"), self.time_type.format_delta(delta))

    def test_format_two_minutes_delta(self):
        delta = self.get_days_delta(days=0, hours=0, minutes=2)
        self.assertEqual(u"2 %s" % _("minutes"), self.time_type.format_delta(delta))

    def test_format_one_hour_delta(self):
        delta = self.get_days_delta(days=0, hours=1, minutes=0)
        self.assertEqual(u"1 %s" % _("hour"), self.time_type.format_delta(delta))

    def test_format_two_hour_delta(self):
        delta = self.get_days_delta(days=0, hours=2, minutes=0)
        self.assertEqual(u"2 %s" % _("hours"), self.time_type.format_delta(delta))

    def test_format_one_day_delta(self):
        delta = self.get_days_delta(days=1, hours=0, minutes=0)
        self.assertEqual(u"1 %s" % _("day"), self.time_type.format_delta(delta))

    def test_format_two_days_delta(self):
        delta = self.get_days_delta(days=2, hours=0, minutes=0)
        self.assertEqual(u"2 %s" % _("days"), self.time_type.format_delta(delta))

    def test_format_one_hour_one_minute_delta(self):
        delta = self.get_days_delta(days=0, hours=1, minutes=1)
        self.assertEqual(u"1 %s 1 %s" % (_("hour"), _("minute")), self.time_type.format_delta(delta))

    def test_format_one_hour_two_minutes_delta(self):
        delta = self.get_days_delta(days=0, hours=1, minutes=2)
        self.assertEqual(u"1 %s 2 %s" % (_("hour"), _("minutes")), self.time_type.format_delta(delta))

    def test_format_one_day_one_hour_delta(self):
        delta = self.get_days_delta(days=1, hours=1, minutes=0)
        self.assertEqual(u"1 %s 1 %s" % (_("day"), _("hour")), self.time_type.format_delta(delta))

    def test_format_one_day_two_hour_delta(self):
        delta = self.get_days_delta(days=1, hours=2, minutes=0)
        self.assertEqual(u"1 %s 2 %s" % (_("day"), _("hours")), self.time_type.format_delta(delta))

    def test_format_two_days_two_hour_delta(self):
        delta = self.get_days_delta(days=2, hours=2, minutes=0)
        self.assertEqual(u"2 %s 2 %s" % (_("days"), _("hours")), self.time_type.format_delta(delta))

    def test_format_two_days_two_hour_one_minute_delta(self):
        delta = self.get_days_delta(days=2, hours=2, minutes=1)
        self.assertEqual(u"2 %s 2 %s 1 %s" % (_("days"), _("hours"), _("minute")), self.time_type.format_delta(delta))

    def test_format_two_days_two_hour_two_minutes_delta(self):
        delta = self.get_days_delta(days=2, hours=2, minutes=2)
        self.assertEqual(u"2 %s 2 %s 2 %s" % (_("days"), _("hours"), _("minutes")), self.time_type.format_delta(delta))

    def test_format_hundred_days_one_minute_delta(self):
        delta = self.get_days_delta(days=100, hours=0, minutes=0)
        self.assertEqual(u"100 %s" % _("days"), self.time_type.format_delta(delta))

    def test_format_2_years_2_months(self):
        time_period1 = self.create_point_period(1, 1, 1999, 0, 0)
        time_period2 = self.create_point_period(1, 3, 2001, 0, 0)
        delta = time_period2.start_time - time_period1.start_time
        self.assertEqual(u"790 %s" % _("days"), self.time_type.format_delta(delta))

    def test_format_overlapping_events(self):
        time_period1 = TimePeriod(self.time_type,
                                  self.time_type.parse_time("2010-08-01 13:44:00"),
                                  self.time_type.parse_time("2010-08-03 13:44:00"))
        time_period2 = TimePeriod(self.time_type,
                                  self.time_type.parse_time("2010-08-01 13:44:00"),
                                  self.time_type.parse_time("2010-08-03 13:44:00"))
        delta = time_period2.start_time - time_period1.end_time
        self.assertEqual("0", self.time_type.format_delta(delta))

    def create_point_period(self, day, month, year, hour, minute):
        dt = Gregorian(year, month, day, hour, minute, 0).to_time()
        return TimePeriod(self.time_type, dt, dt)

    def get_days_delta(self, days=0, hours=0, minutes=0):
        return timeline.TimeDelta(days * 24 * 60 *60 + hours * 60 * 60 + minutes * 60)


class GregorianTimeNavigationFunctionsSpec(unittest.TestCase):

    def test_fit_week_should_display_the_week_of_the_day_that_is_in_the_center(self):
        self.when_navigating(fit_week_fn, "30 Oct 2012", "13 Nov 2012")
        self.then_period_becomes("5 Nov 2012", "12 Nov 2012")

    def test_fit_week_sunday_start_should_display_the_week_of_the_day_that_is_in_the_center(self):
        self.when_navigating(fit_week_fn, "30 Oct 2012", "13 Nov 2012", False)
        self.then_period_becomes("4 Nov 2012", "11 Nov 2012")

    def test_fit_day_should_display_the_day_that_is_in_the_center(self):
        self.when_navigating(fit_day_fn, "1 Jan 2010", "4 Jan 2010")
        self.then_period_becomes("2 Jan 2010", "3 Jan 2010")

    def test_fit_first_day_should_display_the_day_that_is_in_the_center(self):
        self.when_navigating(fit_day_fn, "1 Jan 10", "2 Jan 10")
        self.then_period_becomes("1 Jan 10", "2 Jan 10")

    def test_fit_last_day_should_display_the_day_that_is_in_the_center(self):
        self.when_navigating(fit_day_fn, "31 Dec 9989", "1 Jan 9990")
        self.then_period_becomes("31 Dec 9989", "1 Jan 9990")

    def test_fit_month_should_display_the_month_that_is_in_the_center(self):
        self.when_navigating(fit_month_fn, "1 Jan 2010", "2 Jan 2010")
        self.then_period_becomes("1 Jan 2010", "1 Feb 2010")

    def test_fit_month_december_should_display_the_month_that_is_in_the_center(self):
        self.when_navigating(fit_month_fn, "1 Dec 2010", "2 Dec 2010")
        self.then_period_becomes("1 Dec 2010", "1 Jan 2011")

    def test_fit_first_month_december_should_display_the_month_that_is_in_the_center(self):
        self.when_navigating(fit_month_fn, "1 Jan 10", "2 Jan 10")
        self.then_period_becomes("1 Jan 10", "1 Feb 10")

    def test_fit_last_month_december_should_display_the_month_that_is_in_the_center(self):
        self.when_navigating(fit_month_fn, "1 Dec 9989", "1 Jan 9990")
        self.then_period_becomes("1 Dec 9989", "1 Jan 9990")

    def test_fit_year_should_display_the_year_that_is_in_the_center(self):
        self.when_navigating(fit_year_fn, "1 Jan 2010", "2 Jan 2010")
        self.then_period_becomes("1 Jan 2010", "1 Jan 2011")

    def test_fit_first_year_should_display_the_year_that_is_in_the_center(self):
        self.when_navigating(fit_year_fn, "1 Jan 10", "2 Jan 10")
        self.then_period_becomes("1 Jan 10", "1 Jan 11")

    def test_fit_last_year_should_display_the_year_that_is_in_the_center(self):
        self.when_navigating(fit_year_fn, "1 Jan 9989", "1 Jan 9990")
        self.then_period_becomes("1 Jan 9989", "1 Jan 9990")

    def test_fit_decade_should_display_the_decade_that_is_in_the_center(self):
        self.when_navigating(fit_decade_fn, "1 Jan 2010", "2 Jan 2010")
        self.then_period_becomes("1 Jan 2010", "1 Jan 2020")

    def test_fit_first_decade_should_display_the_decade_that_is_in_the_center(self):
        self.when_navigating(fit_decade_fn, "1 Jan 10", "2 Jan 10")
        self.then_period_becomes("1 Jan 10", "1 Jan 20")

    def test_fit_last_decade_should_display_the_decade_that_is_in_the_center(self):
        self.when_navigating(fit_decade_fn, "1 Jan 9989", "1 Jan 9990")
        self.then_period_becomes("1 Jan 9980", "1 Jan 9990")

    def test_fit_century_should_display_the_century_that_is_in_the_center(self):
        self.when_navigating(fit_century_fn, "1 Jan 2010", "2 Jan 2010")
        self.then_period_becomes("1 Jan 2000", "1 Jan 2100")

    def test_fit_last_century_should_display_the_century_that_is_in_the_center(self):
        self.when_navigating(fit_century_fn, "1 Jan 9989", "1 Jan 9990")
        self.then_period_becomes("1 Jan 9890", "1 Jan 9990")

    def test_fit_first_millennium_should_display_the_millennium_that_is_in_the_center(self):
        self.when_navigating(fit_millennium_fn, "1 Jan -4712", "1 Feb -4712")
        self.then_period_becomes("1 Jan -4712", "1 Jan -3712")

    def test_fit_millennium_should_display_the_millennium_that_is_in_the_center(self):
        self.when_navigating(fit_millennium_fn, "1 Jan 2010", "2 Jan 2010")
        self.then_period_becomes("1 Jan 2000", "1 Jan 3000")

    def test_fit_last_millennium_should_display_the_millennium_that_is_in_the_center(self):
        self.when_navigating(fit_millennium_fn, "1 Jan 9989", "1 Jan 9990")
        self.then_period_becomes("1 Jan 8990", "1 Jan 9990")

    def test_move_page_smart_not_smart_forward(self):
        self.when_navigating(forward_fn, "1 Jan 2010", "5 Jan 2010")
        self.then_period_becomes("5 Jan 2010", "9 Jan 2010")

    def test_move_page_smart_not_smart_backward(self):
        self.when_navigating(backward_fn, "5 Jan 2010", "9 Jan 2010")
        self.then_period_becomes("1 Jan 2010", "5 Jan 2010")

    def test_move_page_smart_month_forward(self):
        self.when_navigating(forward_fn, "1 Jan 2010", "1 Feb 2010")
        self.then_period_becomes("1 Feb 2010", "1 Mar 2010")

    def test_move_page_smart_month_forward_beyond_limit(self):
        self.assert_navigation_raises(
            TimeOutOfRangeRightError, forward_fn, "1 Jan 9000", "1 Dec 9989")

    def test_move_page_smart_month_backward(self):
        self.when_navigating(backward_fn, "1 Feb 2010", "1 Mar 2010")
        self.then_period_becomes("1 Jan 2010", "1 Feb 2010")

    def test_move_page_smart_month_backward_beyond_limit(self):
        self.assert_navigation_raises(
            TimeOutOfRangeLeftError, backward_fn, "1 Jan -4712", "1 Dec -4711")

    def test_move_page_smart_month_over_year_boundry_backward(self):
        self.when_navigating(backward_fn, "1 Jan 2010", "1 Mar 2010")
        self.then_period_becomes("1 Nov 2009", "1 Jan 2010")

    def test_move_page_smart_year_forward(self):
        self.when_navigating(forward_fn, "1 Jan 2010", "1 Jan 2011")
        self.then_period_becomes("1 Jan 2011", "1 Jan 2012")

    def test_move_page_smart_year_forward_beyond_limit(self):
        self.assert_navigation_raises(
            TimeOutOfRangeRightError, forward_fn, "1 Jan 9000", "1 Jan 9989")

    def test_move_page_smart_year_backward(self):
        self.when_navigating(backward_fn, "1 Jan 2011", "1 Jan 2012")
        self.then_period_becomes("1 Jan 2010", "1 Jan 2011")

    def test_move_page_smart_year_backward_beyond_limit(self):
        self.assert_navigation_raises(
            TimeOutOfRangeLeftError, backward_fn, "1 Jan -4712", "1 Jan -4711")

    def test_move_year_forward(self):
        self.when_navigating(forward_one_year_fn, "1 Jan 2009", "1 Jan 2010")
        self.then_period_becomes("1 Jan 2010", "1 Jan 2011")

    def test_move_year_backward(self):
        self.when_navigating(backward_one_year_fn, "1 Jan 2010", "1 Jan 2011")
        self.then_period_becomes("1 Jan 2009", "1 Jan 2010")

    def test_move_month_forward(self):
        self.when_navigating(forward_one_month_fn, "1 Jul 2009", "1 Aug 2009")
        self.then_period_becomes("1 Aug 2009", "1 Sep 2009")

    def test_move_month_backward(self):
        self.when_navigating(backward_one_month_fn, "1 Aug 2009", "1 Sep 2009")
        self.then_period_becomes("1 Jul 2009", "1 Aug 2009")

    def test_move_week_forward(self):
        self.when_navigating(forward_one_week_fn, "1 Jul 2009", "1 Aug 2009")
        self.then_period_becomes("8 Jul 2009", "8 Aug 2009")

    def test_move_week_backward(self):
        self.when_navigating(backward_one_week_fn, "8 Jul 2009", "8 Aug 2009")
        self.then_period_becomes("1 Jul 2009", "1 Aug 2009")

    def assert_navigation_raises(self, exception, fn, start, end):
        def navigation_fn(fn):
            self.assertRaises(exception, fn, self.time_period)
        self.time_period = gregorian_period(start, end)
        fn(None, self.time_period, navigation_fn)

    def when_navigating(self, fn, start, end, week_starts_on_monday=True):
        def navigation_fn(fn):
            self.new_period = fn(self.time_period)
        self.time_period = gregorian_period(start, end)
        main_frame = mock.Mock(MainFrame)
        main_frame.week_starts_on_monday.return_value = week_starts_on_monday
        fn(main_frame, self.time_period, navigation_fn)

    def then_period_becomes(self, start, end):
        self.assertEqual(gregorian_period(start, end), self.new_period)


class GregorianTimeDuplicateFunctionsSpec(unittest.TestCase):

    def test_move_period_num_days_adds_given_number_of_days(self):
        new_period = move_period_num_days(self.period, 6)
        self.assertEqual(
            TimePeriod(
                GregorianTimeType(),
                Gregorian(2010, 1, 7, 12, 0, 0).to_time(),
                Gregorian(2010, 1, 7, 13, 0, 0).to_time()),
            new_period)

    def test_move_period_num_weeks_adds_given_number_of_weeks(self):
        new_period = move_period_num_weeks(self.period, -3)
        self.assertEqual(
            TimePeriod(
                GregorianTimeType(),
                Gregorian(2009, 12, 11, 12, 0, 0).to_time(),
                Gregorian(2009, 12, 11, 13, 0, 0).to_time()),
            new_period)

    def test_move_period_num_months_adds_given_number_of_months(self):
        new_period = move_period_num_months(self.period, 2)
        self.assertEqual(
            TimePeriod(
                GregorianTimeType(),
                Gregorian(2010, 3, 1, 12, 0, 0).to_time(),
                Gregorian(2010, 3, 1, 13, 0, 0).to_time()),
            new_period)

    def test_move_period_num_months_can_handle_year_boundries_up(self):
        new_period = move_period_num_months(self.period, 20)
        self.assertEqual(
            TimePeriod(
                GregorianTimeType(),
                Gregorian(2011, 9, 1, 12, 0, 0).to_time(),
                Gregorian(2011, 9, 1, 13, 0, 0).to_time()),
            new_period)

    def test_move_period_num_months_can_handle_year_boundries_down(self):
        new_period = move_period_num_months(self.period, -1)
        self.assertEqual(
            TimePeriod(
                GregorianTimeType(),
                Gregorian(2009, 12, 1, 12, 0, 0).to_time(),
                Gregorian(2009, 12, 1, 13, 0, 0).to_time()),
            new_period)

    def test_move_period_num_months_returns_none_if_day_does_not_exist(self):
        self.period = TimePeriod(
            GregorianTimeType(),
            Gregorian(2010, 1, 31, 12, 0, 0).to_time(),
            Gregorian(2010, 1, 31, 13, 0, 0).to_time())
        new_period = move_period_num_months(self.period, 1)
        self.assertEqual(None, new_period)

    def test_move_period_num_years_adds_given_number_of_years(self):
        new_period = move_period_num_years(self.period, 1)
        self.assertEqual(
            TimePeriod(
                GregorianTimeType(),
                Gregorian(2011, 1, 1, 12, 0, 0).to_time(),
                Gregorian(2011, 1, 1, 13, 0, 0).to_time()),
            new_period)

    def test_move_period_num_years_returns_none_if_year_does_not_exist(self):
        self.period = TimePeriod(
            GregorianTimeType(),
            Gregorian(2012, 2, 29, 12, 0, 0).to_time(),
            Gregorian(2012, 2, 29, 13, 0, 0).to_time())
        new_period = move_period_num_years(self.period, 1)
        self.assertEqual(None, new_period)
        
    def setUp(self):
        self.period = TimePeriod(
            GregorianTimeType(),
            Gregorian(2010, 1, 1, 12, 0, 0).to_time(),
            Gregorian(2010, 1, 1, 13, 0, 0).to_time())

