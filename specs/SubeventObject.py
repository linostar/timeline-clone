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
from specs.utils import a_container_with
from specs.utils import a_subevent
from specs.utils import a_subevent_with
from specs.utils import gregorian_period
from specs.utils import human_time_to_gregorian
from specs.utils import SUBEVENT_MODIFIERS
from specs.utils import TestCase
from timelinelib.data.subevent import Subevent
from timelinelib.time.gregoriantime import GregorianTimeType
from timelinelib.time.numtime import NumTimeType


class describe_subevent(TestCase):

    def test_can_get_values(self):
        event = Subevent(time_type=GregorianTimeType(),
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
        self.assertEqual(event.get_container_id(), -1)

    def test_can_set_values(self):
        self.assertEqual(
            a_subevent().set_id(15).get_id(),
            15)
        self.assertEqual(
            a_subevent().set_time_period(gregorian_period("1 Jan 2014", "1 Jan 2015")).get_time_period(),
            gregorian_period("1 Jan 2014", "1 Jan 2015"))
        self.assertEqual(
            a_subevent().set_text("cool").get_text(),
            "cool")
        a_parent_category = a_category_with(name="work")
        self.assertEqual(
            a_subevent().set_category(a_parent_category).get_category(),
            a_parent_category)
        self.assertEqual(
            a_subevent().set_time_type(NumTimeType()).get_time_type(),
            NumTimeType())
        self.assertEqual(
            a_subevent().set_fuzzy(True).get_fuzzy(),
            True)
        self.assertEqual(
            a_subevent().set_locked(True).get_locked(),
            True)
        self.assertEqual(
            a_subevent().set_ends_today(True).get_ends_today(),
            True)
        self.assertEqual(
            a_subevent().set_description("cool").get_description(),
            "cool")
        an_icon = "really not an icon"
        self.assertEqual(
            a_subevent().set_icon(an_icon).get_icon(),
            an_icon)
        self.assertEqual(
            a_subevent().set_hyperlink("http://google.com").get_hyperlink(),
            "http://google.com")
        self.assertEqual(
            a_subevent().set_progress(88).get_progress(),
            88)
        self.assertEqual(
            a_subevent().set_alert("2015-01-07 00:00:00;hoho").get_alert(),
            "2015-01-07 00:00:00;hoho")
        self.assertEqual(
            a_subevent().set_container_id(78).get_container_id(),
            78)

    def test_clone_eq_ne(self):
        self.assertCloneEqNe(a_subevent, SUBEVENT_MODIFIERS)

    def test_can_change_container(self):
        subevent = a_subevent_with(start="1 Jan 200 10:01", end="3 Mar 200 10:01")
        container = a_container_with(text="container", cid=99)
        subevent.register_container(container)
        self.assertEqual(99, subevent.cid())
        self.assertEqual(container, subevent.container)

    def test_properties_defaults(self):
        subevent = a_subevent_with(start="1 Jan 200 10:01", end="3 Mar 200 10:01")
        self.assertEqual(-1, subevent.cid())
        self.assertEqual(False, subevent.get_fuzzy())
        self.assertEqual(False, subevent.get_locked())
        self.assertEqual(False, subevent.get_ends_today())
        self.assertEqual(False, subevent.is_container())
        self.assertEqual(True, subevent.is_subevent())

    def test_cid_can_be_set_a_construction(self):
        subevent = a_subevent_with(start="1 Jan 200 10:01", end="3 Mar 200 10:01", cid=99)
        self.assertEqual(99, subevent.cid())


class describe_subevent_cloning(TestCase):

    def test_cloning_returns_new_object(self):
        subevent = a_subevent_with(start="1 Jan 200 10:01", end="3 Mar 200 10:01", cid=99)
        cloned_subevent = subevent.clone()
        self.assertTrue(subevent is not cloned_subevent)
        self.assertTrue(cloned_subevent == subevent)

    def test_cloning_copies_progress(self):
        subevent = a_subevent_with(start="1 Jan 200 10:01", end="3 Mar 200 10:01", cid=99)
        subevent.set_progress(85)
        cloned_subevent = subevent.clone()
        self.assertTrue(cloned_subevent == subevent)

    def test_cloning_copies_alert(self):
        subevent = a_subevent_with(start="1 Jan 200 10:01", end="3 Mar 200 10:01", cid=99)
        subevent.set_alert("1 Jan 200 10:01;Wake up")
        cloned_subevent = subevent.clone()
        self.assertTrue(cloned_subevent == subevent)

    def test_cloning_copies_icon(self):
        subevent = a_subevent_with(start="1 Jan 200 10:01", end="3 Mar 200 10:01", cid=99)
        subevent.set_icon("icon")
        cloned_subevent = subevent.clone()
        self.assertTrue(cloned_subevent == subevent)

    def test_cloning_copies_hyperlink(self):
        subevent = a_subevent_with(start="1 Jan 200 10:01", end="3 Mar 200 10:01", cid=99)
        subevent.set_hyperlink("http://www.svd.se")
        cloned_subevent = subevent.clone()
        self.assertTrue(cloned_subevent == subevent)

    def test_cloning_copies_fuzzy(self):
        subevent = a_subevent_with(start="1 Jan 200 10:01", end="3 Mar 200 10:01", cid=99)
        subevent.set_fuzzy(True)
        cloned_subevent = subevent.clone()
        self.assertTrue(cloned_subevent == subevent)

    def test_cloning_dont_copies_locked(self):
        subevent = a_subevent_with(start="1 Jan 200 10:01", end="3 Mar 200 10:01", cid=99)
        subevent.set_locked(True)
        cloned_subevent = subevent.clone()
        self.assertFalse(cloned_subevent == subevent)

    def test_cloning_dont_copies_ends_today(self):
        subevent = a_subevent_with(start="1 Jan 200 10:01", end="3 Mar 200 10:01", cid=99)
        subevent.set_ends_today(True)
        cloned_subevent = subevent.clone()
        self.assertFalse(cloned_subevent == subevent)
