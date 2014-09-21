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

from mock import Mock, sentinel

from specs.utils import an_event_with, human_time_to_gregorian, ObjectWithTruthValue
from timelinelib.data.db import MemoryDB
from timelinelib.editors.event import EventEditor
from timelinelib.repositories.interface import EventRepository
from timelinelib.time.gregoriantime import GregorianTimeType
from timelinelib.wxgui.dialogs.eventeditor import EventEditorDialog


class EventEditorTestCase(unittest.TestCase):

    def setUp(self):
        self.view = Mock(EventEditorDialog)
        self.event_repository = Mock(EventRepository)
        self.timeline = MemoryDB()

    def when_editing_a_new_event(self):
        self.when_editor_opened_with_time("1 Jan 2010")

    def when_editor_opened_with_time(self, time):
        self.when_editor_opened_with(
            human_time_to_gregorian(time), human_time_to_gregorian(time), None)

    def when_editor_opened_with_period(self, start, end):
        self.when_editor_opened_with(
            human_time_to_gregorian(start), human_time_to_gregorian(end), None)

    def when_editor_opened_with_event(self, event):
        self.when_editor_opened_with(None, None, event)

    def when_editor_opened_with(self, start, end, event):
        self.editor = EventEditor(self.view)
        self.editor.edit(GregorianTimeType(), self.event_repository, self.timeline,
                         start, end, event)

    def simulate_user_enters_start_time(self, time):
        self.view.get_start.return_value = human_time_to_gregorian(time)

    def simulate_user_enters_end_time(self, time):
        self.view.get_end.return_value = human_time_to_gregorian(time)

    def simulate_user_clicks_ok(self):
        self.editor.create_or_update_event()

    def assert_start_time_set_to(self, time):
        self.view.set_start.assert_called_with(human_time_to_gregorian(time))

    def assert_end_time_set_to(self, time):
        self.view.set_end.assert_called_with(human_time_to_gregorian(time))

    def assert_no_event_saved(self):
        self.assertFalse(self.event_repository.save.called)
        self.assertFalse(self.view.close.called)
        self.assertFalse(self.view.clear_dialog.called)


class describe_event_editor__start_time_field(EventEditorTestCase):

    def test_has_value_from_first_argument(self):
        self.when_editor_opened_with_time("1 Jan 2010")
        self.assert_start_time_set_to("1 Jan 2010")

    def test_has_value_from_event(self):
        event = Mock()
        event.time_period.start_time = sentinel.START_TIME
        self.when_editor_opened_with_event(event)
        self.view.set_start.assert_called_with(sentinel.START_TIME)

    def test_has_focus_if_point_event_edited(self):
        self.when_editor_opened_with_time("1 Jan 2010")
        self.view.set_focus.assert_called_with("start")


class describe_event_editor__end_time_field(EventEditorTestCase):

    def test_has_value_from_first_argument_if_only_one_given(self):
        self.when_editor_opened_with_time("1 Jan 2010")
        self.assert_end_time_set_to("1 Jan 2010")

    def test_has_value_from_second_argument(self):
        self.when_editor_opened_with_period("1 Jan 2010", "2 Jan 2010")
        self.assert_end_time_set_to("2 Jan 2010")

    def test_has_value_from_event(self):
        event = Mock()
        event.time_period.end_time = sentinel.END_TIME
        self.when_editor_opened_with_event(event)
        self.view.set_end.assert_called_with(sentinel.END_TIME)

    def test_is_hidden_if_no_period(self):
        self.when_editor_opened_with_time("1 Jan 2010")
        self.view.set_show_period.assert_called_with(False)

    def test_is_shown_if_period(self):
        self.when_editor_opened_with_period("1 Jan 2010", "2 Jan 2010")
        self.view.set_show_period.assert_called_with(True)


class describe_event_editor__time_fields(EventEditorTestCase):

    def test_are_hidden_if_no_time_specified(self):
        self.when_editor_opened_with_time("1 Jan 2010")
        self.view.set_show_time.assert_called_with(False)

    def test_are_shown_if_time_specified(self):
        self.when_editor_opened_with_time("1 Jan 2010 15:30")
        self.view.set_show_time.assert_called_with(True)


class describe_event_editor__fuzzy_checkbox(EventEditorTestCase):

    def test_is_not_checked_by_default(self):
        self.when_editing_a_new_event()
        self.view.set_fuzzy.assert_called_with(False)

    def test_has_value_from_event(self):
        event = Mock()
        event.get_fuzzy.return_value = sentinel.FUZZY
        self.when_editor_opened_with_event(event)
        self.view.set_fuzzy.assert_called_with(sentinel.FUZZY)


