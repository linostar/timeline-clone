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


import os.path
import random
import shutil
import sys
import tempfile
import traceback
import unittest

import wx.lib.inspection

from timelinelib.calendar.gregorian import Gregorian
from timelinelib.calendar.monthnames import ABBREVIATED_ENGLISH_MONTH_NAMES
from timelinelib.config.arguments import ApplicationArguments
from timelinelib.config.dotfile import read_config
from timelinelib.data import Category
from timelinelib.data import Container
from timelinelib.data import Event
from timelinelib.data import Subevent
from timelinelib.data import TimePeriod
from timelinelib.db import db_open
from timelinelib.time.gregoriantime import GregorianTimeType
from timelinelib.time.timeline import delta_from_days
from timelinelib.time.timeline import TimeDelta
from timelinelib.wxgui.setup import start_wx_application


ANY_TIME = "1 Jan 2010"


def gregorian_period(start, end):
    return TimePeriod(GregorianTimeType(), human_time_to_gregorian(start), human_time_to_gregorian(end))


def human_time_to_gregorian(human_time):
    (year, month, day, hour, minute) = human_time_to_ymdhm(human_time)
    return Gregorian(year, month, day, hour, minute, 0).to_time()

def a_time_period():
    year = random.randint(1, 4000)
    month = random.randint(1, 12)
    day = random.randint(1,28)
    end_year = year + random.randint(1, 5)
    end_month = random.randint(1, 12)
    end_day = random.randint(1,28)
    return TimePeriod(GregorianTimeType(),
                      Gregorian(year, month, day, 0, 0, 0).to_time(),
                      Gregorian(end_year, end_month, end_day, 0, 0, 0).to_time())

def human_time_to_ymdhm(human_time):
    parts = human_time.split(" ")
    day_part, month_part, year_part = parts[0], parts[1], parts[2]
    day = int(day_part)
    month = ABBREVIATED_ENGLISH_MONTH_NAMES.index(month_part) + 1
    year = int(year_part)
    if len(parts) == 4:
        hour = int(parts[3][:2])
        minute = int(parts[3][3:5])
    else:
        hour = 0
        minute = 0
    return (year, month, day, hour, minute)


def an_event():
    return an_event_with(time=ANY_TIME)


def an_event_with(start=None, end=None, time=ANY_TIME, text="foo", fuzzy=False,
                  locked=False, ends_today=False, category=None):
    if start and end:
        start = human_time_to_gregorian(start)
        end = human_time_to_gregorian(end)
    else:
        start = human_time_to_gregorian(time)
        end = human_time_to_gregorian(time)
    return Event(
        GregorianTimeType(), start, end, text, category=category,
        fuzzy=fuzzy, locked=locked, ends_today=ends_today)


def a_subevent():
    return a_subevent_with()


def a_subevent_with(start=None, end=None, time=ANY_TIME, text="sub", category=None, container=None, cid=-1):
    if start and end:
        start = human_time_to_gregorian(start)
        end = human_time_to_gregorian(end)
    else:
        start = human_time_to_gregorian(time)
        end = human_time_to_gregorian(time)
    return Subevent(GregorianTimeType(), start, end, text, category=category, container=container, cid=cid)


def a_container(name, category, sub_events):
    cid = 99
    start = human_time_to_gregorian(ANY_TIME)
    end = human_time_to_gregorian(ANY_TIME)
    container = Container(GregorianTimeType(), start, end, name,
                          category=category, cid=cid)
    all_events = []
    all_events.append(container)
    for (name, category) in sub_events:
        all_events.append(Subevent(GregorianTimeType(), start, end, name,
                                   category=category, container=container))
    return all_events


def a_container_with(text="container", category=None, cid=-1):
    start = human_time_to_gregorian(ANY_TIME)
    end = human_time_to_gregorian(ANY_TIME)
    container = Container(GregorianTimeType(), start, end, text, category=category, cid=cid)
    return container


def a_category():
    return a_category_with(name="category")


