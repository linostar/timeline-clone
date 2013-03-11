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
from autopilotlib.app.logger import Logger
from autopilotlib.wrappers.wrapper import Wrapper
import autopilotlib.guinatives.facade as win
from autopilotlib.app.constants import TIME_TO_WAIT_FOR_DIALOG_TO_SHOW_IN_MILLISECONDS
from autopilotlib.guinatives.facade import get_window_text


wxMessageBox = wx.MessageBox


def MessageBox(*args, **kw):
    Logger.add_result("MessageBox '%s' opened" % args[1])
    wx.CallLater(TIME_TO_WAIT_FOR_DIALOG_TO_SHOW_IN_MILLISECONDS, _save_hwnd)
    rv =  wxMessageBox(*args, **kw)
    Logger.add_result("MessageBox '%s' closed" % args[1])
    return rv
        
def _save_hwnd():
    hwnd = win.get_active_window()
    wrapper = Wrapper()
    wrapper.hwnd = win.get_active_window()
    wrapper._explore(None)
    wrapper.messagebox = True
    MessageBox.listener(wrapper)
        
def wrap(listener):
    wx.MessageBox = MessageBox
    MessageBox.listener = listener
