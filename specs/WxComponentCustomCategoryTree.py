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

from mock import Mock

from specs.utils import WxComponentTest
from timelinelib.dataimport.tutorial import create_in_memory_tutorial_db
from timelinelib.drawing.viewproperties import ViewProperties
from timelinelib.wxgui.components.categorytree import CustomCategoryTree


class CustomCategoryTreeComponentTest(WxComponentTest):

    HALT_FOR_MANUAL_INSPECTION = False

    def test_shows_up(self):
        self.handle_db_error = Mock()
        self.db = create_in_memory_tutorial_db()
        self.view_properties = ViewProperties()
        self.add_separator()
        self.add_component("first", CustomCategoryTree, self.handle_db_error)
        self.add_separator()
        self.get_component("first").set_timeline_view(self.db, self.view_properties)
        self.show_test_window()