def a_category_with(name, color=(255, 0, 0), font_color=(0, 255, 255),
                    parent=None):
    return Category(name=name, color=color, font_color=font_color,
                    parent=parent)


def get_random_modifier(modifiers):
    return random.choice(modifiers)


def inc(number):
    if number is None:
        return 8
    else:
        return number + 1


def new_cat(event):
    if event.get_category() is None:
        return a_category_with(name="new category")
    else:
        return a_category_with(name="was: %s" % event.get_category().get_name())


def new_parent(category):
    if category.get_parent() is None:
        return a_category_with(name="new category")
    else:
        return a_category_with(name="was: %s" % category.get_parent().get_name())


def new_time_type(event):
    if event.get_time_type() is None:
        return GregorianTimeType()
    else:
        return None


def new_progress(event):
    if event.get_progress() is None:
        return 8
    else:
        return (event.get_progress() + 1) % 100


def modifier_change_ends_today(event):
    if event.get_locked():
        event.set_locked(False)
        event.set_ends_today(not event.get_ends_today())
        event.set_locked(True)
    else:
        event.set_ends_today(not event.get_ends_today())
    return event



EVENT_MODIFIERS = [
    ("change time type", lambda event:
        event.set_time_type(new_time_type(event))),
    ("change fuzzy", lambda event:
        event.set_fuzzy(not event.get_fuzzy())),
    ("change locked", lambda event:
        event.set_locked(not event.get_locked())),
    ("change ends today", modifier_change_ends_today),
    ("change id", lambda event:
        event.set_id(inc(event.get_id()))),
    ("change time period", lambda event:
        event.set_time_period(event.get_time_period().move_delta(delta_from_days(1)))),
    ("change text", lambda event:
        event.set_text("was: %s" % event.get_text())),
    ("change category", lambda event:
        event.set_category(new_cat(event))),
    ("change icon", lambda event:
        event.set_icon("was: %s" % event.get_icon())),
    ("change description", lambda event:
        event.set_description("was: %s" % event.get_description())),
    ("change hyperlink", lambda event:
        event.set_hyperlink("was: %s" % event.get_hyperlink())),
    ("change progress", lambda event:
        event.set_progress(new_progress(event))),
    ("change alert", lambda event:
        event.set_alert("was: %s" % event.get_alert())),
]


SUBEVENT_MODIFIERS = [
    ("change container id", lambda event:
        event.set_container_id(event.get_container_id()+1)),
] + EVENT_MODIFIERS


CONTAINER_MODIFIERS = [
    ("change container id", lambda event:
        event.set_cid(event.cid()+1)),
] + EVENT_MODIFIERS


CATEGORY_MODIFIERS = [
    ("change name", lambda category:
        category.set_name("was: %s" % category.get_name())),
    ("change id", lambda category:
        category.set_id(inc(category.get_id()))),
    ("change color", lambda category:
        category.set_color(category.get_color()+(1, 0, 3))),
    ("change font color", lambda category:
        category.set_font_color(category.get_font_color()+(1, 0, 3))),
    ("change parent", lambda category:
        category.set_parent(new_parent(category))),
]


TIME_PERIOD_MODIFIERS = [
    ("zoom", lambda time_period:
        time_period.zoom(-1)),
    ("extend left", lambda time_period:
        time_period.update(time_period.start_time-time_period.time_type.get_min_zoom_delta()[0],
                           time_period.end_time)),
    ("extend right", lambda time_period:
        time_period.update(time_period.start_time,
                           time_period.end_time+time_period.time_type.get_min_zoom_delta()[0])),
]


TIME_MODIFIERS = [
    ("add", lambda time: time + TimeDelta(1)),
]


