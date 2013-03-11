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


import autopilotlib.manuscript.scanner as scanner
from autopilotlib.app.logger import Logger
from autopilotlib.instructions.exit import ExitInstruction
from autopilotlib.instructions.clickbutton import ClickButtonInstruction
from autopilotlib.instructions.clickmouse import ClickMouseInstruction
from autopilotlib.instructions.selectmenu import SelectMenuInstruction
from autopilotlib.instructions.include import IncludeInstruction
from autopilotlib.instructions.comment import CommentInstruction
from autopilotlib.instructions.closeframe import CloseFrameInstruction
from autopilotlib.instructions.closedialog import CloseDialogInstruction
from autopilotlib.instructions.hideframe import HideFrameInstruction
from autopilotlib.instructions.entertext import EnterTextInstruction
from autopilotlib.instructions.selectcustomtreecontrol import SelectCustomTreeControlInstruction
from autopilotlib.instructions.selectcombobox import SelectComboboxInstruction


class InstructionSyntaxException():
    pass

 
def create_instruction(text):
    tokens = scanner.scan_instruction(text)
    
    if len(tokens) == 0:
        return None
    
    if tokens[0].id != scanner.KEYWORD:
        return None
    
    if tokens[0].subid == scanner.ID_INCLUDE:
        return IncludeInstruction(tokens)
    
    if tokens[0].subid == scanner.ID_EXIT:
        return ExitInstruction(tokens) 

    if tokens[0].subid == scanner.ID_COMMENT:
        return CommentInstruction(tokens) 

    if tokens[0].subid == scanner.ID_SELECT:
        if tokens[1].lexeme.lower() == "menu":
            syntaxcheck_select_menu_instruction(tokens)
            return SelectMenuInstruction(tokens) 
        elif tokens[1].lexeme.lower() == "customtreecontrol":
            return SelectCustomTreeControlInstruction(tokens) 
        elif tokens[1].lexeme.lower() == "combobox":
            return SelectComboboxInstruction(tokens) 
        else:
            raise InstructionSyntaxException()

    if tokens[0].subid == scanner.ID_ENTER:
        if tokens[1].lexeme.lower() == "text":
            return EnterTextInstruction(tokens) 
        else:
            raise InstructionSyntaxException()
        
    if tokens[0].subid == scanner.ID_CLOSE:
        if tokens[1].lexeme.lower() == "frame":
            return CloseFrameInstruction(tokens) 
        elif tokens[1].lexeme.lower() == "dialog":
            return CloseDialogInstruction(tokens) 
        elif tokens[1].lexeme.lower() == "application":
            return ExitInstruction(tokens) 
        else:
            raise InstructionSyntaxException()
        
    if tokens[0].subid == scanner.ID_HIDE:
        if tokens[1].lexeme.lower() == "frame":
            return HideFrameInstruction(tokens) 
        else:
            raise InstructionSyntaxException()
        
    if tokens[0].subid == scanner.ID_CLICK: 
        if tokens[1].lexeme.lower() == "button":
            return ClickButtonInstruction(tokens) 
        if tokens[1].lexeme.lower() == "mouse":
            return ClickMouseInstruction(tokens) 
        else:
            raise InstructionSyntaxException()


def syntaxcheck_select_menu_instruction(tokens):
    """
    State token-id  token-subid  Next State
    ----- --------  -----------  ----------
    """
    STATES = (
      (0,   scanner.KEYWORD,   scanner.ID_SELECT, 1),
      (1,   scanner.KEYWORD,   scanner.ID_MENU,   2),
      (2,   scanner.LP,        None,              3),
      (3,   scanner.ID,        None,              4),
      (3,   scanner.STRING,    None,              4),
      (4,   scanner.COMMA,     None,              5),
      (5,   scanner.ID,        None,              6),
      (5,   scanner.STRING,    None,              6),
      (6,   scanner.RP,        None,             -1),
      (6,   scanner.COMMA,     None,              5),      
      
    )
    validate(tokens, STATES)


def validate(tokens, states):
    state = 0
    i = 0
    while state != -1:
        state = next_state(state, states, tokens[i])
        i += 1
    
def next_state(current_state, states, token):
    transitions = [state for state in states if state[0] == current_state]
    for state, id, subid, next_state in transitions:
        if token.id == id:
            if subid == None or subid == token.subid:
                return next_state
    raise InstructionSyntaxException()    