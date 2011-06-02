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


import sys

import wx

from timelinelib.wxgui.dialogs.mainframe import MainFrame
from timelinelib.wxgui.dialogs.textdisplay import TextDisplayDialog
from timelinelib.unhandledex import create_error_message


def start_wx_application(application_arguments, before_main_loop_hook=None):
    app = wx.PySimpleApp()
    main_frame = MainFrame(application_arguments)
    main_frame.Show()
    sys.excepthook = unhandled_exception_hook
    if before_main_loop_hook:
        before_main_loop_hook()
    app.MainLoop()


def unhandled_exception_hook(type, value, tb):
    title = "Unexpected Error"
    text = create_error_message(type, value, tb)
    dialog = TextDisplayDialog(title, text)
    dialog.ShowModal()
    dialog.Destroy()
