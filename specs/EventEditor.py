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

from mock import Mock

from timelinelib.gui.dialogs.eventeditor import EventEditor
from timelinelib.gui.dialogs.eventeditor import EventEditorController
from timelinelib.db.objects import Event
from timelinelib.db.objects import Category
from timelinelib.db.interface import TimelineDB
from timelinelib.time import PyTimeType


POINT_NOEVENT_NONZEROTIME = 1
POINT_NOEVENT_ZEROTIME = 2
PERIOD_NOEVENT_NONZEROTIME = 3
PERIOD_NOEVENT_ZEROTIME = 4
POINT_EVENT_NONZEROTIME = 5
POINT_EVENT_ZEROTIME = 6
PERIOD_EVENT_NONZEROTIME = 7
PERIOD_EVENT_ZEROTIME = 8
PERIOD_EVENT_NONZEROTIME_FUZZY_LOCKED = 9

START = 1
END = 2
NAME = 3
FUZZY = 4
LOCKED = 5

class EventEditorControllerSpec(unittest.TestCase):
    
    def setUp(self):
        pass
        
    def testDialogInitialisezWithNewPointEventAtZeroTime(self):
        self._create_controller(POINT_NOEVENT_ZEROTIME)
        self.view.set_start.assert_called_with(create_zero_time1())
        self.view.set_end.assert_called_with(create_zero_time1())
        self.view.set_show_period.assert_called_with(False)
        self.view.set_show_time.assert_called_with(False)
        self.view.set_name.assert_called_with("")
        self.view.set_category.assert_called_with(None)
        self.view.set_show_add_more.assert_called_with(True)
        self.view.set_fuzzy.assert_called_with(False)
        self.view.set_locked.assert_called_with(False)

    def testDialogInitialisezWithNewPointEventAtNonzeroTime(self):
        self._create_controller(POINT_NOEVENT_NONZEROTIME)
        self.view.set_start.assert_called_with(create_nonzero_time1())
        self.view.set_end.assert_called_with(create_nonzero_time1())
        self.view.set_show_period.assert_called_with(False)
        self.view.set_show_time.assert_called_with(True)
        self.view.set_name.assert_called_with("")
        self.view.set_category.assert_called_with(None)
        self.view.set_show_add_more.assert_called_with(True)
        self.view.set_fuzzy.assert_called_with(False)
        self.view.set_locked.assert_called_with(False)

    def testDialogInitialisezWithNewPeriodEventAtZeroTime(self):
        self._create_controller(PERIOD_NOEVENT_ZEROTIME)
        self.view.set_start.assert_called_with(create_zero_time1())
        self.view.set_end.assert_called_with(create_zero_time2())
        self.view.set_show_period.assert_called_with(True)
        self.view.set_show_time.assert_called_with(False)
        self.view.set_name.assert_called_with("")
        self.view.set_category.assert_called_with(None)
        self.view.set_show_add_more.assert_called_with(True)
        self.view.set_fuzzy.assert_called_with(False)
        self.view.set_locked.assert_called_with(False)

    def testDialogInitialisezWithNewPeriodEventAtNonzeroTime(self):
        self._create_controller(PERIOD_NOEVENT_NONZEROTIME)
        self.view.set_start.assert_called_with(create_nonzero_time1())
        self.view.set_end.assert_called_with(create_nonzero_time2())
        self.view.set_show_period.assert_called_with(True)
        self.view.set_show_time.assert_called_with(True)
        self.view.set_name.assert_called_with("")
        self.view.set_category.assert_called_with(None)
        self.view.set_show_add_more.assert_called_with(True)
        self.view.set_fuzzy.assert_called_with(False)
        self.view.set_locked.assert_called_with(False)

    def testDialogInitialisezWithPointEventAtZeroTime(self):
        self._create_controller(POINT_EVENT_ZEROTIME)
        self.view.set_start.assert_called_with(create_zero_time1())
        self.view.set_end.assert_called_with(create_zero_time1())
        self.view.set_show_period.assert_called_with(False)
        self.view.set_show_time.assert_called_with(False)
        self.view.set_name.assert_called_with("foo")
        self.view.set_category.assert_called_with(self.controller.event.category)
        self.view.set_show_add_more.assert_called_with(False)
        self.view.set_fuzzy.assert_called_with(False)
        self.view.set_locked.assert_called_with(False)
        
    def testDialogInitialisezWithPointEventAtNonzeroTime(self):
        self._create_controller(POINT_EVENT_NONZEROTIME)
        self.view.set_start.assert_called_with(create_nonzero_time1())
        self.view.set_end.assert_called_with(create_nonzero_time1())
        self.view.set_show_period.assert_called_with(False)
        self.view.set_show_time.assert_called_with(True)
        self.view.set_name.assert_called_with("foo")
        self.view.set_category.assert_called_with(self.controller.event.category)
        self.view.set_show_add_more.assert_called_with(False)
        self.view.set_fuzzy.assert_called_with(False)
        self.view.set_locked.assert_called_with(False)

    def testDialogInitialisezWithPeriodEventAtZeroTime(self):
        self._create_controller(PERIOD_EVENT_ZEROTIME)
        self.view.set_start.assert_called_with(create_zero_time1())
        self.view.set_end.assert_called_with(create_zero_time2())
        self.view.set_show_period.assert_called_with(True)
        self.view.set_show_time.assert_called_with(False)
        self.view.set_name.assert_called_with("foo")
        self.view.set_category.assert_called_with(self.controller.event.category)
        self.view.set_show_add_more.assert_called_with(False)
        self.view.set_fuzzy.assert_called_with(False)
        self.view.set_locked.assert_called_with(False)

    def testDialogInitialisezWithPeriodEventAtNonzeroTime(self):
        self._create_controller(PERIOD_EVENT_NONZEROTIME)
        self.view.set_start.assert_called_with(create_nonzero_time1())
        self.view.set_end.assert_called_with(create_nonzero_time2())
        self.view.set_show_period.assert_called_with(True)
        self.view.set_show_time.assert_called_with(True)
        self.view.set_name.assert_called_with("foo")
        self.view.set_category.assert_called_with(self.controller.event.category)
        self.view.set_show_add_more.assert_called_with(False)
        self.view.set_fuzzy.assert_called_with(False)
        self.view.set_locked.assert_called_with(False)

    def testOnInitDialogDisplaysFuzzyAndLocked(self):
        self._create_controller(PERIOD_EVENT_NONZEROTIME_FUZZY_LOCKED)
        self.view.set_fuzzy.assert_called_with(True)
        self.view.set_locked.assert_called_with(True)

    def testOnOkFuzzyAndLockedAreUpdated(self):
        self._create_controller(PERIOD_EVENT_NONZEROTIME_FUZZY_LOCKED)
        self.view.set_fuzzy.assert_called_with(True)
        self.view.set_locked.assert_called_with(True)
        self._simulate_user_input(NAME, "new_event")
        self._simulate_user_input(START, create_nonzero_time1())
        self._simulate_user_input(END, create_nonzero_time2())
        self._simulate_user_input(FUZZY, False)
        self._simulate_user_input(LOCKED, False)
        self._simulate_ok_click()
        self.assertFalse(self.controller.event.fuzzy)
        self.assertFalse(self.controller.event.locked)

    def testOnOkNewEventIsSavedToDb(self):
        self._create_controller(POINT_EVENT_ZEROTIME)
        self._simulate_user_input(NAME, "new_event")
        self._simulate_user_input(START, create_nonzero_time1())
        self._simulate_user_input(END, create_nonzero_time2())
        self._simulate_ok_click()
        self.assertTrue(self.controller.db.save_event.called)
        self.assertEquals("new_event", self.controller.event.text)
        
    def testOnOkEventIsUpdated(self):
        self._create_controller(POINT_EVENT_NONZEROTIME)
        self._simulate_user_input(NAME, "updated_event")
        self._simulate_user_input(START, create_nonzero_time1())
        self._simulate_user_input(END, create_nonzero_time2())
        self._simulate_ok_click()
        self.assertTrue(self.controller.db.save_event.called)
        self.assertEquals("updated_event", self.controller.event.text)

    def testNameFieldMustNotBeEmptyWhenClickingOk(self):
        self._create_controller(POINT_NOEVENT_NONZEROTIME)
        self._simulate_user_input(NAME, "")
        self._simulate_ok_click()
        self.assertTrue(self.view.display_invalid_name.called)

    def testStartMustBeLessThenEndWhenClickingOk(self):
        self._create_controller(PERIOD_NOEVENT_NONZEROTIME)
        self._simulate_user_input(NAME, "updated_event")
        self._simulate_user_input(START, create_nonzero_time2())
        self._simulate_user_input(END, create_nonzero_time1())
        self._simulate_ok_click()
        self.assertTrue(self.view.display_invalid_end.called)

    def _create_controller(self, type):
        if type == POINT_NOEVENT_ZEROTIME:
            self.controller = given_no_event_point_at_zero_time()
        elif type == POINT_NOEVENT_NONZEROTIME:
            self.controller = given_no_event_point_event_at_nonzero_time()
        elif type == PERIOD_NOEVENT_ZEROTIME:
            self.controller = given_no_event_period_at_zero_time()
        elif type == PERIOD_NOEVENT_NONZEROTIME:
            self.controller = given_no_event_period_at_nonzero_time()
        elif type == POINT_EVENT_ZEROTIME:
            self.controller = given_event_point_at_zero_time()
        elif type == POINT_EVENT_NONZEROTIME:
            self.controller = given_event_point_at_nonzero_time()
        elif type == PERIOD_EVENT_ZEROTIME:
            self.controller = given_event_period_at_zero_time()
        elif type == PERIOD_EVENT_NONZEROTIME:
            self.controller = given_period_event_at_nonzero_time()
        elif type == PERIOD_EVENT_NONZEROTIME_FUZZY_LOCKED:
            self.controller = given_period_event_at_nonzero_time_fuzzy_and_locked()
        self.view = self.controller.view
        self.controller.initialize()

    def _simulate_user_input(self, control, value):
        if control == START:
            self.view.get_start.return_value = value
        elif control == END:
            self.view.get_end.return_value = value
        elif control == NAME:
            self.view.get_name.return_value = value
        elif control == FUZZY:
            self.view.get_fuzzy.return_value = value
        elif control == LOCKED:
            self.view.get_locked.return_value = value

    def _simulate_ok_click(self):
        self.controller.create_or_update_event()

        
