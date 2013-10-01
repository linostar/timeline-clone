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

from timelinelib.drawing.utils import darken_color


class CustomCategoryTree(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM) # Needed when using
                                                    # wx.AutoBufferedPaintDC
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, self._on_size)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.renderer = CustomCategoryTreeRenderer()
        self.model = CustomCategoryTreeModel()

    def set_timeline_view(self, timeline_view):
        self.model.set_timeline_view(timeline_view)
        self.Refresh()

    def _on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.BeginDrawing()
        (width, height) = self.GetSizeTuple()
        self.renderer.render(dc, width, height, self.model)
        dc.EndDrawing()

    def _on_size(self, event):
        self.Refresh()

    def _on_left_down(self, event):
        self.model.toggle_expandedness(event.GetY())
        self.Refresh()


class CustomCategoryTreeRenderer(object):

    INNER_PADDING = 2
    TRIANGLE_SIZE = 8

    def render(self, dc, width, height, model):
        self.dc = dc
        self.width = width
        self.model = model
        self.render_entries(model.entries)
        del self.dc

    def render_entries(self, entries):
        for entry in entries:
            self.render_entry(entry)

    def render_entry(self, entry):
        self.render_arrow(entry)
        self.render_name(entry)
        self.render_color_box(entry)

    def render_arrow(self, entry):
        self.dc.SetBrush(wx.Brush(wx.Color(100, 100, 100), wx.SOLID))
        self.dc.SetPen(wx.Pen(wx.Color(100, 100, 100), 0, wx.SOLID))
        center_y = entry["y"] + self.model.HEIGHT / 2
        start_x = entry["x"] + self.INNER_PADDING
        if entry["expanded"]:
            open_polygon = [
                wx.Point(start_x + self.INNER_PADDING, center_y - self.TRIANGLE_SIZE / 2),
                wx.Point(start_x + self.INNER_PADDING + self.TRIANGLE_SIZE, center_y - self.TRIANGLE_SIZE / 2),
                wx.Point(start_x + self.INNER_PADDING + self.TRIANGLE_SIZE / 2, center_y),
            ]
            self.dc.DrawPolygon(open_polygon)
        else:
            closed_polygon = [
                wx.Point(start_x + self.INNER_PADDING, center_y - self.TRIANGLE_SIZE / 2),
                wx.Point(start_x + self.INNER_PADDING + self.TRIANGLE_SIZE, center_y),
                wx.Point(start_x + self.INNER_PADDING, center_y + self.TRIANGLE_SIZE / 2),
            ]
            self.dc.DrawPolygon(closed_polygon)

    def render_name(self, entry):
        x = entry["x"] + self.TRIANGLE_SIZE + 4 * self.INNER_PADDING
        (w, h) = self.dc.GetTextExtent(entry["name"])
        self.dc.DrawText(entry["name"], x + self.INNER_PADDING, entry["y"] + self.INNER_PADDING)

    def render_color_box(self, entry):
        color = entry.get("color", None)
        self.dc.SetBrush(wx.Brush(color, wx.SOLID))
        self.dc.SetPen(wx.Pen(darken_color(color), 1, wx.SOLID))
        self.dc.DrawRectangle(
            self.width - self.model.HEIGHT - self.INNER_PADDING,
            entry["y"] + self.INNER_PADDING,
            self.model.HEIGHT - 2 * self.INNER_PADDING,
            self.model.HEIGHT - 2 * self.INNER_PADDING)


class CustomCategoryTreeModel(object):

    HEIGHT = 22
    INDENT_PX = 15

    def __init__(self):
        self.entries = []
        self.collapsed_category_ids = []

    def set_timeline_view(self, timeline_view):
        self.timeline_view = timeline_view
        self.update_entries()

    def toggle_expandedness(self, y_position):
        index = y_position // self.HEIGHT
        if index < len(self.entries):
            id_at_index = self.entries[index]["id"]
            if id_at_index in self.collapsed_category_ids:
                self.collapsed_category_ids.remove(id_at_index)
            else:
                self.collapsed_category_ids.append(id_at_index)
            self.update_entries()

    def get_categories(self):
        return self.timeline_view.get_timeline().get_categories()

    def is_category_visible(self, category):
        return self.timeline_view.get_view_properties().category_visible(category)

    def update_entries(self):
        self.entries = []
        self.y = 0
        self._update_from_tree(self._list_to_tree(self.get_categories()))

    def _list_to_tree(self, categories, parent=None):
        top = [category for category in categories if (category.parent == parent)]
        sorted_top = sorted(top, key=lambda category: category.name)
        return [(category, self._list_to_tree(categories, category)) for
                category in sorted_top]

    def _update_from_tree(self, category_tree, indent_level=0):
        for (category, child_tree) in category_tree:
            expanded = category.id not in self.collapsed_category_ids
            self.entries.append({
                "id": category.id,
                "name": category.name,
                "color": category.color,
                "visible": self.is_category_visible(category),
                "x": indent_level * self.INDENT_PX,
                "y": self.y,
                "expanded": expanded,
            })
            self.y += self.HEIGHT
            if expanded:
                self._update_from_tree(child_tree, indent_level+1)
