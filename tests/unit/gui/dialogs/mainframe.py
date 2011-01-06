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


import datetime
import unittest

from mock import Mock

import timelinelib.gui.dialogs.mainframe as mainframe_module
from timelinelib.gui.dialogs.mainframe import MainFrame
from timelinelib.gui.dialogs.mainframe import MainFrameController
from timelinelib.db.interface import TimelineIOError
from timelinelib.db.objects import Event
from timelinelib.db.objects import TimePeriod
from timelinelib.config import Config


class TestMainFrameController(unittest.TestCase):

    def setUp(self):
        self.main_frame = Mock(MainFrame)
        self.db_open_fn = Mock()
        self.config = Mock(Config)
        self.USE_WIDE_DATE_RANGE = False
        self.config.get_use_wide_date_range.return_value = self.USE_WIDE_DATE_RANGE 
        self.controller = MainFrameController(self.main_frame, self.db_open_fn,
                                              self.config)

    def testOpenTimeline(self):
        # Setup
        opened_timeline = Mock()
        self.db_open_fn.return_value = opened_timeline
        # Call
        self.controller.open_timeline("foo.timeline")
        # Assert
        self.db_open_fn.assert_called_with("foo.timeline", self.USE_WIDE_DATE_RANGE)
        self.config.append_recently_opened.assert_called_with("foo.timeline")
        self.main_frame._update_open_recent_submenu.assert_called_with()
        self.main_frame._display_timeline.assert_called_with(opened_timeline)

    def testOpenTimelineFail(self):
        # Setup
        ex = TimelineIOError("")
        self.db_open_fn.side_effect = ex
        # Call
        self.controller.open_timeline("foo.timeline")
        # Assert
        self.db_open_fn.assert_called_with("foo.timeline", self.USE_WIDE_DATE_RANGE)
        self.main_frame.handle_db_error.assert_called_with(ex)
