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
import autopilotlib.manuscript.scanner as scanner
from autopilotlib.app.logger import Logger


class CloseFrameInstruction(Instruction):
    """
        0        1          2  3       4
        command  object  [  (  target  )  ]?
        
        command ::=  Close
        object  ::=  Frame
        target  ::=  STRING | TEXT
        
        Closes a frame window. If no target name is given the frame to close
        is assumed to be the current window.
        
        Example 1:   Close Frame
        Example 2:   Close Frame(Help)
    """    

    TARGET = 3    
        
    def execute(self, manuscript, win=None):
        Instruction.execute(self, manuscript, win)
        self._close_frame(win)

    def label(self):
        for token in self.tokens:
            if token.id == scanner.ID:
                return token.lexeme
        return ""
    
    def _get_name_of_frame(self):
        return self.arg(CloseFrameInstruction.TARGET)
    
    def _close_frame(self, win):
        frame, frame_name = self._find_frame(win)
        self._close(frame, frame_name)
        
    def _find_frame(self, win):
        try:
            frame_name = self._get_name_of_frame()
            frame = self._find_frame_by_name(frame_name)
        except:
            frame_name = win.GetLabel()
            frame = self._find_frame_from_input(win)
        return frame, frame_name
    
    def _find_frame_by_name(self, frame_name):
        wins = wx.GetTopLevelWindows()
        for frame in wins:
            if frame.ClassName == "wxFrame" and frame.GetLabel() == frame_name:
                return frame

    def _find_frame_from_input(self, win):
        if win.ClassName == "wxFrame":
            return win
        
    def _close(self, frame, frame_name):
        try:
            frame.Destroy()
            Logger.add_result("Frame(%s) closed" % frame_name)
        except:
            Logger.add_error("Frame(%s) not found" % frame_name)        