def given_no_event_point_at_zero_time():
    view, db = create_view_and_db()
    tm = create_zero_time1()
    controller = EventEditorController(view, db, tm, tm, None)
    return controller


def given_no_event_point_event_at_nonzero_time():
    view, db = create_view_and_db()
    tm = create_nonzero_time1()
    controller = EventEditorController(view, db, tm, tm, None)
    return controller


def given_no_event_period_at_zero_time():
    view, db = create_view_and_db()
    tm1 = create_zero_time1()
    tm2 = create_zero_time2()
    controller = EventEditorController(view, db, tm1, tm2, None)
    return controller


def given_no_event_period_at_nonzero_time():
    view, db = create_view_and_db()
    tm1 = create_nonzero_time1()
    tm2 = create_nonzero_time2()
    controller = EventEditorController(view, db, tm1, tm2, None)
    return controller


def given_event_point_at_zero_time():
    view, db = create_view_and_db()
    tm = create_zero_time1()
    cat = Category("bar", None, True)
    event = Event(db, tm, tm, "foo", cat, fuzzy=False, locked=False)
    controller = EventEditorController(view, db, None, None, event)
    return controller

def given_event_point_at_nonzero_time():
    view, db = create_view_and_db()
    tm = create_nonzero_time1()
    cat = Category("bar", None, True)
    event = Event(db, tm, tm, "foo", cat, fuzzy=False, locked=False)
    controller = EventEditorController(view, db, None, None, event)
    return controller


