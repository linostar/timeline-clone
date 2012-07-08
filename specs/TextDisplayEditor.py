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


import unittest
from mock import Mock

from timelinelib.wxgui.dialogs.textdisplay import TextDisplayDialog
from timelinelib.editors.textdisplay import TextDisplayEditor

class TextDisplayEditorSpec(unittest.TestCase):

    def test_set_text_sets_dialog_text(self):
        text = "aha"
        self.editor.set_text(text)
        self.view.set_text.assert_called_with(text)

    def test_initialization_sets_dialog_text(self):
        self.editor.initialize()
        self.view.set_text.assert_called_with(self.text)

    def test_get_text_returns_dialog_text(self):
        self.view.get_text.return_value = "foo"
        self.editor.initialize()
        text = self.editor.get_text()
        self.assertEqual("foo", text) 

    def test_get_text_returns_dialog_text2(self):
        self.view.get_text.return_value = "foo2"
        self.editor.initialize()
        text = self.editor.get_text()
        self.assertEqual("foo2", text) 

    def setUp(self):
        self.text = "buu"
        self.view = Mock(TextDisplayDialog)
        self.editor = TextDisplayEditor(self.view, self.text)
