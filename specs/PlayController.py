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

from timelinelib.wxgui.dialogs.playframe import PlayFrame
from timelinelib.db.interface import TimelineDB
from timelinelib.play.playcontroller import PlayController


class PlayControllerSpec(unittest.TestCase):

    def setUp(self):
        self.play_frame = Mock(PlayFrame)
        self.timeline = Mock(TimelineDB)
        self.controller = PlayController(
            self.play_frame, self.timeline)
        
    def test_on_close_clicked(self):
        self.controller.on_close_clicked()
        self.play_frame.close.assert_called_with()
