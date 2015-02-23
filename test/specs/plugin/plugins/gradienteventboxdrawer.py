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
from timelinelib.plugin.plugins.gradienteventboxdrawer import GradientEventBoxDrawer
from timelinelib.plugin.factory import EVENTBOX_DRAWER


class describe_gradient_event_box_drawer(unittest.TestCase):

    def test_is_a_plugin(self):
        self.assertTrue(self.plugin.isplugin())

    def test_is_an_event_box_drawer(self):
        self.assertEquals(EVENTBOX_DRAWER, self.plugin.service())

    def test_has_a_display_name(self):
        self.assertTrue(len(self.plugin.display_name()) > 0)

    def test_overrides_draw_background(self):
        self.assertTrue(callable(getattr(self.plugin, "_draw_background")))

    def setUp(self):
        self.plugin = GradientEventBoxDrawer()
