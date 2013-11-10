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

from timelinelib.utilities.observer import Observable
from timelinelib.utilities.observer import STATE_CHANGE_ANY
from timelinelib.utilities.observer import STATE_CHANGE_CATEGORY


class ObservableSpec(unittest.TestCase):

    def test_at_construction_there_area_zero_observers(self):
        self.assertTrue(len(self.observable._observers) == 0)

    def test_an_observer_can_be_registered(self):
        self.registerObserver()
        self.assertTrue(len(self.observable._observers) == 1)

    def test_an_observer_can_be_unregistered(self):
        self.registerObserver()
        self.observable.unregister(self.observer.event_triggered)
        self.assertTrue(len(self.observable._observers) == 0)

    def test_an_observer_gets_notifications(self):
        self.registerObserver()
        self.observable._notify(STATE_CHANGE_ANY)
        self.observable._notify(STATE_CHANGE_CATEGORY)
        self.assertTrue(len(self.observer.events) == 2)
        self.assertTrue(self.observer.events[0] == STATE_CHANGE_ANY)
        self.assertTrue(self.observer.events[1] == STATE_CHANGE_CATEGORY)

    def test_can_listen_for_specific_events(self):
        observer = Observer()
        self.observable.listen_for("bananas", observer.event_triggered2)
        self.observable._notify("apples")
        self.observable._notify("bananas")
        self.assertEqual(len(observer.events), 1)

    def test_can_listen_for_all_events(self):
        observer = Observer()
        self.observable.listen_for_any(observer.event_triggered2)
        self.observable._notify()
        self.observable._notify()
        self.assertEqual(len(observer.events), 2)

    def test_can_unlisten(self):
        observer = Observer()
        self.observable.listen_for_any(observer.event_triggered2)
        self.observable._notify()
        self.observable.unlisten(observer.event_triggered2)
        self.observable._notify()
        self.assertEqual(len(observer.events), 1)

    def setUp(self):
        self.observable = Observable()

    def registerObserver(self):
        self.observer = Observer()
        self.observable.register(self.observer.event_triggered)


class Observer():
    
    def __init__(self):
        self.events = []
        
    def event_triggered(self, evt):
        self.events.append(evt)

    def event_triggered2(self):
        self.events.append(None)
