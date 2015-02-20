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

from timelinelib.plugin.pluginbase import PluginBase
from timelinelib.plugin.factory import EVENTBOX_DRAWER
from timelinelib.drawing.utils import darken_color


class DefaultEventBoxDrawer(PluginBase):

    def service(self):
        return EVENTBOX_DRAWER

    def display_name(self):
        return _("Default Event box drawer")

    def run(self, dc, rect, event):
        self._draw_background(dc, rect, event)
        self._draw_fuzzy_edges(dc, rect, event)

    def _draw_background(self, dc, rect, event):
        dc.SetBrush(wx.Brush(self._get_base_color(event), wx.SOLID))
        dc.SetPen(self._get_border_pen(event))
        dc.DrawRectangleRect(rect)

    def _draw_fuzzy_edges(self, dc, rect, event):
        if event.get_fuzzy():
            self._draw_fuzzy_start(dc, rect, event)
            self._draw_fuzzy_end(dc, rect, event)

    def _get_border_pen(self, event):
        return wx.Pen(self._get_border_color(event), 1, wx.SOLID)

    def _get_base_color(self, event):
        if event.get_category():
            base_color = event.get_category().color
        else:
            base_color = (200, 200, 200)
        return base_color

    def _get_border_color(self, event):
        base_color = self._get_base_color(event)
        border_color = darken_color(base_color)
        return border_color

    def _draw_fuzzy_start(self, dc, rect, event):
        """
          p1     /p2 ----------
                /
          p3  <
                \
          p4     \p5 ----------
        """
        x1 = rect.x
        x2 = rect.x + rect.height / 2
        y1 = rect.y
        y2 = rect.y + rect.height / 2
        y3 = rect.y + rect.height
        p1 = wx.Point(x1, y1)
        p2 = wx.Point(x2, y1)
        p3 = wx.Point(x1, y2)
        p4 = wx.Point(x1, y3)
        p5 = wx.Point(x2, y3)
        self.draw_fuzzy(dc, event, p1, p2, p3, p4, p5)

    def _draw_fuzzy_end(self, dc, rect, event):
        """
          ---- P2\    p1
                  \
                   >  p3
                  /
          ---- p4/    p4
        """
        x1 = rect.x + rect.width - rect.height / 2
        x2 = rect.x + rect.width
        y1 = rect.y
        y2 = rect.y + rect.height / 2
        y3 = rect.y + rect.height
        p1 = wx.Point(x2, y1)
        p2 = wx.Point(x1, y1)
        p3 = wx.Point(x2, y2)
        p4 = wx.Point(x2, y3)
        p5 = wx.Point(x1, y3)
        self.draw_fuzzy(dc, event, p1, p2, p3, p4, p5)

    def draw_fuzzy(self, dc, event, p1, p2, p3, p4, p5):
        self._draw_fuzzy_polygon(dc, p1, p2, p3)
        self._draw_fuzzy_polygon(dc, p3, p4, p5)
        self._draw_fuzzy_border(dc, event, p2, p3, p5)

    def _draw_fuzzy_polygon(self, dc, p1, p2, p3):
        dc.SetBrush(wx.WHITE_BRUSH)
        dc.SetPen(wx.WHITE_PEN)
        dc.DrawPolygon((p1, p2, p3))

    def _draw_fuzzy_border(self, dc, event, p1, p2, p3):
        gc = wx.GraphicsContext.Create(dc)
        path = gc.CreatePath()
        path.MoveToPoint(p1.x, p1.y)
        path.AddLineToPoint(p2.x, p2.y)
        path.AddLineToPoint(p3.x, p3.y)
        gc.SetPen(self._get_border_pen(event))
        gc.StrokePath(path)
        