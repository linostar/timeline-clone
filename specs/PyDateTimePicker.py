# Copyright (C) 2009, 2010  Rickard Lindberg, Roger Lindberg
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
import datetime

from mock import Mock

from timelinelib.gui.components.pydatetimepicker import PyDatePicker
from timelinelib.gui.components.pydatetimepicker import PyDatePickerController
from timelinelib.gui.components.pydatetimepicker import PyTimePicker
from timelinelib.gui.components.pydatetimepicker import PyTimePickerController
from timelinelib.gui.components.pydatetimepicker import CalendarPopup
from timelinelib.gui.components.pydatetimepicker import CalendarPopupController


class PyDatePickerBaseFixture(unittest.TestCase):

    def setUp(self):
        self.py_date_picker = Mock(PyDatePicker)
        self.py_date_picker.get_date_string.return_value = "2010-08-31"
        self.py_date_picker.GetBackgroundColour.return_value = (1, 2, 3)
        self.py_date_picker.SetSelection.side_effect = self._update_insertion_point_and_selection
        self.simulate_change_insertion_point(0)
        self.controller = PyDatePickerController(self.py_date_picker, error_bg="pink")

    def assertBackgroundChangedTo(self, bg):
        self.py_date_picker.SetBackgroundColour.assert_called_with(bg)
        self.py_date_picker.Refresh.assert_called_with()

    def simulate_change_date_string(self, new_date_string):
        self.py_date_picker.get_date_string.return_value = new_date_string
        self.controller.on_text_changed()

    def simulate_change_insertion_point(self, new_insertion_point):
        self.py_date_picker.GetSelection.return_value = (new_insertion_point, new_insertion_point) 
        self.py_date_picker.GetInsertionPoint.return_value = new_insertion_point

    def _update_insertion_point_and_selection(self, from_pos, to_pos):
        self.py_date_picker.GetInsertionPoint.return_value = to_pos
        self.py_date_picker.GetSelection.return_value = (from_pos, to_pos)


class APyDatePicker(PyDatePickerBaseFixture):

    def testSelectsYearPartWhenGivenFocus(self):
        self.controller.on_set_focus()
        self.py_date_picker.SetSelection.assert_called_with(0, 4)

    def testChangesToErrorBackgroundWhenIncorrectDateIsEntered(self):
        self.simulate_change_date_string("foo")
        self.assertBackgroundChangedTo("pink")

    def testResetsBackgroundWhenCorrectDateIsEntered(self):
        self.simulate_change_date_string("2007-02-13")
        self.assertBackgroundChangedTo((1, 2, 3))

    def testPopulatesDateFromPyDate(self):
        self.controller.set_py_date(datetime.date(2009, 11, 5))
        self.py_date_picker.set_date_string.assert_called_with("2009-11-05")

    def testParsesEnteredDateAsPyDate(self):
        self.simulate_change_date_string("2008-05-03")
        self.assertEquals(datetime.date(2008, 5, 3),
                          self.controller.get_py_date())

    def testThrowsValueErrorWhenParsingInvalidDate(self):
        self.simulate_change_date_string("2008-05-xx")
        self.assertRaises(ValueError, self.controller.get_py_date)

    def testThrowsValueErrorWhenParsingDateOutsideValidRange(self):
        self.simulate_change_date_string("9-9-9")
        self.assertRaises(ValueError, self.controller.get_py_date)

    def testChangesToErrorBackgroundWhenTooSmallDateIsEntered(self):
        self.simulate_change_date_string("9-12-31")
        self.assertBackgroundChangedTo("pink")

    def testHasOriginalBackgroundWhenSmallestValidDateIsEntered(self):
        self.simulate_change_date_string("10-01-01")
        self.assertBackgroundChangedTo((1, 2, 3))

    def testChangesToErrorBackgroundWhenTooLargeDateIsEntered(self):
        self.simulate_change_date_string("9990-01-01")
        self.assertBackgroundChangedTo("pink")

    def testHasOriginalBackgroundWhenLargestValidDateIsEntered(self):
        self.simulate_change_date_string("9989-12-31")
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
        self.py_date_picker.set_date_string.assert_called_with("2010-02-28")
        self.simulate_change_date_string("2010-02-28")
        self.controller.preferred_day = 30
        self.controller.on_up()
        self.py_date_picker.set_date_string.assert_called_with("2010-03-30")

    def testShowsPreferredDayOnDownWhenMonthIsDecremented(self):
        # Make preferred day = 30
        self.simulate_change_date_string("2010-04-01")
        self.simulate_change_insertion_point(10)
        self.controller.on_down()
        self.assertEqual(self.controller.preferred_day, 31)
        # Change month
        self.simulate_change_insertion_point(7)
        self.controller.on_down()
        self.py_date_picker.set_date_string.assert_called_with("2010-03-31")
        self.simulate_change_date_string("2010-03-31")
        self.controller.on_down()
        self.py_date_picker.set_date_string.assert_called_with("2010-02-28")


