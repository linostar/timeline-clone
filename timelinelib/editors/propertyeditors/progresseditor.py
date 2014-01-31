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


class ProgressEditorGuiCreator(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self._create_gui()

    def _create_gui(self):
        self.progress = wx.SpinCtrl(self, size=(50, -1))
        self.progress.SetRange(0, 100)
        label = wx.StaticText(self, label=_("Progress %:"))
        sizer = wx.GridBagSizer(10, 10)
        sizer.Add(label, wx.GBPosition(1, 0), wx.GBSpan(1, 1))
        sizer.Add(self.progress, wx.GBPosition(1, 1), wx.GBSpan(1, 1))
        self.SetSizerAndFit(sizer)


class ProgressEditor(ProgressEditorGuiCreator):

    def __init__(self, parent, editor):
        ProgressEditorGuiCreator.__init__(self, parent)
        self.editor = editor

    def get_data(self):
        return self.progress.GetValue()

    def set_data(self, data):
        self.progress.SetValue(data)
