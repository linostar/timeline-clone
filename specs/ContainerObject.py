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

from specs.utils import a_category_with
from timelinelib.data.db import MemoryDB
from timelinelib.data import Container
from specs.utils import a_container_with
from specs.utils import a_subevent_with


class describe_container(unittest.TestCase):

    def test_can_have_subevents(self):
        subevent = a_subevent_with(start="1 Jan 200 10:01", end="3 Mar 200 10:01")
        container = a_container_with(text="container")
        container.register_subevent(subevent)
        self.assertEqual(1, len(container.events))
        self.assertEqual(subevent, container.events[0])

    def test_subevents_can_be_unregistered(self):
        subevent = a_subevent_with(start="1 Jan 200 10:01", end="3 Mar 200 10:01")
        container = a_container_with(text="container")
        container.register_subevent(subevent)
        container.unregister_subevent(subevent)
        self.assertEqual(0, len(container.events))

    def test_name_can_be_updated(self):
        container = a_container_with(text="container")
        new_name = "new text"
        container.update_properties(new_name)
        self.assertEqual(new_name, container.get_text())

    def test_category_can_be_updated(self):
        container = a_container_with(text="container")
        new_name = "new text"
        new_category = a_category_with(name="cat")
        container.update_properties(new_name, category=new_category)
        self.assertEqual(new_category, container.get_category())

    def test_default_cid(self):
        container = a_container_with(text="container")
        self.assertEqual(-1, container.cid())

    def test_cid_can_be_changed(self):
        container = a_container_with(text="container")
        container.set_cid(99)
        self.assertEqual(99, container.cid())


class ContainerConstructorSpec(unittest.TestCase):

    def testContainerPropertiesDefaultsToFalse(self):
        self.given_default_container()
        self.assertEqual(-1, self.container.cid())
        self.assertEqual(False, self.container.get_fuzzy())
        self.assertEqual(False, self.container.get_locked())
        self.assertEqual(False, self.container.get_ends_today())
        self.assertEqual(True, self.container.is_container())
        self.assertEqual(False, self.container.is_subevent())
        self.assertEqual(None, self.container.get_category())

    def testContainerPropertyCidCanBeSetAtConstruction(self):
        self.given_container_with_cid()
        self.assertEqual(99, self.container.cid())

    def given_default_container(self):
        self.container = Container(self.db.get_time_type(), self.now, self.now, "container")

    def given_container_with_cid(self):
        self.container = Container(self.db.get_time_type(), self.now, self.now, "evt", cid=99)

    def setUp(self):
        self.db = MemoryDB()
        self.now = self.db.get_time_type().now()


class ContainerCloningSpec(unittest.TestCase):

    def test_cloning_returns_new_object(self):
        self.given_container_event()
        cloned_event = self.event.clone()
        self.assertTrue(self.event is not cloned_event)
        self.assertEqual(cloned_event.get_time_type(),
                         self.event.get_time_type())
        self.assertEqual(cloned_event.get_time_period(),
                         self.event.get_time_period())
        self.assertEqual(cloned_event.get_text(), self.event.get_text())
        self.assertEqual(cloned_event.get_category(), self.event.get_category())
        self.assertEqual(cloned_event.get_fuzzy(), self.event.get_fuzzy())
        self.assertEqual(cloned_event.get_locked(), self.event.get_locked())
        self.assertEqual(cloned_event.get_ends_today(),
                         self.event.get_ends_today())

    def given_container_event(self):
        self.event = Container(self.db.get_time_type(), self.now, self.now, "evt")

    def setUp(self):
        self.db = MemoryDB()
        self.now = self.db.get_time_type().now()
