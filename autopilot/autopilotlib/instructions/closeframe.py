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


from autopilotlib.instructions.instruction import Instruction
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
            
    def _close_frame(self, win):
        win, name = self.find_win(win, "wxFrame", self._get_name())
        self._close(win, name)
        
    def _get_name(self):
        return self.arg(CloseFrameInstruction.TARGET)
    
    def _close(self, win, name):
        try:
            win.Destroy()
            Logger.add_result("Frame(%s) closed" % name)
        except:
            Logger.add_error("Frame(%s) not found" % name)        
