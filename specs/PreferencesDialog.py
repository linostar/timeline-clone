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

from timelinelib.wxgui.dialogs.preferences import PreferencesDialog
from timelinelib.wxgui.dialogs.preferences import PreferencesDialogController
from timelinelib.config import Config


class PreferencesDialogSpec(unittest.TestCase):
    
    def setUp(self):
        self.preferences_dialog = Mock(PreferencesDialog)
        self.config = Mock(Config)
        self.controller = PreferencesDialogController(self.preferences_dialog, self.config)
        
    def test_opens_with_wide_date_range_if_set_in_config(self):
        self.config.get_use_wide_date_range.return_value = True
        self.controller.initialize_controls()
        self.preferences_dialog.set_checkbox_enable_wide_date_range.assert_called_with(True)

    def test_opens_with_nonwide_date_range_if_not_set_in_config(self):
        self.config.get_use_wide_date_range.return_value = False
        self.controller.initialize_controls()
        self.preferences_dialog.set_checkbox_enable_wide_date_range.assert_called_with(False)

    def test_config_changes_when_wide_date_range_changes(self):
        self.controller.on_use_wide_date_range_changed(False)
        self.config.set_use_wide_date_range.assert_called_with(False)
