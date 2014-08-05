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
import wx

from timelinelib.db.backends.memory import MemoryDB
from timelinelib.drawing.drawers.default import DefaultDrawingAlgorithm
from timelinelib.view.drawingarea import DrawingArea
from timelinelib.view.drawingarea import HSCROLL_STEP
from timelinelib.wxgui.components.timeline import TimelineCanvas
from timelinelib.wxgui.dialogs.mainframe import StatusBarAdapter


class DrawingAreaSpec(unittest.TestCase):

    def test_construction_works(self):
        self.timeline_canvas.SetBackgroundColour.assert_called_with(wx.WHITE)
        self.timeline_canvas.SetBackgroundStyle.assert_called_with(wx.BG_STYLE_CUSTOM)
        self.timeline_canvas.set_default_cursor.assert_called()
        self.timeline_canvas.Disable.assert_called()
        self.timeline_canvas.edit_ends.assert_called()

    def test_get_drawer_returns_default_drawing_algorithm(self):
        self.assertEqual(self.drawing_algorithm, self.controller.get_drawer())

    def test_get_timeline_returns_given_null_timeline(self):
        self.controller.set_timeline(None)
        self.assertEqual(None, self.controller.get_timeline())

    def test_get_timeline_returns_given_nonnull_timeline(self):
        db = MemoryDB()
        self.controller.set_timeline(db)
        self.assertEqual(db, self.controller.get_timeline())

    def test_scroll_horizontal_down_increases_scroll_amount(self):
        self.when_scrolling_down_with(1)
        self.assertEqual(HSCROLL_STEP, self.controller.view_properties.hscroll_amount)

    def test_scroll_horizontal_up_decreases_scroll_amount(self):
        self.when_scrolling_down_with(2)
        self.when_scrolling_up_with(1)
        self.assertEqual(HSCROLL_STEP, self.controller.view_properties.hscroll_amount)

    def test_scroll_horizontal_amount_always_ge_zero(self):
        self.when_scrolling_down_with(2)
        self.when_scrolling_up_with(4)
        self.assertEqual(0, self.controller.view_properties.hscroll_amount)

    def when_scrolling_down_with(self, amount):
        for _ in xrange(amount):
            self.when_mouse_wheel_moved(-1)

    def when_scrolling_up_with(self, amount):
        for _ in xrange(amount):
            self.when_mouse_wheel_moved(1)

    def when_mouse_wheel_moved(self, rotation):
        self.controller.mouse_wheel_moved(rotation, True, True, False, 0)

    def setUp(self):
        self.app = wx.App() # a stored app is needed to create fonts
        self.timeline_canvas = Mock(TimelineCanvas)
        status_bar_adapter = Mock(StatusBarAdapter)
        config = Config()
        self.drawing_algorithm = DefaultDrawingAlgorithm()
        divider_line_slider = Mock(wx.Slider)
        divider_line_slider.GetValue.return_value = 1
        fn_handle_db_error = None
        self.controller = DrawingArea(self.timeline_canvas, status_bar_adapter,
                                      config, self.drawing_algorithm,
                                      divider_line_slider, fn_handle_db_error)


class Config(object):

    def get_show_legend(self):
        pass

    def get_balloon_on_hover(self):
        return False
