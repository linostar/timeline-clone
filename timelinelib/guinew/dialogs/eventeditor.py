# Copyright (C) 2009  Rickard Lindberg, Roger Lindberg
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


"""
Dialog used for creating and editing events.
"""


import logging
import os.path

import wx

from timelinelib.db.interface import TimelineIOError
from timelinelib.db.objects import Event
from timelinelib.db.objects import TimePeriod
from timelinelib.guinew.utils import TxtException
from timelinelib.guinew.utils import sort_categories
from timelinelib.guinew.utils import _set_focus_and_select
from timelinelib.guinew.utils import _parse_text_from_textbox
from timelinelib.guinew.utils import _display_error_message
from timelinelib.guinew.utils import BORDER
from timelinelib.guinew.utils import ID_ERROR
from timelinelib.guinew.dialogs.categorieseditor import CategoriesEditor
from timelinelib.guinew.dialogs.categoryeditor import CategoryEditor
from timelinelib.guinew.components.datetimepicker import DateTimePicker


class EventEditor(wx.Dialog):
    """Dialog used for creating and editing events."""

    def __init__(self, parent, title, timeline,
                 start=None, end=None, event=None):
        """
        Create a event editor dialog.

        The 'event' argument is optional. If it is given the dialog is used
        to edit this event and the controls are filled with data from
        the event and the arguments 'start' and 'end' are ignored.

        If the 'event' argument isn't given the dialog is used to create a
        new event, and the controls for start and end time are initially
        filled with data from the arguments 'start' and 'end' if they are
        given. Otherwise they will default to today.
        """
        wx.Dialog.__init__(self, parent, title=title,
                           style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.timeline = timeline
        self.event = event
        self._create_gui()
        self._fill_controls_with_data(start, end)
        self._set_initial_focus()

    def _create_gui(self):
        """Create the controls of the dialog."""
        # Groupbox
        groupbox = wx.StaticBox(self, wx.ID_ANY, _("Event Properties"))
        groupbox_sizer = wx.StaticBoxSizer(groupbox, wx.VERTICAL)
        # Grid
        grid = wx.FlexGridSizer(4, 2, BORDER, BORDER)
        grid.AddGrowableCol(1)
        # Grid: When: Label + DateTimePickers
        grid.Add(wx.StaticText(self, label=_("When:")),
                 flag=wx.ALIGN_CENTER_VERTICAL)
        self.dtp_start = DateTimePicker(self)
        self.lbl_to = wx.StaticText(self, label=_("to"))
        self.dtp_end = DateTimePicker(self)
        when_box = wx.BoxSizer(wx.HORIZONTAL)
        when_box.Add(self.dtp_start, proportion=1)
        when_box.AddSpacer(BORDER)
        when_box.Add(self.lbl_to, flag=wx.ALIGN_CENTER_VERTICAL|wx.RESERVE_SPACE_EVEN_IF_HIDDEN)
        when_box.AddSpacer(BORDER)
        when_box.Add(self.dtp_end, proportion=1,
                     flag=wx.RESERVE_SPACE_EVEN_IF_HIDDEN)
        grid.Add(when_box)
        # Grid: When: Checkboxes
        grid.AddStretchSpacer()
        when_box_props = wx.BoxSizer(wx.HORIZONTAL)
        self.chb_period = wx.CheckBox(self, label=_("Period"))
        self.Bind(wx.EVT_CHECKBOX, self._chb_period_on_checkbox,
                  self.chb_period)
        when_box_props.Add(self.chb_period)
        self.chb_show_time = wx.CheckBox(self, label=_("Show time"))
        self.Bind(wx.EVT_CHECKBOX, self._chb_show_time_on_checkbox,
                  self.chb_show_time)
        when_box_props.Add(self.chb_show_time)
        grid.Add(when_box_props)
        # Grid: Text
        self.txt_text = wx.TextCtrl(self, wx.ID_ANY)
        grid.Add(wx.StaticText(self, label=_("Text:")),
                 flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.txt_text, flag=wx.EXPAND)
        # Grid: Category
        self.lst_category = wx.Choice(self, wx.ID_ANY)
        grid.Add(wx.StaticText(self, label=_("Category:")),
                 flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.lst_category)
        groupbox_sizer.Add(grid, flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.Bind(wx.EVT_CHOICE, self._lst_category_on_choice,
                  self.lst_category)
        # Event data
        self.event_data = []
        notebook = wx.Notebook(self, style=wx.BK_DEFAULT)
        for data_id in self.timeline.supported_event_data():
            if data_id == "description":
                name = _("Description")
                editor_class = DescriptionEditor
            elif data_id == "icon":
                name = _("Icon")
                editor_class = IconEditor
            else:
                continue
            panel = wx.Panel(notebook)
            editor = editor_class(panel)
            notebook.AddPage(panel, name)
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(editor, flag=wx.EXPAND, proportion=1)
            panel.SetSizer(sizer)
            self.event_data.append((data_id, editor))
        groupbox_sizer.Add(notebook, border=BORDER, flag=wx.ALL|wx.EXPAND,
                           proportion=1)
        # Main (vertical layout)
        main_box = wx.BoxSizer(wx.VERTICAL)
        # Main: Groupbox
        main_box.Add(groupbox_sizer, flag=wx.EXPAND|wx.ALL, border=BORDER,
                     proportion=1)
        # Main: Checkbox
        self.chb_add_more = wx.CheckBox(self, label=_("Add more events after this one"))
        main_box.Add(self.chb_add_more, flag=wx.ALL, border=BORDER)
        # Main: Buttons
        button_box = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self._btn_ok_on_click, id=wx.ID_OK)
        main_box.Add(button_box, flag=wx.EXPAND|wx.ALL, border=BORDER)
        # Hide if not creating new
        if self.event != None:
            self.chb_add_more.Show(False)
        # Realize
        self.SetSizerAndFit(main_box)

    def _btn_ok_on_click(self, evt):
        """
        Add new or update existing event.

        If the Close-on-ok checkbox is checked the dialog is also closed.
        """
        try:
            logging.debug("_btn_ok_on_click")
            try:
                # Input value retrieval and validation
                start_time = self.dtp_start.get_value()
                end_time = start_time
                if self.chb_period.IsChecked():
                    end_time = self.dtp_end.get_value()
                selection = self.lst_category.GetSelection()
                category = self.lst_category.GetClientData(selection)
                if start_time > end_time:
                    raise TxtException(_("End must be > Start"), self.dtp_start)
                name = _parse_text_from_textbox(self.txt_text, _("Text"))
                # Update existing event
                if self.updatemode:
                    self.event.update(start_time, end_time, name, category)
                    for data_id, editor in self.event_data:
                        self.event.set_data(data_id,
                                            editor.get_data())
                    self.timeline.save_event(self.event)
                # Create new event
                else:
                    self.event = Event(start_time, end_time, name, category)
                    for data_id, editor in self.event_data:
                        self.event.set_data(data_id,
                                            editor.get_data())
                    self.timeline.save_event(self.event)
                # Close the dialog ?
                if self.chb_add_more.GetValue():
                    self.txt_text.SetValue("")
                    for data_id, editor in self.event_data:
                        editor.clear_data(editor)
                else:
                    self._close()
            except TxtException, ex:
                _display_error_message("%s" % ex.error_message)
                _set_focus_and_select(ex.control)
        except TimelineIOError, e:
            _display_error_message(e.message, self)
            self.error = e
            self.EndModal(ID_ERROR)

    def _chb_period_on_checkbox(self, e):
        self._show_to_time(e.IsChecked())

    def _chb_show_time_on_checkbox(self, e):
        self.dtp_start.show_time(e.IsChecked())
        self.dtp_end.show_time(e.IsChecked())

    def _lst_category_on_choice(self, e):
        new_selection_index = e.GetSelection()
        if new_selection_index > self.last_real_category_index:
            self.lst_category.SetSelection(self.current_category_selection)
            if new_selection_index == self.add_category_item_index:
                self._add_category()
            elif new_selection_index == self.edit_categoris_item_index:
                self._edit_categories()
        else:
            self.current_category_selection = new_selection_index

    def _add_category(self):
        try:
            dialog = CategoryEditor(self, _("Add Category"),
                                    self.timeline, None)
        except TimelineIOError, e:
            _display_error_message(e.message, self)
            self.error = e
            self.EndModal(ID_ERROR)
        else:
            dialog_result = dialog.ShowModal()
            if dialog_result == ID_ERROR:
                self.error = dialog.error
                self.EndModal(ID_ERROR)
            elif dialog_result == wx.ID_OK:
                try:
                    self._update_categories(dialog.get_edited_category())
                except TimelineIOError, e:
                    _display_error_message(e.message, self)
                    self.error = e
                    self.EndModal(ID_ERROR)
            dialog.Destroy()

    def _edit_categories(self):
        try:
            dialog = CategoriesEditor(self, self.timeline)
        except TimelineIOError, e:
            _display_error_message(e.message, self)
            self.error = e
            self.EndModal(ID_ERROR)
        else:
            if dialog.ShowModal() == ID_ERROR:
                self.error = dialog.error
                self.EndModal(ID_ERROR)
            else:
                try:
                    prev_index = self.lst_category.GetSelection()
                    prev_category = self.lst_category.GetClientData(prev_index)
                    self._update_categories(prev_category)
                except TimelineIOError, e:
                    _display_error_message(e.message, self)
                    self.error = e
                    self.EndModal(ID_ERROR)
            dialog.Destroy()

    def _show_to_time(self, show=True):
        self.lbl_to.Show(show)
        self.dtp_end.Show(show)

    def _fill_controls_with_data(self, start=None, end=None):
        """Initially fill the controls in the dialog with data."""
        if self.event == None:
            self.chb_period.SetValue(False)
            self.chb_show_time.SetValue(False)
            text = ""
            category = None
            self.updatemode = False
        else:
            start = self.event.time_period.start_time
            end = self.event.time_period.end_time
            text = self.event.text
            category = self.event.category
            for data_id, editor in self.event_data:
                data = self.event.get_data(data_id)
                if data != None:
                    editor.set_data(data)
            self.updatemode = True
        if start != None and end != None:
            self.chb_show_time.SetValue(TimePeriod(start, end).has_nonzero_time())
            self.chb_period.SetValue(start != end)
        self.dtp_start.set_value(start)
        self.dtp_end.set_value(end)
        self.txt_text.SetValue(text)
        self._update_categories(category)
        self.chb_add_more.SetValue(False)
        self._show_to_time(self.chb_period.IsChecked())
        self.dtp_start.show_time(self.chb_show_time.IsChecked())
        self.dtp_end.show_time(self.chb_show_time.IsChecked())

    def _update_categories(self, select_category):
        # We can not do error handling here since this method is also called
        # from the constructor (and then error handling is done by the code
        # calling the constructor).
        self.lst_category.Clear()
        self.lst_category.Append("", None) # The None-category
        selection_set = False
        current_item_index = 1
        for cat in sort_categories(self.timeline.get_categories()):
            self.lst_category.Append(cat.name, cat)
            if cat == select_category:
                self.lst_category.SetSelection(current_item_index)
                selection_set = True
            current_item_index += 1
        self.last_real_category_index = current_item_index - 1
        self.add_category_item_index = self.last_real_category_index + 2
        self.edit_categoris_item_index = self.last_real_category_index + 3
        self.lst_category.Append("", None)
        self.lst_category.Append(_("Add new"), None)
        self.lst_category.Append(_("Edit categories"), None)
        if not selection_set:
            self.lst_category.SetSelection(0)
        self.current_category_selection = self.lst_category.GetSelection()

    def _set_initial_focus(self):
        self.dtp_start.SetFocus()

    def _close(self):
        """
        Close the dialog.

        Make sure that no events are selected after the dialog is closed.
        """
        # TODO: Replace with EventRuntimeData
        #self.timeline.reset_selected_events()
        self.EndModal(wx.ID_OK)


class DescriptionEditor(wx.TextCtrl):

    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent, style=wx.TE_MULTILINE)

    def get_data(self):
        description = self.GetValue()
        if description.strip() != "":
            return description
        return None

    def set_data(self, data):
        self.SetValue(data)

    def clear_data(self):
        self.SetValue("")


