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


import unittest

import wx
from mock import Mock

from timelinelib.gui.dialogs.mainframe import MenuController
from timelinelib.db.backends.memory import MemoryDB
from timelinelib.gui.dialogs.mainframe import MENU_REQUIRES_TIMELINE      
from timelinelib.gui.dialogs.mainframe import MENU_REQUIRES_TIMELINE_VIEW   
from timelinelib.gui.dialogs.mainframe import MENU_REQUIRES_UPDATE       


class MenuControllerSpec(unittest.TestCase):

    def setUp(self):
        self.app = wx.App()
        self.menu_controller = MenuController()
        self.menu = wx.Menu()
        self.menu_item = wx.MenuItem(self.menu)
        self.menu.AppendItem(self.menu_item)
        self.timeline = Mock(MemoryDB)
        self.menu_controller.on_timeline_change(self.timeline)
        
    def testMenuRequieringUpdateIsDisabledWhenNoTimelineExists(self):
        self.menu_controller.add_menu(self.menu_item, MENU_REQUIRES_UPDATE)
        self.menu_controller.on_timeline_change(None)
        self.menu_controller.enable_disable_menus(True)
        self.assertTrue(self.menu_item.IsEnabled())
        
    def testMenuRequieringUpdateIsEnabledWhenTimelineIsUpdateable(self):
        self.timeline.is_read_only.return_value = False
        self.menu_controller.add_menu(self.menu_item, MENU_REQUIRES_UPDATE)
        self.menu_controller.enable_disable_menus(True)
        self.assertTrue(self.menu_item.IsEnabled())
        
    def testMenuRequieringUpdateIsDisableddWhenTimelineIsReadOnly(self):
        self.timeline.is_read_only.return_value = True
        self.menu_controller.add_menu(self.menu_item, MENU_REQUIRES_UPDATE)
        self.menu_controller.enable_disable_menus(True)
        self.assertFalse(self.menu_item.IsEnabled())
        
    def testMenuRequieringTimelineIsDisabledWhenNoTimelineExists(self):
        self.menu_controller.add_menu(self.menu_item, MENU_REQUIRES_TIMELINE)
        self.menu_controller.on_timeline_change(None)
        self.menu_controller.enable_disable_menus(True)
        self.assertFalse(self.menu_item.IsEnabled())
        
    def testMenuRequieringTimelineIsEnabledWhenTimelineExists(self):
        self.menu_controller.add_menu(self.menu_item, MENU_REQUIRES_TIMELINE)
        self.menu_controller.enable_disable_menus(True)
        self.assertTrue(self.menu_item.IsEnabled())
        
    def testMenuRequieringTimelineViewIsDisabledWhenNoTimelineExists(self):
        self.menu_controller.add_menu(self.menu_item, MENU_REQUIRES_TIMELINE_VIEW)
        self.menu_controller.on_timeline_change(None)
        self.menu_controller.enable_disable_menus(True)
        self.assertFalse(self.menu_item.IsEnabled())
        
    def testMenuRequieringTimelineViewIsDisabledWhenNoTimelineViewExists(self):
        self.menu_controller.add_menu(self.menu_item, MENU_REQUIRES_TIMELINE_VIEW)
        self.menu_controller.enable_disable_menus(False)
        self.assertFalse(self.menu_item.IsEnabled())
        
    def testMenuRequieringTimelineViewIsEnabledWhenTimelineViewExists(self):
        self.menu_controller.add_menu(self.menu_item, MENU_REQUIRES_TIMELINE_VIEW)
        self.menu_controller.enable_disable_menus(True)
        self.assertTrue(self.menu_item.IsEnabled())
