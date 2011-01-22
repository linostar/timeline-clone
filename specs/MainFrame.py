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

from timelinelib.gui.dialogs.mainframe import MainFrame
from timelinelib.gui.dialogs.mainframe import MainFrameController
from timelinelib.db.interface import TimelineIOError
from timelinelib.config import Config


class MainFrameSpec(unittest.TestCase):

    def testUsedDbOpenFactoryMethodToCreateTimeline(self):
        self.whenTimelineIsOpened("foo.timeline")
        self.db_open.assert_called_with("foo.timeline", self.USE_WIDE_DATE_RANGE)

    def testAddsOpenedTimelineToRecentlyOpenedList(self):
        self.whenTimelineIsOpened("foo.timeline")
        self.config.append_recently_opened.assert_called_with("foo.timeline")
        self.main_frame._update_open_recent_submenu.assert_called_with()

    def testDisplaysOpenedTimeline(self):
        opened_timeline = Mock()
        self.givenOpeningReturns(opened_timeline)
        self.whenTimelineIsOpened()
        self.main_frame._display_timeline.assert_called_with(opened_timeline)

    def testHandlesOpenTimelineFailure(self):
        error = TimelineIOError("")
        self.givenOpeningFailsWithError(error)
        self.whenTimelineIsOpened()
        self.main_frame.handle_db_error.assert_called_with(error)

    def setUp(self):
        self.USE_WIDE_DATE_RANGE = False
        self.main_frame = Mock(MainFrame)
        self.db_open = Mock()
        self.config = Mock(Config)
        self.config.get_use_wide_date_range.return_value = self.USE_WIDE_DATE_RANGE 
        self.controller = MainFrameController(
            self.main_frame, self.db_open, self.config)

    def givenOpeningFailsWithError(self, error):
        self.db_open.side_effect = error

    def givenOpeningReturns(self, timeline):
        self.db_open.return_value = timeline

    def whenTimelineIsOpened(self, name=""):
        self.controller.open_timeline(name)