class PyDatePickerWithFocusOnYear(PyDatePickerBaseFixture):

    def setUp(self):
        PyDatePickerBaseFixture.setUp(self)
        self.controller.on_set_focus()
        self.py_date_picker.reset_mock()

    def testReselectsYearWhenLosingAndRegainingFocus(self):
        self.controller.on_kill_focus()
        self.controller.on_set_focus()
        self.py_date_picker.SetSelection.assert_called_with(0, 4)

    def testSelectsMonthPartOnTab(self):
        skip_event = self.controller.on_tab()
        self.assertFalse(skip_event)
        self.py_date_picker.SetSelection.assert_called_with(5, 7)

    def testSkipsShiftTabEvents(self):
        skip_event = self.controller.on_shift_tab()
        self.assertTrue(skip_event)

    def testKeepsSelectionOnUp(self):
        self.controller.on_up()
        self.py_date_picker.SetSelection.assert_called_with(0, 4)

    def testKeepsSelectionOnDown(self):
        self.controller.on_up()
        self.py_date_picker.SetSelection.assert_called_with(0, 4)

    def testIncreasesYearOnUp(self):
        self.simulate_change_date_string("2010-01-01")
        self.controller.on_up()
        self.py_date_picker.set_date_string.assert_called_with("2011-01-01")

    def testDecreasesYearOnDown(self):
        self.simulate_change_date_string("2010-01-01")
        self.controller.on_down()
        self.py_date_picker.set_date_string.assert_called_with("2009-01-01")

    def testDontIncreaseYearOnUpWhenTooLargeDate(self):
        self.simulate_change_date_string("9989-01-01")
        self.controller.on_up()
        self.assertFalse(self.py_date_picker.set_date_string.called)

    def testDontDecreaseYearOnDownWhenTooSmallDate(self):
        self.simulate_change_date_string("10-01-01")
        self.controller.on_down()
        self.assertFalse(self.py_date_picker.set_date_string.called)

    def testChangesDayOnDownWhenLeapYeer(self):
        self.simulate_change_date_string("2012-02-29")
        self.controller.on_down()
        self.py_date_picker.set_date_string.assert_called_with("2011-02-28")

    def testKeepsInsertionPointOnUp(self):
        self.simulate_change_date_string("2010-01-01")
        self.controller.on_up()
        self.py_date_picker.SetSelection.assert_called_with(0, 4)

    def testKeepsInsertionPointOnDown(self):
        self.simulate_change_date_string("2010-01-01")
        self.controller.on_down()
        self.py_date_picker.SetSelection.assert_called_with(0, 4)


class PyDatePickerWithFocusOnMonth(PyDatePickerBaseFixture):

    def setUp(self):
        PyDatePickerBaseFixture.setUp(self)
        self.controller.on_set_focus()
        self.controller.on_tab()
        self.py_date_picker.reset_mock()

    def testReselectsMonthWhenLosingAndRegainingFocus(self):
        self.controller.on_kill_focus()
        self.controller.on_set_focus()
        self.py_date_picker.SetSelection.assert_called_with(5, 7)

    def testSelectsDayPartOnTab(self):
        skip_event = self.controller.on_tab()
        self.assertFalse(skip_event)
        self.py_date_picker.SetSelection.assert_called_with(8, 10)

    def testSelectsYearPartOnShiftTab(self):
        skip_event = self.controller.on_shift_tab()
        self.assertFalse(skip_event)
        self.py_date_picker.SetSelection.assert_called_with(0, 4)

    def testIncreasesMonthOnUp(self):
        self.simulate_change_date_string("2010-01-01")
        self.controller.on_up()
        self.py_date_picker.set_date_string.assert_called_with("2010-02-01")

    def testDecreasesMonthOnDown(self):
        self.simulate_change_date_string("2009-07-31")
        self.controller.on_down()
        self.py_date_picker.set_date_string.assert_called_with("2009-06-30")

    def testDontDecreaseMonthOnDownWhenTooSmallDate(self):
        self.simulate_change_date_string("10-01-01")
        self.controller.on_down()
        self.assertFalse(self.py_date_picker.set_date_string.called)

    def testDecreasesYearOnDownWhenJanuary(self):
        self.simulate_change_date_string("2010-01-01")
        self.controller.on_down()
        self.py_date_picker.set_date_string.assert_called_with("2009-12-01")


