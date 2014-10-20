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


from specs.utils import WxComponentTest
from timelinelib.wxgui.dialogs.importevents import ImportDialog


class ImportDialogTest(WxComponentTest):

    HALT_FOR_MANUAL_INSPECTION = False

    def test_shows_up(self):
        self.add_separator()
        self.add_button("Open import dialog", self._on_open_import_dialog_click)
        self.add_separator()
        self.show_test_window()

    def _on_open_import_dialog_click(self):
        dialog = ImportDialog()
        dialog.ShowModal()
        dialog.Destroy()
