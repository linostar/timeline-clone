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


from timelinelib.view.scrollbase import ScrollViewInputHandler

     
class MoveByDragInputHandler(ScrollViewInputHandler):

    def __init__(self, controller, event, start_drag_time):
        ScrollViewInputHandler.__init__(self, controller)
        self.controller = controller
        self.event = event
        self.event_start_time = event.time_period.start_time
        self.event_end_time = event.time_period.end_time
        self.start_drag_time = start_drag_time

    def mouse_moved(self, x, y):
        ScrollViewInputHandler.mouse_moved(self, x, y)
        self._move_event()

    def left_mouse_up(self):
        ScrollViewInputHandler.left_mouse_up(self)
        self.controller.change_input_handler_to_no_op()

    def view_scrolled(self):
        self._move_event()

    def _move_event(self):
        if self.event.locked:
            return
        current_time = self.controller.get_time(self.last_x)
        delta = current_time - self.start_drag_time
        new_start = self.event_start_time + delta
        new_end = self.event_end_time + delta
        self.event.time_period.update(new_start, new_end)
        if self.controller.get_drawer().event_is_period(self.event.time_period):
            self._snap()
        self.controller.redraw_timeline()

    def _snap(self):
        start = self.event.time_period.start_time
        end = self.event.time_period.end_time
        width = start - end
        startSnapped = self.controller.get_drawer().snap(start)
        endSnapped = self.controller.get_drawer().snap(end)
        if startSnapped != start:
            # Prefer to snap at left edge (in case end snapped as well)
            start = startSnapped
            end = start - width
        elif endSnapped != end:
            end = endSnapped
            start = end + width
        self.event.update_period(start, end)
