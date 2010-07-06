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
from os.path import abspath

from timelinelib.config import Config


class TestConfig(unittest.TestCase):

    def testDefaultValues(self):
        config = Config("")
        self.assertEquals(config.window_size, (900, 500))
        self.assertEquals(config.window_maximized, False)
        self.assertEquals(config.show_sidebar, True)
        self.assertEquals(config.show_legend, True)
        self.assertEquals(config.sidebar_width, 200)
        self.assertEquals(config.recently_opened, [])
        self.assertEquals(config.open_recent_at_startup, True)
        self.assertEquals(config.balloon_on_hover, True)
        self.assertEquals(config.week_start, "monday")

    def testSettingValues(self):
        """
        These are implemented as properties that store data inside a
        ConfigParser object. It is therefore worth testing.
        """
        config = Config("")
        config.window_size = (3, 20)
        self.assertEquals(config.window_size, (3, 20))
        config.window_maximized = True
        self.assertEquals(config.window_maximized, True)
        config.show_sidebar = False
        self.assertEquals(config.show_sidebar, False)
        config.show_legend = False
        self.assertEquals(config.show_legend, False)
        config.sidebar_width = 20
        self.assertEquals(config.sidebar_width, 20)
        config.append_recently_opened(u"foo")
        self.assertEquals(config.recently_opened, [abspath(u"foo")])
        config.open_recent_at_startup = False
        self.assertEquals(config.open_recent_at_startup, False)
        config.balloon_on_hover = False
        self.assertEquals(config.balloon_on_hover, False)
        config.week_start = "sunday"
        self.assertEquals(config.week_start, "sunday")

    def testRecentlyOpenedNotSameTwice(self):
        config = Config("")
        config.append_recently_opened(u"foo")
        self.assertEquals(config.recently_opened, [abspath(u"foo")])
        config.append_recently_opened(u"bar")
        self.assertEquals(config.recently_opened, [abspath(u"bar"), abspath(u"foo")])
        config.append_recently_opened(u"foo")
        # foo should only exists once, but it should be the first
        self.assertEquals(config.recently_opened, [abspath(u"foo"), abspath(u"bar")])

    def testRecentlyOpenedLenght(self):
        config = Config("")
        config.append_recently_opened(u"1")
        config.append_recently_opened(u"2")
        config.append_recently_opened(u"3")
        config.append_recently_opened(u"4")
        config.append_recently_opened(u"5")
        config.append_recently_opened(u"6")
        config.append_recently_opened(u"7")
        # Should contain maximum 5 paths
        res = [abspath(x) for x in [u"7", u"6", u"5", u"4", u"3"]]
        self.assertEquals(config.recently_opened, res)

    def testRecentlyOpenedNonUnicodeConverted(self):
        config = Config("")
        config.append_recently_opened("non-unicode-path")
        self.assertTrue(isinstance(config.recently_opened[0], unicode))

    def testRecentlyOpenedSpecialTimelines(self):
        config = Config("")
        config.append_recently_opened(":tutorial:")
        self.assertEquals([], config.recently_opened)

    def testInvalidWeekStart(self):
        config = Config("")
        # "sunday" and "monday" are ok, others are not
        config.week_start = "sunday"
        config.week_start = "monday"
        def set_invalid_week():
            config.week_start = "friday"
        self.assertRaises(ValueError, set_invalid_week)
