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
from autopilotlib.app.constants import TIME_TO_WAIT_FOR_DIALOG_TO_SHOW_IN_MILLISECONDS
from autopilotlib.app.decorators import Overrides


wxDirDialog = wx.DirDialog


class DirDialog(wx.DirDialog, Wrapper):
    
    def __init__(self, *args, **kw):
        wxDirDialog.__init__(self, *args, **kw)
       
    @Overrides(wxDirDialog)
    def ShowModal(self):
        Logger.add_result("DirDialog '%s' opened" % self.GetMessage())
        wx.CallLater(TIME_TO_WAIT_FOR_DIALOG_TO_SHOW_IN_MILLISECONDS, self._register_and_explore)
        super(DirDialog, self).ShowModal()
    
    @Overrides(wxDirDialog)
    def Destroy(self, *args, **kw):
        Logger.add_result("DirDialog '%s' closed" % self.GetMessage())
        wxDirDialog.Destroy(self, *args, **kw)
    
    def _register_and_explore(self):
        DirDialog.register_win(self)
        self._explore()
        
    @classmethod
    def wrap(self, register_win):
        wx.DirDialog = DirDialog
        DirDialog.register_win = register_win
