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

from timelinelib.db.backends.memory import MemoryDB
from timelinelib.db.container import Container
from timelinelib.db.subevent import Subevent
from timelinelib.db.strategies import DefaultContainerStrategy


class DefaultContainerStartegySpec(unittest.TestCase):
    
    def testConstruction(self):
        self.given_strategy_with_container()
        self.assertEqual(self.container, self.strategy.container)

    def testFirstRegisteredEventDecidesContainerPeriod(self):
        self.given_strategy_with_container()
        self.given_subevent1()
        self.strategy.register_subevent(self.subevent1)
        self.assertEqual(self.container.time_period.start_time, self.subevent1.time_period.start_time)
        self.assertEqual(self.container.time_period.end_time, self.subevent1.time_period.end_time)

    def testSecondRegisteredEventExpandsContainerPeriod(self):
        self.given_strategy_with_container()
        self.given_subevent1()
        self.given_subevent2()
        self.strategy.register_subevent(self.subevent1)
        self.strategy.register_subevent(self.subevent2)
        self.assertEqual(self.container.time_period.start_time, self.subevent1.time_period.start_time)
        self.assertEqual(self.container.time_period.end_time, self.subevent2.time_period.end_time)

    def testRemovingOneEventContractsContainerPeriod(self):
        self.given_strategy_with_container()
        self.given_subevent1()
        self.given_subevent2()
        self.strategy.register_subevent(self.subevent1)
        self.strategy.register_subevent(self.subevent2)
        self.strategy.unregister_subevent(self.subevent1)
        self.assertEqual(self.container.time_period.start_time, self.subevent2.time_period.start_time)
        self.assertEqual(self.container.time_period.end_time, self.subevent2.time_period.end_time)

    def testUpdatingSubeventExpandsContainerPeriod(self):
        self.given_strategy_with_container()
        self.given_subevent1()
        self.given_subevent2()
        self.strategy.register_subevent(self.subevent1)
        self.strategy.register_subevent(self.subevent2)
        self.subevent2.time_period.end_time = self.time("2000-05-01 10:01:01")
        self.strategy.update(self.subevent2)
        self.assertEqual(self.container.time_period.start_time, self.subevent1.time_period.start_time)
        self.assertEqual(self.container.time_period.end_time, self.subevent2.time_period.end_time)
    
    def given_strategy_with_container(self):
        self.container = Container(self.db.get_time_type(), self.time("2000-01-01 10:01:01"), 
                                   self.time("2000-01-01 10:01:01"), "Container1")
        self.strategy = DefaultContainerStrategy(self.container)

    def given_subevent1(self):
        self.subevent1 = Subevent(self.db.get_time_type(), self.time("2000-01-01 10:01:01"), 
                                  self.time("2000-02-01 10:01:01"), "Container1")

    def given_subevent2(self):
        self.subevent2 = Subevent(self.db.get_time_type(), self.time("2000-03-01 10:01:01"), 
                                  self.time("2000-04-01 10:01:01"), "Container1")

    def time(self, tm):
        return self.db.get_time_type().parse_time(tm)
    
    def setUp(self):
        self.db = MemoryDB()
        self.now = self.db.get_time_type().now()
        self.time_type = self.db.get_time_type()
    