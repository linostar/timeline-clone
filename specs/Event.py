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


import random

from specs.utils import a_category_with
from specs.utils import an_event
from specs.utils import an_event_with
from specs.utils import gregorian_period
from specs.utils import human_time_to_gregorian
from specs.utils import TestCase
from timelinelib.data import Event
from timelinelib.time.gregoriantime import GregorianTimeType
from timelinelib.time.numtime import NumTimeType
from timelinelib.time.timeline import delta_from_days


class describe_event(TestCase):

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
            self.an_event.set_id(15).get_id(),
            15)
        self.assertEqual(
            self.an_event.set_time_period(gregorian_period("1 Jan 2014", "1 Jan 2015")).get_time_period(),
            gregorian_period("1 Jan 2014", "1 Jan 2015"))
        self.assertEqual(
            self.an_event.set_text("cool").get_text(),
            "cool")
        self.assertEqual(
            self.an_event.set_category(self.a_category).get_category(),
            self.a_category)
        self.assertEqual(
            self.an_event.set_time_type(NumTimeType()).get_time_type(),
            NumTimeType())
        self.assertEqual(
            self.an_event.set_fuzzy(True).get_fuzzy(),
            True)
        self.assertEqual(
            self.an_event.set_locked(True).get_locked(),
            True)
        self.assertEqual(
            self.an_event.set_ends_today(True).get_ends_today(),
            True)
        self.assertEqual(
            self.an_event.set_description("cool").get_description(),
            "cool")
        self.assertEqual(
            self.an_event.set_icon(self.an_icon).get_icon(),
            self.an_icon)
        self.assertEqual(
            self.an_event.set_hyperlink("http://google.com").get_hyperlink(),
            "http://google.com")
        self.assertEqual(
            self.an_event.set_progress(88).get_progress(),
            88)

    def test_can_be_compared(self):
        self.assertObjectEquality(self.create_equal_events, self.modify_event)

    def test_can_be_cloned(self):
        (original, _, _) = self.create_equal_events()
        clone = original.clone()
        self.assertIsCloneOf(clone, original)

    def create_equal_events(self):
        events = []
        for _ in range(3):
            event = an_event()
            event.set_progress(66)
            events.append(event)
        return events

    def modify_event(self, event):
        if event.get_id():
            new_id = event.get_id() + 1
        else:
            new_id = 8
        return random.choice([
            lambda event: event.clone().set_time_type(None),
            lambda event: event.clone().set_fuzzy(not event.get_fuzzy()),
            lambda event: event.clone().set_locked(not event.get_locked()),
            lambda event: event.clone().set_ends_today(not event.get_ends_today()),
            lambda event: event.clone().set_id(new_id),
            lambda event: event.clone().set_time_period(event.get_time_period().move_delta(delta_from_days(1))),
            lambda event: event.clone().set_text("was: %s" % event.get_text()),
            lambda event: event.clone().set_category(a_category_with(name="another category name")),
            lambda event: event.clone().set_icon("not really an icon"),
            lambda event: event.clone().set_description("another description"),
            lambda event: event.clone().set_hyperlink("http://another.com"),
            lambda event: event.clone().set_progress(6),
        ])(event)

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

    def setUp(self):
        self.an_event = an_event()
        self.a_category = a_category_with(name="work")
        self.an_icon = "really not an icon"
