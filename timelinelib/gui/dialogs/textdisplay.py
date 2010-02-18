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


"""
Dialog for displaying a text that also can be copied.
"""


import wx


class TextDisplayDialog(wx.Dialog):
    """
    Dialog used for display of multiline text that can be selectd.
    
    Selecting the text enables copying it to the clipboard.
    """
    
    def __init__(self, title, text, parent = None):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title)
        self._create_gui()
        self._text.SetValue(text)

    def _create_gui(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        self._text = wx.TextCtrl(self, wx.ID_ANY, "", size = (660, 300), 
                                 style = wx.TE_MULTILINE)
        vbox.Add(self._text, 1, wx.ALIGN_LEFT | wx.ALL, 5)
        btnsizer = wx.StdDialogButtonSizer()
        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btn.SetFocus()
        btnsizer.AddButton(btn)
        btnsizer.Realize()
        vbox.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.SetSizer(vbox)
        vbox.Fit(self)
        self.Bind(wx.EVT_BUTTON, self._btn_close_on_click, btn)
        
    def _btn_close_on_click(self, evt):
        self.Close()