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

from timelinelib.view.scrollbase import ScrollViewInputHandler


class ResizeByDragInputHandler(ScrollViewInputHandler):

    def __init__(self, controller, event, direction):
        ScrollViewInputHandler.__init__(self, controller)
        self.controller = controller
        self.event = event
        self.direction = direction
        self.timer_running = False

    def mouse_moved(self, x, y):
        ScrollViewInputHandler.mouse_moved(self, x, y)
        self._resize_event()

    def left_mouse_up(self):
        ScrollViewInputHandler.left_mouse_up(self)
        self.controller.change_input_handler_to_no_op()

    def view_scrolled(self):
        self._resize_event()

    def _resize_event(self):
        if self.event.locked:
            return
        new_time = self.controller.get_time(self.last_x)
        new_snapped_time = self.controller.get_drawer().snap(new_time)
        if self.direction == wx.LEFT:
            new_start = new_snapped_time
            new_end = self.event.time_period.end_time
            if new_start > new_end:
                new_start = new_end
        else:
            new_start = self.event.time_period.start_time
            new_end = new_snapped_time
            if new_end < new_start:
                new_end = new_start
        self.event.update_period(new_start, new_end)
        self.controller.redraw_timeline()
