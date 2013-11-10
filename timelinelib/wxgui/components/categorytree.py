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
from timelinelib.utilities.observer import Observable


class CategoriesFacade(Observable):

    def __init__(self, db, view_properties):
        Observable.__init__(self)
        self.db = db
        self.view_properties = view_properties
        self.db.register(self._db_changed)
        self.view_properties.register(self._view_properties_changed)

    def get_all(self):
        return self.db.get_categories()

    def is_visible(self, category):
        return self.view_properties.is_category_visible(category)

    def is_event_with_category_visible(self, category):
        return self.view_properties.is_event_with_category_visible(category)

    def set_visible(self, category_id, visible):
        self.view_properties.set_category_with_id_visible(category_id, visible)

    def _db_changed(self, _):
        self._notify(None)

    def _view_properties_changed(self, _):
        self._notify(None)


class CustomCategoryTree(wx.ScrolledWindow):

    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM) # Needed when using
                                                    # wx.AutoBufferedPaintDC
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, self._on_size)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.model = CustomCategoryTreeModel()
        self.renderer = CustomCategoryTreeRenderer(self, self.model)
        self.timeline_view = None
        self.model.register(self._model_changed)
        self._size_to_model()

    def set_timeline_view(self, db, view_properties):
        self.model.set_categories(CategoriesFacade(db, view_properties))

    def _model_changed(self, _):
        self._redraw()

    def _on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        self.DoPrepareDC(dc)
        dc.BeginDrawing()
        dc.SetBackground(wx.Brush(self.GetBackgroundColour(), wx.SOLID))
        dc.Clear()
        self.renderer.render(dc)
        dc.EndDrawing()

    def _on_size(self, event):
        self._size_to_model()

    def _on_left_down(self, event):
        (x, y) = self.CalcUnscrolledPosition(event.GetX(), event.GetY())
        self.model.left_click(x, y)

    def _redraw(self):
        self.SetVirtualSize((-1, self.model.ITEM_HEIGHT_PX * len(self.model.items)))
        self.SetScrollRate(-1, self.model.ITEM_HEIGHT_PX/2)
        self.Refresh()
        self.Update()

    def _size_to_model(self):
        (view_width, view_height) = self.GetVirtualSizeTuple()
        self.model.set_view_size(view_width, view_height)


class CustomCategoryTreeRenderer(object):

    INNER_PADDING = 2
    TRIANGLE_SIZE = 8

    def __init__(self, window, model):
        self.window = window
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
        self._render_checkbox(item)
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
        x = item["x"] + self.TRIANGLE_SIZE + 4 * self.INNER_PADDING + 20
        (w, h) = self.dc.GetTextExtent(item["name"])
        if item["actually_visible"]:
            self.dc.SetTextForeground(wx.BLACK)
        else:
            self.dc.SetTextForeground((150, 150, 150))
        self.dc.DrawText(item["name"], x + self.INNER_PADDING, item["y"] + self.INNER_PADDING)

    def _render_checkbox(self, item):
        bouning_rect = wx.Rect(item["x"] + self.model.INDENT_PX,
                               item["y"] + 4,
                               16,
                               16)
        if item["visible"]:
            flag = wx.CONTROL_CHECKED
        else:
            flag = 0
        renderer = wx.RendererNative.Get()
        renderer.DrawCheckBox(self.window, self.dc, bouning_rect, flag)

    def _render_color_box(self, item):
        color = item.get("color", None)
        self.dc.SetBrush(wx.Brush(color, wx.SOLID))
        self.dc.SetPen(wx.Pen(darken_color(color), 1, wx.SOLID))
        self.dc.DrawRectangle(
            item["x"] + item["width"] - self.model.ITEM_HEIGHT_PX - self.INNER_PADDING,
            item["y"] + self.INNER_PADDING,
            self.model.ITEM_HEIGHT_PX - 2 * self.INNER_PADDING,
            self.model.ITEM_HEIGHT_PX - 2 * self.INNER_PADDING)


class CustomCategoryTreeModel(Observable):

    ITEM_HEIGHT_PX = 22
    INDENT_PX = 15

    def __init__(self):
        Observable.__init__(self)
        self.view_width = 0
        self.view_height = 0
        self.categories = None
        self.collapsed_category_ids = []
        self.items = []

    def get_items(self):
        return self.items

    def set_view_size(self, view_width, view_height):
        self.view_width = view_width
        self.view_height = view_height
        self._update_items()

    def set_categories(self, categories):
        self.categories = categories
        self.categories.register(self._categories_changed)
        self._update_items()

    def _categories_changed(self, _):
        self._update_items()

    def left_click(self, x, y):
        item = self._item_at(y)
        if item:
            if self._hits_arrow(x, item):
                self._toggle_expandedness(item)
            if self._hits_checkbox(x, item):
                self._toggle_visibility(item)

    def _toggle_expandedness(self, item):
        category_id = item["id"]
        if category_id in self.collapsed_category_ids:
            self.collapsed_category_ids.remove(category_id)
        else:
            self.collapsed_category_ids.append(category_id)
        self._update_items()

    def _toggle_visibility(self, item):
        self.categories.set_visible(item["id"], not item["visible"])

    def _item_at(self, y):
        index = y // self.ITEM_HEIGHT_PX
        if index < len(self.items):
            return self.items[index]
        else:
            return None

    def _hits_arrow(self, x, item):
        return (x > item["x"] and
                x < (item["x"] + self.INDENT_PX))

    def _hits_checkbox(self, x, item):
        return (x > (item["x"] + self.INDENT_PX) and
                x < (item["x"] + 2*self.INDENT_PX))

    def _update_items(self):
        self.items = []
        self.y = 0
        self._update_from_tree(self._list_to_tree(self._get_categories()))
        self._notify(None)

    def _get_categories(self):
        if self.categories is None:
            return []
        else:
            return self.categories.get_all()

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
        return self.categories.is_visible(category)

    def _is_event_with_category_visible(self, category):
        return self.categories.is_event_with_category_visible(category)
