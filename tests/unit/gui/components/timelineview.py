# Copyright (C) 2009, 2010  Rickard Lindberg, Roger Lindberg
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

from timelinelib.drawing.interface import Drawer
from timelinelib.db.backends.memory import MemoryDB
from timelinelib.db.objects import TimePeriod
from timelinelib.db.objects import Event
from timelinelib.gui.components.timelineview import DrawingArea
from timelinelib.gui.components.timelineview import DrawingAreaController


class DrawingAreaControllerTest(unittest.TestCase):

    def setUp(self):
        # Wiring
        self.drawer = Mock()
        self.drawer.event_with_rect_at.return_value = None
        self.drawer.balloon_at.return_value = None
        self.drawer.snap = lambda x: x
        self.drawer.snap_selection = lambda x: x
        self.view = Mock(DrawingArea)
        self.view.GetSizeTuple.return_value = (240, 100) # 10 pixels in x = 1 hour
        self.view.get_drawer.return_value = self.drawer
        self.config = Mock()
        self.divider_line_slider = Mock()
        self.divider_line_slider.GetValue.return_value = 50
        self.fn_handle_db_error = Mock()
        self.controller = DrawingAreaController(
            self.view, self.config, self.drawer, self.divider_line_slider,
            self.fn_handle_db_error)
        # Additional set up code
        self.db = MemoryDB()
        self.db._set_displayed_period(
            TimePeriod(datetime(2010, 8, 30, 0, 0, 0),
                       datetime(2010, 8, 31, 0, 0, 0)))
        self.event_foo = Event(datetime(2010, 8, 30, 4, 0, 0),
                               datetime(2010, 8, 30, 6, 0, 0),
                               "foo")
        self.db.save_event(self.event_foo)
        self.controller.set_timeline(self.db)
        # Reset mocks that got called in additional set up
        self.view.reset_mock()

    def testInitializesDisplayedPeriodFromDb(self):
        self.assertDisplaysPeriod(datetime(2010, 8, 30), datetime(2010, 8, 31))

    def testScrollsTimelineWhenDraggingMouse(self):
        self.controller.left_mouse_down(0, 0, ctrl_down=False)
        self.controller.mouse_moved(10, 0, left_down=True, ctrl_down=False, shift_down=False)
        self.assertDisplaysPeriod(datetime(2010, 8, 29, 23, 0, 0),
                                  datetime(2010, 8, 30, 23, 0, 0))
        self.assertTimelineRedrawn()

    def testZoomsTimelineWhenShiftDraggingMouse(self):
        self.controller.left_mouse_down(0, 0, ctrl_down=False)
        self.controller.mouse_moved(20, 0, left_down=True, ctrl_down=False, shift_down=True)
        self.controller.left_mouse_up(20)
        self.assertDisplaysPeriod(datetime(2010, 8, 30, 0, 0, 0),
                                  datetime(2010, 8, 30, 2, 0, 0))
        self.assertTimelineRedrawn()

    def testZoomsTimelineBy10PercentOnEachSideWhenScrollingWhileHoldingDownCtrl(self):
        # 10% of one day = 2.4h = 2h 24m
        self.controller.mouse_wheel_moved(1, ctrl_down=True, shift_down=False)
        self.assertDisplaysPeriod(datetime(2010, 8, 30, 2, 24, 0),
                                  datetime(2010, 8, 30, 21, 36, 0))
        self.assertTimelineRedrawn()

    def testCreatesEventWhenCtrlDraggingMouse(self):
        self.controller.left_mouse_down(10, 0, ctrl_down=True)
        self.controller.mouse_moved(30, 0, left_down=True, ctrl_down=True, shift_down=False)
        self.controller.left_mouse_up(20)
        self.view.create_new_event.assertCalledWith(datetime(2010, 8, 30, 1, 0, 0),
                                                    datetime(2010, 8, 30, 3, 0, 0))
        self.assertTimelineRedrawn()

    def testDisplaysEventInfoInStatusBarWhenHoveringEvent(self):
        self.drawer.event_at.return_value = self.event_foo
        self.controller.mouse_moved(30, 0, left_down=False, ctrl_down=False, shift_down=False)
        self.assertTrue(self.view.display_text_in_statusbar.called)
        text = self.view.display_text_in_statusbar.call_args[0][0]
        self.assertNotEquals("", text)

    def testRemovesEventInfoFromStatusBarWhenUnHoveringEvent(self):
        self.drawer.event_at.return_value = None
        self.controller.mouse_moved(30, 0, left_down=False, ctrl_down=False, shift_down=False)
        self.assertTrue(self.view.display_text_in_statusbar.called)
        text = self.view.display_text_in_statusbar.call_args[0][0]
        self.assertEquals("", text)

    def testCreatesEventWhenDoubleClickingSurface(self):
        self.controller.left_mouse_dclick(20, 8, ctrl_down=False)
        self.view.create_new_event.assertCalledWith(datetime(2010, 8, 30, 2, 0, 0),
                                                    datetime(2010, 8, 30, 2, 0, 0))
        self.assertTimelineRedrawn()

    def testEditsEventWhenDoubleClickingIt(self):
        self.drawer.event_at.return_value = self.event_foo
        self.controller.left_mouse_dclick(20, 8, ctrl_down=False)
        self.view.edit_event.assertCalledWith(self.event_foo)
        self.assertTimelineRedrawn()

    def testSelectsAndDeselectsEventWhenClickingOnEvent(self):
        self.drawer.event_at.return_value = self.event_foo
        self.controller.left_mouse_down(20, 8, ctrl_down=False)
        self.controller.left_mouse_up(20)
        self.assertTrue(self.controller.get_view_properties().is_selected(self.event_foo))
        self.controller.left_mouse_down(20, 8, ctrl_down=False)
        self.controller.left_mouse_up(20)
        self.assertFalse(self.controller.get_view_properties().is_selected(self.event_foo))

    def testDeselectsEventWhenClickingOutsideEvent(self):
        # First select it
        self.drawer.event_at.return_value = self.event_foo
        self.controller.left_mouse_down(20, 8, ctrl_down=False)
        self.controller.left_mouse_up(20)
        self.assertTrue(self.controller.get_view_properties().is_selected(self.event_foo))
        # Then click outside
        self.drawer.event_at.return_value = None
        self.controller.left_mouse_down(20, 8, ctrl_down=False)
        self.controller.left_mouse_up(20)
        self.assertFalse(self.controller.get_view_properties().is_selected(self.event_foo))

    def testMovesEventWhenDraggingMoveIconOnEvent(self):
        self.drawer.event_rect.return_value = wx.Rect(40, 45, 20, 10)
        self.drawer.event_at.return_value = self.event_foo
        self.drawer.event_with_rect_at.return_value = (self.event_foo, wx.Rect(40, 45, 20, 10))
        # First select the event so that move icon is visible
        self.controller.left_mouse_down(50, 50, ctrl_down=False)
        self.controller.left_mouse_up(50)
        # Then start the dragging the move icon
        self.controller.left_mouse_down(50, 50, ctrl_down=False)
        self.controller.mouse_moved(60, 50, left_down=True, ctrl_down=False, shift_down=False)
        self.controller.left_mouse_up(60)
        self.assertFooEventHasPeriod(datetime(2010, 8, 30, 5, 0, 0),
                                     datetime(2010, 8, 30, 7, 0, 0))
        self.assertTimelineRedrawn()

    def testResizesEventWhenDraggingRightDragIconOnEvent(self):
        self.drawer.event_rect.return_value = wx.Rect(40, 45, 20, 10)
        self.drawer.event_at.return_value = self.event_foo
        self.drawer.event_with_rect_at.return_value = (self.event_foo, wx.Rect(40, 45, 20, 10))
        # First select the event so that move icon is visible
        self.controller.left_mouse_down(50, 50, ctrl_down=False)
        self.controller.left_mouse_up(50)
        # Then start the dragging the move icon
        self.controller.left_mouse_down(59, 50, ctrl_down=False)
        self.controller.mouse_moved(70, 50, left_down=True, ctrl_down=False, shift_down=False)
        self.controller.left_mouse_up(70)
        self.assertFooEventHasPeriod(datetime(2010, 8, 30, 4, 0, 0),
                                     datetime(2010, 8, 30, 7, 0, 0))
        self.assertTimelineRedrawn()

    def testResizesEventWhenDraggingLeftDragIconOnEvent(self):
        self.drawer.event_rect.return_value = wx.Rect(40, 45, 20, 10)
        self.drawer.event_at.return_value = self.event_foo
        self.drawer.event_with_rect_at.return_value = (self.event_foo, wx.Rect(40, 45, 20, 10))
        # First select the event so that move icon is visible
        self.controller.left_mouse_down(50, 50, ctrl_down=False)
        self.controller.left_mouse_up(50)
        # Then start the dragging the move icon
        self.controller.left_mouse_down(41, 50, ctrl_down=False)
        self.controller.mouse_moved(30, 50, left_down=True, ctrl_down=False, shift_down=False)
        self.controller.left_mouse_up(30)
        self.assertFooEventHasPeriod(datetime(2010, 8, 30, 3, 0, 0),
                                     datetime(2010, 8, 30, 6, 0, 0))
        self.assertTimelineRedrawn()

    def testScrollsTimelineWhenResizingEvent(self):
        self.drawer.event_rect.return_value = wx.Rect(210, 45, 20, 10)
        self.drawer.event_at.return_value = self.event_foo
        self.drawer.event_with_rect_at.return_value = (self.event_foo, wx.Rect(210, 45, 20, 10))
        # First select the event so that move icon is visible
        self.controller.left_mouse_down(50, 50, ctrl_down=False)
        self.controller.left_mouse_up(50)
        # Then start the dragging the move icon
        self.controller.left_mouse_down(229, 50, ctrl_down=False)
        self.controller.mouse_moved(230, 50, left_down=True, ctrl_down=False, shift_down=False)
        self.assertTrue(self.view.start_dragscroll_timer.called)
        # Simulate timer
        self.controller.dragscroll_timer_fired()
        self.controller.left_mouse_up(230)
        # Should move 10% to the right, 10% of one day = 2.4h = 2h 24m
        self.assertDisplaysPeriod(datetime(2010, 8, 30, 2, 24, 0),
                                  datetime(2010, 8, 31, 2, 24, 0))
        self.assertTimelineRedrawn()

    def testScrollsWith10PercentWhenUsingMouseWheel(self):
        # 10% of one day = 2.4h = 2h 24m
        # Scroll forward
        self.controller.mouse_wheel_moved(-1, ctrl_down=False, shift_down=False)
        self.assertDisplaysPeriod(datetime(2010, 8, 30, 2, 24, 0),
                                  datetime(2010, 8, 31, 2, 24, 0))
        self.assertTimelineRedrawn()
        # Scroll back
        self.controller.mouse_wheel_moved(1, ctrl_down=False, shift_down=False)
        self.assertDisplaysPeriod(datetime(2010, 8, 30, 0, 0, 0),
                                  datetime(2010, 8, 31, 0, 0, 0))
        self.assertTimelineRedrawn()

    def testDeletesSelectedEventsWhenPressingDelAndAnsweringYesInDialog(self):
        self.view.ask_question.return_value = wx.YES
        self.drawer.event_at.return_value = self.event_foo
        self.controller.left_mouse_down(20, 8, ctrl_down=False)
        self.controller.key_down(wx.WXK_DELETE)
        self.assertEquals([], self.db.get_all_events())

    def testDeletesNoSelectedEventsWhenPressingDelAndAnsweringNoInDialog(self):
        self.view.ask_question.return_value = wx.NO
        self.drawer.event_at.return_value = self.event_foo
        self.controller.left_mouse_down(20, 8, ctrl_down=False)
        self.controller.key_down(wx.WXK_DELETE)
        self.assertEquals([self.event_foo], self.db.get_all_events())

    def testShiftScrollChangesDividerLineValueAndRedraws(self):
        self.controller.mouse_wheel_moved(1, ctrl_down=False, shift_down=True)
        self.assertTrue(self.divider_line_slider.SetValue.called)
        self.assertTimelineRedrawn()

    def assertFooEventHasPeriod(self, start, end):
        self.assertEquals(TimePeriod(start, end), self.event_foo.time_period)

    def assertDisplaysPeriod(self, start, end):
        self.assertEquals(TimePeriod(start, end),
                          self.controller.get_time_period())

    def assertTimelineRedrawn(self):
        self.assertTrue(self.view.redraw_surface.called)
