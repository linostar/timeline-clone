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


class ClickButtonInstruction(Instruction):
    """
        0        1       2  3       4
        command  object  (  target  )
        
        command ::=  Click
        object  ::=  Button | Btn
        target  ::=  STRING | TEXT | NUM
        
        Example 1:   Click Button (OK)
        Example 2:   Click Btn ("Save as...")
        Example 3:   Click Button(2)   
    """    
    
    TARGET = 3
    
    def label(self):
        return self.arg(ClickButtonInstruction.TARGET)
    
    def execute(self, manuscript, dialog):
        Instruction.execute(self, manuscript, dialog)
        dialog.click_button(self.label())