class PyDatePickerWithFocusOnDay(PyDatePickerBaseFixture):

    def setUp(self):
        PyDatePickerBaseFixture.setUp(self)
        self.controller.on_set_focus()
        self.controller.on_tab()
        self.controller.on_tab()
        self.py_date_picker.reset_mock()

    def testReselectsDayWhenLosingAndRegainingFocus(self):
        self.controller.on_kill_focus()
        self.controller.on_set_focus()
        self.py_date_picker.SetSelection.assert_called_with(8, 10)

    def testSkipsTabEvent(self):
        skip_event = self.controller.on_tab()
        self.assertTrue(skip_event)

    def testSelectsMonthPartOnShiftTab(self):
        skip_event = self.controller.on_shift_tab()
        self.assertFalse(skip_event)
        self.py_date_picker.SetSelection.assert_called_with(5, 7)

    def testIncreasesDayOnUp(self):
        self.simulate_change_date_string("2010-01-01")
        self.controller.on_up()
        self.py_date_picker.set_date_string.assert_called_with("2010-01-02")

    def testDecreasesDayOnDown(self):
        self.simulate_change_date_string("2010-01-10")
        self.controller.on_down()
        self.py_date_picker.set_date_string.assert_called_with("2010-01-09")

    def testDontDecreaseDayOnDownWhenTooSmallDate(self):
        self.simulate_change_date_string("10-01-01")
        self.controller.on_down()
        self.assertFalse(self.py_date_picker.set_date_string.called)

    def testDecreasesMonthOnDownWhenDayOne(self):
        self.simulate_change_date_string("2010-02-01")
        self.controller.on_down()
        self.py_date_picker.set_date_string.assert_called_with("2010-01-31")

    def testDecreasesMonthAndYearOnDownWhenJanuaryTheFirst(self):
        self.simulate_change_date_string("2010-01-01")
        self.controller.on_down()
        self.py_date_picker.set_date_string.assert_called_with("2009-12-31")

    def testIncreasesMonthWhenLastDayInMonthOnUp(self):
        self.simulate_change_date_string("2010-01-31")
        self.controller.on_up()
        self.py_date_picker.set_date_string.assert_called_with("2010-02-01")


class PyTimePickerBaseFixture(unittest.TestCase):

    def setUp(self):
        self.py_time_picker = Mock(PyTimePicker)
        self.py_time_picker.get_time_string.return_value = "13:50"
        self.py_time_picker.GetBackgroundColour.return_value = (1, 2, 3)
        self.py_time_picker.SetSelection.side_effect = self._update_insertion_point_and_selection
        self.controller = PyTimePickerController(self.py_time_picker)

    def assertBackgroundChangedTo(self, bg):
        self.py_time_picker.SetBackgroundColour.assert_called_with(bg)
        self.py_time_picker.Refresh.assert_called_with()

    def simulate_change_time_string(self, new_time_string):
        self.py_time_picker.get_time_string.return_value = new_time_string
        self.controller.on_text_changed()

    def simulate_change_insertion_point(self, new_insertion_point):
        self.py_time_picker.GetSelection.return_value = (new_insertion_point, new_insertion_point) 
        self.py_time_picker.GetInsertionPoint.return_value = new_insertion_point

    def _update_insertion_point_and_selection(self, from_pos, to_pos):
        self.py_time_picker.GetInsertionPoint.return_value = from_pos
        self.py_time_picker.GetSelection.return_value = (from_pos, to_pos) 


