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


class CloseDialogInstruction(Instruction):
    
    def __init__(self, tokens):
        Instruction.__init__(self, tokens)
        
    def label(self):
        for token in self.tokens:
            if token.id == scanner.ID:
                return token.lexeme
        return ""
    
    def execute(self, manuscript, dialog):
        wx.CallLater(500, manuscript.execute_next_instruction)
        #dialog.Destroy()
        dialog.click_button("OK")
        

