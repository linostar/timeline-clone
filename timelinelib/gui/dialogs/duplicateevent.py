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


DAY = 0
WEEK = 1
MONTH = 2
YEAR = 3

FORWARD = 0
BACKWARD = 1
BOTH = 2


class DuplicateEvent(wx.Dialog):
    """
    This dialog is used to make copies of one selected event.
    """

    def __init__(self, parent, db, event):
        """
        Arguments:
            parent      The parent window (mainframe)
            db          The event database object used by the application
            event       The event object to be duplicated
        """
        wx.Dialog.__init__(self, parent, title=_("Duplicate Event"))
        self._create_gui()
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
        
    def set_period_type(self, period):
        self.rb_period.SetSelection(period)

    def get_period_type(self):
        return self.rb_period.GetSelection()                             

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
        
    def _create_gui(self):
        PERIOD_LIST = [_("Day"), _("Week"), _("Month"), _("Year")]
        DIRECTION_LIST = [_("Forward"), _("Backward"), _("Both")]
        # Create all controls
        sc_count_box = self._creat_count_spin_control()
        sc_frequency_box = self._creat_frequency_spin_control()
        self.rb_period = wx.RadioBox(self, wx.ID_ANY, _("Period"), 
                                          wx.DefaultPosition, wx.DefaultSize, 
                                          PERIOD_LIST)#, 1, 
                                          #wx.RA_SPECIFY_COLS)
        self.rb_direction = wx.RadioBox(self, wx.ID_ANY, _("Direction"), 
                                        choices=DIRECTION_LIST)
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
        self.period = self.event.time_period
        
    def initialize(self):
        self.view.set_count(1)
        self.view.set_frequency(1)
        self.view.set_period_type(DAY)
        self.view.set_direction(FORWARD)

    def create_duplicates_and_save(self):
        repetitions = self.view.get_count()
        period_type = self.view.get_period_type()
        frequency = self.view.get_frequency()
        direction = self.view.get_direction()
        periods, nbr_of_missing_dates = repeat_period(self.db.get_time_type(), 
                                                      self.period, period_type, 
                                                      frequency, repetitions, 
                                                      direction)
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
            

def repeat_period(time_type, event_period, period_type, frequency, repetitions, 
                  direction):
        """
        Returns a list of calculated TimePeriods and the number of missing 
        dates as tuple (periods, nbr_of_missing_dates).
        
        Missing dates, can occur for example if you try do duplicate a
        TimePeriod each month and the TimePeriod starts at 2010-01-31.
        2010-02-31 Doesn't exist, so it's a missing date.
        
        Arguments:
            event_period    The TimePeriod of the event that is duplicated
            period_type     A member of (DAY, WEEK, MONTH, YEAR)
            frequency       A number saying how often a period will be created.
                            1=Every period_type, 2=Every second Period_type, ..
            repetitions     A number saying how many duplicates to create in
                            each direction.
            direction       A member of (FORWARD, BACKWARD, BOTH)
        """
        # Calculate indexes relative the event_period for the periods to create
        if direction == FORWARD:
            inxs = range(1, repetitions + 1)
        elif direction == BACKWARD:
            inxs = range(-repetitions, 0)
        elif direction == BOTH:
            inxs = range(-repetitions, repetitions + 1)
            inxs.remove(0)
        periods = []     
        # Calculate a TimePeriod for each index
        nbr_of_missing_dates = 0
        for inx in inxs:
            if period_type == DAY:
                new_period = _get_day_period(time_type, event_period, inx, frequency)
            elif period_type == WEEK:
                new_period = _get_week_period(time_type, event_period, inx, frequency)
            elif period_type == MONTH:
                new_period = _get_month_period(time_type, event_period, inx, frequency)
            elif period_type == YEAR:
                new_period = _get_year_period(time_type, event_period, inx, frequency)
            if new_period == None:
               nbr_of_missing_dates += 1
               continue
            periods.append(new_period)     
        return periods, nbr_of_missing_dates
    
    
def _get_day_period(time_type, period, inx, frequency):
    delta = timedelta(days=1) * frequency * inx
    start_time = period.start_time + delta  
    end_time = period.end_time + delta  
    return TimePeriod(time_type, start_time, end_time)


def _get_week_period(time_type, period, inx, frequency):
    delta = timedelta(weeks=1) * frequency * inx
    start_time = period.start_time + delta
    end_time = period.end_time + delta
    return TimePeriod(time_type, start_time, end_time)


def _get_month_period(time_type, period, inx, frequency):
    try:
        delta = inx * frequency
        years = abs(delta) / 12
        if inx < 0:
            years = -years
        delta = delta - 12 * years
        if delta < 0:
            start_month = period.start_time.month + 12 + delta
            end_month = period.end_time.month + 12 + delta
            if start_month > 12:
                start_month -=12
                end_month -=12
            if start_month > period.start_time.month:
                years -= 1
        else:
            start_month = period.start_time.month + delta
            end_month = period.start_time.month + delta
            if start_month > 12:
                start_month -=12
                end_month -=12
                years += 1
        start_year = period.start_time.year + years
        end_year = period.start_time.year + years
        start_time = period.start_time.replace(year=start_year, month=start_month)
        end_time = period.end_time.replace(year=end_year, month=end_month)
        return TimePeriod(time_type, start_time, end_time)
    except ValueError:
        return None


def _get_year_period(time_type, period, inx, frequency):
    try:
        delta = inx * frequency
        start_year = period.start_time.year
        end_year = period.end_time.year
        start_time = period.start_time.replace(year=start_year + delta)
        end_time = period.end_time.replace(year=end_year + delta)
        return TimePeriod(time_type, start_time, end_time)
    except ValueError:
        return None
