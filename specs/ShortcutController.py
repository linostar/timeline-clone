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

from timelinelib.config.shortcut import ShortcutController
from timelinelib.config.dotfile import Config
import timelinelib.wxgui.dialogs.mainframe as mf
import timelinelib.config.shortcut as sc


NEW_FUNCTION = "#File#->#File Timeline...#"
SIDEBAR_FUNCTION = "#View#->#Sidebar#"


class ShortcutControllerSpec(unittest.TestCase):

    def test_get_functions_returns_list(self):
        list = self.controller.get_functions()
        self.assertTrue(len(list) > 0)
        self.assertEqual(NEW_FUNCTION, list[0])
        
    def test_get_function_returns_function(self):
        function = self.controller.get_function("Ctrl+N")
        self.assertEqual(NEW_FUNCTION, function)

    def test_get_modifier_and_key_returns_ok(self):
        modifier, key = self.controller.get_modifier_and_key(NEW_FUNCTION)
        self.assertEqual("Ctrl", modifier)
        self.assertEqual("N", key)

    def test_valid_shortcuts(self):
        self.assertTrue(self.controller.is_valid("", ""))
        for modifier in sc.NON_EMPTY_MODIFIERS:
            self.assertTrue(self.controller.is_valid(modifier, "N"))
        
    def test_invalid_shortcuts(self):
        self.assertFalse(self.controller.is_valid("", "N"))
        self.assertFalse(self.controller.is_valid("Ctrl", ""))
        self.assertFalse(self.controller.is_valid("Ctrl+", "N"))
        self.assertFalse(self.controller.is_valid("+", "N"))
        self.assertFalse(self.controller.is_valid("+", ""))

    def test_exists(self):
        self.assertTrue(self.controller.exists("Ctrl+N"))

    def test_dont_exists(self):
        self.assertFalse(self.controller.exists("Ctrl+F3"))

    def test_wxid_exists(self):
        self.assertTrue(self.controller.wxid_exists(mf.ID_NEW))

    def test_wxid_dont_exists(self):
        self.assertFalse(self.controller.wxid_exists(mf.ID_NAVIGATE))

    def test_is_function_key(self):
        for key in sc.FUNCTION_KEYS:
            self.assertTrue(self.controller.is_function_key(key))

    def test_is_not_function_key(self):
        self.assertFalse(self.controller.is_function_key("N"))

    def test_edit(self):
        self.controller.edit(SIDEBAR_FUNCTION, "Ctrl+X")
        function = self.controller.get_function("Ctrl+X")
        self.assertEqual(SIDEBAR_FUNCTION, function)
        
    def setUp(self):
        config = Mock(Config)
        menuitem = wx.MenuItem(wx.Menu("title"), -1, "label")
        self.controller = ShortcutController(config, {mf.ID_SIDEBAR:menuitem,})

