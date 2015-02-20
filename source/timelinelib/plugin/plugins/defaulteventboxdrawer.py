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

    def _draw_background(self, dc, rect, event):
        dc.SetBrush(wx.Brush(self._get_base_color(event), wx.SOLID))
        dc.SetPen(self._get_border_pen(event))
        dc.DrawRectangleRect(rect)

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
