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


from specs.utils import a_category_with
from specs.utils import an_event
from specs.utils import an_event_with
from specs.utils import EVENT_MODIFIERS
from specs.utils import get_random_modifier
from specs.utils import gregorian_period
from specs.utils import human_time_to_gregorian
from specs.utils import TestCase
from timelinelib.data.db import MemoryDB
from timelinelib.data.event import clone_event_list
from timelinelib.data import Container
from timelinelib.data import Event
from timelinelib.data import Subevent
from timelinelib.data.timeperiod import TimePeriod
from timelinelib.time.gregoriantime import GregorianTimeType
from timelinelib.time.numtime import NumTimeType
from timelinelib.time.timeline import delta_from_days


class describe_event_fundamentals(TestCase):

    def test_can_get_values(self):
        event = Event(time_type=GregorianTimeType(),
                      start_time=human_time_to_gregorian("11 Jul 2014"),
                      end_time=human_time_to_gregorian("12 Jul 2014"),
                      text="a day in my life")
        self.assertEqual(event.get_id(), None)
        self.assertEqual(event.get_time_period(),
                         gregorian_period("11 Jul 2014", "12 Jul 2014"))
        self.assertEqual(event.get_text(), "a day in my life")
        self.assertEqual(event.get_category(), None)
        self.assertEqual(event.get_time_type(), GregorianTimeType())
        self.assertEqual(event.get_fuzzy(), False)
        self.assertEqual(event.get_locked(), False)
        self.assertEqual(event.get_ends_today(), False)
        self.assertEqual(event.get_description(), None)
        self.assertEqual(event.get_icon(), None)
        self.assertEqual(event.get_hyperlink(), None)
        self.assertEqual(event.get_progress(), None)

    def test_can_set_values(self):
        self.assertEqual(
            an_event().set_id(15).get_id(),
            15)
        self.assertEqual(
            an_event().set_time_period(gregorian_period("1 Jan 2014", "1 Jan 2015")).get_time_period(),
            gregorian_period("1 Jan 2014", "1 Jan 2015"))
        self.assertEqual(
            an_event().set_text("cool").get_text(),
            "cool")
        a_parent_category = a_category_with(name="work")
        self.assertEqual(
            an_event().set_category(a_parent_category).get_category(),
            a_parent_category)
        self.assertEqual(
            an_event().set_time_type(NumTimeType()).get_time_type(),
            NumTimeType())
        self.assertEqual(
            an_event().set_fuzzy(True).get_fuzzy(),
            True)
        self.assertEqual(
            an_event().set_locked(True).get_locked(),
            True)
        self.assertEqual(
            an_event().set_ends_today(True).get_ends_today(),
            True)
        self.assertEqual(
            an_event().set_description("cool").get_description(),
            "cool")
        an_icon = "really not an icon"
        self.assertEqual(
            an_event().set_icon(an_icon).get_icon(),
            an_icon)
        self.assertEqual(
            an_event().set_hyperlink("http://google.com").get_hyperlink(),
            "http://google.com")
        self.assertEqual(
            an_event().set_progress(88).get_progress(),
            88)
        self.assertEqual(
            an_event().set_alert("2015-01-07 00:00:00;hoho").get_alert(),
            "2015-01-07 00:00:00;hoho")

    def test_can_be_compared(self):
        one = an_event()
        other = one.clone()
        self.assertEqNeWorks(one, other, get_random_modifier(EVENT_MODIFIERS))

    def test_can_be_cloned(self):
        original = an_event()
        clone = original.clone()
        self.assertIsCloneOf(clone, original)


