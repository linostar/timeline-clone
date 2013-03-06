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


class EnterTextInstruction(Instruction):
    """
        0        1       2  3  4  5    6
        command  object  (  n  ,  text )
        
        command ::=  Enter
        object  ::=  Text
        pos     ::=  NUM
        text    ::=  STRING | TEXT
        
        n     Indicates the n:th text field in the dialog. n starts with 1.
        
        Example 1:   Enter text(1, "2013-10-12")
        Example 2:   Enter text(2, myname)
    """    

    POS_TARGET = 3    
    TXT_TARGET = 5
    
    def execute(self, manuscript, win):
        Instruction.execute(self, manuscript, win)
        win.enter_text(self._pos(), self._text())

    def _pos(self):
        return int(self.tokens[EnterTextInstruction.POS_TARGET].lexeme)

    def _text(self):
        text = self.tokens[EnterTextInstruction.TXT_TARGET].lexeme
        if text.startswith('"'):
            text = text[1:-1]
        return text
    
