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


import datetime
import unittest

from mock import Mock

from specs.utils import an_event
from timelinelib.wxgui.dialogs.playframe import PlayFrame
from timelinelib.db.interface import TimelineDB
from timelinelib.play.playcontroller import PlayController
from timelinelib.time.pytime import PyTimeType


class PlayControllerSpec(unittest.TestCase):

    def setUp(self):
        self.play_frame = Mock(PlayFrame)
        self.play_frame.get_view_period_length.return_value = datetime.timedelta(1)
        self.timeline = Mock(TimelineDB)
        self.timeline.get_first_event.return_value = an_event()
        self.timeline.get_time_type.return_value = PyTimeType()
        self.drawing_algorithm = Mock()
        self.config = Mock()
        self.controller = PlayController(self.play_frame, self.timeline,
                self.drawing_algorithm, self.config)
        
    def test_on_close_clicked(self):
        self.controller.on_close_clicked()
        self.play_frame.close.assert_called_with()

    def test_draws_timeline_on_screen_by_passing_function_that_draws(self):
        self.controller.start_movie()
        self.assert_redraw_called_once_with_draw_fn()

    def test_forwards_drawing_to_drawing_algorithm(self):
        self.controller.start_movie()

        dc = Mock()
        self.get_draw_fn()(dc)

        self.assertEquals(dc, self.drawing_algorithm.draw.call_args[0][0])
        self.assertEquals(self.timeline, self.drawing_algorithm.draw.call_args[0][1])
        self.assertEquals(self.config, self.drawing_algorithm.draw.call_args[0][3])

    def get_draw_fn(self):
        mock = self.play_frame.redraw_drawing_area
        self.assertEquals(1, mock.call_count)
        self.assertEquals(1, len(mock.call_args[0]))
        draw_fn = mock.call_args[0][0]
        return draw_fn

    def assert_redraw_called_once_with_draw_fn(self):
        self.assert_is_draw_fn(self.get_draw_fn())

    def assert_is_draw_fn(self, draw_fn):
        dc = Mock()
        draw_fn(dc)
