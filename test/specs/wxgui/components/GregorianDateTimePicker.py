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

from mock import Mock

from timelinelib.calendar.gregorian import Gregorian
from timelinelib.time.gregoriantime import GregorianTimeType
from timelinelib.time.timeline import delta_from_days
import timelinelib.calendar.gregorian as gregorian 
from timelinelib.wxgui.components.gregoriandatetimepicker import GregorianDateTimePickerController
from timelinelib.wxgui.components.gregoriandatetimepicker import GregorianDatePicker
from timelinelib.wxgui.components.gregoriandatetimepicker import GregorianDatePickerController
from timelinelib.wxgui.components.gregoriandatetimepicker import GregorianTimePicker
from timelinelib.wxgui.components.gregoriandatetimepicker import GregorianTimePickerController
from timelinelib.wxgui.components.gregoriandatetimepicker import CalendarPopup
from timelinelib.wxgui.components.gregoriandatetimepicker import CalendarPopupController


class AGregorianDateTimePicker(unittest.TestCase):

    def setUp(self):
        self.date_picker = Mock(GregorianDatePicker)
        self.time_picker = Mock(GregorianTimePicker)
        self.now_fn = Mock()
        self.controller = GregorianDateTimePickerController(
            self.date_picker, self.time_picker, self.now_fn)

    def testDateControlIsAssignedDatePartFromSetValue(self):
        self.controller.set_value(Gregorian(2010, 11, 20, 15, 33, 0).to_time())
        self.date_picker.set_value.assert_called_with((2010, 11, 20))

    # TODO: Is this really GregorianDateTimePicker's responsibility?
    def testDateControlIsAssignedCurrentDateIfSetWithValueNone(self):
        self.now_fn.return_value = Gregorian(2010, 8, 31, 0, 0, 0).to_time()
        self.controller.set_value(None)
        self.date_picker.set_value.assert_called_with((2010, 8, 31))

    def testTimeControlIsAssignedTimePartFromSetValue(self):
        self.controller.set_value(Gregorian(2010, 11, 20, 15, 33, 0).to_time())
        self.time_picker.set_value.assert_called_with((15, 33, 0))

    # TODO: Is this really GregorianDateTimePicker's responsibility?
    def testTimeControlIsAssignedCurrentTimeIfSetWithValueNone(self):
        self.now_fn.return_value = Gregorian(2010, 8, 31, 12, 15, 0).to_time()
        self.controller.set_value(None)
        self.time_picker.set_value.assert_called_with((12, 15, 0))

    def testGetValueWhenTimeIsShownShouldReturnDateWithTime(self):
        self.time_picker.IsShown.return_value = True
        self.time_picker.get_value.return_value = (14, 30, 0)
        self.date_picker.get_value.return_value = (2010, 8, 31)
        self.assertEqual(Gregorian(2010, 8, 31, 14, 30, 0).to_time(), self.controller.get_value())

    def testGetValueWhenTimeIsHiddenShouldReturnDateWithoutTime(self):
        self.time_picker.IsShown.return_value = False
        self.time_picker.get_value.return_value = (14, 30, 0)
        self.date_picker.get_value.return_value = (2010, 8, 31)
        self.assertEqual(Gregorian(2010, 8, 31, 0, 0, 0).to_time(), self.controller.get_value())

    def testControllerCanConverDateTupleToWxDate(self):
        wx_date = self.controller.date_tuple_to_wx_date((2010, 8, 31))
        self.assertEqual((2010, 8, 31), (wx_date.Year, wx_date.Month + 1, wx_date.Day))
        
    def testControllerCanConverWxdateToDateTuple(self):
        wx_date = self.controller.date_tuple_to_wx_date((2010, 8, 31))
        year, month, day = self.controller.wx_date_to_date_tuple(wx_date)
        self.assertEqual((2010, 8, 31), (year, month, day))


class GregorianDatePickerBaseFixture(unittest.TestCase):

    def setUp(self):
        self.date_picker = Mock(GregorianDatePicker)
        self.date_picker.get_date_string.return_value = "2010-08-31"
        self.date_picker.GetBackgroundColour.return_value = (1, 2, 3)
        self.date_picker.SetSelection.side_effect = self._update_insertion_point_and_selection
        self.simulate_change_insertion_point(0)
        self.controller = GregorianDatePickerController(self.date_picker, error_bg="pink")

    def assertBackgroundChangedTo(self, bg):
        self.date_picker.SetBackgroundColour.assert_called_with(bg)
        self.date_picker.Refresh.assert_called_with()

    def simulate_change_date_string(self, new_date_string):
        self.date_picker.get_date_string.return_value = new_date_string
        self.controller.on_text_changed()

    def simulate_change_insertion_point(self, new_insertion_point):
        self.date_picker.GetSelection.return_value = (new_insertion_point, new_insertion_point)
        self.date_picker.GetInsertionPoint.return_value = new_insertion_point

    def _update_insertion_point_and_selection(self, from_pos, to_pos):
        self.date_picker.GetInsertionPoint.return_value = to_pos
        self.date_picker.GetSelection.return_value = (from_pos, to_pos)


