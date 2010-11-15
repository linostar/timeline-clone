# Copyright (C) 2009, 2010  Rickard Lindberg, Roger Lindberg
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

from timelinelib.gui.dialogs.gotonumtime import GotoNumTimeDialog
from timelinelib.gui.dialogs.gotonumtime import GotoNumTimeDialogController
from timelinelib.time import NumTimeType


class goto_numtime_dialog_spec_base(unittest.TestCase):
    
    def setUp(self):
        self.controller = GotoNumTimeDialogController(self._create_view_mock(),
                                                      1)

    def _create_view_mock(self):
        self.view = Mock(GotoNumTimeDialog)
        return self.view


class a_newly_initialized_dialog(goto_numtime_dialog_spec_base):

    def setUp(self):
        goto_numtime_dialog_spec_base.setUp(self)
        self.controller.initialize()            
        
    def test_time_should_be_1(self):
        self.view.set_time.assert_called_with(1)


class a_dialog_with_time_changed_to_560_when_ok_cliked(goto_numtime_dialog_spec_base):

    def setUp(self):
        goto_numtime_dialog_spec_base.setUp(self)
        self.controller.initialize() 
        self.view.get_time.return_value = 560 
        self.controller.btn_ok_clicked()
        
    def test_time_should_be_560(self):
        self.assertEqual(self.controller.time, 560)
        
    def test_the_dialog_should_close(self):
        self.assertTrue(self.view.close.assert_called)        
