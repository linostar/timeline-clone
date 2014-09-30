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


from specs.utils import TestCase
from timelinelib.data.db import MemoryDB
from timelinelib.data.event import clone_event_list
from timelinelib.data import Container
from timelinelib.data import Event
from timelinelib.data import Subevent
from timelinelib.data.timeperiod import TimePeriod 
from specs.utils import an_event_with


class describe_duration_label_for_period_event(TestCase):

    def test_duration_label_for_period_events(self):
        cases = ( ("11 Jul 2014 10:11", "11 Jul 2014 10:12", "1 #minute#"), 
                  ("11 Jul 2014 10:11", "11 Jul 2014 11:11", "1 #hour#"), 
                  ("11 Jul 2014 10:11", "12 Jul 2014 10:11", "1 #day#"), 
                  ("11 Jul 2014 10:11", "11 Jul 2014 11:12", "1 #hour# 1 #minute#"), 
                  ("11 Jul 2014 10:11", "12 Jul 2014 10:12", "1 #day# 1 #minute#"), 
                  ("11 Jul 2014 10:11", "12 Jul 2014 11:11", "1 #day# 1 #hour#"), 
                  ("11 Jul 2014 10:11", "12 Jul 2014 11:12", "1 #day# 1 #hour# 1 #minute#"), 
                  ("11 Jul 2014 10:11", "11 Jul 2014 10:13", "2 #minutes#"), 
                  ("11 Jul 2014 10:11", "11 Jul 2014 12:11", "2 #hours#"), 
                  ("11 Jul 2014 10:11", "13 Jul 2014 10:11", "2 #days#"), 
                  ("11 Jul 2014 10:11", "11 Jul 2014 12:13", "2 #hours# 2 #minutes#"), 
                  ("11 Jul 2014 10:11", "13 Jul 2014 10:13", "2 #days# 2 #minutes#"), 
                  ("11 Jul 2014 10:11", "13 Jul 2014 12:11", "2 #days# 2 #hours#"), 
                  ("11 Jul 2014 10:11", "13 Jul 2014 12:13", "2 #days# 2 #hours# 2 #minutes#"), 
                  ("11 Jul 2014 10:11", "11 Jul 2014 11:13", "1 #hour# 2 #minutes#"), 
                  ("11 Jul 2014 10:11", "12 Jul 2014 10:13", "1 #day# 2 #minutes#"), 
                  ("11 Jul 2014 10:11", "12 Jul 2014 12:11", "1 #day# 2 #hours#"), 
                  ("11 Jul 2014 10:11", "12 Jul 2014 12:13", "1 #day# 2 #hours# 2 #minutes#"), 
                )
        for start, end, label in cases:
            event = an_event_with(start=start, end=end)
            self.assertEqual(label, event._get_duration_label())


class describe_event_construction(TestCase):

    def testEventPropertiesDefaultsToFalse(self):
        self.given_default_point_event()
        self.assertEqual(False, self.event.get_fuzzy())
        self.assertEqual(False, self.event.get_locked())
        self.assertEqual(False, self.event.get_ends_today())
        self.assertEqual(False, self.event.is_container())
        self.assertEqual(False, self.event.is_subevent())

    def testEventPropertyFuzzyCanBeSetAtConstruction(self):
        self.given_fuzzy_point_event()
        self.assertEqual(True, self.event.get_fuzzy())

    def testEventPropertyLockedCanBeSetAtConstruction(self):
        self.given_locked_point_event()
        self.assertEqual(True, self.event.get_locked())

    def testEventPropertyEndsTodayCanBeSetAtConstruction(self):
        self.given_point_event_wich_ends_today()
        self.assertEqual(True, self.event.get_ends_today())

    def given_default_point_event(self):
        self.event = Event(self.db.get_time_type(), self.now, self.now, "evt")

    def given_point_event_wich_ends_today(self):
        self.event = Event(self.db.get_time_type(), self.now, self.now, "evt", ends_today=True)

    def given_fuzzy_point_event(self):
        self.event = Event(self.db.get_time_type(), self.now, self.now, "evt", fuzzy=True)

    def given_locked_point_event(self):
        self.event = Event(self.db.get_time_type(), self.now, self.now, "evt", locked=True)

    def setUp(self):
        self.db = MemoryDB()
        self.now = self.db.get_time_type().now()


class describe_event_functions(TestCase):

    def test_zero_time_span(self):
        self.given_default_point_event()
        self.assertEqual(self.event.get_time_type().get_zero_delta(),
                         self.event.time_span())

    def given_default_point_event(self):
        self.event = Event(self.db.get_time_type(), self.now, self.now, "evt")

    def setUp(self):
        self.db = MemoryDB()
        self.now = self.db.get_time_type().now()


