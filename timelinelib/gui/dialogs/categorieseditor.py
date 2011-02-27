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

import timelinelib.gui.utils as gui_utils
from timelinelib.gui.utils import BORDER
from timelinelib.gui.components.cattree import CategoriesTree
from timelinelib.gui.components.cattree import add_category
from timelinelib.gui.components.cattree import edit_category
from timelinelib.gui.components.cattree import delete_category


class CategoriesEditor(wx.Dialog):
    """
    Dialog used to edit categories of a timeline.

    The edits happen immediately. In other words: when the dialog is closing
    all edits have been applied already.
    """

    def __init__(self, parent, timeline):
        wx.Dialog.__init__(self, parent, title=_("Edit Categories"))
        self.cat_tree = self._create_gui()
        self.controller = CategoriesEditorController(self, timeline)
        self.controller.initialize(self.cat_tree)

    def get_selected_category(self):
        return self.cat_tree.get_selected_category()
            
    def initialize(self, db):
        self.cat_tree.initialize_from_db(db)
        
    def _create_gui(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        cat_tree = self._create_cat_tree(vbox)
        self._create_buttons(vbox)
        self.SetSizerAndFit(vbox)
        self.Bind(wx.EVT_CLOSE, self._window_on_close)
        return cat_tree

    def _create_cat_tree(self, vbox):
        cat_tree = CategoriesTree(self, self.handle_db_error)
        cat_tree.SetMinSize((-1, 200))
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self._cat_tree_on_sel_changed,
                  cat_tree)
        vbox.Add(cat_tree, flag=wx.ALL|wx.EXPAND, border=BORDER)
        return cat_tree

    def _create_buttons(self, vbox):
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_edit = self._create_edit_button(button_box)
        self._create_add_button(button_box)
        self.btn_del = self._create_delete_button(button_box)
        self._create_close_button(button_box)
        vbox.Add(button_box, flag=wx.ALL|wx.EXPAND, border=BORDER)

    def _create_edit_button(self, button_box):
        btn_edit = wx.Button(self, wx.ID_EDIT)
        btn_edit.Disable()
        self.Bind(wx.EVT_BUTTON, self._btn_edit_on_click, btn_edit)
        button_box.Add(btn_edit, flag=wx.RIGHT, border=BORDER)
        return btn_edit
        
    def _create_add_button(self, button_box):
        btn_add = wx.Button(self, wx.ID_ADD)
        self.Bind(wx.EVT_BUTTON, self._btn_add_on_click, btn_add)
        button_box.Add(btn_add, flag=wx.RIGHT, border=BORDER)

    def _create_delete_button(self, button_box):
        btn_del = wx.Button(self, wx.ID_DELETE)
        btn_del.Disable()
        self.Bind(wx.EVT_BUTTON, self._btn_del_on_click, btn_del)
        button_box.Add(btn_del, flag=wx.RIGHT, border=BORDER)
        button_box.AddStretchSpacer()
        return btn_del

    def _create_close_button(self, button_box):
        btn_close = wx.Button(self, wx.ID_CLOSE)
        btn_close.SetDefault()
        btn_close.SetFocus()
        self.SetAffirmativeId(wx.ID_CLOSE)
        self.Bind(wx.EVT_BUTTON, self._btn_close_on_click, btn_close)
        button_box.Add(btn_close, flag=wx.LEFT, border=BORDER)
        
    def handle_db_error(self, e):
        gui_utils.handle_db_error_in_dialog(self, e)

    def _cat_tree_on_sel_changed(self, e):
        self._updateButtons()

    def _updateButtons(self):
        cat_selected = self.cat_tree.get_selected_category() is not None
        self.btn_edit.Enable(cat_selected)
        self.btn_del.Enable(cat_selected)
        
    def _window_on_close(self, e):
        self.cat_tree.destroy()
        self.EndModal(wx.ID_CLOSE)

    def _btn_edit_on_click(self, e):
        self.controller.edit()
        self._updateButtons()
        
    def _btn_add_on_click(self, e):
        self.controller.add()
        self._updateButtons()
        
    def _btn_del_on_click(self, e):
        self.controller.delete()
        self._updateButtons()

    def _btn_close_on_click(self, e):
        self.Close()
                

class CategoriesEditorController(object):

    def __init__(self, view, db):
        self.view = view
        self.db = db

    def initialize(self, cat_tree):
        self.view.initialize(self.db)
    
    def edit(self):
        cat = self.view.get_selected_category()
        if cat:
            edit_category(self.view, self.db, cat, self.handle_db_error)

    def add(self):
        add_category(self.view, self.db, self.handle_db_error)

    def delete(self):
        cat = self.view.get_selected_category()
        if cat:
            delete_category(self.view, self.db, cat, self.handle_db_error)
            
    def handle_db_error(self, e):
        gui_utils.handle_db_error_in_dialog(self, e)
