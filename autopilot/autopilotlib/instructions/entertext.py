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


class EnterTextInstruction(Instruction):
    
    def __init__(self, tokens):
        Instruction.__init__(self, tokens)
        
    def index(self):
        return int(self.tokens[3].lexeme)

    def text(self):
        text = self.tokens[5].lexeme
        if text.startswith('"'):
            text = text[1:-1]
        return text
    
    def execute(self, manuscript, dialog):
        wx.CallLater(500, manuscript.execute_next_instruction)
        dialog.enter_text(self.index(), self.text())