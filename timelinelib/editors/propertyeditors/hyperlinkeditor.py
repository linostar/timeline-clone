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
import webbrowser


class HyperlinkEditor(wx.Panel):

    def __init__(self, parent, editor):
        wx.Panel.__init__(self, parent)
        self.editor = editor
        self._create_gui()
        self._initialize_data()

    def _create_gui(self):
        self._create_controls()
        self._layout_controls()

    def _initialize_data(self):
        self._set_initial_text()
        self._set_visible(False)

    def _set_initial_text(self):
        self.text_data.SetValue("")

    def _create_controls(self):
        self.btn_add = self._create_add_button()
        self.btn_clear = self._create_clear_button()
        self.btn_test = self._create_test_button()
        self.url_panel = self._create_input_controls()

    def _layout_controls(self):
        self._layout_input_controls(self.url_panel)
        sizer = wx.GridBagSizer(5, 5)
        sizer.Add(self.btn_add, wx.GBPosition(0, 0), wx.GBSpan(1, 1))
        sizer.Add(self.btn_clear, wx.GBPosition(0, 1), wx.GBSpan(1, 1))
        sizer.Add(self.btn_test, wx.GBPosition(0, 2), wx.GBSpan(1, 1))
        sizer.Add(self.url_panel, wx.GBPosition(1, 0), wx.GBSpan(4, 5))
        self.SetSizerAndFit(sizer)

    def _create_add_button(self):
        btn_add = wx.Button(self, wx.ID_ADD)
        self.Bind(wx.EVT_BUTTON, self._btn_add_on_click, btn_add)
        return btn_add

    def _create_clear_button(self):
        btn_clear = wx.Button(self, wx.ID_CLEAR)
        self.Bind(wx.EVT_BUTTON, self._btn_clear_on_click, btn_clear)
        return btn_clear

    def _create_test_button(self):
        btn_test = wx.Button(self, wx.ID_ANY, _("Test"))
        self.Bind(wx.EVT_BUTTON, self._btn_test_on_click, btn_test)
        return btn_test

    def _create_input_controls(self):
        alert_panel = wx.Panel(self)
        self.text_data = wx.TextCtrl(alert_panel, size=(300,20))
        return alert_panel

    def _layout_input_controls(self, alert_panel):
        text = wx.StaticText(alert_panel, label=_("URL:"))
        sizer = wx.GridBagSizer(5, 10)
        sizer.Add(text, wx.GBPosition(1, 0), wx.GBSpan(1, 1))
        sizer.Add(self.text_data, wx.GBPosition(1, 1), wx.GBSpan(1, 9))
        alert_panel.SetSizerAndFit(sizer)

    def get_data(self):
        if self.url_visible:
            return self.text_data.GetValue()
        else:
            return None

    def set_data(self, data):
        if data == None:
            self._set_visible(False)
        else:
            self._set_visible(True)
            self.text_data.SetValue(data)

    def _btn_add_on_click(self, evt):
        self._set_visible(True)

    def _btn_clear_on_click(self, evt):
        self.clear_data()

    def _btn_test_on_click(self, evt):
        webbrowser.open(self.get_data())

    def clear_data(self):
        self._set_initial_text()
        self._set_visible(False)

    def _set_visible(self, value):
        self.url_visible = value
        self.url_panel.Show(self.url_visible)
        self.btn_add.Enable(not value)
        self.btn_clear.Enable(value)
        self.btn_test.Enable(value)
        self.GetSizer().Layout()