class AGregorianDatePicker(GregorianDatePickerBaseFixture):

    def testSelectsYearPartWhenGivenFocus(self):
        self.controller.on_set_focus()
        self.date_picker.SetSelection.assert_called_with(0, 4)

    def testChangesToErrorBackgroundWhenNoDateTextIsEntered(self):
        self.simulate_change_date_string("foo")
        self.assertBackgroundChangedTo("pink")

    def testChangesToErrorBackgroundWhenIncorrectDateIsEntered(self):
        self.simulate_change_date_string("2013-13-01")
        self.assertBackgroundChangedTo("pink")

    def testResetsBackgroundWhenCorrectDateIsEntered(self):
        self.simulate_change_date_string("2007-02-13")
        self.assertBackgroundChangedTo((1, 2, 3))

    def testPopulatesDateFromGregorianDate(self):
        self.controller.set_value((2009, 11, 5))
        self.date_picker.set_date_string.assert_called_with("2009-11-05")

    def testPopulatesDateFromGregorianLargeDate(self):
        self.controller.set_value((9009, 11, 5))
        self.date_picker.set_date_string.assert_called_with("9009-11-05")

    def testParsesEnteredDateAsGregorianDate(self):
        self.simulate_change_date_string("2008-05-03")
        self.assertEqual((2008, 5, 3), self.controller.get_value())

    def testParsesEnteredDateAsGregorianLargeDate(self):
        self.simulate_change_date_string("9008-05-03")
        self.assertEqual((9008, 5, 3), self.controller.get_value())

    def testThrowsValueErrorWhenParsingInvalidDate(self):
        self.simulate_change_date_string("2008-05-xx")
        self.assertRaises(ValueError, self.controller.get_value)

    def testChangesToErrorBackgroundWhenTooSmallDateIsEntered(self):
        year, month, day = gregorian.from_time(GregorianTimeType().get_min_time()[0]).to_date_tuple()
        self.simulate_change_date_string("%d-%02d-%02d" % (year - 1, month, day))
        self.assertBackgroundChangedTo("pink")

    def testHasOriginalBackgroundWhenSmallestValidDateIsEntered(self):
        self.simulate_change_date_string(get_min_time_string())
        self.assertBackgroundChangedTo((1, 2, 3))

    def testChangesToErrorBackgroundWhenTooLargeDateIsEntered(self):
        year, month, day = gregorian.from_time(GregorianTimeType().get_max_time()[0]).to_date_tuple()
        self.simulate_change_date_string("%d-%02d-%02d" % (year + 1, month, day))
        self.assertBackgroundChangedTo("pink")

    def testHasOriginalBackgroundWhenLargestValidDateIsEntered(self):
        self.simulate_change_date_string(get_max_time_string())
        self.assertBackgroundChangedTo((1, 2, 3))

    def testShowsPreferredDayOnUpWhenMonthIsIncremented(self):
        # Make preferred day = 30
        self.simulate_change_date_string("2010-01-29")
        self.simulate_change_insertion_point(10)
        self.controller.on_up()
        self.assertEqual(self.controller.preferred_day, 30)
        # Change month
        self.simulate_change_insertion_point(7)
        self.controller.on_up()
        self.date_picker.set_date_string.assert_called_with("2010-02-28")
        self.simulate_change_date_string("2010-02-28")
        self.controller.preferred_day = 30
        self.controller.on_up()
        self.date_picker.set_date_string.assert_called_with("2010-03-30")

    def testShowsPreferredDayOnDownWhenMonthIsDecremented(self):
        # Make preferred day = 30
        self.simulate_change_date_string("2010-04-01")
        self.simulate_change_insertion_point(10)
        self.controller.on_down()
        self.assertEqual(self.controller.preferred_day, 31)
        # Change month
        self.simulate_change_insertion_point(7)
        self.controller.on_down()
        self.date_picker.set_date_string.assert_called_with("2010-03-31")
        self.simulate_change_date_string("2010-03-31")
        self.controller.on_down()
        self.date_picker.set_date_string.assert_called_with("2010-02-28")

        