def given_event_period_at_zero_time():
    view, db = create_view_and_db()
    tm1 = create_zero_time1()
    tm2 = create_zero_time2()
    cat = Category("bar", None, True) 
    event = Event(db, tm1, tm2, "foo", cat, fuzzy=False, locked=False)
    controller = EventEditorController(view, db, None, None, event)
    return controller


def given_period_event_at_nonzero_time():
    view, db = create_view_and_db()
    tm1 = create_nonzero_time1()
    tm2 = create_nonzero_time2()
    cat = Category("bar", None, True)
    event = Event(db, tm1, tm2, "foo", cat, fuzzy=False, locked=False)
    controller = EventEditorController(view, db, None, None, event)
    return controller
    
    
def given_period_event_at_nonzero_time_fuzzy_and_locked():
    view, db = create_view_and_db()
    tm1 = create_nonzero_time1()
    tm2 = create_nonzero_time2()
    cat = Category("bar", None, True)
    event = Event(db, tm1, tm2, "foo", cat, fuzzy=True, locked=True)
    controller = EventEditorController(view, db, None, None, event)
    return controller
    
    
def create_view_and_db():
    view =  Mock(EventEditor)
    db = Mock(TimelineDB)
    db.get_time_type.return_value = PyTimeType()
    return (view, db)


def create_zero_time1():
    return  PyTimeType().parse_time("2011-01-01 00:00:00")


def create_zero_time2():
    return PyTimeType().parse_time("2011-01-02 00:00:00")


def create_nonzero_time1():
    return PyTimeType().parse_time("2011-01-01 12:00:00")


def create_nonzero_time2():
    return  PyTimeType().parse_time("2011-01-02 00:00:00")
