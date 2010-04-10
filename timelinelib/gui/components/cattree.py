# Copyright (C) 2009, 2010  Rickard Lindberg, Roger Lindberg
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
import wx.lib.agw.customtreectrl as customtreectrl

from timelinelib.gui.utils import category_tree
from timelinelib.db.interface import TimelineIOError
from timelinelib.db.interface import STATE_CHANGE_CATEGORY


CHECKBOX_TYPE = 1


class CategoriesTree(customtreectrl.CustomTreeCtrl):
    """
    Display categories as tree and let user change visibility with check boxes.
    """

    def __init__(self, parent):
        style = (wx.BORDER_SUNKEN |
                 customtreectrl.TR_HIDE_ROOT |
                 customtreectrl.TR_HAS_VARIABLE_ROW_HEIGHT |
                 customtreectrl.TR_LINES_AT_ROOT |
                 customtreectrl.TR_HAS_BUTTONS)
        customtreectrl.CustomTreeCtrl.__init__(self, parent, style=style)
        self.view = None
        self.Bind(customtreectrl.EVT_TREE_ITEM_CHECKED,
                  self._on_tree_item_checked, self)

    def set_view(self, view):
        if self.view is not None:
            self.view.timeline.unregister(self._timeline_changed)
        self.view = view
        if self.view:
            self.view.timeline.register(self._timeline_changed)
            self._update_categories()
        else:
            self.DeleteAllItems()
        
    def _on_tree_item_checked(self, e):
        tree_item = e.GetItem()
        cat = tree_item.GetData()
        tree_item_checked = tree_item.IsChecked()
        self.view.view_properties.set_category_visible(cat, tree_item_checked)
        self.view.redraw_timeline()
        self._update_enableness()

    def _timeline_changed(self, state_change):
        if state_change == STATE_CHANGE_CATEGORY:
            self._update_categories()

    def _update_categories(self):
        try:
            categories = self.view.timeline.get_categories()
        except TimelineIOError, e:
            wx.GetTopLevelParent(self).handle_timeline_error(e)
        else:
            tree = category_tree(categories)
            self.DeleteAllItems()
            self.root = self.AddRoot("") # This will be hidden
            self._update_categories_from_tree(tree, self.root)
            self.ExpandAll()

    def _update_categories_from_tree(self, tree, root_item):
        for (cat, subtree) in tree:
            legend_panel = wx.Panel(self, size=(10, 10))
            legend_panel.SetBackgroundColour(cat.color)
            item = self.AppendItem(root_item, cat.name, ct_type=CHECKBOX_TYPE,
                                   wnd=legend_panel, data=cat)
            visible = self.view.view_properties.category_visible(cat)
            self.CheckItem2(item, visible)
            self._update_categories_from_tree(subtree, item)
            self._update_enableness()

    def _update_enableness(self):
        def update(parent_visible, tree_items):
            for item in tree_items:
                self.EnableItem(item, parent_visible)
                cat = item.GetData()
                visible = self.view.view_properties.category_visible(cat)
                update(visible, item.GetChildren())
        update(True, self.root.GetChildren())
