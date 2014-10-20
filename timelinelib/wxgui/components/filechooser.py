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


class FileChooser(wx.Panel):

    BORDER = 1

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self._create_gui()

    def _create_gui(self):
        self._create_path_text_field()
        self._create_browse_button()
        self._layout_components()

    def _create_path_text_field(self):
        self._path_text_field = wx.TextCtrl(self)

    def _create_browse_button(self):
        self._browse_button = wx.Button(self, wx.ID_OPEN)

    def _layout_components(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self._path_text_field,
                  proportion=1,
                  flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,
                  border=self.BORDER)
        sizer.Add(self._browse_button,
                  proportion=0,
                  flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,
                  border=self.BORDER)
        self.SetSizer(sizer)
