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


import wx

from timelinelib.gui.utils import BORDER
from timelinelib.gui.utils import _display_error_message
from timelinelib.gui.components.datetimepicker import DateTimePicker
from timelinelib.utils import ex_msg


class GotoDateDialog(wx.Dialog):

    def __init__(self, parent, time):
        wx.Dialog.__init__(self, parent, title=_("Go to Date"))
        self._create_gui()
        self.dtpc.set_value(time)

    def _create_gui(self):
        self.dtpc = DateTimePicker(self)
        checkbox = wx.CheckBox(self, label=_("Show time"))
        checkbox.SetValue(False)
        self.dtpc.show_time(checkbox.IsChecked())
        self.Bind(wx.EVT_CHECKBOX, self._chb_show_time_on_checkbox, checkbox)
        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(checkbox, flag=wx.LEFT|wx.TOP|wx.RIGHT,
                 border=BORDER, proportion=1)
        vbox.Add(self.dtpc, flag=wx.EXPAND|wx.RIGHT|wx.BOTTOM|wx.LEFT,
                 border=BORDER, proportion=1)
        self.Bind(wx.EVT_BUTTON, self._btn_ok_on_click, id=wx.ID_OK)
        button_box = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        vbox.Add(button_box, flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.dtpc.SetFocus()
        self.SetSizerAndFit(vbox)

    def _chb_show_time_on_checkbox(self, e):
        self.dtpc.show_time(e.IsChecked())

    def _btn_ok_on_click(self, e):
        try:
            self.time = self.dtpc.get_value()
        except ValueError, ex:
            _display_error_message(ex_msg(ex))
        else:
            self.EndModal(wx.ID_OK)
