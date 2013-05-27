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

from timelinelib.editors.setcategory import SetCategoryEditor
from timelinelib.wxgui.components.categorychoice import CategoryChoice
from timelinelib.wxgui.utils import BORDER


class CategoryEditorGuiCreator(object):
    
    def _create_gui(self):
        properties_box = self._create_properties_box()
        self._create_buttons(properties_box)
        self.SetSizerAndFit(properties_box)
        self.lst_category.select(None)

    def _create_properties_box(self):
        properties_box = wx.BoxSizer(wx.VERTICAL)
        self._create_propeties_controls(properties_box)
        return properties_box

    def _create_propeties_controls(self, sizer):
        main_box_content = wx.BoxSizer(wx.VERTICAL)
        self._create_detail_content(main_box_content)
        sizer.Add(main_box_content, flag=wx.EXPAND|wx.ALL,
                           border=BORDER, proportion=1)

    def _create_detail_content(self, properties_box_content):
        details = self._create_details()
        properties_box_content.Add(details, flag=wx.ALL|wx.EXPAND,
                                   border=BORDER)

    def _create_details(self):
        grid = wx.FlexGridSizer(4, 2, BORDER, BORDER)
        grid.AddGrowableCol(1)
        self._create_categories_listbox(grid)
        return grid

    def _create_categories_listbox(self, grid):
        self.lst_category = CategoryChoice(self, self.timeline)
        label = wx.StaticText(self, label=_("Select a Category:"))
        grid.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.lst_category)
        self.Bind(wx.EVT_CHOICE, self.lst_category.on_choice, self.lst_category)

    def _create_buttons(self, properties_box):
        button_box = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self._btn_ok_on_click, id=wx.ID_OK)
        properties_box.Add(button_box, flag=wx.EXPAND|wx.ALL, border=BORDER)

    
class SetCategoryEditorDialog(wx.Dialog, CategoryEditorGuiCreator):

    
    def __init__(self, parent, timeline, view_properties=None):
        TITLE = _("Set Category on events without category")
        wx.Dialog.__init__(self, parent, title=TITLE, name="set_category_editor",
                           style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.timeline = timeline
        self._create_gui()
        self.controller = SetCategoryEditor(self, timeline, view_properties)

    def get_category(self):
        return self.lst_category.get()
        
    def close(self):
        self.EndModal(wx.ID_OK)

    def cancel(self):
        self.EndModal(wx.ID_CANCEL)

    def _btn_ok_on_click(self, evt):
        self.controller.save()
