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

from specs.utils import human_time_to_py
from timelinelib.db.interface import TimelineDB
from timelinelib.db.objects import Category
from timelinelib.db.objects import Event
from timelinelib.editors.event import EventEditor
from timelinelib.time import PyTimeType
from timelinelib.wxgui.dialogs.eventform import EventFormDialog


class EventEditorSpec(unittest.TestCase):

    def setUp(self):
        self.view =  Mock(EventFormDialog)
        self.db = Mock(TimelineDB)
        self.db.get_time_type.return_value = PyTimeType()
    
    def test_dialog_initializes_with_new_point_event_at_zero_time(self):
        self.when_editor_opened_with_time("1 Jan 2010")
        self.view.set_start.assert_called_with(human_time_to_py("1 Jan 2010"))
        self.view.set_end.assert_called_with(human_time_to_py("1 Jan 2010"))
        self.view.set_show_period.assert_called_with(False)
        self.view.set_show_time.assert_called_with(False)
        self.view.set_name.assert_called_with("")
        self.view.set_category.assert_called_with(None)
        self.view.set_show_add_more.assert_called_with(True)
        self.view.set_fuzzy.assert_called_with(False)
        self.view.set_locked.assert_called_with(False)
        self.view.set_ends_today.assert_called_with(False)
        self.view.set_focus.assert_called_with("start")

    def test_dialog_initializes_with_new_point_event_at_nonzero_time(self):
        self.when_editor_opened_with_time("1 Jan 2010 13:50")
        self.view.set_start.assert_called_with(human_time_to_py("1 Jan 2010 13:50"))
        self.view.set_end.assert_called_with(human_time_to_py("1 Jan 2010 13:50"))
        self.view.set_show_period.assert_called_with(False)
        self.view.set_show_time.assert_called_with(True)
        self.view.set_name.assert_called_with("")
        self.view.set_category.assert_called_with(None)
        self.view.set_show_add_more.assert_called_with(True)
        self.view.set_fuzzy.assert_called_with(False)
        self.view.set_locked.assert_called_with(False)
        self.view.set_ends_today.assert_called_with(False)
        self.view.set_focus.assert_called_with("start")

    def test_dialog_initializes_with_new_period_event_at_zero_time(self):
        self.when_editor_opened_with_period("1 Jan 2010", "2 Jan 2010")
        self.view.set_start.assert_called_with(human_time_to_py("1 Jan 2010"))
        self.view.set_end.assert_called_with(human_time_to_py("2 Jan 2010"))
        self.view.set_show_period.assert_called_with(True)
        self.view.set_show_time.assert_called_with(False)
        self.view.set_name.assert_called_with("")
        self.view.set_category.assert_called_with(None)
        self.view.set_show_add_more.assert_called_with(True)
        self.view.set_fuzzy.assert_called_with(False)
        self.view.set_locked.assert_called_with(False)
        self.view.set_ends_today.assert_called_with(False)
        self.view.set_focus.assert_called_with("text")

    def test_dialog_initializes_with_new_period_event_at_nonzero_time(self):
        self.when_editor_opened_with_period("1 Jan 2010 13:00", "1 Jan 2010 14:00")
        self.view.set_start.assert_called_with(human_time_to_py("1 Jan 2010 13:00"))
        self.view.set_end.assert_called_with(human_time_to_py("1 Jan 2010 14:00"))
        self.view.set_show_period.assert_called_with(True)
        self.view.set_show_time.assert_called_with(True)
        self.view.set_name.assert_called_with("")
        self.view.set_category.assert_called_with(None)
        self.view.set_show_add_more.assert_called_with(True)
        self.view.set_fuzzy.assert_called_with(False)
        self.view.set_locked.assert_called_with(False)
        self.view.set_ends_today.assert_called_with(False)
        self.view.set_focus.assert_called_with("text")

    def test_dialog_initializes_with_point_event_at_zero_time(self):
        self.when_editor_opened_with_event(self.anEventWith(time="1 Jan 2010"))
        self.view.set_start.assert_called_with(human_time_to_py("1 Jan 2010"))
        self.view.set_end.assert_called_with(human_time_to_py("1 Jan 2010"))
        self.view.set_show_period.assert_called_with(False)
        self.view.set_show_time.assert_called_with(False)
        self.view.set_name.assert_called_with("foo")
        self.view.set_category.assert_called_with(self.controller.event.category)
        self.view.set_show_add_more.assert_called_with(False)
        self.view.set_fuzzy.assert_called_with(False)
        self.view.set_locked.assert_called_with(False)
        self.view.set_ends_today.assert_called_with(False)
        self.view.set_focus.assert_called_with("start")
        
    def test_dialog_initializes_with_point_event_at_nonzero_time(self):
        self.when_editor_opened_with_event(self.anEventWith(time="1 Jan 2010 13:50"))
        self.view.set_start.assert_called_with(human_time_to_py("1 Jan 2010 13:50"))
        self.view.set_end.assert_called_with(human_time_to_py("1 Jan 2010 13:50"))
        self.view.set_show_period.assert_called_with(False)
        self.view.set_show_time.assert_called_with(True)
        self.view.set_name.assert_called_with("foo")
        self.view.set_category.assert_called_with(self.controller.event.category)
        self.view.set_show_add_more.assert_called_with(False)
        self.view.set_fuzzy.assert_called_with(False)
        self.view.set_locked.assert_called_with(False)
        self.view.set_ends_today.assert_called_with(False)
        self.view.set_focus.assert_called_with("start")

    def test_dialog_initializes_with_period_event_at_zero_time(self):
        self.when_editor_opened_with_event(self.anEventWith(start="1 Jan 2010", end="2 Jan 2010"))
        self.view.set_start.assert_called_with(human_time_to_py("1 Jan 2010"))
        self.view.set_end.assert_called_with(human_time_to_py("2 Jan 2010"))
        self.view.set_show_period.assert_called_with(True)
        self.view.set_show_time.assert_called_with(False)
        self.view.set_name.assert_called_with("foo")
        self.view.set_category.assert_called_with(self.controller.event.category)
        self.view.set_show_add_more.assert_called_with(False)
        self.view.set_fuzzy.assert_called_with(False)
        self.view.set_locked.assert_called_with(False)
        self.view.set_ends_today.assert_called_with(False)
        self.view.set_focus.assert_called_with("text")

    def test_dialog_initializes_with_period_event_at_nonzero_time(self):
        self.when_editor_opened_with_event(self.anEventWith(start="1 Jan 2010 13:30", end="2 Jan 2010 14:15"))
        self.view.set_start.assert_called_with(human_time_to_py("1 Jan 2010 13:30"))
        self.view.set_end.assert_called_with(human_time_to_py("2 Jan 2010 14:15"))
        self.view.set_show_period.assert_called_with(True)
        self.view.set_show_time.assert_called_with(True)
        self.view.set_name.assert_called_with("foo")
        self.view.set_category.assert_called_with(self.controller.event.category)
        self.view.set_show_add_more.assert_called_with(False)
        self.view.set_fuzzy.assert_called_with(False)
        self.view.set_locked.assert_called_with(False)
        self.view.set_ends_today.assert_called_with(False)
        self.view.set_focus.assert_called_with("text")

    def test_on_init_dialog_displays_fuzzy_and_locked(self):
        self.when_editor_opened_with_event(self.anEventWith(start="1 Jan 2010 13:30", end="2 Jan 2010 14:15", fuzzy=True, locked=True))
        self.view.set_fuzzy.assert_called_with(True)
        self.view.set_locked.assert_called_with(True)

    def test_on_init_dialog_displays_ends_today(self):
        self.when_editor_opened_with_event(self.anEventWith(time="1 Jan 2010", ends_today=True))
        self.view.set_ends_today.assert_called_with(True)

    def test_on_ok_fuzzy_and_locked_are_updated(self):
        self.when_editor_opened_with_event(self.anEventWith(start="1 Jan 2010 13:30", end="2 Jan 2010 14:15", fuzzy=True, locked=True))
        self.view.set_fuzzy.assert_called_with(True)
        self.view.set_locked.assert_called_with(True)
        self.simulate_user_enters_name("new_event")
        self.simulate_user_enters_start_time(human_time_to_py("1 Jan 2011 12:00"))
        self.simulate_user_enters_end_time(human_time_to_py("2 Jan 2011 12:00"))
        self.simulate_user_marks_as_fuzzy(False)
        self.simulate_user_marks_as_locked(False)
        self.simulate_user_clicks_ok()
        self.assertFalse(self.controller.event.fuzzy)
        self.assertFalse(self.controller.event.locked)

    def test_on_ok_new_event_is_saved_to_db(self):
        self.when_editor_opened_with_event(self.anEventWith(time="1 Jan 2010"))
        self.simulate_user_enters_name("new_event")
        self.simulate_user_enters_start_time(human_time_to_py("1 Jan 2011 12:00"))
        self.simulate_user_enters_end_time(human_time_to_py("2 Jan 2011 12:00"))
        self.simulate_user_marks_as_locked(False)
        self.simulate_user_clicks_ok()
        self.assertTrue(self.controller.db.save_event.called)
        self.assertEquals("new_event", self.controller.event.text)
        
    def test_on_ok_event_is_updated(self):
        self.when_editor_opened_with_event(self.anEventWith(time="1 Jan 2010 13:50"))
        self.simulate_user_enters_name("updated_event")
        self.simulate_user_enters_start_time(human_time_to_py("1 Jan 2011 12:00"))
        self.simulate_user_enters_end_time(human_time_to_py("2 Jan 2011 12:00"))
        self.simulate_user_marks_as_locked(False)
        self.simulate_user_clicks_ok()
        self.assertTrue(self.controller.db.save_event.called)
        self.assertEquals("updated_event", self.controller.event.text)

    def test_on_ok_event_prorty_ends_today_is_updated(self):
        self.when_editor_opened_with_event(self.anEventWith(time="1 Jan 2010"))
        self.simulate_user_enters_name("evt")
        self.simulate_user_enters_start_time(human_time_to_py("1 Jan 2010"))
        self.simulate_user_enters_end_time(human_time_to_py("1 Jan 2010"))
        self.simulate_user_marks_ends_today(True)
        self.simulate_user_clicks_ok()
        self.assertTrue(self.view.get_ends_today.called)
        self.assertEquals(True, self.controller.event.ends_today)

    def test_name_field_must_not_be_empty_when_clicking_ok(self):
        self.when_editor_opened_with_time("1 Jan 2010 13:50")
        self.simulate_user_enters_name("")
        self.simulate_user_clicks_ok()
        self.assertTrue(self.view.display_invalid_name.called)

    def test_start_must_be_less_then_end_when_clicking_ok(self):
        self.when_editor_opened_with_period("1 Jan 2010 13:00", "1 Jan 2010 14:00")
        self.simulate_user_enters_name("updated_event")
        self.simulate_user_enters_start_time(human_time_to_py("2 Jan 2011 12:00"))
        self.simulate_user_enters_end_time(human_time_to_py("1 Jan 2011 12:00"))
        self.simulate_user_clicks_ok()
        self.assertTrue(self.view.display_invalid_start.called)

    def test_time_cant_change_when_event_is_locked(self):
        self.when_editor_opened_with_time("1 Jan 2010 13:50")
        self.simulate_user_enters_start_time(human_time_to_py("2 Jan 2011 12:00"))
        self.simulate_user_enters_end_time(human_time_to_py("1 Jan 2011 12:00"))
        self.simulate_user_marks_as_locked(True)
        self.simulate_user_clicks_ok()
        msg = _("You can't change time when the Event is locked")
        self.view.display_invalid_start.assert_called_with(msg)
        
    def anEventWith(self, start=None, end=None, time=None, fuzzy=False,
                    locked=False, ends_today=False):
        if time:
            start = human_time_to_py(time)
            end = human_time_to_py(time)
        else:
            start = human_time_to_py(start)
            end = human_time_to_py(end)
        return Event(
            self.db, start, end, "foo", Category("bar", None, True),
            fuzzy=fuzzy, locked=locked, ends_today=ends_today)

    def when_editor_opened_with_time(self, time):
        self.when_editor_opened_with(
            human_time_to_py(time), human_time_to_py(time), None)

    def when_editor_opened_with_period(self, start, end):
        self.when_editor_opened_with(
            human_time_to_py(start), human_time_to_py(end), None)

    def when_editor_opened_with_event(self, event):
        self.when_editor_opened_with(None, None, event)

    def when_editor_opened_with(self, start, end, event):
        self.controller = EventEditor(self.view, self.db, start, end, event)
        self.controller.initialize()

    def simulate_user_enters_start_time(self, time):
        self.view.get_start.return_value = time

    def simulate_user_enters_end_time(self, time):
        self.view.get_end.return_value = time

    def simulate_user_enters_name(self, value):
        self.view.get_name.return_value = value

    def simulate_user_marks_as_fuzzy(self, value):
        self.view.get_fuzzy.return_value = value

    def simulate_user_marks_as_locked(self, value):
        self.view.get_locked.return_value = value

    def simulate_user_marks_ends_today(self, value):
        self.view.get_ends_today.return_value = value

    def simulate_user_clicks_ok(self):
        return self.controller.create_or_update_event()
