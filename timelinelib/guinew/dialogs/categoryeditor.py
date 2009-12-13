# Copyright (C) 2009  Rickard Lindberg, Roger Lindberg
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

from timelinelib.db.interface import TimelineIOError
from timelinelib.db.objects import Category
from timelinelib.guinew.utils import _display_error_message
from timelinelib.guinew.utils import _set_focus_and_select
from timelinelib.guinew.utils import _display_error_message
from timelinelib.guinew.utils import BORDER
from timelinelib.guinew.utils import ID_ERROR


class CategoryEditor(wx.Dialog):
    """
    Dialog used to edit a category.

    The edited category can be fetched with get_edited_category.
    """

    def __init__(self, parent, title, timeline, category):
        wx.Dialog.__init__(self, parent, title=title)
        self._create_gui()
        self.timeline = timeline
        self.category = category
        self.create_new = False
        if self.category == None:
            self.create_new = True
            self.category = Category("", (200, 200, 200), True)
        self.txt_name.SetValue(self.category.name)
        self.colorpicker.SetColour(self.category.color)
        self.chb_visible.SetValue(self.category.visible)

    def get_edited_category(self):
        return self.category

    def _create_gui(self):
        # The name text box
        self.txt_name = wx.TextCtrl(self, size=(150, -1))
        # The color chooser
        self.colorpicker = colourselect.ColourSelect(self)
        # The visible check box
        self.chb_visible = wx.CheckBox(self)
        # Setup layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        # Grid for controls
        field_grid = wx.FlexGridSizer(3, 2, BORDER, BORDER)
        field_grid.Add(wx.StaticText(self, label=_("Name:")),
                       flag=wx.ALIGN_CENTER_VERTICAL)
        field_grid.Add(self.txt_name)
        field_grid.Add(wx.StaticText(self, label=_("Color:")),
                       flag=wx.ALIGN_CENTER_VERTICAL)
        field_grid.Add(self.colorpicker)
        field_grid.Add(wx.StaticText(self, label=_("Visible:")),
                       flag=wx.ALIGN_CENTER_VERTICAL)
        field_grid.Add(self.chb_visible)
        vbox.Add(field_grid, flag=wx.EXPAND|wx.ALL, border=BORDER)
        # Buttons
        button_box = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self._btn_ok_on_click, id=wx.ID_OK)
        vbox.Add(button_box, flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.SetSizerAndFit(vbox)
        _set_focus_and_select(self.txt_name)

    def _btn_ok_on_click(self, e):
        try:
            name = self.txt_name.GetValue().strip()
            if not self._name_valid(name):
                msg = _("Category name '%s' not valid. Must be non-empty.")
                _display_error_message(msg % name, self)
                return
            if self._name_in_use(name):
                msg = _("Category name '%s' already in use.")
                _display_error_message(msg % name, self)
                return
            self.category.name = name
            self.category.color = self.colorpicker.GetColour()
            self.category.visible = self.chb_visible.IsChecked()
            if self.create_new:
                self.timeline.add_category(self.category)
            else:
                self.timeline.save_category(self.category)
            self.EndModal(wx.ID_OK)
        except TimelineIOError, e:
            _display_error_message(e.message, self)
            self.error = e
            self.EndModal(ID_ERROR)

    def _name_valid(self, name):
        return len(name) > 0

    def _name_in_use(self, name):
        for cat in self.timeline.get_categories():
            if cat != self.category and cat.name == name:
                return True
        return False
