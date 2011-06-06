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


import wx

from timelinelib.view.inputhandler import InputHandler


# Used by Sizer and Mover classes to detect when to go into action
HIT_REGION_PX_WITH = 5


class NoOpInputHandler(InputHandler):

    def __init__(self, controller, view):
        self.controller = controller
        self.view = view
        self.drawer = controller.drawing_algorithm
        self.view_properties = controller.view_properties
        self.show_timer_running = False
        self.hide_timer_running = False

    def left_mouse_down(self, x, y, ctrl_down, shift_down):
        self._toggle_balloon_stickyness(x, y)
        event = self.drawer.event_at(x, y)
        time_at_x = self.controller.get_time(x)
        if self._hit_resize_handle(x, y) is not None:
            direction = self._hit_resize_handle(x, y)
            self.controller.change_input_handler_to_resize_by_drag(event, direction)
            return
        if self._hit_move_handle(x, y):
            self.controller.change_input_handler_to_move_by_drag(event, time_at_x)
            return
        if (event is None and ctrl_down == False and shift_down == False):
            self.controller._toggle_event_selection(x, y, ctrl_down)
            self.controller.change_input_handler_to_scroll_by_drag(time_at_x)
            return
        if (event is None and ctrl_down == True):
            self.controller._toggle_event_selection(x, y, ctrl_down)
            self.controller.change_input_handler_to_create_period_event_by_drag(time_at_x)
            return
        if (event is None and shift_down == True):
            self.controller._toggle_event_selection(x, y, ctrl_down)
            self.controller.change_input_handler_to_zoom_by_drag(time_at_x)
            return
        self.controller._toggle_event_selection(x, y, ctrl_down)

    def _toggle_balloon_stickyness(self, x, y):
        event_with_balloon = self.drawer.balloon_at(x, y)
        if event_with_balloon: 
            stick = not self.view_properties.event_has_sticky_balloon(event_with_balloon)
            self.view_properties.set_event_has_sticky_balloon(event_with_balloon, has_sticky=stick)
            if stick:
                self.controller._redraw_timeline()
            else:
                if self.view_properties.show_balloons_on_hover:
                    self.controller._redraw_balloons(event_with_balloon)
                else:
                    self.controller._redraw_balloons(None)

    def mouse_moved(self, x, y):
        self.last_hovered_event = self.drawer.event_at(x, y)
        self.last_hovered_balloon_event = self.drawer.balloon_at(x, y)
        self._start_balloon_timers()
        self.controller._display_eventinfo_in_statusbar(x, y)
        if self._hit_resize_handle(x, y) is not None:
            self.view.set_size_cursor()
        elif self._hit_move_handle(x, y):
            self.view.set_move_cursor()
        else:
            self.view.set_default_cursor()

    def _start_balloon_timers(self):
        if self._balloons_disabled():
            return
        if self._current_event_selected():
            return
        if self.show_timer_running:
            return
        if self.hide_timer_running:
            return
        if self._should_start_balloon_show_timer():
            self.view.start_balloon_show_timer(milliseconds=500, oneShot=True)
            self.show_timer_running = True
        elif self._should_start_balloon_hide_timer():
            self.view.start_balloon_hide_timer(milliseconds=100, oneShot=True)
            self.hide_timer_running = True

    def _balloons_disabled(self):
        return not self.view_properties.show_balloons_on_hover

    def _current_event_selected(self):
        return (self.last_hovered_event is not None and
                self.view_properties.is_selected(self.last_hovered_event))

    def _should_start_balloon_show_timer(self):
        return (self._mouse_is_over_event() and
                not self._mouse_is_over_balloon() and
                not self._balloon_shown_for_event(self.last_hovered_event))

    def _should_start_balloon_hide_timer(self):
        return (self._balloon_is_shown() and
                not self._mouse_is_over_event() and
                not self._balloon_shown_for_event(self.last_hovered_balloon_event))

    def _mouse_is_over_event(self):
        return self.last_hovered_event is not None

    def _mouse_is_over_balloon(self):
        return self.last_hovered_balloon_event is not None

    def _balloon_is_shown(self):
        return self.view_properties.hovered_event is not None

    def _balloon_shown_for_event(self, event):
        return self.view_properties.hovered_event == event

    def balloon_show_timer_fired(self):
        self.show_timer_running = False
        self.controller._redraw_balloons(self.last_hovered_event)

    def balloon_hide_timer_fired(self):
        self.hide_timer_running = False
        hevt = self.view_properties.hovered_event
        # If there is no balloon visible we don't have to do anything
        if hevt is None:
            return
        cevt = self.last_hovered_event
        bevt = self.last_hovered_balloon_event
        # If the visible balloon doesn't belong to the event pointed to
        # we remove the ballloon.
        if hevt != cevt and hevt != bevt: 
            self.controller._redraw_balloons(None)

    def _hit_move_handle(self, x, y):
        event_and_rect = self.drawer.event_with_rect_at(x, y)
        if event_and_rect is None:
            return False
        event, rect = event_and_rect
        if event.locked:
            return None
        if not self.controller.get_view_properties().is_selected(event):
            return False
        center = rect.X + rect.Width / 2
        if abs(x - center) <= HIT_REGION_PX_WITH:
            return True
        return False

    def _hit_resize_handle(self, x, y):
        event_and_rect = self.drawer.event_with_rect_at(x, y)
        if event_and_rect == None:
            return None
        event, rect = event_and_rect
        if event.locked:
            return None
        if not self.controller.get_view_properties().is_selected(event):
            return None
        if abs(x - rect.X) < HIT_REGION_PX_WITH:
            return wx.LEFT
        elif abs(rect.X + rect.Width - x) < HIT_REGION_PX_WITH:
            return wx.RIGHT
        return None