class describe_event_editor__locked_checkbox(EventEditorTestCase):

    def test_is_not_checked_by_default(self):
        self.when_editing_a_new_event()
        self.view.set_locked.assert_called_with(False)

    def test_has_value_from_event(self):
        event = Mock()
        event.get_locked.return_value = sentinel.LOCKED
        self.when_editor_opened_with_event(event)
        self.view.set_locked.assert_called_with(sentinel.LOCKED)

    def test_new_event_starting_in_history(self):
        self.when_editor_opened_with_time("1 Jan 3010")
        self.assertFalse(self.editor.start_is_in_history())

    def test_new_event_not_starting_in_history(self):
        self.when_editor_opened_with_time("1 Jan 2010")
        self.assertTrue(self.editor.start_is_in_history())

    def test_event_not_starting_in_history(self):
        event = Mock()
        event.time_period.start_time = human_time_to_gregorian("1 Jan 3010")
        self.when_editor_opened_with_event(event)
        self.assertFalse(self.editor.start_is_in_history())

    def test_event_starting_in_history(self):
        event = Mock()
        event.time_period.start_time = human_time_to_gregorian("1 Jan 2010")
        self.when_editor_opened_with_event(event)
        self.assertTrue(self.editor.start_is_in_history())


class describe_event_editor__ends_today_checkbox(EventEditorTestCase):

    def test_is_not_checked_by_default(self):
        self.when_editing_a_new_event()
        self.view.set_ends_today.assert_called_with(False)

    def test_has_value_from_event(self):
        event = Mock()
        event.get_ends_today.return_value = sentinel.ENDS_TODYAY
        self.when_editor_opened_with_event(event)
        self.view.set_ends_today.assert_called_with(sentinel.ENDS_TODYAY)

    def test_no_endtime_check(self):
        self.when_editor_opened_with_period("2 Jan 2010", "3 Jan 2010")
        self.editor.ends_today = True
        end_time = human_time_to_gregorian("1 Jan 2010")
        self.assertTrue(end_time <= self.editor._validate_and_save_end(end_time))

class describe_event_editor__text_field(EventEditorTestCase):

    def test_has_no_value_by_default(self):
        self.when_editing_a_new_event()
        self.view.set_name.assert_called_with("")

    def test_has_value_from_event(self):
        event = Mock()
        event.text = sentinel.TEXT
        self.when_editor_opened_with_event(event)
        self.view.set_name.assert_called_with(sentinel.TEXT)

    def test_has_focus_if_period_event_edited(self):
        self.when_editor_opened_with_period("1 Jan 2010", "2 Jan 2010")
        self.view.set_focus.assert_called_with("text")


class describe_event_editor__category_field(EventEditorTestCase):

    def test_has_no_value_by_default(self):
        self.when_editing_a_new_event()
        self.view.set_category.assert_called_with(None)

    def test_has_value_from_event(self):
        event = Mock()
        event.category = sentinel.CATEGORY
        self.when_editor_opened_with_event(event)
        self.view.set_category.assert_called_with(sentinel.CATEGORY)


class describe_event_editor__additional_data(EventEditorTestCase):

    def test_is_populated_from_event(self):
        event = Mock()
        event.data = sentinel.DATA
        self.when_editor_opened_with_event(event)
        self.view.set_event_data.assert_called_with(sentinel.DATA)

    def test_is_not_set_for_new_events(self):
        self.when_editing_a_new_event()
        self.assertFalse(self.view.set_event_data.called)


class describe_event_editor__add_more_checkbox(EventEditorTestCase):

    def test_is_hidden_when_editing_existing_event(self):
        self.when_editor_opened_with_event(an_event_with(time="1 Jan 2010"))
        self.view.set_show_add_more.assert_called_with(False)

    def test_is_shown_when_editing_new_event(self):
        self.when_editing_a_new_event()
        self.view.set_show_add_more.assert_called_with(True)