class GregorianDatePickerWithFocusOnYear(GregorianDatePickerBaseFixture):

    def setUp(self):
        GregorianDatePickerBaseFixture.setUp(self)
        self.controller.on_set_focus()
        self.date_picker.reset_mock()

    def testReselectsYearWhenLosingAndRegainingFocus(self):
        self.controller.on_kill_focus()
        self.controller.on_set_focus()
        self.date_picker.SetSelection.assert_called_with(0, 4)

    def testSelectsMonthPartOnTab(self):
        skip_event = self.controller.on_tab()
        self.assertFalse(skip_event)
        self.date_picker.SetSelection.assert_called_with(5, 7)

    def testSkipsShiftTabEvents(self):
        skip_event = self.controller.on_shift_tab()
        self.assertTrue(skip_event)

    def testKeepsSelectionOnUp(self):
        self.controller.on_up()
        self.date_picker.SetSelection.assert_called_with(0, 4)

    def testKeepsSelectionOnDown(self):
        self.controller.on_up()
        self.date_picker.SetSelection.assert_called_with(0, 4)

    def testIncreasesYearOnUp(self):
        self.simulate_change_date_string("2010-01-01")
        self.controller.on_up()
        self.date_picker.set_date_string.assert_called_with("2011-01-01")

    def testDecreasesYearOnDown(self):
        self.simulate_change_date_string("2010-01-01")
        self.controller.on_down()
        self.date_picker.set_date_string.assert_called_with("2009-01-01")

    def testDontIncreaseYearOnUpWhenTooLargeDate(self):
        self.simulate_change_date_string(get_max_time_string())
        self.controller.on_up()
        self.assertFalse(self.date_picker.set_date_string.called)

    def testDontDecreaseYearOnDownWhenTooSmallDate(self):
        self.simulate_change_date_string(get_min_time_string())
        self.controller.on_down()
        self.assertFalse(self.date_picker.set_date_string.called)

    def testChangesDayOnDownWhenLeapYeer(self):
        self.simulate_change_date_string("2012-02-29")
        self.controller.on_down()
        self.date_picker.set_date_string.assert_called_with("2011-02-28")

    def testKeepsInsertionPointOnUp(self):
        self.simulate_change_date_string("2010-01-01")
        self.controller.on_up()
        self.date_picker.SetSelection.assert_called_with(0, 4)

    def testKeepsInsertionPointOnDown(self):
        self.simulate_change_date_string("2010-01-01")
        self.controller.on_down()
        self.date_picker.SetSelection.assert_called_with(0, 4)


class GregorianDatePickerWithFocusOnMonth(GregorianDatePickerBaseFixture):

    def setUp(self):
        GregorianDatePickerBaseFixture.setUp(self)
        self.controller.on_set_focus()
        self.controller.on_tab()
        self.date_picker.reset_mock()

    def testReselectsMonthWhenLosingAndRegainingFocus(self):
        self.controller.on_kill_focus()
        self.controller.on_set_focus()
        self.date_picker.SetSelection.assert_called_with(5, 7)

    def testSelectsDayPartOnTab(self):
        skip_event = self.controller.on_tab()
        self.assertFalse(skip_event)
        self.date_picker.SetSelection.assert_called_with(8, 10)

    def testSelectsYearPartOnShiftTab(self):
        skip_event = self.controller.on_shift_tab()
        self.assertFalse(skip_event)
        self.date_picker.SetSelection.assert_called_with(0, 4)

    def testIncreasesMonthOnUp(self):
        self.simulate_change_date_string("2010-01-01")
        self.controller.on_up()
        self.date_picker.set_date_string.assert_called_with("2010-02-01")

    def testIncreasesMonthOnUpToNextYear(self):
        self.simulate_change_date_string("2010-12-01")
        self.controller.on_up()
        self.date_picker.set_date_string.assert_called_with("2011-01-01")

    def testDecreasesMonthOnDown(self):
        self.simulate_change_date_string("2009-07-31")
        self.controller.on_down()
        self.date_picker.set_date_string.assert_called_with("2009-06-30")

    def testDontDecreaseMonthOnDownWhenTooSmallDate(self):
        self.simulate_change_date_string(get_min_time_string())
        self.controller.on_down()
        self.assertFalse(self.date_picker.set_date_string.called)

    def testDecreasesYearOnDownWhenJanuary(self):
        self.simulate_change_date_string("2010-01-01")
        self.controller.on_down()
        self.date_picker.set_date_string.assert_called_with("2009-12-01")