class IconEditor(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.MAX_SIZE = (128, 128)
        # Controls
        self.img_icon = wx.StaticBitmap(self, size=self.MAX_SIZE)
        description = wx.StaticText(self, label=_("Images will be scaled to fit inside a %ix%i box.") % self.MAX_SIZE)
        btn_select = wx.Button(self, wx.ID_OPEN)
        btn_clear = wx.Button(self, wx.ID_CLEAR)
        self.Bind(wx.EVT_BUTTON, self._btn_select_on_click, btn_select)
        self.Bind(wx.EVT_BUTTON, self._btn_clear_on_click, btn_clear)
        # Layout
        sizer = wx.GridBagSizer(5, 5)
        sizer.Add(description, wx.GBPosition(0, 0), wx.GBSpan(1, 2))
        sizer.Add(btn_select, wx.GBPosition(1, 0), wx.GBSpan(1, 1))
        sizer.Add(btn_clear, wx.GBPosition(1, 1), wx.GBSpan(1, 1))
        sizer.Add(self.img_icon, wx.GBPosition(0, 2), wx.GBSpan(2, 1))
        self.SetSizerAndFit(sizer)
        # Data
        self.bmp = None

    def get_data(self):
        return self.get_icon()

    def set_data(self, data):
        self.set_icon(data)

    def clear_data(self):
        self.set_icon(None)

    def set_icon(self, bmp):
        self.bmp = bmp
        if self.bmp == None:
            self.img_icon.SetBitmap(wx.EmptyBitmap(1, 1))
        else:
            self.img_icon.SetBitmap(bmp)
        self.GetSizer().Layout()

    def get_icon(self):
        return self.bmp

    def _btn_select_on_click(self, evt):
        dialog = wx.FileDialog(self, message=_("Select Icon"),
                               wildcard="*", style=wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            if os.path.exists(path):
                image = wx.EmptyImage(0, 0)
                success = image.LoadFile(path)
                # LoadFile will show error popup if not successful
                if success:
                    # Resize image if too large
                    (w, h) = image.GetSize()
                    (W, H) = self.MAX_SIZE
                    if w > W:
                        factor = float(W) / float(w)
                        w = w * factor
                        h = h * factor
                    if h > H:
                        factor = float(H) / float(h)
                        w = w * factor
                        h = h * factor
                    image = image.Scale(w, h, wx.IMAGE_QUALITY_HIGH)
                    self.set_icon(image.ConvertToBitmap())
        dialog.Destroy()

    def _btn_clear_on_click(self, evt):
        self.set_icon(None)
