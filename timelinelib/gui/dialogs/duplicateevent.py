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


from datetime import timedelta

import wx

from timelinelib.db.interface import TimelineIOError
from timelinelib.gui.utils import BORDER
from timelinelib.gui.utils import _set_focus_and_select
from timelinelib.gui.utils import _display_error_message
from timelinelib.db.objects import Event
from timelinelib.db.objects import TimePeriod
import timelinelib.gui.utils as gui_utils


FORWARD = 0
BACKWARD = 1
BOTH = 2


class DuplicateEvent(wx.Dialog):

    def __init__(self, parent, db, event):
        wx.Dialog.__init__(self, parent, title=_("Duplicate Event"))
        self._create_gui(db.get_time_type().get_duplicate_functions())
        self.controller = DuplicateEventController(self, db, event)
        self.controller.initialize()

    def set_count(self, count):
        self.sc_count.SetValue(count)

    def get_count(self):
        return self.sc_count.GetValue() 
        
    def set_frequency(self, count):
        self.sc_frequency.SetValue(count)
        
    def get_frequency(self):
        return self.sc_frequency.GetValue() 
        
    def select_move_period_fn_at_index(self, index):
        self.rb_period.SetSelection(index)

    def get_move_period_fn(self):
        return self._move_period_fns[self.rb_period.GetSelection()]

    def set_direction(self, direction):
        self.rb_direction.SetSelection(direction)                             

    def get_direction(self):
        return self.rb_direction.GetSelection()                             

    def close(self):
        self.EndModal(wx.ID_OK)

    def handle_db_error(self, e):
        gui_utils.handle_db_error_in_dialog(self, e)

    def handle_date_errors(self, error_count):
       _display_error_message(
            _("%d Events not duplicated due to missing dates.") 
            % error_count)
        
    def _create_gui(self, move_period_config):
        self._move_period_fns = [fn for (label, fn) in move_period_config]
        period_list = [label for (label, fn) in move_period_config]
        direction_list = [_("Forward"), _("Backward"), _("Both")]
        # Create all controls
        sc_count_box = self._creat_count_spin_control()
        sc_frequency_box = self._creat_frequency_spin_control()
        self.rb_period = wx.RadioBox(self, wx.ID_ANY, _("Period"), 
                                          wx.DefaultPosition, wx.DefaultSize, 
                                          period_list)#, 1, 
                                          #wx.RA_SPECIFY_COLS)
        self.rb_direction = wx.RadioBox(self, wx.ID_ANY, _("Direction"), 
                                        choices=direction_list)
        button_box = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        # Place controls in grid
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(sc_count_box, border=BORDER)
        vbox.Add(self.rb_period, flag=wx.ALL|wx.EXPAND, border=BORDER)
        vbox.Add(sc_frequency_box, border=BORDER)
        vbox.Add(self.rb_direction, flag=wx.ALL|wx.EXPAND, border=BORDER)
        vbox.Add(button_box, flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.SetSizerAndFit(vbox)
        # Bind event handlers to controls
        self.Bind(wx.EVT_BUTTON, self._btn_ok_on_click, id=wx.ID_OK)
        _set_focus_and_select(self.sc_count)

    def _creat_frequency_spin_control(self):
        st_frequency = wx.StaticText(self, label=_("Frequency:"))
        self.sc_frequency = wx.SpinCtrl(self, wx.ID_ANY, size=(50,-1))
        self.sc_frequency.SetRange(1,999)
        self.sc_frequency.SetValue(1)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(st_frequency, flag=wx.ALL, border=BORDER)
        hbox.Add(self.sc_frequency, flag=wx.ALL, border=BORDER)
        return hbox

    def _creat_count_spin_control(self):
        st_count = wx.StaticText(self, label=_("Number of duplicates:"))
        self.sc_count = wx.SpinCtrl(self, wx.ID_ANY, size=(50,-1))
        self.sc_count.SetRange(1,999)
        self.sc_count.SetValue(1)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(st_count, flag=wx.ALL, border=BORDER)
        hbox.Add(self.sc_count, flag=wx.ALL, border=BORDER)
        return hbox
        
    def _btn_ok_on_click(self, e):
        gui_utils.set_wait_cursor(self)
        self.controller.create_duplicates_and_save()
        gui_utils.set_default_cursor(self)

        
class DuplicateEventController(object):

    def __init__(self, view, db, event):
        self.view = view
        self.db = db
        self.event = event
        
    def initialize(self):
        self.view.set_count(1)
        self.view.set_frequency(1)
        self.view.select_move_period_fn_at_index(0)
        self.view.set_direction(FORWARD)

    def create_duplicates_and_save(self):
        (periods, nbr_of_missing_dates) = self._repeat_period(
            self.db.get_time_type(), 
            self.event.time_period, 
            self.view.get_move_period_fn(),
            self.view.get_frequency(),
            self.view.get_count(),
            self.view.get_direction())
        try:
            for period in periods: 
                event = self.event.clone()
                event.update_period(period.start_time, period.end_time)
                self.db.save_event(event)
            if nbr_of_missing_dates > 0:
                self.view.handle_date_errors(nbr_of_missing_dates)
            self.view.close()
        except TimelineIOError, e:
            self.view.handle_db_error(e)

    def _repeat_period(self, time_type, period, move_period_fn, frequency,
                       repetitions, direction):
        periods = []     
        nbr_of_missing_dates = 0
        for index in self._calc_indicies(direction, repetitions):
            new_period = move_period_fn(time_type, period, index, frequency)
            if new_period == None:
                nbr_of_missing_dates += 1
            else:
                periods.append(new_period)     
        return (periods, nbr_of_missing_dates)

    def _calc_indicies(self, direction, repetitions):
        if direction == FORWARD:
            return range(1, repetitions + 1)
        elif direction == BACKWARD:
            return range(-repetitions, 0)
        elif direction == BOTH:
            indicies = range(-repetitions, repetitions + 1)
            indicies.remove(0)
            return indicies
        else:
            raise Exception("Invalid direction.")
