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
from autopilotlib.app.constants import TIME_TO_WAIT_FOR_DIALOG_TO_SHOW_IN_MILLISECONDS
import autopilotlib.manuscript.scanner as scanner


class MenuNotFoundException():
    pass


class SelectMenuInstruction(Instruction):
    """
        0        1       2  3        4  5        6  7
        command  object  (  target1  ,  target2  ,  target3  )
        
        command ::=  Select
        object  ::=  Menu | Mnu
        target  ::=  STRING | TEXT 
        
        Example 1:   Select menu (Show, Sidebar)
        Example 2:   Select menu (Show, "Balloons on hover")
        
        At least 2 targets must be present.
    """    
        
    def __init__(self, tokens):
        Instruction.__init__(self, tokens)
        
    def execute(self, manuscript, win=None):
        try:
            item_id = self._find_menu_item_id()
            self._continue_instruction_loop(manuscript)
            Logger.add_result("Menu selected")
            self._click_menu_item(manuscript, item_id)    
        except MenuNotFoundException:
            Logger.add_error("Menu not found")
            manuscript.execute_next_instruction()
            
    def _labels(self):
        labels = []
        for token in self.tokens:
            if token.id == scanner.ID:
                labels.append(token.lexeme)
            elif token.id == scanner.STRING:
                labels.append(token.lexeme[1:-1])
        return labels
    
    def _continue_instruction_loop(self, manuscript):
        wx.CallLater(TIME_TO_WAIT_FOR_DIALOG_TO_SHOW_IN_MILLISECONDS,
                     manuscript.execute_next_instruction)
        
    def _click_menu_item(self, manuscript, item_id):
        wx.GetActiveWindow().ProcessCommand(item_id)

    def _find_menu_item_id(self):
        labels = self._labels()
        menu_bar = self._get_menu_bar()
        item_id = self.get_item_id(menu_bar, labels[0], labels[1])
        labels = labels [2:]
        while len(labels) > 0:
            menu_item = menu_bar.FindItemById(item_id)
            submenu = menu_item.GetSubMenu()
            item_id = submenu.FindItem(labels[0])
            if item_id == wx.NOT_FOUND:
                raise MenuNotFoundException()
            labels = labels [1:]
        return item_id

    def get_item_id(self, menu_bar, label1, label2):
        item_id = menu_bar.FindMenuItem(label1, label2)
        if item_id == wx.NOT_FOUND:
            # Try with elipses
            item_id = menu_bar.FindMenuItem(label1, label2 + "...")
        if item_id == wx.NOT_FOUND:
            # Try with accelerator
            for i in range(len(label2)):
                label = label2[0:i] + "&" + label2[i:]
                item_id = menu_bar.FindMenuItem(label1, label)
                if item_id != wx.NOT_FOUND:
                    break;
        if item_id == wx.NOT_FOUND:
            raise MenuNotFoundException()
        return item_id

    def get_submenuitem_id(self, submenu, label):
        item_id = submenu.FindMenuItem(label)
        if item_id == wx.NOT_FOUND:
            # Try with elipses
            item_id = submenu.FindMenuItem(label + "...")
        if item_id == wx.NOT_FOUND:
            # Try with accelerator
            for i in range(len(label)):
                lbl = label[0:i] + "&" + label[i:]
                item_id = submenu.FindMenuItem(lbl)
                if item_id != wx.NOT_FOUND:
                    break;
        if item_id == wx.NOT_FOUND:
            raise MenuNotFoundException()
        return item_id
        
    def _get_menu_bar(self):
        menu_bar = wx.GetActiveWindow().GetMenuBar()
        if menu_bar is None:
            raise MenuNotFoundException()
        return menu_bar
