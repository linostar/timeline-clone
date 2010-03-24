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


from datetime import datetime
import unittest

from mock import Mock

from timelinelib.db.interface import TimelineIOError
from timelinelib.db.objects import Category
from timelinelib.db.objects import Event
from timelinelib.db.objects import TimePeriod
from timelinelib.db.backends.memory import MemoryDB
from timelinelib.drawing.interface import ViewProperties


class TestMemoryDB(unittest.TestCase):

    def setUp(self):
        self.db = MemoryDB()
        self.db._save = Mock()
        self.db_listener = Mock()
        self.c1 = Category("work", (255, 0, 0), True)
        self.c2 = Category("private", (0, 255, 0), True)
        self.e1 = Event(datetime(2010, 2, 13), datetime(2010, 2, 13), "holiday")
        self.e2 = Event(datetime(2010, 2, 14), datetime(2010, 2, 14), "work starts")
        self.db.register(self.db_listener)

    def testInitialState(self):
        db = MemoryDB()
        self.assertEquals(db.path, "")
        self.assertEquals(db.displayed_period, None)
        self.assertEquals(db.hidden_categories, [])
        self.assertEquals(db.is_read_only(), False)
        self.assertEquals(db.supported_event_data(), ["description", "icon"])
        self.assertEquals(db.search(""), [])
        self.assertEquals(db.get_first_event(), None)
        self.assertEquals(db.get_last_event(), None)
        self.assertEquals(db.get_categories(), [])

    def testLoadSaveViewProperties(self):
        # Make sure the database contains categories
        self.db.save_category(self.c1)
        self.db.save_category(self.c2)
        # Set up a view properties object that simulates having selected a
        # specific period and hidden one category
        vp = ViewProperties()
        vp.set_category_visible(self.c1, False)
        start = datetime(2010, 3, 23)
        end = datetime(2010, 3, 24)
        tp = TimePeriod(start, end)
        vp.displayed_period = tp
        # Save these properties and assert that the database fields are written
        # correctly
        self.db.save_view_properties(vp)
        self.assertEquals(self.db.displayed_period, tp)
        self.assertEquals(self.db.hidden_categories, [self.c1])
        # Load view properties from db simulating that this db was just loaded
        # into memory and the view is being configured
        new_vp = ViewProperties()
        self.db.load_view_properties(new_vp)
        self.assertFalse(new_vp.category_visible(self.c1))
        self.assertTrue(new_vp.category_visible(self.c2))
        self.assertEquals(new_vp.displayed_period, self.db.displayed_period)
        # Assert virtual _save method called: 2 save categories, 1 save view
        # properties
        self.assertEquals(self.db._save.call_count, 3)

    def testSaveNewCategory(self):
        self.db.save_category(self.c1)
        self.assertTrue(self.c1.has_id())
        self.assertEqual(self.db.get_categories(), [self.c1])
        self.assertEqual(self.db_listener.call_count, 1)
        # Assert virtual _save method called: 1 save category
        self.assertEquals(self.db._save.call_count, 1)

    def testSaveExistingCategory(self):
        self.db.save_category(self.c1)
        id_before = self.c1.id
        self.c1.name = "new name"
        self.db.save_category(self.c1)
        self.assertEqual(id_before, self.c1.id)
        self.assertEqual(self.db.get_categories(), [self.c1])
        self.assertEqual(self.db_listener.call_count, 2) # 2 save
        # Assert virtual _save method called: 2 save category
        self.assertEquals(self.db._save.call_count, 2)

    def testSaveNonExistingCategory(self):
        other_db = MemoryDB()
        other_db.save_category(self.c1)
        # It has id but is not in this db
        self.assertRaises(TimelineIOError, self.db.save_category, self.c1)
        # Assert virtual _save method not called
        self.assertEquals(self.db._save.call_count, 0)

    def testDeleteExistingCategory(self):
        # Add two categories to the db
        self.db.save_category(self.c1)
        self.db.save_category(self.c2)
        # Make category 1 hidden
        vp = ViewProperties()
        vp.set_category_visible(self.c1, False)
        self.db.save_view_properties(vp)
        # Assert both categories in db
        categories = self.db.get_categories()
        self.assertEquals(len(categories), 2)
        self.assertTrue(self.c1 in categories)
        self.assertTrue(self.c2 in categories)
        # Remove first (by category)
        self.db.delete_category(self.c1)
        categories = self.db.get_categories()
        self.assertEquals(len(categories), 1)
        self.assertTrue(self.c2 in categories)
        self.assertFalse(self.c1.has_id())
        self.assertFalse(self.c1 in self.db.hidden_categories)
        # Remove second (by id)
        self.db.delete_category(self.c2.id)
        categories = self.db.get_categories()
        self.assertEquals(len(categories), 0)
        self.assertFalse(self.c2.has_id())
        # Check events
        self.assertEqual(self.db_listener.call_count, 4) # 2 save, 2 delete
        # Assert virtual _save method called: 2 save category, 1 save view
        # properties, 2 delete categories
        self.assertEquals(self.db._save.call_count, 5)

    def testDeleteNonExistingCategory(self):
        self.assertRaises(TimelineIOError, self.db.delete_category, self.c1)
        self.assertRaises(TimelineIOError, self.db.delete_category, 5)
        other_db = MemoryDB()
        other_db.save_category(self.c2)
        self.assertRaises(TimelineIOError, self.db.delete_category, self.c2)
        # Assert virtual _save method not called
        self.assertEquals(self.db._save.call_count, 0)

    def testSaveEventUnknownCategory(self):
        # A new
        self.e1.category = self.c1
        self.assertRaises(TimelineIOError, self.db.save_event, self.e1)
        # An existing
        self.db.save_event(self.e2)
        self.e2.category = self.c1
        self.assertRaises(TimelineIOError, self.db.save_event, self.e2)
        # Assert virtual _save method not called
        self.assertEquals(self.db._save.call_count, 1)

    def testSaveNewEvent(self):
        self.db.save_event(self.e1)
        tp = TimePeriod(datetime(2010, 2, 12), datetime(2010, 2, 14))
        self.assertTrue(self.e1.has_id())
        self.assertEqual(self.db.get_events(tp), [self.e1])
        self.assertEqual(self.db_listener.call_count, 1) # 1 save
        # Assert virtual _save method called: 1 save event
        self.assertEquals(self.db._save.call_count, 1)

    def testSaveExistingEvent(self):
        self.db.save_event(self.e1)
        id_before = self.e1.id
        self.e1.text = "new text"
        self.db.save_event(self.e1)
        tp = TimePeriod(datetime(2010, 2, 12), datetime(2010, 2, 14))
        self.assertEqual(id_before, self.e1.id)
        self.assertEqual(self.db.get_events(tp), [self.e1])
        self.assertEqual(self.db_listener.call_count, 2) # 1 save
        # Assert virtual _save method called: 2 save event
        self.assertEquals(self.db._save.call_count, 2)

    def testSaveNonExistingEvent(self):
        other_db = MemoryDB()
        other_db.save_event(self.e1)
        # It has id but is not in this db
        self.assertRaises(TimelineIOError, self.db.save_event, self.e1)
        # Assert virtual _save method not called
        self.assertEquals(self.db._save.call_count, 0)

    def testDeleteExistingEvent(self):
        tp = TimePeriod(datetime(2010, 2, 12), datetime(2010, 2, 15))
        self.db.save_event(self.e1)
        self.db.save_event(self.e2)
        # Assert both in db
        self.assertEquals(len(self.db.get_events(tp)), 2)
        self.assertTrue(self.e1 in self.db.get_events(tp))
        self.assertTrue(self.e2 in self.db.get_events(tp))
        # Delete first (by event)
        self.db.delete_event(self.e1)
        self.assertFalse(self.e1.has_id())
        self.assertEquals(len(self.db.get_events(tp)), 1)
        self.assertTrue(self.e2 in self.db.get_events(tp))
        # Delete second (by id)
        self.db.delete_event(self.e2.id)
        self.assertFalse(self.e2.has_id())
        self.assertEquals(len(self.db.get_events(tp)), 0)
        # Check events
        self.assertEqual(self.db_listener.call_count, 4) # 2 save, 2 delete
        # Assert virtual _save method called: 2 save event, 2 delete event
        self.assertEquals(self.db._save.call_count, 4)

    def testDeleteNonExistingEvent(self):
        self.assertRaises(TimelineIOError, self.db.delete_event, self.e1)
        self.assertRaises(TimelineIOError, self.db.delete_event, 5)
        other_db = MemoryDB()
        other_db.save_event(self.e2)
        self.assertRaises(TimelineIOError, self.db.delete_event, self.c2)
        # Assert virtual _save method not called
        self.assertEquals(self.db._save.call_count, 0)
