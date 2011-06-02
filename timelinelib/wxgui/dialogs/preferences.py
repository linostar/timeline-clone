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

from timelinelib.wxgui.utils import BORDER


class PreferencesDialog(wx.Dialog):
    """
    Dialog used to edit application preferences.

    This is essentially a GUI for parts of the preferences in the config
    module.
    """

    def __init__(self, parent, config):
        wx.Dialog.__init__(self, parent, title=_("Preferences"))
        self.weeks_map = ((0, "monday"), (1, "sunday"))
        self.config = config
        self._create_gui()
        self._controller = PreferencesDialogController(self, self.config)
        self._controller.initialize_controls()

    def _create_gui(self):
        main_box = self._create_main_box()
        self.SetSizerAndFit(main_box)

    def _create_main_box(self):
        notebook = self._create_nootebook_control()
        button_box = self._create_button_box()
        main_box = wx.BoxSizer(wx.VERTICAL)
        main_box.Add(notebook, border=BORDER, flag=wx.ALL|wx.EXPAND,
                     proportion=1)
        main_box.Add(button_box, flag=wx.ALL|wx.EXPAND, border=BORDER)
        return main_box

    def _create_nootebook_control(self):
        notebook = wx.Notebook(self, style=wx.BK_DEFAULT)
        self._create_general_tab(notebook)
        self._create_date_time_tab(notebook)
        return notebook
        
    def _create_button_box(self):
        btn_close = self._create_close_button()
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        button_box.AddStretchSpacer()
        button_box.Add(btn_close, flag=wx.LEFT, border=BORDER)
        return button_box
        
    def _create_general_tab(self, notebook):
        panel = self._create_tab_panel(notebook, _("General")) 
        controls = self._create_general_tab_controls(panel)
        self._size_tab_panel(panel, controls)

    def _create_general_tab_controls(self, panel):
        chb_open_recent_startup = wx.CheckBox(panel, 
                                              label=_("Open most recent timeline on startup"))
        self.Bind(wx.EVT_CHECKBOX, self._chb_open_recent_startup_on_checkbox,
                  chb_open_recent_startup)
        chb_open_recent_startup.SetValue(self.config.get_open_recent_at_startup())
        return (chb_open_recent_startup,)

    def _create_date_time_tab(self, notebook):
        panel = self._create_tab_panel(notebook, _("Date && Time")) 
        controls = self._create_date_time_tab_controls(panel)
        self._size_tab_panel(panel, controls)
        
    def _create_date_time_tab_controls(self, panel):
        self.chb_wide_date_range = self._create_chb_wide_date_range(panel)
        choice_week = self._create_choice_week(panel)
        grid = wx.FlexGridSizer(1, 2, BORDER, BORDER)
        grid.Add(wx.StaticText(panel, label=_("Week start on:")), 
                 flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(choice_week, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        warning = _("This feature is experimental. If events are\ncreated in the extended range, you can not\ndisable this option and successfully load\nthe timeline again. A reload of the timeline\nis also needed for this to take effect.")
        warning_text_control = wx.StaticText(panel, label=warning)
        warning_text_control.SetForegroundColour((255, 0, 0))
        return (grid, self.chb_wide_date_range, warning_text_control)

    def _create_chb_wide_date_range(self, panel):
        chb_wide_date_range = wx.CheckBox(panel, label=_("Use extended date range (before 1 AD)"))
        self.Bind(wx.EVT_CHECKBOX, self._chb_use_wide_date_range_on_checkbox,
                  chb_wide_date_range)
        chb_wide_date_range.SetValue(self.config.get_use_wide_date_range())
        return chb_wide_date_range 

    def _create_choice_week(self, panel):
        choice_week = wx.Choice(panel, choices=[_("Monday"), _("Sunday")])
        self.Bind(wx.EVT_CHOICE, self._choice_week_on_choice, choice_week)
        index = self._week_index(self.config.week_start)
        choice_week.SetSelection(index)
        return choice_week
    
    def _create_tab_panel(self, notebook, label):
        panel = wx.Panel(notebook)
        notebook.AddPage(panel, label)
        return panel
    
    def _size_tab_panel(self, panel, controls):
        sizer = wx.BoxSizer(wx.VERTICAL)
        for control in controls:
            sizer.Add(control, flag=wx.ALL|wx.EXPAND, border=BORDER)
        panel.SetSizer(sizer)
        
    def _create_close_button(self):
        btn_close = wx.Button(self, wx.ID_CLOSE)
        btn_close.SetDefault()
        btn_close.SetFocus()
        self.SetAffirmativeId(wx.ID_CLOSE)
        self.Bind(wx.EVT_BUTTON, self._btn_close_on_click, btn_close)
        return btn_close 
        
    def _chb_use_wide_date_range_on_checkbox(self, evt):
        self._controller.on_use_wide_date_range_changed(evt.IsChecked())
    
    def _chb_open_recent_startup_on_checkbox(self, evt):
        self.config.set_open_recent_at_startup(evt.IsChecked())

    def _choice_week_on_choice(self, evt):
        self.config.week_start = self._index_week(evt.GetSelection())

    def _btn_close_on_click(self, e):
        self.Close()

    def _week_index(self, week):
        for (i, w) in self.weeks_map:
            if w == week:
                return i
        raise ValueError("Unknown week '%s'." % week)

    def _index_week(self, index):
        for (i, w) in self.weeks_map:
            if i == index:
                return w
        raise ValueError("Unknown week index '%s'." % index)

    def set_checkbox_enable_wide_date_range(self, value):
        self.chb_wide_date_range.SetValue(value)
    

class PreferencesDialogController(object):
    
    def __init__(self, dialog, config):
        self.dialog = dialog
        self.config = config
        
    def initialize_controls(self):
        self.dialog.set_checkbox_enable_wide_date_range(
            self.config.get_use_wide_date_range())
        
    def on_use_wide_date_range_changed(self, value):
        self.config.set_use_wide_date_range(value)
