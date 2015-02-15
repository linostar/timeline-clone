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


class GradientEventBoxDrawer(PluginBase):

    def service(self):
        return EVENTBOX_DRAWER

    def display_name(self):
        return _("Gradient Event box drawer")

    def run(self, dc, rect, event):
        dc.SetBrush(wx.GREEN_BRUSH)
        dc.SetPen(wx.RED_PEN)
        dc.DrawRectangleRect(rect)