class describe_event(TestCase):

    def test_can_not_set_values(self):
        self.assertEqual(
            an_event_with(locked=True).set_ends_today(True).get_ends_today(),
            False)

    def test_ends_today_can_be_changed_with_update(self):
        event = an_event_with(ends_today=False)
        event.update(event.get_time_period().start_time, event.get_time_period().end_time, event.get_text(), ends_today=True)
        self.assertTrue(event.get_ends_today())

    def test_fuzzy_can_be_changed_with_update(self):
        event = an_event_with(fuzzy=False)
        event.update(event.get_time_period().start_time, event.get_time_period().end_time, event.get_text(), fuzzy=True)
        self.assertTrue(event.get_fuzzy())

    def test_locked_can_be_changed_with_update(self):
        event = an_event_with(locked=False)
        event.update(event.get_time_period().start_time, event.get_time_period().end_time, event.get_text(), locked=True)
        self.assertTrue(event.get_locked())

    def test_ends_today_can_not_be_set_with_update_on_locked_event(self):
        event = an_event_with(ends_today=False, locked=True)
        event.update(event.get_time_period().start_time, event.get_time_period().end_time, event.get_text(), ends_today=True)
        self.assertFalse(event.get_ends_today())

    def test_ends_today_can_not_be_unset_with_update_on_locked_event(self):
        event = an_event_with(ends_today=True, locked=True)
        event.update(event.get_time_period().start_time, event.get_time_period().end_time, event.get_text(), ends_today=False)
        self.assertTrue(event.get_ends_today())

    def test_point_event_has_a_label(self):
        event = an_event_with(text="foo", time="11 Jul 2014 10:11")
        self.assertEqual(u"foo (11 #Jul# 2014 10:11)", event.get_label())

    def test_point_event_has_an_empty_duration_label(self):
        event = an_event_with(text="foo", time="11 Jul 2014 10:11")
        self.assertEqual(u"", event._get_duration_label())

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

    def test_event_properties_defaults_to_false(self):
        event = an_event()
        self.assertEqual(False, event.get_fuzzy())
        self.assertEqual(False, event.get_locked())
        self.assertEqual(False, event.get_ends_today())
        self.assertEqual(False, event.is_container())
        self.assertEqual(False, event.is_subevent())

    def test_event_property_fuzzy_can_be_set_at_construction(self):
        event = an_event_with(fuzzy=True)
        self.assertTrue(event.get_fuzzy())

    def test_event_property_locked_can_be_set_at_construction(self):
        event = an_event_with(locked=True)
        self.assertTrue(event.get_locked())

    def test_event_property_ends_today_can_be_set_at_construction(self):
        event = an_event_with(ends_today=True)
        self.assertTrue(event.get_ends_today())


class describe_event_functions(TestCase):

    def test_zero_time_span(self):
        event = an_event()
        self.assertEqual(event.get_time_type().get_zero_delta(), event.time_span())


class describe_event_cloning(TestCase):

    def test_cloning_returns_new_object(self):
        event = an_event()
        clone = event.clone()
        self.assertTrue(clone is not event)

    def test_cloning_returns_object_equal_to_event(self):
        event = an_event()
        clone = event.clone()
        self.assertEqual(clone, event)

    def test_id_of_clone_is_none(self):
        event = an_event()
        event.set_id(999)
        clone = event.clone()
        self.assertEqual(clone.get_id(), None)

    def test_cloning_copies_fuzzy_attribute(self):
        event = an_event()
        event.set_fuzzy(True)
        clone = event.clone()
        self.assertEqual(clone, event)

    def test_cloning_copies_locked_attribute(self):
        event = an_event()
        event.set_locked(True)
        clone = event.clone()
        self.assertEqual(clone, event)

    def test_cloning_copies_ends_today_attribute(self):
        event = an_event()
        event.set_ends_today(True)
        clone = event.clone()
        self.assertEqual(clone, event)
        
    def test_cloning_copies_progress_attribute(self):
        event = an_event()
        event.set_progress(75) 
        clone = event.clone()
        self.assertEqual(clone, event)

    def test_cloning_copies_icon_attribute(self):
        event = an_event()
        event.set_icon("icon") 
        clone = event.clone()
        self.assertEqual(clone, event)

    def test_cloning_copies_hyperlink_attribute(self):
        event = an_event()
        event.set_hyperlink("hyperlink") 
        clone = event.clone()
        self.assertEqual(clone, event)

    def test_cloning_copies_alert_attribute(self):
        event = an_event()
        event.set_alert("2015-01-07 00:00:00;hoho") 
        clone = event.clone()
        self.assertEqual(clone, event)

    def test_cloning_copies_description_attribute(self):
        event = an_event()
        event.set_description("Description") 
        clone = event.clone()
        self.assertEqual(clone, event)

    def test_cloning_copies_category_attribute(self):
        event = an_event()
        event.set_category("Category") 
        clone = event.clone()
        self.assertEqual(clone, event)

    def test_cloning_copies_text_attribute(self):
        event = an_event()
        event.set_text("Text") 
        clone = event.clone()
        self.assertEqual(clone, event)

    def test_cloning_copies_time_period_attribute(self):
        event = an_event()
        time_period = TimePeriod(event.time_type,
                                 event.time_type.parse_time("2010-08-01 13:44:00"),
                                 event.time_type.parse_time("2014-08-01 13:44:00"))
        event.set_time_period(time_period) 
        clone = event.clone()
        self.assertEqual(clone, event)

    def test_cloned_time_periods_are_not_the_same_object(self):
        event = an_event()
        time_period = TimePeriod(event.time_type,
                                 event.time_type.parse_time("2010-08-01 13:44:00"),
                                 event.time_type.parse_time("2014-08-01 13:44:00"))
        event.set_time_period(time_period) 
        clone = event.clone()
        self.assertTrue(time_period is not clone.get_time_period())


class describe_event_cloning_of_containers(TestCase):

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

    def setUp(self):
        self.db = MemoryDB()
        self.now = self.db.get_time_type().now()
