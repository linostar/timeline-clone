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

    def __init__(self, drawing_area, event, start_drag_time):
        ScrollViewInputHandler.__init__(self, drawing_area)
        self.drawing_area = drawing_area
        self.event = event
        self.original_period = self.event.time_period
        self.start_drag_time = start_drag_time

    def mouse_moved(self, x, y):
        ScrollViewInputHandler.mouse_moved(self, x, y)
        self._move_event()

    def left_mouse_up(self):
        ScrollViewInputHandler.left_mouse_up(self)
        self.drawing_area.change_input_handler_to_no_op()

    def view_scrolled(self):
        self._move_event()

    def _move_event(self):
        if self.event.locked:
            return
        self.event.update_period_o(
            self.original_period.move_delta(self._get_total_move_delta()))
        self.drawing_area.redraw_timeline()

    def _get_total_move_delta(self):
        moved_delta = self._get_moved_delta()
        if self.drawing_area.event_is_period(self.event):
            new_period = self.original_period.move_delta(moved_delta)
            snapped_period = self._snap(new_period)
            return snapped_period.start_time - self.original_period.start_time
        else:
            return moved_delta

    def _get_moved_delta(self):
        current_time = self.drawing_area.get_time(self.last_x)
        delta = current_time - self.start_drag_time
        return delta

    def _snap(self, period):
        start = period.start_time
        end = period.end_time
        start_snapped = self.drawing_area.snap(start)
        end_snapped = self.drawing_area.snap(end)
        if start_snapped != start:
            return period.move_delta(start_snapped - start)
        elif end_snapped != end:
            return period.move_delta(end_snapped - end)
        else:
            return period
