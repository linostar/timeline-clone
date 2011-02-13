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
import wx

from specs.utils import human_time_to_py
from specs.utils import py_period
from timelinelib.config import Config
from timelinelib.db.backends.memory import MemoryDB
from timelinelib.db.objects import Event
from timelinelib.gui.components.timelineview import DrawingArea
from timelinelib.gui.components.timelineview import DrawingAreaController
from timelinelib.gui.dialogs.mainframe import StatusBarAdapter


# TODO: testSavesEventAfterMove
# TODO: testSavesEventAfterResize


DISPLAYED_PERIOD      = py_period("1 Aug 2010", "21 Aug 2010")
PERIOD_LENGTH_IN_DAYS = 20
VIEW_WIDTH            = PERIOD_LENGTH_IN_DAYS * 10
VIEW_HEIGHT           = 100
EVENT_HEIGHT          = 10
POINT_Y               = VIEW_HEIGHT / 2 - EVENT_HEIGHT * 2
PERIOD_Y              = VIEW_HEIGHT / 2 + EVENT_HEIGHT


class TimelineViewSpec(unittest.TestCase):

    def test_initializes_displayed_period_from_db(self):
        self.given_db_set()
        self.assert_displays_period("1 Aug 2010", "21 Aug 2010")

    def test_scrolls_timeline_when_dragging_mouse(self):
        self.given_db_set()
        self.simulate_mouse_down_move_up(0, 0, 10, 0, ctrl_down=False, shift_down=False)
        self.assert_changed_displayed_period_to("31 Jul 2010", "20 Aug 2010")

    def test_zooms_timeline_when_shift_dragging_mouse(self):
        self.given_db_set()
        self.simulate_mouse_down_move_up(0, 0, 20, 0, ctrl_down=False, shift_down=True)
        self.assert_changed_displayed_period_to("1 Aug 2010", "3 Aug 2010")

    def test_centers_displayed_period_around_middle_click_position(self):
        self.given_db_set()
        self.controller.middle_mouse_clicked(110)
        self.assert_changed_displayed_period_to("2 Aug 2010", "22 Aug 2010")

    def test_zooms_timeline_by_10_percent_on_each_side_when_scrolling_while_holding_down_ctrl(self):
        self.given_db_set()
        self.controller.mouse_wheel_moved(1, ctrl_down=True, shift_down=False)
        self.assert_changed_displayed_period_to("3 Aug 2010", "19 Aug 2010")

    def test_displays_balloon_for_event_with_description(self):
        event = self.add_event("4 Aug 2010", "10 Aug 2010", description="test")
        self.given_db_set()
        self.controller.mouse_moved(50, PERIOD_Y)
        self.assertTrue(self.view.start_balloon_show_timer.called)
        self.controller.balloon_show_timer_fired()
        self.assertEquals(event, self.controller.get_view_properties().hovered_event)

    def test_hides_balloon_when_leaving_event(self):
        event = self.add_event("4 Aug 2010", "10 Aug 2010", description="test")
        self.given_db_set()
        self.controller.mouse_moved(50, PERIOD_Y)
        self.assertTrue(self.view.start_balloon_show_timer.called)
        self.controller.balloon_show_timer_fired()
        self.assertEquals(event, self.controller.get_view_properties().hovered_event)
        self.controller.mouse_moved(0, 0)
        self.assertTrue(self.view.start_balloon_hide_timer.called)
        self.controller.balloon_hide_timer_fired()
        self.assertEquals(None, self.controller.get_view_properties().hovered_event)

    def test_creates_event_when_ctrl_dragging_mouse(self):
        self.given_db_set()
        self.simulate_mouse_down_move_up(10, 0, 30, 0, ctrl_down=True, shift_down=False)
        self.assert_created_event_with_period("2 Aug 2010", "4 Aug 2010")
        self.assert_timeline_redrawn()

    def test_displays_event_info_in_status_bar_when_hovering_event(self):
        self.add_event("4 Aug 2010", "10 Aug 2010", "Period event")
        self.given_db_set()
        self.simulate_mouse_move(50, PERIOD_Y)
        self.assertTrue("Period event" in self.get_status_text())

    def test_removes_event_info_from_status_bar_when_un_hovering_event(self):
        self.given_db_set()
        self.simulate_mouse_move(30, 0)
        self.assertEquals("", self.get_status_text())

    def test_displays_hidden_event_count_in_status_bar(self):
        self.given_db_set()
        self.assertTrue("3" in self.get_hidden_event_count_text())

    def test_creates_event_when_double_clicking_surface(self):
        self.given_db_set()
        self.simulate_mouse_double_click(20, 8)
        self.assert_created_event_with_period("3 Aug 2010", "3 Aug 2010")
        self.assert_timeline_redrawn()

    def test_edits_event_when_double_clicking_it(self):
        event = self.add_event("4 Aug 2010", "10 Aug 2010")
        self.given_db_set()
        self.simulate_mouse_double_click(50, PERIOD_Y)
        self.view.edit_event.assert_called_with(event)
        self.assert_timeline_redrawn()

    def test_selects_and_deselects_event_when_clicking_on_it(self):
        event = self.add_event("4 Aug 2010", "10 Aug 2010")
        self.given_db_set()
        self.simulate_mouse_click(40, PERIOD_Y)
        self.assertTrue(self.controller.get_view_properties().is_selected(event))
        self.simulate_mouse_click(40, PERIOD_Y)
        self.assertFalse(self.controller.get_view_properties().is_selected(event))

    def test_deselects_event_when_clicking_outside_of_it(self):
        event = self.add_event("4 Aug 2010", "10 Aug 2010")
        self.given_db_set()
        self.simulate_mouse_click(50, PERIOD_Y)
        self.assertTrue(self.controller.get_view_properties().is_selected(event))
        self.simulate_mouse_click(0, 0)
        self.assertFalse(self.controller.get_view_properties().is_selected(event))

    def test_selects_multiple_events_when_clicked_if_ctrl_is_pressed(self):
        period_event = self.add_event("4 Aug 2010", "10 Aug 2010")
        point_event = self.add_event("15 Aug 2010", "15 Aug 2010")
        self.given_db_set()
        self.simulate_mouse_click(50, PERIOD_Y)
        self.simulate_mouse_click(140, POINT_Y, ctrl_down=True)
        self.assertTrue(self.controller.get_view_properties().is_selected(period_event))
        self.assertTrue(self.controller.get_view_properties().is_selected(point_event))

    def test_moves_event_when_dragging_move_icon_on_event(self):
        event = self.add_event("1 Aug 2010", "3 Aug 2010")
        self.given_db_set()
        self.simulate_mouse_click(10, PERIOD_Y)
        self.simulate_mouse_down_move_up(10, PERIOD_Y, 0, 50, ctrl_down=False, shift_down=False)
        self.assert_event_has_period(event, "31 Jul 2010", "2 Aug 2010")
        self.assert_timeline_redrawn()

    def test_displays_move_cursor_when_hovering_move_icon_on_event(self):
        self.add_event("1 Aug 2010", "3 Aug 2010")
        self.given_db_set()
        self.simulate_mouse_click(10, PERIOD_Y)
        self.simulate_mouse_move(10, PERIOD_Y)
        self.assertTrue(self.view.set_move_cursor.called)

    def test_displays_resize_cursor_when_hovering_resize_icons_on_event(self):
        self.add_event("4 Aug 2010", "10 Aug 2010")
        self.given_db_set()
        self.simulate_mouse_click(50, PERIOD_Y)
        self.simulate_mouse_move(31, PERIOD_Y)
        self.simulate_mouse_move(89, PERIOD_Y)
        self.assertEquals(2, self.view.set_size_cursor.call_count)

    def test_resizes_event_when_dragging_right_drag_icon_on_event(self):
        event = self.add_event("4 Aug 2010", "10 Aug 2010")
        self.given_db_set()
        self.simulate_mouse_click(50, PERIOD_Y)
        self.simulate_mouse_down_move_up(89, PERIOD_Y, 109, PERIOD_Y, ctrl_down=False, shift_down=False)
        self.assert_event_has_period(event, "4 Aug 2010", "11 Aug 2010")
        self.assert_timeline_redrawn()

    def test_resizes_event_when_dragging_left_drag_icon_on_event(self):
        event = self.add_event("4 Aug 2010", "10 Aug 2010")
        self.given_db_set()
        self.simulate_mouse_click(50, PERIOD_Y)
        self.simulate_mouse_down_move_up(31, PERIOD_Y, 20, PERIOD_Y, ctrl_down=False, shift_down=False)
        self.assert_event_has_period(event, "3 Aug 2010", "10 Aug 2010")
        self.assert_timeline_redrawn()

    def test_snaps_event_edge_when_resizing_event(self):
        self.mock_drawer.setup_snap("13 Aug 2010", "27 Aug 2010")
        event = self.add_event("4 Aug 2010", "10 Aug 2010")
        self.given_db_set()
        self.simulate_mouse_click(50, PERIOD_Y)
        self.simulate_mouse_down_move_up(89, PERIOD_Y, 120, PERIOD_Y, ctrl_down=False, shift_down=False)
        self.assert_event_has_period(event, "4 Aug 2010", "27 Aug 2010")
        self.assert_timeline_redrawn()

    def test_snaps_event_when_moving_event(self):
        self.mock_drawer.setup_snap("2 Aug 2010", "28 Jul 2010")
        event = self.add_event("4 Aug 2010", "10 Aug 2010")
        self.given_db_set()
        self.simulate_mouse_click(55, PERIOD_Y)
        self.simulate_mouse_down_move_up(31, PERIOD_Y, 10, PERIOD_Y, ctrl_down=False, shift_down=False)
        self.assert_event_has_period(event, "28 Jul 2010", "10 Aug 2010")
        self.assert_timeline_redrawn()

    def test_scrolls_timeline_by_10_percent_when_moving_event(self):
        self.add_event("4 Aug 2010", "10 Aug 2010")
        self.given_db_set()
        self.simulate_mouse_click(50, PERIOD_Y)
        self.controller.left_mouse_down(65, PERIOD_Y, ctrl_down=False, shift_down=False)
        self.controller.mouse_moved(199, PERIOD_Y)
        self.assertTrue(self.view.start_dragscroll_timer.called)
        self.controller.dragscroll_timer_fired()
        self.controller.left_mouse_up()
        self.assert_displays_period("3 Aug 2010", "23 Aug 2010")
        self.assert_timeline_redrawn()

    def test_scrolls_timeline_by_10_percent_when_resizing_event(self):
        self.add_event("4 Aug 2010", "10 Aug 2010")
        self.given_db_set()
        self.simulate_mouse_click(50, PERIOD_Y)
        self.controller.left_mouse_down(89, PERIOD_Y, ctrl_down=False, shift_down=False)
        self.controller.mouse_moved(199, PERIOD_Y)
        self.assertTrue(self.view.start_dragscroll_timer.called)
        self.controller.dragscroll_timer_fired()
        self.controller.left_mouse_up()
        self.assert_displays_period("3 Aug 2010", "23 Aug 2010")
        self.assert_timeline_redrawn()

    def test_scrolls_with_10_percent_when_using_mouse_wheel(self):
        self.given_db_set()
        self.controller.mouse_wheel_moved(-1, ctrl_down=False, shift_down=False)
        self.assert_displays_period("3 Aug 2010", "23 Aug 2010")
        self.assert_timeline_redrawn()
        self.controller.mouse_wheel_moved(1, ctrl_down=False, shift_down=False)
        self.assert_displays_period("1 Aug 2010", "21 Aug 2010")
        self.assert_timeline_redrawn()

    def test_deletes_selected_events_when_pressing_del_and_answering_yes_in_dialog(self):
        period_event = self.add_event("4 Aug 2010", "10 Aug 2010")
        point_event = self.add_event("15 Aug 2010", "15 Aug 2010")
        self.given_db_set()
        self.view.ask_question.return_value = wx.YES
        self.simulate_mouse_click(50, PERIOD_Y)
        self.controller.key_down(wx.WXK_DELETE)
        self.assertEquals([point_event], self.db.get_all_events())

    def test_deletes_no_selected_events_when_pressing_del_and_answering_no_in_dialog(self):
        period_event = self.add_event("4 Aug 2010", "10 Aug 2010")
        point_event = self.add_event("15 Aug 2010", "15 Aug 2010")
        self.given_db_set()
        self.view.ask_question.return_value = wx.NO
        self.simulate_mouse_click(50, PERIOD_Y)
        self.controller.key_down(wx.WXK_DELETE)
        self.assertTrue(period_event in self.db.get_all_events())
        self.assertTrue(point_event in self.db.get_all_events())

    def test_shift_scroll_changes_divider_line_value_and_redraws(self):
        self.given_db_set()
        self.controller.mouse_wheel_moved(1, ctrl_down=False, shift_down=True)
        self.assertTrue(self.divider_line_slider.SetValue.called)
        self.assert_timeline_redrawn()

    def test_disables_view_if_no_timeline_set(self):
        self.controller.set_timeline(None)
        self.view.Disable.assert_called_with()

    def setUp(self):
        self.db = MemoryDB()
        self.db._set_displayed_period(DISPLAYED_PERIOD.clone())
        self.view = Mock(DrawingArea)
        self.view.GetSizeTuple.return_value = (VIEW_WIDTH, VIEW_HEIGHT)
        self.status_bar_adapter = Mock(StatusBarAdapter)
        self.config = Mock(Config)
        self.mock_drawer = MockDrawer()
        self.divider_line_slider = Mock()
        self.divider_line_slider.GetValue.return_value = 50
        self.fn_handle_db_error = Mock()
        self.controller = DrawingAreaController(
            self.view,
            self.status_bar_adapter,
            self.config,
            self.mock_drawer,
            self.divider_line_slider,
            self.fn_handle_db_error)

    def given_db_set(self):
        self.controller.set_timeline(self.db)
        self.view.reset_mock()

    def simulate_mouse_double_click(self, x, y):
        self.simulate_mouse_click(x, y)
        self.controller.left_mouse_dclick(x, y, ctrl_down=False)

    def simulate_mouse_click(self, x, y, ctrl_down=False):
        self.controller.left_mouse_down(x, y, ctrl_down=ctrl_down, shift_down=False)
        self.controller.left_mouse_up()

    def simulate_mouse_down_move_up(self, x1, y1, x2, y2, ctrl_down, shift_down):
        self.controller.left_mouse_down(x1, y1, ctrl_down, shift_down)
        self.controller.mouse_moved(x2, y2)
        self.controller.left_mouse_up()

    def simulate_mouse_move(self, x, y):
        self.controller.mouse_moved(x, y)

    def add_event(self, start, end, text="text", description=None):
        event = Event(self.db, human_time_to_py(start), human_time_to_py(end), text)
        if description is not None:
            event.set_data("description", description)
        self.db.save_event(event)
        self.mock_drawer.add_rect_for(event)
        return event

    def get_status_text(self):
        self.assertTrue(self.status_bar_adapter.set_text.called)
        text = self.status_bar_adapter.set_text.call_args[0][0]
        return text

    def get_hidden_event_count_text(self):
        self.assertTrue(self.status_bar_adapter.set_hidden_event_count_text.called)
        text = self.status_bar_adapter.set_hidden_event_count_text.call_args[0][0]
        return text

    def assert_event_has_period(self, event, start, end):
        self.assertEquals(py_period(start, end), event.time_period)
    
    def assert_changed_displayed_period_to(self, start, end):
        self.assert_displays_period(start, end)
        self.assert_timeline_redrawn()

    def assert_displays_period(self, start, end):
        self.assertEquals(
            py_period(start, end),
            self.controller.get_time_period())

    def assert_timeline_redrawn(self):
        self.assertTrue(self.view.redraw_surface.called)

    def assert_created_event_with_period(self, start, end):
        self.view.create_new_event.assert_called_with(
            human_time_to_py(start), human_time_to_py(end))


