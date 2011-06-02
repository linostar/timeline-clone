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


from timelinelib.wxgui.utils import BORDER

import wx


class TextDisplayDialog(wx.Dialog):

    def __init__(self, title, text, parent=None):
        wx.Dialog.__init__(self, parent, title=title)
        self._create_gui()
        self._text.SetValue(text)

    def _create_gui(self):
        self._text = wx.TextCtrl(self, size=(660, 300), style=wx.TE_MULTILINE)
        btn_copy = wx.Button(self, wx.ID_COPY)
        self.Bind(wx.EVT_BUTTON, self._btn_copy_on_click, btn_copy)
        btn_close = wx.Button(self, wx.ID_CLOSE)
        btn_close.SetDefault()
        btn_close.SetFocus()
        self.SetAffirmativeId(wx.ID_CLOSE)
        self.Bind(wx.EVT_BUTTON, self._btn_close_on_click, btn_close)
        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self._text, flag=wx.ALL|wx.EXPAND, border=BORDER)
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        button_box.Add(btn_copy, flag=wx.RIGHT, border=BORDER)
        button_box.AddStretchSpacer()
        button_box.Add(btn_close, flag=wx.LEFT, border=BORDER)
        vbox.Add(button_box, flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.SetSizerAndFit(vbox)
        
    def _btn_copy_on_click(self, evt):
        if wx.TheClipboard.Open():
            obj = wx.TextDataObject(self._text.GetValue())
            wx.TheClipboard.SetData(obj)
            wx.TheClipboard.Close()
        else:
            msg = _("Unable to copy to clipboard.")
            _display_error_message(msg)

    def _btn_close_on_click(self, evt):
        self.Close()