class APyTimePicker(PyTimePickerBaseFixture):

    def testSelectsHourPartWhenGivenFocus(self):
        self.controller.on_set_focus()
        self.py_time_picker.SetSelection.assert_called_with(0, 2)

    def testSetsPinkBackgroundWhenIncorrectTimeIsEntered(self):
        self.simulate_change_time_string("foo")
        self.assertBackgroundChangedTo("pink")

    def testResetsBackgroundWhenCorrectTimeIsEntered(self):
        self.simulate_change_time_string("11:20")
        self.assertBackgroundChangedTo((1, 2, 3))

    def testPopulatesTimeFromPyTime(self):
        py_time = datetime.time(6, 9)
        self.controller.set_py_time(py_time)
        self.py_time_picker.set_time_string.assert_called_with("06:09")


class PyTimePickerWithFocusOnHour(PyTimePickerBaseFixture):

    def setUp(self):
        PyTimePickerBaseFixture.setUp(self)
        self.simulate_change_insertion_point(0)
        self.controller.on_set_focus()
        self.py_time_picker.reset_mock()

    def testReselectsHourWhenLosingAndRegainingFocus(self):
        self.controller.on_kill_focus()
        self.controller.on_set_focus()
        self.py_time_picker.SetSelection.assert_called_with(0, 2)

    def testSelectsMinutePartOnTab(self):
        skip_event = self.controller.on_tab()
        self.assertFalse(skip_event)
        self.py_time_picker.SetSelection.assert_called_with(3, 5)

    def testSkipsShiftTabEvent(self):
        skip_event = self.controller.on_shift_tab()
        self.assertTrue(skip_event)

    def testIncreasesHourOnUp(self):
        self.simulate_change_time_string("04:04")
        self.controller.on_up()
        self.py_time_picker.set_time_string.assert_called_with("05:04")

    def testMakesHourZeroOnUpWhenLastHour(self):
        self.simulate_change_time_string("23:04")
        self.controller.on_up()
        self.py_time_picker.set_time_string.assert_called_with("00:04")

    def testNoChangeOnUpWhenInvalidTime(self):
        self.simulate_change_time_string("aa:bb")
        self.controller.on_up()
        self.assertFalse(self.py_time_picker.set_time_string.called)

    def testDecreasesHourOnDown(self):
        self.simulate_change_time_string("04:04")
        self.controller.on_down()
        self.py_time_picker.set_time_string.assert_called_with("03:04")

    def testSetLastHourOnDownWhenZeroHour(self):
        self.simulate_change_time_string("00:04")
        self.controller.on_down()
        self.py_time_picker.set_time_string.assert_called_with("23:04")


class PyTimeCtrlWithFocusOnMinute(PyTimePickerBaseFixture):

    def setUp(self):
        PyTimePickerBaseFixture.setUp(self)
        self.simulate_change_insertion_point(3)
        self.controller.on_set_focus()
        self.controller.on_tab()
        self.py_time_picker.reset_mock()

    def testReselectsMinuteWhenLosingAndRegainingFocus(self):
        self.controller.on_kill_focus()
        self.controller.on_set_focus()
        self.py_time_picker.SetSelection.assert_called_with(3, 5)

    def testSkipsTabEvent(self):
        skip_event = self.controller.on_tab()
        self.assertTrue(skip_event)

    def testSelectsMinutesPartOnShiftTab(self):
        skip_event = self.controller.on_shift_tab()
        self.assertFalse(skip_event)
        self.py_time_picker.SetSelection.assert_called_with(0, 2)

    def testIncreasesMinutesOnUp(self):
        self.simulate_change_time_string("04:04")
        self.controller.on_up()
        self.py_time_picker.set_time_string.assert_called_with("04:05")

    def testSetsMinutesToZeroAndIncrementsHourWhenUpOnLastMinute(self):
        self.simulate_change_time_string("04:59")
        self.controller.on_up()
        self.py_time_picker.set_time_string.assert_called_with("05:00")

    def testDecreasesMinutesOnDown(self):
        self.simulate_change_time_string("04:04")
        self.controller.on_down()
        self.py_time_picker.set_time_string.assert_called_with("04:03")

    def testLastTimeOnDownWhenZeroTime(self):
        self.simulate_change_time_string("00:00")
        self.controller.on_down()
        self.py_time_picker.set_time_string.assert_called_with("23:59")


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
        call = self.calendar_popup.reset_mock()
        self._simulateMonthChange()
        self.assertFalse(self.calendar_popup.Popup.called)
        
    def _simulateMonthChange(self):
        self.controller.on_month()
        self.controller.on_dismiss()

    def _simulateDateChange(self):
        self.controller.on_day()
        self.controller.on_dismiss()
