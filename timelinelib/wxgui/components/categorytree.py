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


class CustomCategoryTree(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.renderer = CustomCategoryTreeRenderer()
        self.model = CustomCategoryTreeModel()

    def update_from_timeline_view(self, timeline_view):
        self.model.update_from_timeline_view(timeline_view)
        self.Refresh()

    def _on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.BeginDrawing()
        (width, height) = self.GetSizeTuple()
        self.renderer.render(dc, width, height, self.model)
        dc.EndDrawing()


class CustomCategoryTreeRenderer(object):

    HEIGHT = 20

    def render(self, dc, width, height, model):
        y = 0
        for entry in model.entries:
            dc.DrawRectangle(0, y, width, self.HEIGHT)
            dc.DrawText(entry.get("name", ""), 0, y)
            y += self.HEIGHT


class CustomCategoryTreeModel(object):

    def __init__(self):
        self.entries = []

    def update_from_timeline_view(self, timeline_view):
        self.entries = []
        for category in timeline_view.get_timeline().get_categories():
            self.entries.append({
                "name": category.name,
                "color": category.color,
                "visible":
                timeline_view.get_view_properties().category_visible(category),
            })
