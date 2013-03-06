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

from autopilotlib.instructions.instruction import Instruction
from autopilotlib.app.logger import Logger


class CloseDialogInstruction(Instruction):
    """
        0        1          2  3       4
        command  object  [  (  target  )  ]?
        
        command ::=  Close
        object  ::=  Dialog
        target  ::=  STRING | TEXT
        
        Closes a modal dialog. If no target name is given the dialog to close
        is assumed to be the current window.
        
        Example 1:   Close Dialog("Create Event")
        Example 2:   Close Dialog
    """    

    TARGET = 3
    
    def execute(self, manuscript, win):
        Instruction.execute(self, manuscript, win)
        self._close_dialog(win)
    
    def _close_dialog(self, win):
        win, name = self.find_win(win, "wxDialog", self._get_name())
        self._close(win, name)
        
    def _get_name(self):
        return self.arg(CloseDialogInstruction.TARGET)
    
    def _close(self, win, name):
        try:
            win.EndModal(wx.ID_CANCEL)
            Logger.add_result("Dialog(%s) closed" % name)
        except:
            Logger.add_error("Dialog(%s) not found" % name)        

