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

from timelinelib.gui.components.pydatetimepicker import PyDateTimePicker
from timelinelib.gui.components.pydatetimepicker import PyDatePicker
from timelinelib.gui.components.pydatetimepicker import PyDatePickerController
from timelinelib.gui.components.pydatetimepicker import PyTimePicker
from timelinelib.gui.components.pydatetimepicker import PyTimePickerController


# TODO: Test only dates in a specific range can be selected
# TODO: Test up/down should increase/decrease selected component in both date and time


class PyDatePickerBaseFixture(unittest.TestCase):

    def setUp(self):
        self.py_date_picker = Mock(PyDatePicker)
        self.py_date_picker.get_date_string.return_value = "2010-08-31"
        self.py_date_picker.SetSelection.side_effect = self._update_insertion_point_from_selection
        self.py_date_picker.GetBackgroundColour.return_value = (1, 2, 3)
        self.controller = PyDatePickerController(self.py_date_picker)

    def simulate_change_date_string(self, new_date_string):
        self.py_date_picker.get_date_string.return_value = new_date_string
        self.controller.on_text_changed()

    def _update_insertion_point_from_selection(self, from_pos, to_pos):
        self.py_date_picker.GetInsertionPoint.return_value = to_pos


class APyDatePicker(PyDatePickerBaseFixture):

    def testSelectsYearPartWhenGivenFocus(self):
        self.controller.on_set_focus()
        self.py_date_picker.SetSelection.assert_called_with(0, 4)

    def testSetsPinkBackgroundWhenIncorrectDateIsEntered(self):
        self.simulate_change_date_string("foo")
        self.py_date_picker.SetBackgroundColour.assert_called_with("pink")
        self.py_date_picker.Refresh.assert_called_with()

    def testResetsBackgroundWhenCorrectDateIsEntered(self):
        self.simulate_change_date_string("2007-02-13")
        self.py_date_picker.SetBackgroundColour.assert_called_with((1, 2, 3))
        self.py_date_picker.Refresh.assert_called_with()

    def testPopulatesDateFromPyDate(self):
        py_date = datetime.date(2009, 11, 5)
        self.controller.set_py_date(py_date)
        self.py_date_picker.set_date_string.assert_called_with("2009-11-05")


class PyDatePickerWithYearSelected(PyDatePickerBaseFixture):

    def setUp(self):
        PyDatePickerBaseFixture.setUp(self)
        self.controller.on_set_focus()
        self.py_date_picker.reset_mock()

    def testSelectsMonthPartOnTab(self):
        skip_event = self.controller.on_tab()
        self.assertFalse(skip_event)
        self.py_date_picker.SetSelection.assert_called_with(5, 7)

    def testSkipsShiftTabEvents(self):
        skip_event = self.controller.on_shift_tab()
        self.assertTrue(skip_event)


class PyDatePickerWithMonthSelected(PyDatePickerBaseFixture):

    def setUp(self):
        PyDatePickerBaseFixture.setUp(self)
        self.controller.on_set_focus()
        self.controller.on_tab()
        self.py_date_picker.reset_mock()

    def testSelectsDayPartOnTab(self):
        skip_event = self.controller.on_tab()
        self.assertFalse(skip_event)
        self.py_date_picker.SetSelection.assert_called_with(8, 10)

    def testSelectsYearPartOnShiftTab(self):
        skip_event = self.controller.on_shift_tab()
        self.assertFalse(skip_event)
        self.py_date_picker.SetSelection.assert_called_with(0, 4)


class PyDatePickerWithDaySelected(PyDatePickerBaseFixture):

    def setUp(self):
        PyDatePickerBaseFixture.setUp(self)
        self.controller.on_set_focus()
        self.controller.on_tab()
        self.controller.on_tab()
        self.py_date_picker.reset_mock()

    def testSkipsTabEvent(self):
        skip_event = self.controller.on_tab()
        self.assertTrue(skip_event)

    def testSelectsMonthPartOnShiftTab(self):
        skip_event = self.controller.on_shift_tab()
        self.assertFalse(skip_event)
        self.py_date_picker.SetSelection.assert_called_with(5, 7)


class PyTimePickerBaseFixture(unittest.TestCase):

    def setUp(self):
        self.py_time_picker = Mock(PyTimePicker)
        self.py_time_picker.get_time_string.return_value = "13:50"
        self.py_time_picker.SetSelection.side_effect = self._update_insertion_point_from_mark
        self.py_time_picker.GetBackgroundColour.return_value = (1, 2, 3)
        self.controller = PyTimePickerController(self.py_time_picker)

    def simulate_change_time_string(self, new_time_string):
        self.py_time_picker.get_time_string.return_value = new_time_string
        self.controller.on_text_changed()

    def _update_insertion_point_from_mark(self, from_pos, to_pos):
        self.py_time_picker.GetInsertionPoint.return_value = from_pos


class APyTimePicker(PyTimePickerBaseFixture):

    def testSelectsHourPartWhenGivenFocus(self):
        self.controller.on_set_focus()
        self.py_time_picker.SetSelection.assert_called_with(0, 2)

    def testSetsPinkBackgroundWhenIncorrectTimeIsEntered(self):
        self.simulate_change_time_string("foo")
        self.py_time_picker.SetBackgroundColour.assert_called_with("pink")
        self.py_time_picker.Refresh.assert_called_with()

    def testResetsBackgroundWhenCorrectTimeIsEntered(self):
        self.simulate_change_time_string("11:20")
        self.py_time_picker.SetBackgroundColour.assert_called_with((1, 2, 3))
        self.py_time_picker.Refresh.assert_called_with()
    
    def testPopulatesTimeFromPyTime(self):
        py_time = datetime.time(6, 9)
        self.controller.set_py_time(py_time)
        self.py_time_picker.set_time_string.assert_called_with("06:09")


class PyTimePickerWithHourPartSelected(PyTimePickerBaseFixture):

    def setUp(self):
        PyTimePickerBaseFixture.setUp(self)
        self.controller.on_set_focus()
        self.py_time_picker.reset_mock()

    def testSelectsMinutePartOnTab(self):
        skip_event = self.controller.on_tab()
        self.assertFalse(skip_event)
        self.py_time_picker.SetSelection.assert_called_with(3, 5)

    def testSkipsShiftTabEvent(self):
        skip_event = self.controller.on_shift_tab()
        self.assertTrue(skip_event)


class PyTimeCtrlWithMinutePartSelected(PyTimePickerBaseFixture):

    def setUp(self):
        PyTimePickerBaseFixture.setUp(self)
        self.controller.on_set_focus()
        self.controller.on_tab()
        self.py_time_picker.reset_mock()

    def testSkipsTabEvent(self):
        skip_event = self.controller.on_tab()
        self.assertTrue(skip_event)

    def testSelectedsMinutesPartOnShiftTab(self):
        skip_event = self.controller.on_shift_tab()
        self.assertFalse(skip_event)
        self.py_time_picker.SetSelection.assert_called_with(0, 2)
