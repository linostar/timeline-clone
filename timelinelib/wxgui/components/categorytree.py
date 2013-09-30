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
    INDENT_PX = 10

    def render(self, dc, width, height, model):
        y = 0
        for entry in model.entries:
            x = self.INDENT_PX * entry.get("indent_level", 0)
            dc.DrawRectangle(x, y, width, self.HEIGHT)
            dc.DrawText(entry.get("name", ""), x, y)
            y += self.HEIGHT


class CustomCategoryTreeModel(object):

    def __init__(self):
        self.entries = []

    def update_from_timeline_view(self, timeline_view):
        self.timeline_view = timeline_view
        self.update_entries()

    def get_categories(self):
        return self.timeline_view.get_timeline().get_categories()

    def is_category_visible(self, category):
        return self.timeline_view.get_view_properties().category_visible(category)

    def update_entries(self):
        self.entries = []
        self._update_from_tree(self._list_to_tree(self.get_categories()))

    def _list_to_tree(self, categories, parent=None):
        top = [category for category in categories if (category.parent == parent)]
        return [(category, self._list_to_tree(categories, category)) for category in top]

    def _update_from_tree(self, category_tree, indent_level=0):
        for (category, child_tree) in category_tree:
            self.entries.append({
                "name": category.name,
                "color": category.color,
                "visible": self.is_category_visible(category),
            })
            if indent_level > 0:
                self.entries[-1]["indent_level"] = indent_level
            self._update_from_tree(child_tree, indent_level+1)