class TestCase(unittest.TestCase):

    def assertListIsCloneOf(self, cloned_list, original_list):
        self.assertEqual(cloned_list, original_list)
        self.assertTrue(cloned_list is not original_list)
        for i in range(len(cloned_list)):
            self.assertIsCloneOf(cloned_list[i], original_list[i])

    def assertIsCloneOf(self, clone, original):
        self.assertEqual(clone, original)
        self.assertTrue(clone is not original, "%r" % clone)

    def assertInstanceNotIn(self, object_, list_):
        for element in list_:
            if element is object_:
                self.fail("%r was in list" % object_)

    def assertEqNeImplementationIsCorrect(self, create_fn, modifiers):
        (modification_description, modifier_fn) = get_random_modifier(modifiers)
        one = modifier_fn(create_fn())
        other = modifier_fn(create_fn())
        fail_message_one_other = "%r vs %r (%s)" % (one, other,
                                                    modification_description)
        self.assertTrue(type(one) == type(other), fail_message_one_other)
        self.assertFalse(one == None, fail_message_one_other)
        self.assertTrue(one != None, fail_message_one_other)
        self.assertTrue(one is not other, fail_message_one_other)
        self.assertFalse(one is other, fail_message_one_other)
        self.assertTrue(one == other, fail_message_one_other)
        self.assertFalse(one != other, fail_message_one_other)
        self.assertTrue(one == one, fail_message_one_other)
        self.assertFalse(one != one, fail_message_one_other)
        (modification_description, modifier_fn) = get_random_modifier(modifiers)
        modified = modifier_fn(other)
        fail_message_modified_one = "%r vs %r (%s)" % (modified, one,
                                                       modification_description)
        self.assertTrue(type(modified) == type(one), fail_message_modified_one)
        self.assertTrue(modified is not one, fail_message_modified_one)
        self.assertFalse(modified is one, fail_message_modified_one)
        self.assertTrue(modified != one, fail_message_modified_one)
        self.assertFalse(modified == one, fail_message_modified_one)


class TmpDirTestCase(TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="timeline-test")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def get_tmp_path(self, name):
        return os.path.join(self.tmp_dir, name)


