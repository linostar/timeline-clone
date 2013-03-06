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


class HideFrameInstruction(Instruction):
    """
        0        1         2  3       4
        command  object [  (  target  )   ]?
        
        command ::=  Hide
        object  ::=  Frame
        target  ::=  STRING | TEXT 
        
        Example 1:   Hide Frame(Help)
        Example 2:   Hide Frame
    """       
    
    TARGET = 3
    
    def execute(self, manuscript, win=None):
        Instruction.execute(self, manuscript, win)
        self._hide_frame(win)
        
    def _get_name_of_dialog(self):
        return self.arg(HideFrameInstruction.TARGET)
    
    def _hide_frame(self, win):
        frame, frame_name = self._find_dialog(win)
        self._hide(frame, frame_name)
        
    def _find_dialog(self, win):
        try:
            frame_name = self._get_name_of_dialog()
            frame = self._find_frame_by_name(frame_name)
        except:
            frame_name = win.GetLabel()
            frame = self._find_dialog_from_input(win)
        return frame, frame_name
    
    def _find_frame_by_name(self, frame_name):
        wins = wx.GetTopLevelWindows()
        for frame in wins:
            if frame.ClassName == "wxFrame" and frame.GetLabel() == frame_name:
                return frame

    def _find_dialog_from_input(self, win):
        if win.ClassName == "wxFrame":
            return win
        
    def _hide(self, frame, frame_name):
        try:
            frame.Hide()
            Logger.add_result("Frame(%s) hidden" % frame_name)
        except:
            Logger.add_error("Frame(%s) not found" % frame_name)
        