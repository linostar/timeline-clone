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


import os.path

import wx

from timelinelib.wxgui.components.filechooser import FileChooser
from timelinelib.wxgui.utils import BORDER


class ImportDialog(wx.Dialog):

    def __init__(self, parent=None):
        wx.Dialog.__init__(self, parent, title=_("Import events"))
        self._create_gui()

    def _create_gui(self):
        self._create_file_chooser()
        self._create_preview_text()
        self._create_buttons()
        self._layout_components()
        self._show_preview()

    def _create_file_chooser(self):
        self._file_chooser = FileChooser(self)
        self._file_chooser.Bind(FileChooser.EVT_FILE_PATH_CHANGED,
                                self._on_file_path_changed)

    def _on_file_path_changed(self, evt):
        self._show_preview()

    def _create_preview_text(self):
        self._preview_text = wx.StaticText(self, size=(300, 100))

    def _create_buttons(self):
        self._buttons = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)

    def _layout_components(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._file_chooser, flag=wx.ALL|wx.EXPAND, border=BORDER)
        sizer.Add(self._preview_text, flag=wx.ALL|wx.EXPAND, border=BORDER)
        sizer.Add(self._buttons, flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.SetSizerAndFit(sizer)

    def _show_preview(self):
        if not os.path.exists(self._file_chooser.GetFilePath()):
            self._preview_text.SetLabel("file does not exist")
        else:
            self._preview_text.SetLabel("OK")
