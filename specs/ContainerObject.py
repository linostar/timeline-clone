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
from timelinelib.data import Subevent


class ContainerSpec(unittest.TestCase):

    def testContainerCanHaveSubevents(self):
        self.given_period_subevent()
        self.given_default_container()
        self.container.register_subevent(self.event)
        self.assertEqual(1, len(self.container.events))

    def testSubeventsCanBeUnregistered(self):
        self.given_period_subevent()
        self.given_default_container()
        self.container.register_subevent(self.event)
        self.assertEqual(1, len(self.container.events))
        self.container.unregister_subevent(self.event)
        self.assertEqual(0, len(self.container.events))

    def testNameCanBeUpdated(self):
        self.given_default_container()
        new_name = "new text"
        self.container.update_properties(new_name)
        self.assertEqual(new_name, self.container.get_text())

    def testNameAndCategoryCanBeUpdated(self):
        self.given_default_container()
        new_name = "new text"
        new_category = a_category_with(name="cat")
        self.container.update_properties(new_name, new_category)
        self.assertEqual(new_category, self.container.get_category())

    def testCidCanBeChanged(self):
        self.given_default_container()
        self.container.set_cid(99)
        self.assertEqual(99, self.container.cid())

    def given_default_container(self):
        self.container = Container(self.db.get_time_type(), self.now, self.now, "container")

    def given_period_subevent(self):
        self.event = Subevent(self.db.get_time_type(), self.time("2000-01-01 10:01:01"),
                              self.time("2000-01-03 10:01:01"), "evt")

    def time(self, tm):
        return self.db.get_time_type().parse_time(tm)

    def setUp(self):
        self.db = MemoryDB()
        self.now = self.db.get_time_type().now()


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
        self.assertTrue(self.event != cloned_event)
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
