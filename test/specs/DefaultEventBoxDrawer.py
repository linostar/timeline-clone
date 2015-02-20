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


import wx
import unittest
from mock import Mock
from timelinelib.plugin.plugins.defaulteventboxdrawer import DefaultEventBoxDrawer
from timelinelib.plugin.factory import EVENTBOX_DRAWER
from specs.utils import an_event_with
from specs.utils import a_category_with


class describe_default_event_box_drawer(unittest.TestCase):

    def test_is_a_plugin(self):
        self.assertTrue(self.plugin.isplugin())

    def test_is_an_event_box_drawer(self):
        self.assertEquals(EVENTBOX_DRAWER, self.plugin.service())

    def test_has_a_display_name(self):
        self.assertTrue(len(self.plugin.display_name()) > 0)

    def test_base_color_is_gray_when_event_has_no_category(self):
        event = an_event_with(category=None)
        self.assertEquals((200, 200, 200), self.plugin._get_base_color(event))

    def test_base_color_is_category_color_when_event_has_category(self):
        category = a_category_with(name="test", color=(100, 100, 100))
        event = an_event_with(category=category)
        self.assertEquals((100, 100, 100), self.plugin._get_base_color(event))

    def test_border_color_is_dark_gray_when_event_has_no_category(self):
        event = an_event_with(category=None)
        self.assertEquals((140, 140, 140), self.plugin._get_border_color(event))

    def test_base_color_is_dark_category_color_when_event_has_category(self):
        category = a_category_with(name="test", color=(100, 100, 100))
        event = an_event_with(category=category)
        self.assertEquals((70, 70, 70), self.plugin._get_border_color(event))

    def test_run_calls_wx_dc_methods(self):
        event = an_event_with(category=None)
        self.plugin.run(self.dc, wx.Rect(), event)
        self.dc.SetBrush.assert_called()
        self.dc.SetPen.assert_called()
        self.dc.DrawRectangleRect.assert_called()

    def setUp(self):
        self.plugin = DefaultEventBoxDrawer()
        self.dc = Mock(wx.DC)
