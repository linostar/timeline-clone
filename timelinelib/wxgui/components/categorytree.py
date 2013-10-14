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
        self.model = CustomCategoryTreeModel()
        self.timeline_view = None
        self.renderer = CustomCategoryTreeRenderer(self.model)
        self._size_to_model()

    def set_timeline_view(self, timeline_view):
        if self.timeline_view:
            self.timeline_view.unregister(self._db_changed)
        self.timeline_view = timeline_view
        self.timeline_view.register(self._db_changed)
        self._db_changed(None)

    def _db_changed(self, _):
        self.model.set_timeline_view(self.timeline_view)
        self._redraw()

    def _on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.BeginDrawing()
        dc.SetBackground(wx.Brush(self.GetBackgroundColour(), wx.SOLID))
        dc.Clear()
        self.renderer.render(dc)
        dc.EndDrawing()

    def _on_size(self, event):
        self._size_to_model()
        self._redraw()

    def _on_left_down(self, event):
        self.model.toggle_expandedness(event.GetY())
        self._redraw()

    def _redraw(self):
        self.Refresh()
        self.Update()

    def _size_to_model(self):
        (view_width, view_height) = self.GetSizeTuple()
        self.model.set_view_size(view_width, view_height)


class CustomCategoryTreeRenderer(object):

    INNER_PADDING = 2
    TRIANGLE_SIZE = 8

    def __init__(self, model):
        self.model = model

    def render(self, dc):
        self.dc = dc
        self._render_items(self.model.items)
        del self.dc

    def _render_items(self, items):
        for item in items:
            self._render_item(item)

    def _render_item(self, item):
        if item["has_children"]:
            self._render_arrow(item)
        if item["visible"]:
            self._render_visible_toggle(item)
        self._render_name(item)
        self._render_color_box(item)

    def _render_arrow(self, item):
        self.dc.SetBrush(wx.Brush(wx.Color(100, 100, 100), wx.SOLID))
        self.dc.SetPen(wx.Pen(wx.Color(100, 100, 100), 0, wx.SOLID))
        offset = self.TRIANGLE_SIZE/2
        center_x = item["x"] + 2*self.INNER_PADDING + offset
        center_y = item["y"] + self.model.ITEM_HEIGHT_PX/2
        if item["expanded"]:
            open_polygon = [
                wx.Point(center_x - offset, center_y - offset),
                wx.Point(center_x + offset, center_y - offset),
                wx.Point(center_x         , center_y + offset),
            ]
            self.dc.DrawPolygon(open_polygon)
        else:
            closed_polygon = [
                wx.Point(center_x - offset, center_y - offset),
                wx.Point(center_x - offset, center_y + offset),
                wx.Point(center_x + offset, center_y),
            ]
            self.dc.DrawPolygon(closed_polygon)

    def _render_name(self, item):
        x = item["x"] + self.TRIANGLE_SIZE + 4 * self.INNER_PADDING
        (w, h) = self.dc.GetTextExtent(item["name"])
        if item["actually_visible"]:
            self.dc.SetTextForeground(wx.BLACK)
        else:
            self.dc.SetTextForeground((150, 150, 150))
        self.dc.DrawText(item["name"], x + self.INNER_PADDING, item["y"] + self.INNER_PADDING)

    def _render_visible_toggle(self, item):
        color = (150, 150, 150)
        self.dc.SetBrush(wx.Brush(color, wx.SOLID))
        self.dc.SetPen(wx.Pen(darken_color(color), 1, wx.SOLID))
        self.dc.DrawCircle(
            item["x"] + item["width"] - self.model.ITEM_HEIGHT_PX*2,
            item["y"] + self.model.ITEM_HEIGHT_PX/2,
            self.model.ITEM_HEIGHT_PX/4)

    def _render_color_box(self, item):
        color = item.get("color", None)
        self.dc.SetBrush(wx.Brush(color, wx.SOLID))
        self.dc.SetPen(wx.Pen(darken_color(color), 1, wx.SOLID))
        self.dc.DrawRectangle(
            item["x"] + item["width"] - self.model.ITEM_HEIGHT_PX - self.INNER_PADDING,
            item["y"] + self.INNER_PADDING,
            self.model.ITEM_HEIGHT_PX - 2 * self.INNER_PADDING,
            self.model.ITEM_HEIGHT_PX - 2 * self.INNER_PADDING)


class CustomCategoryTreeModel(object):

    ITEM_HEIGHT_PX = 22
    INDENT_PX = 15

    def __init__(self):
        self.view_width = 0
        self.view_height = 0
        self.timeline_view = None
        self.collapsed_category_ids = []
        self.items = []

    def get_items(self):
        return self.items

    def set_view_size(self, view_width, view_height):
        self.view_width = view_width
        self.view_height = view_height
        self._update_items()

    def set_timeline_view(self, timeline_view):
        self.timeline_view = timeline_view
        self._update_items()

    def toggle_expandedness(self, y_position):
        index = y_position // self.ITEM_HEIGHT_PX
        if index < len(self.items):
            id_at_index = self.items[index]["id"]
            if id_at_index in self.collapsed_category_ids:
                self.collapsed_category_ids.remove(id_at_index)
            else:
                self.collapsed_category_ids.append(id_at_index)
            self._update_items()

    def _update_items(self):
        self.items = []
        self.y = 0
        self._update_from_tree(self._list_to_tree(self._get_categories()))

    def _get_categories(self):
        if self.timeline_view is None:
            return []
        else:
            return self.timeline_view.get_timeline().get_categories()

    def _list_to_tree(self, categories, parent=None):
        top = [category for category in categories if (category.parent == parent)]
        sorted_top = sorted(top, key=lambda category: category.name)
        return [(category, self._list_to_tree(categories, category)) for
                category in sorted_top]

    def _update_from_tree(self, category_tree, indent_level=0):
        for (category, child_tree) in category_tree:
            expanded = category.id not in self.collapsed_category_ids
            self.items.append({
                "id": category.id,
                "name": category.name,
                "color": category.color,
                "visible": self._is_category_visible(category),
                "x": indent_level * self.INDENT_PX,
                "y": self.y,
                "width": self.view_width - indent_level * self.INDENT_PX,
                "expanded": expanded,
                "has_children": len(child_tree) > 0,
                "actually_visible": self._is_event_with_category_visible(category),
            })
            self.y += self.ITEM_HEIGHT_PX
            if expanded:
                self._update_from_tree(child_tree, indent_level+1)

    def _is_category_visible(self, category):
        return self.timeline_view.get_view_properties().is_category_visible(category)

    def _is_event_with_category_visible(self, category):
        return self.timeline_view.get_view_properties().is_event_with_category_visible(category)
