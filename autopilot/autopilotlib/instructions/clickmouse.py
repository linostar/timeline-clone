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


class ClickMouseInstruction(Instruction):
    """
        0        1       2  3  4  5  6
        command  object  (  x  ,  y  )
        
        command ::=  Click
        object  ::=  Mouse
        x, y    ::=  NUM
        
        X, y is measured relative the position of the active window and are
        expressed in pixels.s
        
        Example 1:   Click Mouse (100,200)
    """    
    
    TARGET_X = 3
    TARGET_Y = 5
    
    def position(self, dialog):
        x, y = dialog.GetPosition()
        return (x + int(self.tokens[ClickMouseInstruction.TARGET_X].lexeme),
                y + int(self.tokens[ClickMouseInstruction.TARGET_Y].lexeme))

    def execute(self, manuscript, win):
        Instruction.execute(self, manuscript, win)
        win.click_mouse(self.position(win))