class MockDrawer(object):

    def __init__(self):
        self.events_and_rects = []
        self.snaps = []

    def add_rect_for(self, event):
        x_start = self._x_for_time(event.time_period.start_time)
        x_end = self._x_for_time(event.time_period.end_time)
        if event.time_period.is_period():
            width = x_end - x_start
            x = x_start
            y = PERIOD_Y - EVENT_HEIGHT/2
        else:
            width = 20
            x = x_start - width/2
            y = POINT_Y - EVENT_HEIGHT/2
        rect = wx.Rect(x, y, width, EVENT_HEIGHT)
        self.events_and_rects.append((event, rect))

    def setup_snap(self, time, snap_to):
        self.snaps.append((human_time_to_py(time), human_time_to_py(snap_to)))

    def _x_for_time(self, time):
        return (time.day - 1) * 10

    def snap(self, time):
        for (time_inner, snap_to) in self.snaps:
            if time_inner == time:
                return snap_to
        return time

    def snap_selection(self, selection):
        return selection

    def event_at(self, x, y):
        for (event, rect) in self.events_and_rects:
            if rect.Contains((x, y)):
                return event
        return None

    def event_rect(self, event):
        for (event_inner, rect) in self.events_and_rects:
            if event_inner == event:
                return rect
        raise Exception("Should not get here in tests.")

    def event_with_rect_at(self, x, y):
        event = self.event_at(x, y)
        if event is None:
            return None
        return (event, self.event_rect(event))

    def get_time(self, x):
        day = int((float(x) / VIEW_WIDTH) * PERIOD_LENGTH_IN_DAYS) + 1
        return human_time_to_py("%s Aug 2010" % day)

    def balloon_at(self, x, y):
        return None

    def get_hidden_event_count(self):
        return 3

    def event_is_period(self, event):
        return False
