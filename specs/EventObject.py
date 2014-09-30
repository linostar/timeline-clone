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
from specs.utils import an_event
from specs.utils import an_event_with


class describe_event_cloning(TestCase):

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
