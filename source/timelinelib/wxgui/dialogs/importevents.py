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


import os.path

import wx

from timelinelib.db.exceptions import TimelineIOError
from timelinelib.db import db_open
from timelinelib.wxgui.components.filechooser import FileChooser
from timelinelib.wxgui.utils import BORDER
from timelinelib.wxgui.utils import handle_db_error
from timelinelib.wxgui.utils import WildcardHelper


class ImportDialog(wx.Dialog):

    def __init__(self, db, parent=None):
        wx.Dialog.__init__(self, parent, title=_("Import events"))
        self._db = db
        self._create_gui()
        self._show_preview()

    def _create_gui(self):
        self._create_header()
        self._create_file_chooser()
        self._create_preview_text()
        self._create_buttons()
        self._layout_components()

    def _create_header(self):
        self._header = Header(self, label=_("Select timeline to import from:"))

    def _create_file_chooser(self):
        self._file_chooser = FileChooser(
            self,
            dialog_wildcard=WildcardHelper(
                _("Timeline files"), ["timeline", "ics"]).wildcard_string())
        self._file_chooser.Bind(FileChooser.EVT_FILE_PATH_CHANGED,
                                self._on_file_path_changed)

    def _on_file_path_changed(self, evt):
        self._show_preview()

    def _create_preview_text(self):
        self._preview_text = FeedbackText(self, size=(300, 70))

    def _create_buttons(self):
        self._buttons = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self._on_button_ok_clicked, id=wx.ID_OK)

    def _layout_components(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._header, flag=wx.ALL|wx.EXPAND, border=BORDER)
        sizer.Add(self._file_chooser, flag=wx.ALL|wx.EXPAND, border=BORDER)
        sizer.Add(self._preview_text, flag=wx.ALL|wx.EXPAND, border=BORDER)
        sizer.Add(self._buttons, flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.SetSizerAndFit(sizer)

    def _show_preview(self):
        if not os.path.exists(self._file_chooser.GetFilePath()):
            self._set_error(_("File does not exist."))
        else:
            try:
                db_to_import = db_open(self._file_chooser.GetFilePath())
            except Exception, e:
                self._set_error(_("Unable to load events: %s.") % str(e))
            else:
                if db_to_import.get_time_type() != self._db.get_time_type():
                    self._set_error(_("The selected timeline has a different time type."))
                else:
                    self._set_success(db_to_import, _("%d events will be imported." % len(db_to_import.get_all_events())))

    def _on_button_ok_clicked(self, evt):
        if not self._db_to_import:
            return
        try:
            self._db.import_db(self._db_to_import)
        except TimelineIOError, e:
            handle_db_error(e)
        else:
            self.Close()

    def _set_success(self, db_to_import, text):
        self._db_to_import = db_to_import
        self._preview_text.SetSuccess(text)
        self.GetSizer().Layout()

    def _set_error(self, text):
        self._db_to_import = None
        self._preview_text.SetError(text)
        self.GetSizer().Layout()


class Header(wx.StaticText):

    def __init__(self, *args, **kwargs):
        wx.StaticText.__init__(self, *args, **kwargs)
        font = self.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.SetFont(font)


class FeedbackText(wx.StaticText):

    def SetError(self, text):
        self.SetForegroundColour((255, 0, 0))
        self.SetLabel(text)

    def SetSuccess(self, text):
        self.SetForegroundColour((0, 0, 0))
        self.SetLabel(text)