class describe_event_editor__saving(object):

    def given_saving_valid_event(self):
        self.locked_value = ObjectWithTruthValue(False)
        self.ends_today_value = ObjectWithTruthValue(False)
        self.simulate_user_enters_start_time("1 Jan 2010")
        self.simulate_user_enters_end_time("2 Jan 2010")
        self.view.get_fuzzy.return_value = sentinel.FUZZY
        self.view.get_locked.return_value = self.locked_value
        self.view.get_ends_today.return_value = self.ends_today_value
        self.view.get_name.return_value = "new event"
        self.view.get_category.return_value = sentinel.CATEGORY
        self.view.get_event_data.return_value = sentinel.EVENT_DATA
        self.view.get_container.return_value = None
        self.simulate_user_clicks_ok()
        er = self.event_repository
        ca = self.event_repository.save.call_args
        self.saved_event = self.event_repository.save.call_args[0][0]
        pass

    def test_saves_start_time(self):
        self.given_saving_valid_event()
        self.assertEqual(self.saved_event.time_period.start_time,
                          human_time_to_gregorian("1 Jan 2010"))

    def test_saves_end_time(self):
        self.given_saving_valid_event()
        self.assertEqual(self.saved_event.time_period.end_time,
                          human_time_to_gregorian("2 Jan 2010"))

    def test_saves_end_time_from_start_time(self):
        self.view.get_show_period.return_value = False
        self.given_saving_valid_event()
        self.assertEqual(self.saved_event.time_period.end_time,
                          human_time_to_gregorian("1 Jan 2010"))

    def test_saves_text(self):
        self.given_saving_valid_event()
        self.assertEqual(self.saved_event.text, "new event")

    def test_saves_category(self):
        self.given_saving_valid_event()
        self.assertEqual(self.saved_event.category, sentinel.CATEGORY)

    def test_saves_fuzzy(self):
        self.given_saving_valid_event()
        self.assertEqual(self.saved_event.get_fuzzy(), sentinel.FUZZY)

    def test_saves_locked(self):
        self.given_saving_valid_event()
        self.assertEqual(self.saved_event.get_locked(), self.locked_value)

    def test_saves_ends_today(self):
        self.given_saving_valid_event()
        self.assertEqual(self.saved_event.get_ends_today(), self.ends_today_value)

    def test_saves_data(self):
        self.given_saving_valid_event()
        self.assertEqual(self.saved_event.data, sentinel.EVENT_DATA)


class describe_event_editor__saving_new(
    EventEditorTestCase, describe_event_editor__saving):

    def setUp(self):
        EventEditorTestCase.setUp(self)
        self.when_editing_a_new_event()


class describe_event_editor__saving_existing(
    EventEditorTestCase, describe_event_editor__saving):

    def setUp(self):
        EventEditorTestCase.setUp(self)
        self.when_editor_opened_with_event(an_event_with(time="1 Jan 2010"))


class describe_event_editor__validation(EventEditorTestCase):

    def test_name_field_must_not_be_empty(self):
        self.when_editing_a_new_event()
        self.view.get_name.return_value = ""
        self.simulate_user_clicks_ok()
        self.assertTrue(self.view.display_invalid_name.called)
        self.assert_no_event_saved()

    def test_start_must_be_valid(self):
        self.when_editing_a_new_event()
        self.view.get_start.side_effect = ValueError
        self.simulate_user_clicks_ok()
        self.assertTrue(self.view.display_invalid_start.called)
        self.assert_no_event_saved()

    def test_end_must_be_valid(self):
        self.when_editing_a_new_event()
        self.view.get_end.side_effect = ValueError
        self.simulate_user_clicks_ok()
        self.assertTrue(self.view.display_invalid_end.called)
        self.assert_no_event_saved()

    def test_start_must_be_less_then_end(self):
        self.when_editor_opened_with_period("1 Jan 2010", "1 Jan 2010")
        self.view.get_name.return_value = "updated_event"
        self.view.get_ends_today.return_value = False
        self.simulate_user_enters_start_time("2 Jan 2011")
        self.simulate_user_enters_end_time("1 Jan 2011")
        self.simulate_user_clicks_ok()
        self.assertTrue(self.view.display_invalid_start.called)
        self.assert_no_event_saved()

    def test_period_can_not_be_too_long(self):
        self.when_editor_opened_with_time("1 Jan 2010")
        self.view.get_name.return_value = "a valid name" # why needed?
        self.view.get_locked.return_value = False # why needed?
        self.view.get_ends_today.return_value = False
        self.simulate_user_enters_start_time("1 Jan 2000")
        self.simulate_user_enters_end_time("1 Jan 5000")
        self.simulate_user_clicks_ok()
        self.assertEqual(1, self.view.display_error_message.call_count)
        self.assert_no_event_saved()

    def test_time_cant_change_when_event_is_locked(self):
        self.when_editor_opened_with_event(an_event_with(time="1 Jan 2010"))
        self.simulate_user_enters_start_time("2 Jan 2011 12:00")
        self.simulate_user_enters_end_time("1 Jan 2011 12:00")
        self.view.get_locked.return_value = True
        self.simulate_user_clicks_ok()
        self.view.display_invalid_start.assert_called_with(
            _("You can't change time when the Event is locked"))
        self.assert_no_event_saved()
