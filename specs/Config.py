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


from os.path import abspath
import unittest

from timelinelib.config import Config


class ConfigSpec(unittest.TestCase):
    
    def testShouldHaveDefaultValuesBeforeConfigHasBeenRead(self):
        self.assertEquals(self.config.window_size, (900, 500))
        self.assertEquals(self.config.window_maximized, False)
        self.assertEquals(self.config.show_sidebar, True)
        self.assertEquals(self.config.show_legend, True)
        self.assertEquals(self.config.sidebar_width, 200)
        self.assertEquals(self.config.recently_opened, [])
        self.assertEquals(self.config.open_recent_at_startup, True)
        self.assertEquals(self.config.balloon_on_hover, True)
        self.assertEquals(self.config.week_start, "monday")
        self.assertEquals(self.config.get_use_wide_date_range(), False)
        self.assertEquals(self.config.get_use_inertial_scrolling(), False)

    def testWindowSizeCanBeReadAfterStored(self):
        self.config.window_size = (3, 20)
        self.assertEquals(self.config.window_size, (3, 20))

    def testWindowMaximizedCanBeReadAfterStored(self):
        self.config.window_maximized = True
        self.assertEquals(self.config.window_maximized, True)

    def testShowSidebarCanBeReadAfterStored(self):
        self.config.show_sidebar = False
        self.assertEquals(self.config.show_sidebar, False)

    def testShowLegendCanBeReadAfterStored(self):
        self.config.show_legend = False
        self.assertEquals(self.config.show_legend, False)

    def testSidebarWidthCanBeReadAfterStored(self):
        self.config.sidebar_width = 20
        self.assertEquals(self.config.sidebar_width, 20)

    def testRecentlyOpenedCanBeReadAfterStored(self):
        self.config.append_recently_opened(u"foo")
        self.assertEquals(self.config.recently_opened, [abspath(u"foo")])

    def testOpenRecentAtStartupCanBeReadAfterStored(self):
        self.config.open_recent_at_startup = False
        self.assertEquals(self.config.open_recent_at_startup, False)

    def testBalloonOnHoverCanBeReadAfterStored(self):
        self.config.balloon_on_hover = False
        self.assertEquals(self.config.balloon_on_hover, False)

    def testWeekStartCanBeReadAfterStored(self):
        self.config.week_start = "sunday"
        self.assertEquals(self.config.week_start, "sunday")

    def testInertialScrollingCanBeReadAfterStored(self):
        self.config.use_inertial_scrolling = False
        self.assertEquals(self.config.use_inertial_scrolling, False)

    def testConfigReturnsWideDateRangeIsTrueWhenSetToTrue(self):
        self.config.set_use_wide_date_range(True)
        self.assertTrue(self.config.get_use_wide_date_range())

    def testConfigReturnsWideDateRangeIsFalseWhenSetToFalse(self):
        self.config.set_use_wide_date_range(False)
        self.assertFalse(self.config.get_use_wide_date_range())

    def testConfigReturnsUseInertialScrollingIsTrueWhenSetToTrue(self):
        self.config.set_use_inertial_scrolling(True)
        self.assertTrue(self.config.get_use_inertial_scrolling())

    def testConfigReturnsUseInertialScrollingIsFalseWhenSetToFalse(self):
        self.config.set_use_inertial_scrolling(False)
        self.assertFalse(self.config.get_use_inertial_scrolling())

    def testConfigReturnsWideDateRangeIsFalseWhenSetToFalseAsPropety(self):
        self.config.use_wide_date_range = False
        self.assertFalse(self.config.use_wide_date_range)
        
    def testConfigReturnsWideDateRangeIsTrueWhenSetToTrueAsPropety(self):
        self.config.use_wide_date_range = True
        self.assertTrue(self.config.use_wide_date_range)

    def testRecentlyOpenedContainsLast5Entries(self):
        self.config.append_recently_opened("1")
        self.config.append_recently_opened("2")
        self.config.append_recently_opened("3")
        self.config.append_recently_opened("4")
        self.config.append_recently_opened("5")
        self.config.append_recently_opened("6")
        self.config.append_recently_opened("7")
        last_five = [abspath(entry) for entry in ["7", "6", "5", "4", "3"]]
        self.assertEquals(self.config.recently_opened, last_five)

    def testRecentlyOpenedListDoesNotContainDuplicates(self):
        self.config.append_recently_opened("foo")
        self.config.append_recently_opened("bar")
        self.config.append_recently_opened("foo")
        self.assertEquals(
            self.config.recently_opened,
            [abspath("foo"), abspath("bar")])

    def testConvertsRecentlyOpenedPathToUnicode(self):
        self.config.append_recently_opened("non-unicode-path")
        self.assertTrue(isinstance(self.config.recently_opened[0], unicode))

    def testRecentlyOpenedDoesNotStoreSpecialTutorialFile(self):
        self.config.append_recently_opened(":tutorial:")
        self.assertEquals([], self.config.recently_opened)

    def testSettingInvalidWeekStartRaisesValueError(self):
        def set_invalid_week():
            self.config.week_start = "friday"
        self.assertRaises(ValueError, set_invalid_week)

    def setUp(self):
        self.config = Config("")
