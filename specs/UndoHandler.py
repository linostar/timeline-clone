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

from timelinelib.data.db import MemoryDB
from timelinelib.data import Event
from timelinelib.data.undohandler import UndoHandler


class UndoHandlerSpec(unittest.TestCase):

    def test_undo_buffer_is_empty_after_construction(self):
        self.assertEqual(0, len(self.undo_handler._undo_buffer))

    def test_undo_handler_position_is_invalid_after_construction(self):
        self.assertEqual(-1, self.undo_handler._pos)

    def test_undo_handler_is_disabled_after_construction(self):
        self.assertEqual(False, self.undo_handler._enabled)

    def test_get_data_returns_empty_list_after_construction(self):
        self.assertEqual([], self.undo_handler.get_data())

    def test_undo_handler_can_be_enabled(self):
        self.undo_handler.enable(True)
        self.assertEqual(True, self.undo_handler._enabled)

    def test_save_has_no_effect_when_undo_handler_is_disabled(self):
        buffer_size = len(self.undo_handler._undo_buffer)
        self.given_timeline_with_two_events()
        self.undo_handler.enable(False)
        self.undo_handler.save()
        self.assertEqual(buffer_size, len(self.undo_handler._undo_buffer))

    def test_undo_buffer_updated_when_undo_handler_is_enabled(self):
        buffer_size = len(self.undo_handler._undo_buffer)
        self.given_timeline_with_two_events()
        self.undo_handler.enable(True)
        self.undo_handler.save()
        self.assertEqual(buffer_size + 1, len(self.undo_handler._undo_buffer))

    def test_events_in_undo_buffer_are_cloned(self):
        self.given_timeline_with_two_events()
        self.undo_handler.enable(True)
        self.undo_handler.save()
        self.assertFalse(self.undo_handler._undo_buffer[0][0] == self.db.events[0])
        self.assertFalse(self.undo_handler._undo_buffer[0][1] == self.db.events[1])

    def test_save_of_empty_timeline(self):
        self.given_empty_timeline()
        self.assertEqual(1, len(self.undo_handler._undo_buffer))
        self.assertEqual(0, len(self.undo_handler._undo_buffer[0][1]))

    def test_undo_when_nothing_to_undo(self):
        self.given_empty_timeline()
        self.undo_handler.undo()
        self.assertEqual(1, len(self.undo_handler._undo_buffer))
        self.assertEqual(0, len(self.undo_handler.get_data()[1]))

    def test_save_of_timeline(self):
        self.given_timeline_with_two_events_added()
        self.assertEqual(3, len(self.undo_handler._undo_buffer))
        self.assertEqual(2, len(self.undo_handler.get_data()[1]))

    def test_undo(self):
        self.given_timeline_with_two_events_added()
        self.undo_handler.undo()
        self.assertEqual(3, len(self.undo_handler._undo_buffer))
        self.assertEqual(1, len(self.get_event_list()))

    def test_save_not_possible_when_undo_disabled(self):
        self.given_empty_timeline()
        self.undo_handler.enable(False)
        self.assertEqual(1, len(self.undo_handler._undo_buffer))
        self.given_point_event()
        self.undo_handler.save()
        self.assertEqual(1, len(self.undo_handler._undo_buffer))

    def setUp(self):
        self.db = MemoryDB()
        self.undo_handler = UndoHandler(self.db)

    def given_empty_timeline(self):
        self.undo_handler.enable(True)
        self.undo_handler.save()

    def given_timeline_with_two_events(self):
        self.given_point_event()
        self.given_period_event()

    def given_timeline_with_two_events_added(self):
        self.undo_handler.enable(True)
        self.undo_handler.save()
        self.given_point_event()
        self.undo_handler.save()
        self.given_period_event()
        self.undo_handler.save()

    def given_event_list(self):
        self.given_point_event()
        self.given_period_event()

    def given_point_event(self):
        event = Event(self.db.get_time_type(), self.time("2000-01-01 10:01:01"),
                           self.time("2000-01-01 10:01:01"), "evt")
        self.db.events.append(event)

    def given_period_event(self, days=0, hours=0, minutes=0):
        days += 1
        hours += 1
        minutes += 1
        event = Event(self.db.get_time_type(), self.time("2000-01-01 01:01:01"),
                           self.time("2000-01-0%d %d:%d:01" % (days, hours, minutes)), "period evt")
        self.db.events.append(event)

    def time(self, tm):
        return self.db.get_time_type().parse_time(tm)

    def get_event_list(self):
        return self.undo_handler.get_data()[1]
