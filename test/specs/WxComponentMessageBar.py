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


import sys
import unittest

from specs.utils import WxComponentTest
from timelinelib.wxgui.components.messagebar import MessageBar


class MessageBarComponentTest(WxComponentTest):

    HALT_FOR_MANUAL_INSPECTION = False

    INFORMATION_TEXT = "This is an\ninformation message."
    WARNING_TEXT = "This is a\nwarning message!"

    def test_shows_up(self):
        self.add_button("Hide",
                        self._show_no_message, "information")
        self.add_button("Show information",
                        self._show_information_message, "information")
        self.add_button("Show warning",
                        self._show_warning_message, "information")
        self.add_separator()
        self.add_component("information", MessageBar)
        self.add_separator()
        self.add_component("warning", MessageBar)
        self.add_separator()
        self._show_information_message(self.get_component("information"))
        self._show_warning_message(self.get_component("warning"))
        self.show_test_window()

    def _show_no_message(self, message_bar):
        message_bar.ShowNoMessage()

    def _show_information_message(self, message_bar):
        message_bar.ShowInformationMessage(self.INFORMATION_TEXT)

    def _show_warning_message(self, message_bar):
        message_bar.ShowWarningMessage(self.WARNING_TEXT)