class describe_event_cloning(TestCase):

    def test_cloning_returns_new_object(self):
        event = self.point_event()
        clone = event.clone()
        self.assertTrue(clone is not event)

    def test_cloning_returns_object_equal_to_event(self):
        event = self.point_event()
        clone = event.clone()
        self.assertEqual(clone, event)

    def test_id_of_clone_is_none(self):
        event = self.point_event()
        event.set_id(999)
        clone = event.clone()
        self.assertEqual(clone.get_id(), None)

    def test_cloning_copies_fuzzy_attribute(self):
        event = self.point_event()
        event.set_fuzzy(True)
        clone = event.clone()
        self.assertEqual(clone, event)

    def test_cloning_copies_locked_attribute(self):
        event = self.point_event()
        event.set_locked(True)
        clone = event.clone()
        self.assertEqual(clone, event)

    def test_cloning_copies_ends_today_attribute(self):
        event = self.point_event()
        event.set_ends_today(True)
        clone = event.clone()
        self.assertEqual(clone, event)
        
    def test_cloning_copies_progress_attribute(self):
        event = self.point_event()
        event.set_progress(75) 
        clone = event.clone()
        self.assertEqual(clone, event)

    def test_cloning_copies_icon_attribute(self):
        event = self.point_event()
        event.set_icon("icon") 
        clone = event.clone()
        self.assertEqual(clone, event)

    def test_cloning_copies_hyperlink_attribute(self):
        event = self.point_event()
        event.set_hyperlink("hyperlink") 
        clone = event.clone()
        self.assertEqual(clone, event)

    def test_cloning_copies_description_attribute(self):
        event = self.point_event()
        event.set_description("Description") 
        clone = event.clone()
        self.assertEqual(clone, event)

    def test_cloning_copies_category_attribute(self):
        event = self.point_event()
        event.set_category("Category") 
        clone = event.clone()
        self.assertEqual(clone, event)

    def test_cloning_copies_text_attribute(self):
        event = self.point_event()
        event.set_text("Text") 
        clone = event.clone()
        self.assertEqual(clone, event)

    def test_cloning_copies_time_period_attribute(self):
        event = self.point_event()
        time_period = TimePeriod(event.time_type,
                                 event.time_type.parse_time("2010-08-01 13:44:00"),
                                 event.time_type.parse_time("2014-08-01 13:44:00"))
        event.set_time_period(time_period) 
        clone = event.clone()
        self.assertEqual(clone, event)

    def test_cloned_time_periods_are_not_the_same_object(self):
        event = self.point_event()
        time_period = TimePeriod(event.time_type,
                                 event.time_type.parse_time("2010-08-01 13:44:00"),
                                 event.time_type.parse_time("2014-08-01 13:44:00"))
        event.set_time_period(time_period) 
        clone = event.clone()
        self.assertTrue(time_period is not clone.get_time_period())

    def test_container_relationships_are_maintained_when_cloning(self):
        self.given_container_with_subevents()
        cloned_event_list = clone_event_list(self.events)
        self.assertListIsCloneOf(cloned_event_list, self.events)
        self.assertTrue(isinstance(cloned_event_list[0], Container))
        self.assertTrue(isinstance(cloned_event_list[1], Subevent))
        self.assertTrue(isinstance(cloned_event_list[2], Subevent))
        self.assertTrue(cloned_event_list[1] in cloned_event_list[0].events)
        self.assertTrue(cloned_event_list[2] in cloned_event_list[0].events)
        self.assertEquals(cloned_event_list[1].container_id, cloned_event_list[0].container_id)
        self.assertEquals(cloned_event_list[2].container_id, cloned_event_list[0].container_id)

    def given_container_with_subevents(self):
        self.container = Container(self.db.get_time_type(), self.now, self.now, "container", category=None, cid=1)
        self.subevent1 = Subevent(self.db.get_time_type(), self.now, self.now, "sub1", category=None, container=self.container, cid=1)
        self.subevent2 = Subevent(self.db.get_time_type(), self.now, self.now, "sub2", category=None, container=self.container)
        self.container.register_subevent(self.subevent1)
        self.container.register_subevent(self.subevent2)
        self.events = [self.container, self.subevent1, self.subevent2]

    def point_event(self):
        return Event(self.db.get_time_type(), self.now, self.now, "evt")

    def setUp(self):
        self.db = MemoryDB()
        self.now = self.db.get_time_type().now()
