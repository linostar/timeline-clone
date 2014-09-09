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

from timelinelib.application import TimelineApplication
from timelinelib.config.dotfile import Config
from timelinelib.db.exceptions import TimelineIOError
from timelinelib.wxgui.dialogs.mainframe import MainFrame
from timelinelib.time.numtime import NumTimeType


class describe_timeline_application(unittest.TestCase):

    def test_uses_db_open_function_to_create_timeline(self):
        self.application.open_timeline("foo.timeline")
        self.db_open.assert_called_with("foo.timeline", timetype=None)

    def test_uses_db_open_function_to_create_numeric_timeline(self):
        timetype = NumTimeType()
        self.application.open_timeline("foo.timeline", timetype=timetype)
        self.db_open.assert_called_with("foo.timeline", timetype=timetype)

    def test_displays_opened_timeline(self):
        timeline = Mock()
        self.db_open.return_value = timeline
        self.application.open_timeline("foo.timeline")
        self.main_frame.display_timeline.assert_called_with(timeline)

    def test_can_set_no_timeline(self):
        self.application.set_no_timeline()
        self.main_frame.display_timeline.assert_called_with(None)

    def test_saves_current_timeline_data_when_opening_new_timeline(self):
        self.application.open_timeline("foo.timeline")
        self.main_frame.save_current_timeline_data.assert_called_with()

    def test_does_not_save_current_timeline_data_when_reloading_from_disk(self):
        self.application.open_timeline("foo.timeline")
        self.main_frame.reset_mock()
        self.application.reload_from_disk()
        self.assertFalse(self.main_frame.save_current_timeline_data.called)

    def test_adds_opened_timeline_to_recently_opened_list(self):
        self.application.open_timeline("foo.timeline")
        self.config.append_recently_opened.assert_called_with("foo.timeline")
        self.main_frame.update_open_recent_submenu.assert_called_with()

    def test_handles_open_timeline_failure(self):
        error = TimelineIOError("")
        self.db_open.side_effect = error
        self.application.open_timeline("foo.timeline")
        self.main_frame.handle_db_error.assert_called_with(error)

    def setUp(self):
        self.main_frame = Mock(MainFrame)
        self.main_frame.main_panel = Mock()
        self.main_frame.main_panel.timeline_panel = Mock()
        self.main_frame.main_panel.timeline_panel.timeline_canvas = Mock()
        self.db_open = Mock()
        self.config = Mock(Config)
        self.application = TimelineApplication(self.main_frame, self.db_open,
                                               self.config)
