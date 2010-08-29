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
        self.controller = DrawingAreaController(
            self.view, self.config, self.drawer, self.divider_line_slider,
            self.fn_handle_db_error)
        # Additional set up code
        self.controller.set_timeline(self.db)
        # Reset mocks that got called in additional set up
        self.view.reset_mock()

    def setUpDb(self):
        self.db = MemoryDB()
        self.db._set_displayed_period(
            TimePeriod(datetime(2010, 8, 30, 0, 0, 0),
                       datetime(2010, 8, 31, 0, 0, 0)))
        self.point_event = Event(datetime(2010, 8, 30, 15, 0, 0),
                                 datetime(2010, 8, 30, 15, 0, 0),
                                 "Point event")
        self.db.save_event(self.point_event)
        self.period_event = Event(datetime(2010, 8, 30, 4, 0, 0),
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
        self.drawer = Mock()
        self.drawer.balloon_at.return_value = None
        self.drawer.snap.side_effect               = snap_mock
        self.drawer.snap_selection.side_effect     = snap_selection_mock
        self.drawer.event_at.side_effect           = event_at_mock
        self.drawer.event_with_rect_at.side_effect = event_with_rect_at_mock
        self.drawer.event_rect.side_effect         = event_rect_mock

    def testInitializesDisplayedPeriodFromDb(self):
        self.assertDisplaysPeriod(datetime(2010, 8, 30), datetime(2010, 8, 31))

    def testScrollsTimelineWhenDraggingMouse(self):
        self.simulateMouseDownMoveUp(0, 0, 10, 0, ctrl_down=False, shift_down=False)
        self.assertChangedDisplayedPeriodTo(datetime(2010, 8, 29, 23, 0, 0),
                                            datetime(2010, 8, 30, 23, 0, 0))

    def testZoomsTimelineWhenShiftDraggingMouse(self):
        self.simulateMouseDownMoveUp(0, 0, 20, 0, ctrl_down=False, shift_down=True)
        self.assertChangedDisplayedPeriodTo(datetime(2010, 8, 30, 0, 0, 0),
                                            datetime(2010, 8, 30, 2, 0, 0))

    def testCentersDisplayedPeriodAroundMiddleClickPosition(self):
        self.controller.middle_mouse_clicked(130)
        self.assertChangedDisplayedPeriodTo(datetime(2010, 8, 30, 1, 0, 0),
                                            datetime(2010, 8, 31, 1, 0, 0))

    def testZoomsTimelineBy10PercentOnEachSideWhenScrollingWhileHoldingDownCtrl(self):
        self.controller.mouse_wheel_moved(1, ctrl_down=True, shift_down=False)
        self.assertChangedDisplayedPeriodTo(datetime(2010, 8, 30, 2, 24, 0),
                                            datetime(2010, 8, 30, 21, 36, 0))

    def testDisplaysBalloonForEventWithDescription(self):
        self.controller.mouse_moved(50, 80)
        self.assertTrue(self.view.start_balloon_timer1.called)
        self.controller.balloon_timer1_fired()
        self.assertEquals(self.period_event, self.controller.get_view_properties().hovered_event)

    def testHidesBalloonWhenLeavingEvent(self):
        self.controller.mouse_moved(50, 80)
        self.assertTrue(self.view.start_balloon_timer1.called)
        self.controller.balloon_timer1_fired()
        self.assertEquals(self.period_event, self.controller.get_view_properties().hovered_event)
        self.controller.mouse_moved(0, 0)
        self.assertTrue(self.view.start_balloon_timer2.called)
        self.controller.balloon_timer2_fired()
        self.assertEquals(None, self.controller.get_view_properties().hovered_event)

    def testCreatesEventWhenCtrlDraggingMouse(self):
        self.simulateMouseDownMoveUp(10, 0, 30, 0, ctrl_down=True, shift_down=False)
        self.view.create_new_event.assert_called_with(datetime(2010, 8, 30, 1, 0, 0),
                                                      datetime(2010, 8, 30, 3, 0, 0))
        self.assertTimelineRedrawn()

    def testDisplaysEventInfoInStatusBarWhenHoveringEvent(self):
        self.simulateMouseMove(50, 80)
        self.assertTrue(self.view.display_text_in_statusbar.called)
        text = self.view.display_text_in_statusbar.call_args[0][0]
        self.assertTrue("Period event" in text)

    def testRemovesEventInfoFromStatusBarWhenUnHoveringEvent(self):
        self.simulateMouseMove(30, 0)
        self.assertTrue(self.view.display_text_in_statusbar.called)
        text = self.view.display_text_in_statusbar.call_args[0][0]
        self.assertEquals("", text)

    def testCreatesEventWhenDoubleClickingSurface(self):
        self.simulateMouseDoubleClick(20, 8)
        self.view.create_new_event.assert_called_with(datetime(2010, 8, 30, 2, 0, 0),
                                                      datetime(2010, 8, 30, 2, 0, 0))
        self.assertTimelineRedrawn()

    def testEditsEventWhenDoubleClickingIt(self):
        self.simulateMouseDoubleClick(50, 80)
        self.view.edit_event.assert_called_with(self.period_event)
        self.assertTimelineRedrawn()

    def testSelectsAndDeselectsEventWhenClickingOnIt(self):
        self.simulateMouseClick(47, 80)
        self.assertTrue(self.controller.get_view_properties().is_selected(self.period_event))
        self.simulateMouseClick(47, 80)
        self.assertFalse(self.controller.get_view_properties().is_selected(self.period_event))

    def testDeselectsEventWhenClickingOutsideOfIt(self):
        self.simulateMouseClick(50, 80)
        self.assertTrue(self.controller.get_view_properties().is_selected(self.period_event))
        self.simulateMouseClick(0, 0)
        self.assertFalse(self.controller.get_view_properties().is_selected(self.period_event))

    def testSelectsMultipleEventsWhenClickedIfCtrlIsPressed(self):
        self.simulateMouseClick(50, 80)
        self.simulateMouseClick(130, 50, ctrl_down=True)
        self.assertTrue(self.controller.get_view_properties().is_selected(self.period_event))
        self.assertTrue(self.controller.get_view_properties().is_selected(self.point_event))

    def testMovesEventWhenDraggingMoveIconOnEvent(self):
        self.simulateMouseClick(50, 80)
        self.simulateMouseDownMoveUp(55, 80, 65, 50, ctrl_down=False, shift_down=False)
        self.assertPeriodEventHasPeriod(datetime(2010, 8, 30, 5, 0, 0),
                                        datetime(2010, 8, 30, 8, 0, 0))
        self.assertTimelineRedrawn()

    def testDisplaysMoveCursorWhenHoveringMoveIconOnEvent(self):
        self.simulateMouseClick(50, 80)
        self.simulateMouseMove(50, 80)
        self.assertTrue(self.view.set_move_cursor.called)

    def testDisplaysResizeCursorWhenHoveringResizeIconsOnEvent(self):
        self.simulateMouseClick(50, 80)
        self.simulateMouseMove(41, 80)
        self.simulateMouseMove(69, 80)
        self.assertTrue(self.view.set_size_cursor.called)
        self.assertEquals(2, self.view.set_size_cursor.call_count)

    def testResizesEventWhenDraggingRightDragIconOnEvent(self):
        # First select the event so that move icon is visible
        self.simulateMouseClick(50, 80)
        # Then start the dragging the right drag icon
        self.simulateMouseDownMoveUp(69, 80, 80, 80, ctrl_down=False, shift_down=False)
        self.assertPeriodEventHasPeriod(datetime(2010, 8, 30, 4, 0, 0),
                                        datetime(2010, 8, 30, 8, 0, 0))
        self.assertTimelineRedrawn()

    def testResizesEventWhenDraggingLeftDragIconOnEvent(self):
        # First select the event so that move icon is visible
        self.simulateMouseClick(50, 80)
        # Then start the dragging the left drag icon
        self.simulateMouseDownMoveUp(41, 80, 30, 80, ctrl_down=False, shift_down=False)
        self.assertPeriodEventHasPeriod(datetime(2010, 8, 30, 3, 0, 0),
                                        datetime(2010, 8, 30, 7, 0, 0))
        self.assertTimelineRedrawn()

    def testSnapsEventEdgeWhenResizingEvent(self):
        def snap_mock(time):
            if time == datetime(2010, 8, 30, 8, 0, 0):
                return datetime(2010, 8, 30, 9, 0, 0)
            return time
        self.drawer.snap.side_effect = snap_mock
        self.simulateMouseClick(50, 80)
        self.simulateMouseDownMoveUp(69, 80, 80, 80, ctrl_down=False, shift_down=False)
        self.assertPeriodEventHasPeriod(datetime(2010, 8, 30, 4, 0, 0),
                                        datetime(2010, 8, 30, 9, 0, 0))
        self.assertTimelineRedrawn()

    def testSnapsEventWhenMovingEvent(self):
        def snap_mock(time):
            if time == datetime(2010, 8, 30, 5, 0, 0):
                return datetime(2010, 8, 30, 6, 0, 0)
            return time
        self.drawer.snap.side_effect = snap_mock
        self.simulateMouseClick(55, 80)
        self.simulateMouseDownMoveUp(55, 80, 65, 80, ctrl_down=False, shift_down=False)
        self.assertPeriodEventHasPeriod(datetime(2010, 8, 30, 6, 0, 0),
                                        datetime(2010, 8, 30, 9, 0, 0))
        self.assertTimelineRedrawn()

    def testScrollsTimelineBy10PercentWhenMovingEvent(self):
        self.simulateMouseClick(50, 80)
        self.controller.left_mouse_down(55, 80, ctrl_down=False, shift_down=False)
        self.controller.mouse_moved(230, 80)
        self.assertTrue(self.view.start_dragscroll_timer.called)
        self.controller.dragscroll_timer_fired()
        self.controller.left_mouse_up()
        self.assertDisplaysPeriod(datetime(2010, 8, 30, 2, 24, 0),
                                  datetime(2010, 8, 31, 2, 24, 0))
        self.assertTimelineRedrawn()

    def testScrollsTimelineBy10PercentWhenResizingEvent(self):
        # First select the event so that move icon is visible
        self.simulateMouseClick(50, 80)
        # Then start the dragging the move icon
        self.controller.left_mouse_down(69, 80, ctrl_down=False, shift_down=False)
        self.controller.mouse_moved(230, 80)
        self.assertTrue(self.view.start_dragscroll_timer.called)
        # Simulate timer
        self.controller.dragscroll_timer_fired()
        self.controller.left_mouse_up()
        self.assertDisplaysPeriod(datetime(2010, 8, 30, 2, 24, 0),
                                  datetime(2010, 8, 31, 2, 24, 0))
        self.assertTimelineRedrawn()

    def testScrollsWith10PercentWhenUsingMouseWheel(self):
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
        self.simulateMouseClick(50, 80)
        self.controller.key_down(wx.WXK_DELETE)
        self.assertEquals([self.point_event], self.db.get_all_events())

    def testDeletesNoSelectedEventsWhenPressingDelAndAnsweringNoInDialog(self):
        self.view.ask_question.return_value = wx.NO
        self.simulateMouseClick(50, 80)
        self.controller.key_down(wx.WXK_DELETE)
        self.assertTrue(self.period_event in self.db.get_all_events())
        self.assertTrue(self.point_event in self.db.get_all_events())

    def testShiftScrollChangesDividerLineValueAndRedraws(self):
        self.controller.mouse_wheel_moved(1, ctrl_down=False, shift_down=True)
        self.assertTrue(self.divider_line_slider.SetValue.called)
        self.assertTimelineRedrawn()

    def simulateMouseDoubleClick(self, x, y):
        self.simulateMouseClick(x, y)
        self.controller.left_mouse_dclick(x, y, ctrl_down=False)

    def simulateMouseClick(self, x, y, ctrl_down=False):
        self.controller.left_mouse_down(x, y, ctrl_down=ctrl_down, shift_down=False)
        self.controller.left_mouse_up()

    def simulateMouseDownMoveUp(self, x1, y1, x2, y2, ctrl_down, shift_down):
        self.controller.left_mouse_down(x1, y1, ctrl_down, shift_down)
        self.controller.mouse_moved(x2, y2)
        self.controller.left_mouse_up()

    def simulateMouseMove(self, x, y):
        self.controller.mouse_moved(x, y)

    def assertPeriodEventHasPeriod(self, start, end):
        self.assertEquals(TimePeriod(start, end), self.period_event.time_period)
    
    def assertChangedDisplayedPeriodTo(self, start, end):
        self.assertDisplaysPeriod(start, end)
        self.assertTimelineRedrawn()

    def assertDisplaysPeriod(self, start, end):
        self.assertEquals(TimePeriod(start, end),
                          self.controller.get_time_period())

    def assertTimelineRedrawn(self):
        self.assertTrue(self.view.redraw_surface.called)
