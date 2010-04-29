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

from timelinelib.db.interface import TimelineIOError
from timelinelib.db.interface import STATE_CHANGE_CATEGORY
import timelinelib.gui.utils as gui_utils
from timelinelib.gui.utils import sort_categories
from timelinelib.gui.utils import _display_error_message
from timelinelib.gui.utils import _ask_question
from timelinelib.gui.utils import BORDER
from timelinelib.gui.utils import ID_ERROR
from timelinelib.gui.dialogs.categoryeditor import CategoryEditor
from timelinelib.gui.components.cattree import CategoriesTree
from timelinelib.gui.components.cattree import add_category
from timelinelib.gui.components.cattree import edit_category
from timelinelib.gui.components.cattree import delete_category
from timelinelib.utils import ex_msg


class CategoriesEditor(wx.Dialog):
    """
    Dialog used to edit categories of a timeline.

    The edits happen immediately. In other words: when the dialog is closing
    all edits have been applied already.
    """

    def __init__(self, parent, timeline):
        wx.Dialog.__init__(self, parent, title=_("Edit Categories"))
        self._create_gui()
        self.db = timeline
        self.cat_tree.initialize_from_db(self.db)

    def _create_gui(self):
        self.Bind(wx.EVT_CLOSE, self._window_on_close)
        # The tree
        self.cat_tree = CategoriesTree(self, self.handle_db_error)
        self.cat_tree.SetMinSize((-1, 200))
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self._cat_tree_on_sel_changed,
                  self.cat_tree)
        # The Add button
        btn_add = wx.Button(self, wx.ID_ADD)
        self.Bind(wx.EVT_BUTTON, self._btn_add_on_click, btn_add)
        # The Delete button
        self.btn_del = wx.Button(self, wx.ID_DELETE)
        self.btn_del.Disable()
        self.Bind(wx.EVT_BUTTON, self._btn_del_on_click, self.btn_del)
        # The close button
        btn_close = wx.Button(self, wx.ID_CLOSE)
        btn_close.SetDefault()
        btn_close.SetFocus()
        self.SetAffirmativeId(wx.ID_CLOSE)
        self.Bind(wx.EVT_BUTTON, self._btn_close_on_click, btn_close)
        # Setup layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.cat_tree, flag=wx.ALL|wx.EXPAND, border=BORDER)
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        button_box.Add(btn_add, flag=wx.RIGHT, border=BORDER)
        button_box.Add(self.btn_del, flag=wx.RIGHT, border=BORDER)
        button_box.AddStretchSpacer()
        button_box.Add(btn_close, flag=wx.LEFT, border=BORDER)
        vbox.Add(button_box, flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.SetSizerAndFit(vbox)

    def handle_db_error(self, e):
        gui_utils.handle_db_error_in_dialog(self, e)

    def _cat_tree_on_sel_changed(self, e):
        self._update_del_button()

    def _window_on_close(self, e):
        self.cat_tree.destroy()
        self.EndModal(wx.ID_CLOSE)

    def _btn_add_on_click(self, e):
        add_category(self, self.db, self.handle_db_error)
        
    def _btn_del_on_click(self, e):
        cat = self.cat_tree.get_selected_category()
        if cat:
            delete_category(self, self.db, cat, self.handle_db_error)
        self._update_del_button()

    def _update_del_button(self):
        self.btn_del.Enable(self.cat_tree.get_selected_category() is not None)

    def _btn_close_on_click(self, e):
        self.Close()
