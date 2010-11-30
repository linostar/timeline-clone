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

from timelinelib.utils import ex_msg
from timelinelib.gui.utils import BORDER
from timelinelib.gui.utils import _display_error_message
from timelinelib.gui.components.numtimepicker import NumTimePicker


class GotoNumTimeDialog(wx.Dialog):

    def __init__(self, parent, time):
        wx.Dialog.__init__(self, parent, title=_("Go to Time"))
        self._create_gui()
        self.controller = GotoNumTimeDialogController(self, time)
        self.controller.initialize()

    def set_time(self, time):
        self.time_picker.set_value(time)
        
    def select_all(self):
        self.time_picker.select_all()

    def get_time(self):
        return self.time_picker.get_value()
        
    def close(self):
        self.EndModal(wx.ID_OK)        
        
    def _create_gui(self):
        self.time_picker = NumTimePicker(self)
        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.time_picker, flag=wx.EXPAND|wx.RIGHT|wx.BOTTOM|wx.LEFT,
                 border=BORDER, proportion=1)
        self.Bind(wx.EVT_BUTTON, self._btn_ok_on_click, id=wx.ID_OK)
        button_box = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        vbox.Add(button_box, flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.time_picker.SetFocus()
        self.SetSizerAndFit(vbox)

    def _btn_ok_on_click(self, e):
        self.controller.btn_ok_clicked()
        

class GotoNumTimeDialogController(object):

    def __init__(self, view,time):
        self.view = view
        self.time = time
        
    def initialize(self):
        self.view.set_time(self.time)
        self.view.select_all()
        
    def btn_ok_clicked(self):
        try:
            self.time = self.view.get_time()
        except ValueError, ex:
            _display_error_message(ex_msg(ex))
        else:
            self.view.close()
        