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

import timelinelib.config as config
from timelinelib.gui.utils import BORDER


class PreferencesDialog(wx.Dialog):
    """
    Dialog used to edit application preferences.

    This is essentially a GUI for parts of the preferences in the config
    module.
    """

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title=_("Preferences"))
        self._create_gui()

    def _create_gui(self):
        notebook = wx.Notebook(self, style=wx.BK_DEFAULT)
        # General tab
        panel = wx.Panel(notebook)
        notebook.AddPage(panel, _("General"))
        sizer = wx.BoxSizer(wx.VERTICAL)
        chb_open_recent_startup = wx.CheckBox(panel, label=_("Open most recent timeline on startup"))
        chb_open_recent_startup.SetValue(config.get_open_recent_at_startup())
        self.Bind(wx.EVT_CHECKBOX, self._chb_open_recent_startup_on_checkbox,
                  chb_open_recent_startup)
        sizer.Add(chb_open_recent_startup, border=BORDER, flag=wx.ALL)
        panel.SetSizer(sizer)
        # The close button
        btn_close = wx.Button(self, wx.ID_CLOSE)
        btn_close.SetDefault()
        btn_close.SetFocus()
        self.SetAffirmativeId(wx.ID_CLOSE)
        self.Bind(wx.EVT_BUTTON, self._btn_close_on_click, btn_close)
        # Layout
        main_box = wx.BoxSizer(wx.VERTICAL)
        main_box.Add(notebook, border=BORDER, flag=wx.ALL|wx.EXPAND,
                     proportion=1)
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        button_box.AddStretchSpacer()
        button_box.Add(btn_close, flag=wx.LEFT, border=BORDER)
        main_box.Add(button_box, flag=wx.ALL|wx.EXPAND, border=BORDER)
        # Realize
        self.SetSizerAndFit(main_box)

    def _chb_open_recent_startup_on_checkbox(self, evt):
        config.set_open_recent_at_startup(evt.IsChecked())

    def _btn_close_on_click(self, e):
        self.Close()
