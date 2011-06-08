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


class PreferencesEditor(object):
    
    def __init__(self, dialog, config):
        self.dialog = dialog
        self.config = config
        
    def initialize_controls(self):
        self.dialog.set_checkbox_enable_wide_date_range(
            self.config.get_use_wide_date_range())
        self.dialog.set_checkbox_use_inertial_scrolling(
            self.config.get_use_inertial_scrolling())
        
    def on_use_wide_date_range_changed(self, value):
        self.config.set_use_wide_date_range(value)

    def on_use_inertial_scrolling_changed(self, value):
        self.config.set_use_inertial_scrolling(value)
