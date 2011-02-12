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


from datetime import datetime
from datetime import timedelta
import unittest

import wx
from mock import Mock

from timelinelib.time import PyTimeType
from timelinelib.drawing.interface import Drawer
from timelinelib.drawing.drawers.default import DefaultDrawingAlgorithm
from timelinelib.db.backends.memory import MemoryDB
from timelinelib.db.objects import TimePeriod
from timelinelib.db.objects import Event
from timelinelib.gui.components.timelineview import DrawingArea
from timelinelib.gui.components.timelineview import DrawingAreaController
from timelinelib.gui.dialogs.mainframe import StatusBarAdapter


# TODO: testSavesEventAfterMove
# TODO: testSavesEventAfterResize


class TimelineView(unittest.TestCase):

    def setUp(self):
        # Simulate a view like this:
        #
        # +--------------------------------------------------+         \
        # |                   (120, 45)__________            |         |
        # |                       |_Point_event_|            | | 10 px |
        # |                              |                   |         |
        # +------------------------------+-------------------+         | 100 px
        # |(40, 75)_____________                             |         |
        # |   |_Period_event___|                             | | 10 px |
        # |                                                  |         |
        # +--------------------------------------------------+         /
        # 2010-08-30                                2010-08-31
        #     \----------------/  \-------------/
        #            30 px             30 px
        # \--------------------------------------------------/
        #                       240 px                         
        #                      24 hours
        #                  10 pixels = 1 hour
        #               10% = 2.4 hours = 2h 24m
        self.divider_line_slider = Mock()
        self.divider_line_slider.GetValue.return_value = 50
        self.setUpDb()
        self.setUpMockDrawer()
        self.config = Mock()
        self.fn_handle_db_error = Mock()
        self.view = Mock(DrawingArea)
        self.view.GetSizeTuple.return_value = (240, 100)
        self.view.get_drawer.return_value = self.drawer
        self.status_bar_adapter = Mock(StatusBarAdapter)
        self.controller = DrawingAreaController(
            self.view, self.status_bar_adapter, self.config, self.drawer,
            self.divider_line_slider, self.fn_handle_db_error)
        # Additional set up code
        self.controller.set_timeline(self.db)
        # Reset mocks that got called in additional set up
        self.view.reset_mock()

    def setUpDb(self):
        self.db = MemoryDB()
        self.db._set_displayed_period(
            TimePeriod(self.db.get_time_type(), 
                       datetime(2010, 8, 30, 0, 0, 0),
                       datetime(2010, 8, 31, 0, 0, 0)))
        self.point_event = Event(self.db, datetime(2010, 8, 30, 15, 0, 0),
                                 datetime(2010, 8, 30, 15, 0, 0),
                                 "Point event")
        self.db.save_event(self.point_event)
        self.period_event = Event(self.db, datetime(2010, 8, 30, 4, 0, 0),
                                  datetime(2010, 8, 30, 7, 0, 0),
                                  "Period event")
        self.period_event.set_data("description", "I am a period event!")
        self.db.save_event(self.period_event)

    def setUpMockDrawer(self):
        def snap_mock(time):
            return time
        def snap_selection_mock(sel):
            return sel
        def event_at_mock(x, y):
            if self.point_event_rect.Contains((x, y)):
                return self.point_event
            if self.period_event_rect.Contains((x, y)):
                return self.period_event
            return None
        def event_rect_mock(event):
            if event == self.period_event:
                return self.period_event_rect
            if event == self.point_event:
                return self.point_event_rect
            raise Exception("Should not get here in tests.")
        def event_with_rect_at_mock(x, y):
            event = event_at_mock(x, y)
            if event is None:
                return None
            return (event, event_rect_mock(event))
        self.point_event_rect = wx.Rect(120, 45, 30, 10)
        self.period_event_rect = wx.Rect(40, 75, 30, 10)
        self.drawer = Mock(DefaultDrawingAlgorithm)
        self.drawer.balloon_at.return_value = None
        self.drawer.snap.side_effect               = snap_mock
        self.drawer.snap_selection.side_effect     = snap_selection_mock
        self.drawer.event_at.side_effect           = event_at_mock
        self.drawer.event_with_rect_at.side_effect = event_with_rect_at_mock
        self.drawer.event_rect.side_effect         = event_rect_mock
        self.drawer.get_hidden_event_count.return_value = 3

    def test_initializes_displayed_period_from_db(self):
        self.assert_displays_period(datetime(2010, 8, 30), datetime(2010, 8, 31))

    def test_scrolls_timeline_when_dragging_mouse(self):
        self.simulate_mouse_down_move_up(0, 0, 10, 0, ctrl_down=False, shift_down=False)
        self.assert_changed_displayed_period_to(datetime(2010, 8, 29, 23, 0, 0),
                                                datetime(2010, 8, 30, 23, 0, 0))

    def test_zooms_timeline_when_shift_dragging_mouse(self):
        self.simulate_mouse_down_move_up(0, 0, 20, 0, ctrl_down=False, shift_down=True)
        self.assert_changed_displayed_period_to(datetime(2010, 8, 30, 0, 0, 0),
                                                datetime(2010, 8, 30, 2, 0, 0))

    def test_centers_displayed_period_around_middle_click_position(self):
        self.controller.middle_mouse_clicked(130)
        self.assert_changed_displayed_period_to(datetime(2010, 8, 30, 1, 0, 0),
                                                datetime(2010, 8, 31, 1, 0, 0))

    def test_zooms_timeline_by_10_percent_on_each_side_when_scrolling_while_holding_down_ctrl(self):
        self.controller.mouse_wheel_moved(1, ctrl_down=True, shift_down=False)
        self.assert_changed_displayed_period_to(datetime(2010, 8, 30, 2, 24, 0),
                                                datetime(2010, 8, 30, 21, 36, 0))

    def test_displays_balloon_for_event_with_description(self):
        self.controller.mouse_moved(50, 80)
        self.assertTrue(self.view.start_balloon_timer1.called)
        self.controller.balloon_timer1_fired()
        self.assertEquals(self.period_event, self.controller.get_view_properties().hovered_event)

    def test_hides_balloon_when_leaving_event(self):
        self.controller.mouse_moved(50, 80)
        self.assertTrue(self.view.start_balloon_timer1.called)
        self.controller.balloon_timer1_fired()
        self.assertEquals(self.period_event, self.controller.get_view_properties().hovered_event)
        self.controller.mouse_moved(0, 0)
        self.assertTrue(self.view.start_balloon_timer2.called)
        self.controller.balloon_timer2_fired()
        self.assertEquals(None, self.controller.get_view_properties().hovered_event)

    def test_creates_event_when_ctrl_dragging_mouse(self):
        self.simulate_mouse_down_move_up(10, 0, 30, 0, ctrl_down=True, shift_down=False)
        self.view.create_new_event.assert_called_with(datetime(2010, 8, 30, 1, 0, 0),
                                                      datetime(2010, 8, 30, 3, 0, 0))
        self.assert_timeline_redrawn()

    def test_displays_event_info_in_status_bar_when_hovering_event(self):
        self.simulate_mouse_move(50, 80)
        self.assertTrue(self.status_bar_adapter.set_text.called)
        text = self.status_bar_adapter.set_text.call_args[0][0]
        self.assertTrue("Period event" in text)

    def test_removes_event_info_from_status_bar_when_un_hovering_event(self):
        self.simulate_mouse_move(30, 0)
        self.assertTrue(self.status_bar_adapter.set_text.called)
        text = self.status_bar_adapter.set_text.call_args[0][0]
        self.assertEquals("", text)

    def test_displays_hidden_event_count_in_status_bar(self):
        self.controller.set_timeline(self.db)
        self.assertTrue(self.status_bar_adapter.set_hidden_event_count_text.called)
        text = self.status_bar_adapter.set_hidden_event_count_text.call_args[0][0]
        self.assertTrue("3" in text)

    def test_creates_event_when_double_clicking_surface(self):
        self.simulate_mouse_double_click(20, 8)
        self.view.create_new_event.assert_called_with(datetime(2010, 8, 30, 2, 0, 0),
                                                      datetime(2010, 8, 30, 2, 0, 0))
        self.assert_timeline_redrawn()

    def test_edits_event_when_double_clicking_it(self):
        self.simulate_mouse_double_click(50, 80)
        self.view.edit_event.assert_called_with(self.period_event)
        self.assert_timeline_redrawn()

    def test_selects_and_deselects_event_when_clicking_on_it(self):
        self.simulate_mouse_click(47, 80)
        self.assertTrue(self.controller.get_view_properties().is_selected(self.period_event))
        self.simulate_mouse_click(47, 80)
        self.assertFalse(self.controller.get_view_properties().is_selected(self.period_event))

    def test_deselects_event_when_clicking_outside_of_it(self):
        self.simulate_mouse_click(50, 80)
        self.assertTrue(self.controller.get_view_properties().is_selected(self.period_event))
        self.simulate_mouse_click(0, 0)
        self.assertFalse(self.controller.get_view_properties().is_selected(self.period_event))

    def test_selects_multiple_events_when_clicked_if_ctrl_is_pressed(self):
        self.simulate_mouse_click(50, 80)
        self.simulate_mouse_click(130, 50, ctrl_down=True)
        self.assertTrue(self.controller.get_view_properties().is_selected(self.period_event))
        self.assertTrue(self.controller.get_view_properties().is_selected(self.point_event))

    def test_moves_event_when_dragging_move_icon_on_event(self):
        self.simulate_mouse_click(50, 80)
        self.simulate_mouse_down_move_up(55, 80, 65, 50, ctrl_down=False, shift_down=False)
        self.assert_period_event_has_period(datetime(2010, 8, 30, 5, 0, 0),
                                            datetime(2010, 8, 30, 8, 0, 0))
        self.assert_timeline_redrawn()

    def test_displays_move_cursor_when_hovering_move_icon_on_event(self):
        self.simulate_mouse_click(50, 80)
        self.simulate_mouse_move(50, 80)
        self.assertTrue(self.view.set_move_cursor.called)

    def test_displays_resize_cursor_when_hovering_resize_icons_on_event(self):
        self.simulate_mouse_click(50, 80)
        self.simulate_mouse_move(41, 80)
        self.simulate_mouse_move(69, 80)
        self.assertTrue(self.view.set_size_cursor.called)
        self.assertEquals(2, self.view.set_size_cursor.call_count)

    def test_resizes_event_when_dragging_right_drag_icon_on_event(self):
        # First select the event so that move icon is visible
        self.simulate_mouse_click(50, 80)
        # Then start the dragging the right drag icon
        self.simulate_mouse_down_move_up(69, 80, 80, 80, ctrl_down=False, shift_down=False)
        self.assert_period_event_has_period(datetime(2010, 8, 30, 4, 0, 0),
                                            datetime(2010, 8, 30, 8, 0, 0))
        self.assert_timeline_redrawn()

    def test_resizes_event_when_dragging_left_drag_icon_on_event(self):
        # First select the event so that move icon is visible
        self.simulate_mouse_click(50, 80)
        # Then start the dragging the left drag icon
        self.simulate_mouse_down_move_up(41, 80, 30, 80, ctrl_down=False, shift_down=False)
        self.assert_period_event_has_period(datetime(2010, 8, 30, 3, 0, 0),
                                            datetime(2010, 8, 30, 7, 0, 0))
        self.assert_timeline_redrawn()

    def test_snaps_event_edge_when_resizing_event(self):
        def snap_mock(time):
            if time == datetime(2010, 8, 30, 8, 0, 0):
                return datetime(2010, 8, 30, 9, 0, 0)
            return time
        self.drawer.snap.side_effect = snap_mock
        self.simulate_mouse_click(50, 80)
        self.simulate_mouse_down_move_up(69, 80, 80, 80, ctrl_down=False, shift_down=False)
        self.assert_period_event_has_period(datetime(2010, 8, 30, 4, 0, 0),
                                            datetime(2010, 8, 30, 9, 0, 0))
        self.assert_timeline_redrawn()

    def test_snaps_event_when_moving_event(self):
        def snap_mock(time):
            if time == datetime(2010, 8, 30, 5, 0, 0):
                return datetime(2010, 8, 30, 6, 0, 0)
            return time
        self.drawer.snap.side_effect = snap_mock
        self.simulate_mouse_click(55, 80)
        self.simulate_mouse_down_move_up(55, 80, 65, 80, ctrl_down=False, shift_down=False)
        self.assert_period_event_has_period(datetime(2010, 8, 30, 6, 0, 0),
                                            datetime(2010, 8, 30, 9, 0, 0))
        self.assert_timeline_redrawn()

    def test_scrolls_timeline_by_10_percent_when_moving_event(self):
        self.simulate_mouse_click(50, 80)
        self.controller.left_mouse_down(55, 80, ctrl_down=False, shift_down=False)
        self.controller.mouse_moved(230, 80)
        self.assertTrue(self.view.start_dragscroll_timer.called)
        self.controller.dragscroll_timer_fired()
        self.controller.left_mouse_up()
        self.assert_displays_period(datetime(2010, 8, 30, 2, 24, 0),
                                    datetime(2010, 8, 31, 2, 24, 0))
        self.assert_timeline_redrawn()

    def test_scrolls_timeline_by_10_percent_when_resizing_event(self):
        # First select the event so that move icon is visible
        self.simulate_mouse_click(50, 80)
        # Then start the dragging the move icon
        self.controller.left_mouse_down(69, 80, ctrl_down=False, shift_down=False)
        self.controller.mouse_moved(230, 80)
        self.assertTrue(self.view.start_dragscroll_timer.called)
        # Simulate timer
        self.controller.dragscroll_timer_fired()
        self.controller.left_mouse_up()
        self.assert_displays_period(datetime(2010, 8, 30, 2, 24, 0),
                                    datetime(2010, 8, 31, 2, 24, 0))
        self.assert_timeline_redrawn()

    def test_scrolls_with_10_percent_when_using_mouse_wheel(self):
        # Scroll forward
        self.controller.mouse_wheel_moved(-1, ctrl_down=False, shift_down=False)
        self.assert_displays_period(datetime(2010, 8, 30, 2, 24, 0),
                                    datetime(2010, 8, 31, 2, 24, 0))
        self.assert_timeline_redrawn()
        # Scroll back
        self.controller.mouse_wheel_moved(1, ctrl_down=False, shift_down=False)
        self.assert_displays_period(datetime(2010, 8, 30, 0, 0, 0),
                                    datetime(2010, 8, 31, 0, 0, 0))
        self.assert_timeline_redrawn()

    def test_deletes_selected_events_when_pressing_del_and_answering_yes_in_dialog(self):
        self.view.ask_question.return_value = wx.YES
        self.simulate_mouse_click(50, 80)
        self.controller.key_down(wx.WXK_DELETE)
        self.assertEquals([self.point_event], self.db.get_all_events())

    def test_deletes_no_selected_events_when_pressing_del_and_answering_no_in_dialog(self):
        self.view.ask_question.return_value = wx.NO
        self.simulate_mouse_click(50, 80)
        self.controller.key_down(wx.WXK_DELETE)
        self.assertTrue(self.period_event in self.db.get_all_events())
        self.assertTrue(self.point_event in self.db.get_all_events())

    def test_shift_scroll_changes_divider_line_value_and_redraws(self):
        self.controller.mouse_wheel_moved(1, ctrl_down=False, shift_down=True)
        self.assertTrue(self.divider_line_slider.SetValue.called)
        self.assert_timeline_redrawn()

    def test_disables_view_if_no_timeline_set(self):
        self.controller.set_timeline(None)
        self.view.Disable.assert_called_with()

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

    def assert_period_event_has_period(self, start, end):
        self.assertEquals(TimePeriod(PyTimeType(), start, end), 
                          self.period_event.time_period)
    
    def assert_changed_displayed_period_to(self, start, end):
        self.assert_displays_period(start, end)
        self.assert_timeline_redrawn()

    def assert_displays_period(self, start, end):
        self.assertEquals(TimePeriod(PyTimeType(), start, end),
                          self.controller.get_time_period())

    def assert_timeline_redrawn(self):
        self.assertTrue(self.view.redraw_surface.called)