class WxComponentTest(TestCase):

    def setUp(self):
        self._app = wx.App(False)
        self._main_frame = wx.Frame(None)
        self._main_frame.Bind(wx.EVT_CLOSE, self._main_frame_on_close)
        self._main_panel = wx.Panel(self._main_frame)
        self._components = []
        self._component_by_name = {}
        self._is_close_called = False

    def tearDown(self):
        self._close()

    def add_component(self, name, cls, *args):
        self._component_by_name[name] = cls(self._main_panel, *args)
        self._components.append(self._component_by_name[name])

    def add_button(self, text, callback, component_name=None):
        button = wx.Button(self._main_panel, label=text)
        self._components.append(button)
        def event_listener(event):
            if component_name:
                callback(self.get_component(component_name))
            else:
                callback()
        button.Bind(wx.EVT_BUTTON, event_listener)

    def add_separator(self):
        label = "----- separator -----"
        self._components.append(wx.StaticText(self._main_panel, label=label))

    def get_component(self, name):
        return self._component_by_name[name]

    def show_test_window(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        for component in self._components:
            sizer.Add(component, flag=wx.ALL|wx.GROW, border=3)
        self._main_panel.SetSizer(sizer)
        self._main_frame.Show()
        if not self.HALT_FOR_MANUAL_INSPECTION:
            wx.CallAfter(self._close)
        self._app.MainLoop()

    def _main_frame_on_close(self, event):
        self._is_close_called = True
        self._main_frame.Destroy()

    def _close(self):
        if not self._is_close_called:
            self._main_frame.Close()
            self._is_close_called = True


class WxEndToEndTestCase(TmpDirTestCase):

    def setUp(self):
        TmpDirTestCase.setUp(self)
        self.timeline_path = self.get_tmp_path("test.timeline")
        self.config_file_path = self.get_tmp_path("thetimelineproj.cfg")
        self.config = read_config(self.config_file_path)
        self.standard_excepthook = sys.excepthook
        self.error_in_gui_thread = None

    def tearDown(self):
        TmpDirTestCase.tearDown(self)
        sys.excepthook = self.standard_excepthook

    def start_timeline_and(self, steps_to_perform_in_gui):
        self.config.write()
        self.steps_to_perform_in_gui = steps_to_perform_in_gui
        application_arguments = ApplicationArguments()
        application_arguments.parse_from(
            ["--config-file", self.config_file_path, self.timeline_path])
        start_wx_application(application_arguments, self._before_main_loop_hook)
        if self.error_in_gui_thread:
            exc_type, exc_value, exc_traceback = self.error_in_gui_thread
            a = traceback.format_exception(exc_type, exc_value, exc_traceback)
            self.fail("Exception in GUI thread: %s" % "".join(a))

    def read_written_timeline(self):
        return db_open(self.timeline_path)

    def _before_main_loop_hook(self):
        sys.excepthook = self.standard_excepthook
        self._setup_steps_to_perform_in_gui(self.steps_to_perform_in_gui)

    def _setup_steps_to_perform_in_gui(self, steps, in_sub_step_mode=False):
        def perform_current_step_and_queue_next():
            if len(steps) >= 2 and isinstance(steps[1], list):
                self._setup_steps_to_perform_in_gui(steps[1], True)
                next_step_index = 2
            else:
                next_step_index = 1
            try:
                steps[0]()
            except Exception:
                wx.GetApp().GetTopWindow().Close()
                self.error_in_gui_thread = sys.exc_info()
            else:
                if steps[0] != self.show_widget_inspector:
                    self._setup_steps_to_perform_in_gui(steps[next_step_index:], in_sub_step_mode)
        if len(steps) > 0:
            wx.CallAfter(perform_current_step_and_queue_next)
        elif not in_sub_step_mode:
            wx.CallAfter(wx.GetApp().GetTopWindow().Close)

    def show_widget_inspector(self):
        wx.lib.inspection.InspectionTool().Show()

    def click_menu_item(self, item_path):
        def click():
            item_names = [_(x) for x in item_path.split(" -> ")]
            menu_bar = wx.GetApp().GetTopWindow().GetMenuBar()
            menu = menu_bar.GetMenu(menu_bar.FindMenu(item_names[0]))
            for sub in item_names[1:]:
                menu = menu_bar.FindItemById(menu.FindItem(sub))
            wx.GetApp().GetTopWindow().ProcessEvent(
                wx.CommandEvent(wx.EVT_MENU.typeId, menu.GetId()))
        return click

    def click_button(self, component_path):
        def click():
            component = self.find_component(component_path)
            component.ProcessEvent(wx.CommandEvent(wx.EVT_BUTTON.typeId, component.GetId()))
        return click

    def enter_text(self, component_path, text):
        def enter():
            self.find_component(component_path).SetValue(text)
        return enter

    def find_component(self, component_path):
        components_to_search_in = wx.GetTopLevelWindows()
        for component_name in component_path.split(" -> "):
            component = self._find_component_with_name_in(
                components_to_search_in, component_name)
            if component == None:
                self.fail("Could not find component with path '%s'." % component_path)
            else:
                components_to_search_in = component.GetChildren()
        return component

    def _find_component_with_name_in(self, components, seeked_name):
        for component in components:
            if self._matches_seeked_name(component, seeked_name):
                return component
        for component in components:
            sub = self._find_component_with_name_in(component.GetChildren(), seeked_name)
            if sub:
                return sub
        return None

    def _matches_seeked_name(self, component, seeked_name):
        if component.GetName() == seeked_name:
            return True
        elif component.GetId() == self._wx_id_from_name(seeked_name):
            return True
        elif hasattr(component, "GetLabelText") and component.GetLabelText() == _(seeked_name):
            return True
        elif component.GetLabel() == _(seeked_name):
            return True
        return False

    def _wx_id_from_name(self, name):
        if name.startswith("wxID_"):
            return getattr(wx, name[2:])
        return None


class ObjectWithTruthValue(object):

    def __init__(self, truth_value):
        self.truth_value = truth_value

    def __nonzero__(self):
        return self.truth_value
