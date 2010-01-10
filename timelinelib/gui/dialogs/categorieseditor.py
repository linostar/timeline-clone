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
from timelinelib.gui.utils import sort_categories
from timelinelib.gui.utils import _display_error_message
from timelinelib.gui.utils import _ask_question
from timelinelib.gui.utils import BORDER
from timelinelib.gui.utils import ID_ERROR
from timelinelib.gui.dialogs.categoryeditor import CategoryEditor


class CategoriesEditor(wx.Dialog):
    """
    Dialog used to edit categories of a timeline.

    The edits happen immediately. In other words: when the dialog is closing
    all edits have been applied already.
    """

    def __init__(self, parent, timeline):
        wx.Dialog.__init__(self, parent, title=_("Edit Categories"))
        self._create_gui()
        self.timeline = timeline
        # Note: We must unregister before we close this dialog. When we close
        # this dialog it will be disposed and self._timeline_changed will no
        # longer exist. The next time the timeline gets updated it will try to
        # call a method that does not exist.
        self.timeline.register(self._timeline_changed)
        self._update_categories()

    def _create_gui(self):
        self.Bind(wx.EVT_CLOSE, self._window_on_close)
        # The list box
        self.lst_categories = wx.ListBox(self, size=(200, 180),
                                         style=wx.LB_SINGLE)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self._lst_categories_on_dclick,
                  self.lst_categories)
        self.Bind(wx.EVT_LISTBOX, self._lst_categories_on_change,
                  self.lst_categories)
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
        self.lst_categories.Bind(wx.EVT_KEY_DOWN, self._lst_categories_on_key_down)
        # Setup layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.lst_categories, flag=wx.ALL|wx.EXPAND, border=BORDER)
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        button_box.Add(btn_add, flag=wx.RIGHT, border=BORDER)
        button_box.Add(self.btn_del, flag=wx.RIGHT, border=BORDER)
        button_box.AddStretchSpacer()
        button_box.Add(btn_close, flag=wx.LEFT, border=BORDER)
        vbox.Add(button_box, flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.SetSizerAndFit(vbox)
        self.lst_categories.SetFocus()

    def _window_on_close(self, e):
        # This will always be called before the dialog closes so we can do the
        # unregister here.
        self.timeline.unregister(self._timeline_changed)
        self.EndModal(wx.ID_CLOSE)

    def _lst_categories_on_dclick(self, e):
        try:
            selection = e.GetSelection()
            dialog = CategoryEditor(self, _("Edit Category"), self.timeline,
                                    e.GetClientData())
        except TimelineIOError, e:
            _display_error_message(e.message, self)
            self.error = e
            self.EndModal(ID_ERROR)
        else:
            if dialog.ShowModal() == ID_ERROR:
                self.error = dialog.error
                self.EndModal(ID_ERROR)
            dialog.Destroy()

    def _lst_categories_on_change(self, e):
        cat = self.lst_categories.GetSelection()
        if cat > -1:
            self.btn_del.Enable()

    def _btn_add_on_click(self, e):
        try:
            dialog = CategoryEditor(self, _("Add Category"), self.timeline,
                                    None)
        except TimelineIOError, e:
            _display_error_message(e.message, self)
            self.error = e
            self.EndModal(ID_ERROR)
        else:
            if dialog.ShowModal() == ID_ERROR:
                self.error = dialog.error
                self.EndModal(ID_ERROR)
            dialog.Destroy()
        
    def _btn_del_on_click(self, e):
        try:
            self._delete_selected_category()
        except TimelineIOError, e:
            _display_error_message(e.message, self)
            self.error = e
            self.EndModal(ID_ERROR)

    def _btn_close_on_click(self, e):
        self.Close()

    def _lst_categories_on_key_down(self, e):
        try:
            keycode = e.GetKeyCode()
            if keycode == wx.WXK_DELETE:
                self._delete_selected_category()
            e.Skip()
        except TimelineIOError, e:
            _display_error_message(e.message, self)
            self.error = e
            self.EndModal(ID_ERROR)

    def _timeline_changed(self, state_change):
        try:
            if state_change == STATE_CHANGE_CATEGORY:
                self._update_categories()
        except TimelineIOError, e:
            _display_error_message(e.message, self)
            self.error = e
            self.EndModal(ID_ERROR)

    def _delete_selected_category(self):
        selection = self.lst_categories.GetSelection()
        if selection != wx.NOT_FOUND:
            if _ask_question(_("Are you sure to delete?"), self) == wx.YES:
                cat = self.lst_categories.GetClientData(selection)
                self.timeline.delete_category(cat)

    def _update_categories(self):
        self.lst_categories.Clear()
        for category in sort_categories(self.timeline.get_categories()):
            self.lst_categories.Append(category.name, category)
        self.btn_del.Disable()
