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

from timelinelib.wxgui.components.numtimepicker import NumTimePickerController
from timelinelib.wxgui.components.numtimepicker import NumTimePicker


class desribe_NumTimePickerController(unittest.TestCase):

    def test_time_control_is_assigned_time_from_set_value(self):
        self.controller.set_value(5)
        self.time_picker.set_value.assert_called_with(5)

    def test_time_control_is_assigned_zero_if_set_with_value_none(self):
        self.controller.set_value(None)
        self.time_picker.set_value.assert_called_with(0)

    def test_time_range_is_set(self):
        self.time_picker.set_range.assert_called_with(-1000000000, 1000000000)

    def setUp(self):
        self.time_picker = Mock(NumTimePicker)
        self.controller = NumTimePickerController(self.time_picker, 0)
