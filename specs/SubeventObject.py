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
from timelinelib.data import Container
from timelinelib.data import Subevent


class SubeventSpec(unittest.TestCase):

    def testSubeventCanChangeContainer(self):
        self.given_default_subevent()
        self.given_container_with_cid()
        self.subevent.register_container(self.container)
        self.assertEqual(99, self.subevent.cid())
        self.assertEqual(self.container, self.subevent.container)

    def given_default_subevent(self):
        self.subevent = Subevent(self.db.get_time_type(), self.time("2000-01-01 10:01:01"),
                                 self.time("2000-01-03 10:01:01"), "evt")

    def given_container_with_cid(self):
        self.container = Container(self.db.get_time_type(), self.now, self.now, "evt", cid=99)


    def time(self, tm):
        return self.db.get_time_type().parse_time(tm)

    def setUp(self):
        self.db = MemoryDB()
        self.now = self.db.get_time_type().now()


class ContainerSubeventSpec(unittest.TestCase):

    def testSubeventPropertiesDefaultsToFalse(self):
        self.given_default_subevent()
        self.assertEqual(-1, self.subevent.cid())
        self.assertEqual(False, self.subevent.get_fuzzy())
        self.assertEqual(False, self.subevent.get_locked())
        self.assertEqual(False, self.subevent.get_ends_today())
        self.assertEqual(False, self.subevent.is_container())
        self.assertEqual(True, self.subevent.is_subevent())

    def testSubeventPropertyCidCanBeSetAtConstruction(self):
        self.given_subevent_with_cid()
        self.assertEqual(99, self.subevent.cid())

    def given_default_subevent(self):
        self.subevent = Subevent(self.db.get_time_type(), self.time("2000-01-01 10:01:01"),
                                 self.time("2000-01-03 10:01:01"), "evt")

    def given_subevent_with_cid(self):
        self.subevent = Subevent(self.db.get_time_type(), self.time("2000-01-01 10:01:01"),
                                 self.time("2000-01-03 10:01:01"), "evt", cid=99)

    def time(self, tm):
        return self.db.get_time_type().parse_time(tm)

    def setUp(self):
        self.db = MemoryDB()
        self.now = self.db.get_time_type().now()


class SubeventCloningSpec(unittest.TestCase):

    def test_cloning_returns_new_object(self):
        self.given_subevent_event()
        cloned_event = self.event.clone()
        self.assertTrue(self.event != cloned_event)
        self.assertEqual(cloned_event.get_time_type(),
                         self.event.get_time_type())
        self.assertEqual(cloned_event.get_time_period(),
                         self.event.get_time_period())
        self.assertEqual(cloned_event.text, self.event.text)
        self.assertEqual(cloned_event.category, self.event.category)
        self.assertEqual(cloned_event.get_fuzzy(), self.event.get_fuzzy())
        self.assertEqual(cloned_event.get_locked(), self.event.get_locked())
        self.assertEqual(cloned_event.get_ends_today(),
                         self.event.get_ends_today())

    def given_subevent_event(self):
        self.event = Subevent(self.db.get_time_type(), self.now, self.now, "evt")

    def setUp(self):
        self.db = MemoryDB()
        self.now = self.db.get_time_type().now()
