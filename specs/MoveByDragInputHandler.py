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

from specs.utils import an_event_with, human_time_to_py, py_period
from timelinelib.view.drawingarea import DrawingArea
from timelinelib.view.move import MoveByDragInputHandler


class MoveByDragInputHandlerSpec(unittest.TestCase):

    def test_moves_point_events(self):
        self.given_time_at_x_is(50, human_time_to_py("5 Jan 2011"))
        self.when_moving(an_event_with(time="1 Jan 2011"),
                         from_time="1 Jan 2011", to_x=50)
        self.assert_event_has_period("5 Jan 2011", "5 Jan 2011")

    def test_moves_period_events(self):
        self.given_time_at_x_is(50, human_time_to_py("5 Jan 2011"))
        self.when_moving(an_event_with(start="1 Jan 2011", end="3 Jan 2011"),
                         from_time="3 Jan 2011", to_x=50)
        self.assert_event_has_period("3 Jan 2011", "5 Jan 2011")

    def test_redraws_timeline_after_move(self):
        self.given_time_at_x_is(50, human_time_to_py("5 Jan 2011"))
        self.when_moving(an_event_with(time="1 Jan 2011"), from_time="1 Jan 2011", to_x=50)
        self.assertTrue(self.drawing_area.redraw_timeline.called)

    def setUp(self):
        self.times_at = {}
        self.drawing_area = Mock(DrawingArea)
        self.drawing_area.view = Mock()
        self.drawing_area.get_time.side_effect = lambda x: self.times_at[x]
        self.given_no_snap()

    def given_no_snap(self):
        self.drawing_area.event_is_period.return_value = False

    def given_time_at_x_is(self, x, time):
        self.times_at[x] = time

    def when_moving(self, event, from_time, to_x):
        self.moved_event = event
        handler = MoveByDragInputHandler(self.drawing_area, event, human_time_to_py(from_time))
        handler.mouse_moved(to_x, 10)

    def assert_event_has_period(self, start, end):
        self.assertEquals(self.moved_event.time_period, py_period(start, end))
