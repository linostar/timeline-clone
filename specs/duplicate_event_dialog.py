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

from timelinelib.db.interface import TimelineDB
from timelinelib.db.interface import TimelineIOError
from timelinelib.db.objects import Event
from timelinelib.db.objects import TimePeriod
from timelinelib.gui.dialogs.duplicateevent import DuplicateEvent
from timelinelib.gui.dialogs.duplicateevent import DuplicateEventController
from timelinelib.time import PyTimeType

from timelinelib.gui.dialogs.duplicateevent import DAY
from timelinelib.gui.dialogs.duplicateevent import WEEK
from timelinelib.gui.dialogs.duplicateevent import MONTH
from timelinelib.gui.dialogs.duplicateevent import YEAR
from timelinelib.gui.dialogs.duplicateevent import FORWARD
from timelinelib.gui.dialogs.duplicateevent import BACKWARD
from timelinelib.gui.dialogs.duplicateevent import BOTH
from timelinelib.gui.dialogs.duplicateevent import _get_day_period


class duplicate_event_dialog_spec_base(unittest.TestCase):

    def setUp(self):
        self.db = Mock(TimelineDB)
        self.db.get_time_type.return_value = PyTimeType()
        self.view = Mock(DuplicateEvent)
        self.view.get_count.return_value = 1
        self.view.get_period_type.return_value = _get_day_period
        self.view.get_frequency.return_value = 1
        self.view.get_direction.return_value = FORWARD
        self.event = Event(
            self.db, 
            datetime.datetime(2010, 1, 1, 12, 0, 0),
            datetime.datetime(2010, 1, 1, 13, 0, 0),
            "foo",
            category=None)
        self.controller = DuplicateEventController(self.view, self.db, self.event)


class when_the_dialog_is_opened(duplicate_event_dialog_spec_base):

    def setUp(self):
        duplicate_event_dialog_spec_base.setUp(self)
        self.controller.initialize()

    def test_count_should_be_one(self):
        self.view.set_count.assert_called_with(1)

    def test_period_should_be_day(self):
        self.view.set_period_type.assert_called_with(DAY)

    def test_frequency_should_be_one(self):
        self.view.set_frequency.assert_called_with(1)

    def test_direction_should_be_forward(self):
        self.view.set_direction.assert_called_with(FORWARD)


class when_pressing_create(duplicate_event_dialog_spec_base):

    def setUp(self):
        duplicate_event_dialog_spec_base.setUp(self)
        self.controller.create_duplicates_and_save()

    def test_one_new_event_is_saved_to_the_db(self):
        self.assertEquals(1, self.db.save_event.call_count)

    def test_the_new_event_is_one_day_ahead(self):
        new_event = self.db.save_event.call_args[0][0]
        new_period = new_event.time_period
        expected_period = TimePeriod(
            PyTimeType(),
            datetime.datetime(2010, 1, 2, 12, 0, 0),
            datetime.datetime(2010, 1, 2, 13, 0, 0))
        self.assertEquals(expected_period, new_period)

    def test_the_dialog_should_close(self):
        self.assertTrue(self.view.close.assert_called)


class when_pressing_create_and_db_save_fails(duplicate_event_dialog_spec_base):

    def setUp(self):
        duplicate_event_dialog_spec_base.setUp(self)
        self.db.save_event.side_effect = TimelineIOError
        self.controller.create_duplicates_and_save()

    def test_the_failure_is_handled(self):
        self.assertTrue(self.view.handle_db_error.called)

    def test_the_dialog_is_not_closed(self):
        self.assertFalse(self.view.close.called)