class GregorianDatePickerWithFocusOnDay(GregorianDatePickerBaseFixture):

    def setUp(self):
        GregorianDatePickerBaseFixture.setUp(self)
        self.controller.on_set_focus()
        self.controller.on_tab()
        self.controller.on_tab()
        self.date_picker.reset_mock()

    def testReselectsDayWhenLosingAndRegainingFocus(self):
        self.controller.on_kill_focus()
        self.controller.on_set_focus()
        self.date_picker.SetSelection.assert_called_with(8, 10)

    def testSkipsTabEvent(self):
        skip_event = self.controller.on_tab()
        self.assertTrue(skip_event)

    def testSelectsMonthPartOnShiftTab(self):
        skip_event = self.controller.on_shift_tab()
        self.assertFalse(skip_event)
        self.date_picker.SetSelection.assert_called_with(5, 7)

    def testIncreasesDayOnUp(self):
        self.simulate_change_date_string("2010-01-01")
        self.controller.on_up()
        self.date_picker.set_date_string.assert_called_with("2010-01-02")

    def testDecreasesDayOnDown(self):
        self.simulate_change_date_string("2010-01-10")
        self.controller.on_down()
        self.date_picker.set_date_string.assert_called_with("2010-01-09")

    def testDontDecreaseDayOnDownWhenTooSmallDate(self):
        self.simulate_change_date_string(get_min_time_string())
        self.controller.on_down()
        self.assertFalse(self.date_picker.set_date_string.called)

    def testDecreasesMonthOnDownWhenDayOne(self):
        self.simulate_change_date_string("2010-02-01")
        self.controller.on_down()
        self.date_picker.set_date_string.assert_called_with("2010-01-31")

    def testDecreasesMonthAndYearOnDownWhenJanuaryTheFirst(self):
        self.simulate_change_date_string("2010-01-01")
        self.controller.on_down()
        self.date_picker.set_date_string.assert_called_with("2009-12-31")

    def testIncreasesMonthWhenLastDayInMonthOnUp(self):
        self.simulate_change_date_string("2010-01-31")
        self.controller.on_up()
        self.date_picker.set_date_string.assert_called_with("2010-02-01")


class GregorianTimePickerBaseFixture(unittest.TestCase):

    def setUp(self):
        self.time_picker = Mock(GregorianTimePicker)
        self.time_picker.get_time_string.return_value = "13:50"
        self.time_picker.GetBackgroundColour.return_value = (1, 2, 3)
        self.time_picker.SetSelection.side_effect = self._update_insertion_point_and_selection
        self.controller = GregorianTimePickerController(self.time_picker)

    def assertBackgroundChangedTo(self, bg):
        self.time_picker.SetBackgroundColour.assert_called_with(bg)
        self.time_picker.Refresh.assert_called_with()

    def simulate_change_time_string(self, new_time_string):
        self.time_picker.get_time_string.return_value = new_time_string
        self.controller.on_text_changed()

    def simulate_change_insertion_point(self, new_insertion_point):
        self.time_picker.GetSelection.return_value = (new_insertion_point, new_insertion_point)
        self.time_picker.GetInsertionPoint.return_value = new_insertion_point

    def _update_insertion_point_and_selection(self, from_pos, to_pos):
        self.time_picker.GetInsertionPoint.return_value = from_pos
        self.time_picker.GetSelection.return_value = (from_pos, to_pos)


class AGregorianTimePicker(GregorianTimePickerBaseFixture):

    def testSelectsHourPartWhenGivenFocus(self):
        self.controller.on_set_focus()
        self.time_picker.SetSelection.assert_called_with(0, 2)

    def testSetsPinkBackgroundWhenIncorrectTimeIsEntered(self):
        self.simulate_change_time_string("foo")
        self.assertBackgroundChangedTo("pink")

    def testSetsPinkBackgroundWhenInvalidTimeIsEntered(self):
        self.simulate_change_time_string("25:15")
        self.assertBackgroundChangedTo("pink")

    def testResetsBackgroundWhenCorrectTimeIsEntered(self):
        self.simulate_change_time_string("11:20")
        self.assertBackgroundChangedTo((1, 2, 3))

    def testPopulatesTimeFromTimeTuple(self):
        time = (6, 9, 0)
        self.controller.set_value(time)
        self.time_picker.set_time_string.assert_called_with("06:09")


