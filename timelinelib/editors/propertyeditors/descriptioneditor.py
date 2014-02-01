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

from timelinelib.editors.propertyeditors.baseeditor import BaseEditor


class DescriptionEditor(BaseEditor, wx.TextCtrl):

    def __init__(self, parent, editor):
        BaseEditor.__init__(self, editor)
        self.data = self
        wx.TextCtrl.__init__(self, parent, style=wx.TE_MULTILINE)
        self.Bind(wx.EVT_CHAR, self._on_char)

    def get_data(self):
        description = self.GetValue().strip()
        if description != "":
            return description
        return None

#     def set_data(self, data):
#         self.SetValue(data)

    def clear_data(self):
        self.SetValue("")

    def _on_char(self, evt):
        if self._ctrl_a(evt):
            self.SelectAll()
        else: 
            evt.Skip()
        
    def _ctrl_a(self, evt):
        KEY_CODE_A = 1
        return evt.ControlDown() and evt.KeyCode == KEY_CODE_A
