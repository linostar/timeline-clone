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

import wx
from mock import Mock

from timelinelib.gui.dialogs.mainframe import MenuController
from timelinelib.db.backends.memory import MemoryDB
from timelinelib.gui.dialogs.mainframe import MENU_REQUIRES_TIMELINE      
from timelinelib.gui.dialogs.mainframe import MENU_REQUIRES_TIMELINE_VIEW   
from timelinelib.gui.dialogs.mainframe import MENU_REQUIRES_UPDATE       


class MenuControllerSpec(unittest.TestCase):

    def testMenuRequieringUpdateIsDisabledWhenNoTimelineExists(self):
        self.givenMenuItemRequiresUpdate()
        self.givenNoTimelineExists()
        self.whenMenuStatePossiblyHasChanged()
        self.menu_item.Enable.assert_called_with(False)

    def testMenuRequieringUpdateIsEnabledWhenTimelineIsUpdateable(self):
        self.givenMenuItemRequiresUpdate()
        self.givenTimelineIsUpdateable()
        self.whenMenuStatePossiblyHasChanged()
        self.menu_item.Enable.assert_called_with(True)

    def testMenuRequieringUpdateIsDisableddWhenTimelineIsReadOnly(self):
        self.givenMenuItemRequiresUpdate()
        self.givenTimelineIsReadOnly()
        self.whenMenuStatePossiblyHasChanged()
        self.menu_item.Enable.assert_called_with(False)

    def testMenuRequieringTimelineIsDisabledWhenNoTimelineExists(self):
        self.givenMenuItemRequiresTimeline()
        self.givenNoTimelineExists()
        self.whenMenuStatePossiblyHasChanged()
        self.menu_item.Enable.assert_called_with(False)

    def testMenuRequieringTimelineIsEnabledWhenTimelineExists(self):
        self.givenMenuItemRequiresTimeline()
        self.givenTimelineExists()
        self.whenMenuStatePossiblyHasChanged()
        self.menu_item.Enable.assert_called_with(True)

    def testMenuRequieringTimelineViewIsDisabledWhenNoTimelineExists(self):
        self.givenMenuItemRequiresTimelineView()
        self.givenNoTimelineExists()
        self.whenMenuStatePossiblyHasChanged()
        self.menu_item.Enable.assert_called_with(False)

    def testMenuRequieringTimelineViewIsDisabledWhenNoTimelineViewExists(self):
        self.givenMenuItemRequiresTimelineView()
        self.givenTimelineExists()
        self.givenNoTimelineViewExists()
        self.whenMenuStatePossiblyHasChanged()
        self.menu_item.Enable.assert_called_with(False)

    def testMenuRequieringTimelineViewIsEnabledWhenTimelineViewExists(self):
        self.givenMenuItemRequiresTimelineView()
        self.givenTimelineExists()
        self.givenTimelineViewExists()
        self.whenMenuStatePossiblyHasChanged()
        self.menu_item.Enable.assert_called_with(True)

    def setUp(self):
        self.menu_controller = MenuController()
        self.menu_item = Mock(wx.MenuItem)
        self.timeline = Mock(MemoryDB)
        self.menu_controller.on_timeline_change(self.timeline)
        self.timeline_panel_visible = False

    def givenMenuItemRequiresUpdate(self):
        self.menu_controller.add_menu(self.menu_item, MENU_REQUIRES_UPDATE)

    def givenMenuItemRequiresTimeline(self):
        self.menu_controller.add_menu(self.menu_item, MENU_REQUIRES_TIMELINE)

    def givenMenuItemRequiresTimelineView(self):
        self.menu_controller.add_menu(self.menu_item, MENU_REQUIRES_TIMELINE_VIEW)

    def givenNoTimelineExists(self):
        self.menu_controller.on_timeline_change(None)
        
    def givenTimelineExists(self):
        self.menu_controller.on_timeline_change(self.timeline)

    def givenNoTimelineViewExists(self):
        self.timeline_panel_visible = False
        
    def givenTimelineViewExists(self):
        self.timeline_panel_visible = True
        
    def givenTimelineIsUpdateable(self):
        self.timeline.is_read_only.return_value = False

    def givenTimelineIsReadOnly(self):
        self.timeline.is_read_only.return_value = True

    def givenTimelinePanelIsVisible(self):
        self.timeline_panel_visible = True
        
    def whenMenuStatePossiblyHasChanged(self):
        self.menu_controller.enable_disable_menus(self.timeline_panel_visible)
