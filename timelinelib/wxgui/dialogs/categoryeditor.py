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
import wx.lib.colourselect as colourselect

import timelinelib.wxgui.utils as gui_utils
from timelinelib.wxgui.utils import _display_error_message
from timelinelib.wxgui.utils import _set_focus_and_select
from timelinelib.wxgui.utils import BORDER
from timelinelib.editors.category import CategoryEditorController


class CategoryEditor(wx.Dialog):

    def __init__(self, parent, title, timeline, category):
        wx.Dialog.__init__(self, parent, title=title)
        self._create_gui()
        self.controller = CategoryEditorController(self, timeline, category)
        self.controller.initialize()

    def set_category_tree(self, tree):
        def add_tree(tree, indent=""):
            for (root, subtree) in tree:
                self.parentlistbox.Append(indent + root.name, root)
                add_tree(subtree, indent + "    ")
        self.parentlistbox.Clear()
        self.parentlistbox.Append("", None) # No parent
        add_tree(tree)

    def get_name(self):
        return self.txt_name.GetValue().strip()

    def set_name(self, new_name):
        self.txt_name.SetValue(new_name)

    def get_color(self):
        # Convert wx.Color to (r, g, b) tuple
        (r, g, b) = self.colorpicker.GetValue()
        return (r, g, b)

    def get_font_color(self):
        # Convert wx.Color to (r, g, b) tuple
        (r, g, b) = self.fontcolorpicker.GetValue()
        return (r, g, b)

    def set_color(self, new_color):
        self.colorpicker.SetValue(new_color)

    def set_font_color(self, new_color):
        self.fontcolorpicker.SetValue(new_color)

    def get_parent(self):
        selection = self.parentlistbox.GetSelection()
        if selection == wx.NOT_FOUND:
            return None
        return self.parentlistbox.GetClientData(selection)

    def set_parent(self, parent):
        no_items = self.parentlistbox.GetCount()
        for i in range(0, no_items):
            if self.parentlistbox.GetClientData(i) is parent:
                self.parentlistbox.SetSelection(i)
                return

    def close(self):
        self.EndModal(wx.ID_OK)

    def handle_invalid_name(self, name):
        msg = _("Category name '%s' not valid. Must be non-empty.")
        _display_error_message(msg % name, self)
        _set_focus_and_select(self.txt_name)

    def handle_used_name(self, name):
        msg = _("Category name '%s' already in use.")
        _display_error_message(msg % name, self)
        _set_focus_and_select(self.txt_name)

    def handle_db_error(self, e):
        gui_utils.handle_db_error_in_dialog(self, e)

    def get_edited_category(self):
        return self.controller.category

    def _create_gui(self):
        self.txt_name = wx.TextCtrl(self, size=(150, -1))
        self.colorpicker = colourselect.ColourSelect(self)
        self.fontcolorpicker = colourselect.ColourSelect(self)
        self.parentlistbox = wx.Choice(self, wx.ID_ANY)
        vbox = wx.BoxSizer(wx.VERTICAL)
        field_grid = wx.FlexGridSizer(3, 2, BORDER, BORDER)
        field_grid.Add(wx.StaticText(self, label=_("Name:")),
                       flag=wx.ALIGN_CENTER_VERTICAL)
        field_grid.Add(self.txt_name)
        field_grid.Add(wx.StaticText(self, label=_("Color:")),
                       flag=wx.ALIGN_CENTER_VERTICAL)
        field_grid.Add(self.colorpicker)
        field_grid.Add(wx.StaticText(self, label=_("Font Color:")),
                       flag=wx.ALIGN_CENTER_VERTICAL)
        field_grid.Add(self.fontcolorpicker)
        field_grid.Add(wx.StaticText(self, label=_("Parent:")),
                       flag=wx.ALIGN_CENTER_VERTICAL)
        field_grid.Add(self.parentlistbox)
        vbox.Add(field_grid, flag=wx.EXPAND|wx.ALL, border=BORDER)
        # Buttons
        button_box = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self._btn_ok_on_click, id=wx.ID_OK)
        vbox.Add(button_box, flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.SetSizerAndFit(vbox)
        _set_focus_and_select(self.txt_name)

    def _btn_ok_on_click(self, e):
        self.controller.save()