class GregorianTimePickerWithFocusOnHour(GregorianTimePickerBaseFixture):

    def setUp(self):
        GregorianTimePickerBaseFixture.setUp(self)
        self.simulate_change_insertion_point(0)
        self.controller.on_set_focus()
        self.time_picker.reset_mock()

    def testReselectsHourWhenLosingAndRegainingFocus(self):
        self.controller.on_kill_focus()
        self.controller.on_set_focus()
        self.time_picker.SetSelection.assert_called_with(0, 2)

    def testSelectsMinutePartOnTab(self):
        skip_event = self.controller.on_tab()
        self.assertFalse(skip_event)
        self.time_picker.SetSelection.assert_called_with(3, 5)

    def testSkipsShiftTabEvent(self):
        skip_event = self.controller.on_shift_tab()
        self.assertTrue(skip_event)

    def testIncreasesHourOnUp(self):
        self.simulate_change_time_string("04:04")
        self.controller.on_up()
        self.time_picker.set_time_string.assert_called_with("05:04")

    def testMakesHourZeroOnUpWhenLastHour(self):
        self.simulate_change_time_string("23:04")
        self.controller.on_up()
        self.time_picker.set_time_string.assert_called_with("00:04")

    def testNoChangeOnUpWhenInvalidTime(self):
        self.simulate_change_time_string("aa:bb")
        self.controller.on_up()
        self.assertFalse(self.time_picker.set_time_string.called)

    def testDecreasesHourOnDown(self):
        self.simulate_change_time_string("04:04")
        self.controller.on_down()
        self.time_picker.set_time_string.assert_called_with("03:04")

    def testSetLastHourOnDownWhenZeroHour(self):
        self.simulate_change_time_string("00:04")
        self.controller.on_down()
        self.time_picker.set_time_string.assert_called_with("23:04")


class GregorianTimeCtrlWithFocusOnMinute(GregorianTimePickerBaseFixture):

    def setUp(self):
        GregorianTimePickerBaseFixture.setUp(self)
        self.simulate_change_insertion_point(3)
        self.controller.on_set_focus()
        self.controller.on_tab()
        self.time_picker.reset_mock()

    def testReselectsMinuteWhenLosingAndRegainingFocus(self):
        self.controller.on_kill_focus()
        self.controller.on_set_focus()
        self.time_picker.SetSelection.assert_called_with(3, 5)

    def testSkipsTabEvent(self):
        skip_event = self.controller.on_tab()
        self.assertTrue(skip_event)

    def testSelectsMinutesPartOnShiftTab(self):
        skip_event = self.controller.on_shift_tab()
        self.assertFalse(skip_event)
        self.time_picker.SetSelection.assert_called_with(0, 2)

    def testIncreasesMinutesOnUp(self):
        self.simulate_change_time_string("04:04")
        self.controller.on_up()
        self.time_picker.set_time_string.assert_called_with("04:05")

    def testSetsMinutesToZeroAndIncrementsHourWhenUpOnLastMinute(self):
        self.simulate_change_time_string("04:59")
        self.controller.on_up()
        self.time_picker.set_time_string.assert_called_with("05:00")

    def testDecreasesMinutesOnDown(self):
        self.simulate_change_time_string("04:04")
        self.controller.on_down()
        self.time_picker.set_time_string.assert_called_with("04:03")

    def testLastTimeOnDownWhenZeroTime(self):
        self.simulate_change_time_string("00:00")
        self.controller.on_down()
        self.time_picker.set_time_string.assert_called_with("23:59")


class ACalendarPopup(unittest.TestCase):

    def setUp(self):
        self.calendar_popup = Mock(CalendarPopup)
        self.controller = CalendarPopupController(self.calendar_popup)

    def testStaysOpenOnMonthChange(self):
        self._simulateMonthChange()
        self.assertTrue(self.calendar_popup.Popup.called)

    def testStaysOpenOnDayChange(self):
        self._simulateDateChange()
        self.assertTrue(self.calendar_popup.Popup.called)

    def testPopupCallAllowedJustOnce(self):
        self._simulateMonthChange()
        self.assertTrue(self.calendar_popup.Popup.called)
        self.calendar_popup.reset_mock()
        self._simulateMonthChange()
        self.assertFalse(self.calendar_popup.Popup.called)

    def _simulateMonthChange(self):
        self.controller.on_month()
        self.controller.on_dismiss()

    def _simulateDateChange(self):
        self.controller.on_day()
        self.controller.on_dismiss()


def get_min_time_string():
    year, month, day = gregorian.from_time(GregorianTimeType().get_min_time()[0]).to_date_tuple()
    return "%d-%02d-%02d" % (year, month, day)

def get_max_time_string():
    # max_time is not a valid date so we must decrease with one day
    year, month, day = gregorian.from_time(GregorianTimeType().get_max_time()[0] - delta_from_days(1)).to_date_tuple()
    return "%d-%02d-%02d" % (year, month, day)
