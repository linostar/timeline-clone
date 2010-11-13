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


import sys
import re

#import wx

from timelinelib.time.typeinterface import TimeType
from timelinelib.db.objects import time_period_center
from timelinelib.drawing.interface import Strip
from timelinelib.drawing.utils import get_default_font


class NumTimeType(TimeType):
    
    def time_string(self, time):
        return "%s" % (time)

    def parse_time(self, time_string):
        match = re.search(r"^([-]?\d+(.\d+)?)$", time_string)
        if match:
            time = float(match.group(1))
            try:
                return time
            except ValueError:
                raise ValueError("Invalid time, time string = '%s'" % time_string)
        else:
            raise ValueError("Time not on correct format = '%s'" % time_string)
        
    def create_time_picker(self, parent):
        from timelinelib.gui.components.numtimepicker import NumTimePicker
        return NumTimePicker(parent)

    def get_navigation_functions(self):
        return [
            (_("Go to &Time\tCtrl+T"), go_to_time_fn),
            ("SEP", None),
            (_("Backward\tPgUp"), backward_fn),
            (_("Forward\tPgDn"), forward_fn),
        ]

    def is_date_time_type(self):
        return False

    def format_period(self, time_period):
        """Returns a unicode string describing the time period."""
        if time_period.is_period():
            label = u"%s to %s" % (time_period.start_time, time_period.end_time)
        else:
            label = u"%s" % time_period.start_time
        return label
    
    def get_min_time(self):
        return -sys.maxint - 1

    def get_max_time(self):
        return sys.maxint

    def choose_strip(self, metrics):
        return (StripSmall(), StripSmall())
    
    def mult_timedelta(self, delta, num):
        return delta * num

    def get_default_time_period(self):
        return time_period_center(self, 0, 100)

    def now(self):
        return 0

    def get_time_at_x(self, time_period, x_percent_of_width):
        """Return the time at pixel `x`."""
        delta = time_period.end_time - time_period.start_time
        return delta * x_percent_of_width 
        
    def div_timedeltas(self, delta1, delta2):
       return delta1 / delta2
    
    def get_max_zoom_delta(self):
        return 1000

    def get_min_zoom_delta(self):
        return 2
    
    def get_zero_delta(self):
        return 0
    
    def time_period_has_nonzero_time(self, time_period):
        return False

    def get_name(self):
        return u"numtime"

        
class StripSmall(Strip):

    def label(self, time, major=False):
        return "%s" % (time)

    def start(self, time):
        return time

    def increment(self, time):
        return time + 1

    def get_font(self, time_period):
        return get_default_font(8)


def go_to_time_fn(main_frame, current_period, navigation_fn):
    #from timelinelib.gui.dialogs.gototime import GotoTimeDialog
    #dialog = GotoTimeDialog(main_frame, current_period.mean_time())
    #if dialog.ShowModal() == wx.ID_OK:
    #    navigation_fn(lambda tp: tp.center(dialog.time))
    #dialog.Destroy()
    raise NotImplementedError("go_to_time_fn not implemented.")


def backward_fn(main_frame, current_period, navigation_fn):
    delta = current_period.start_time - current_period.end_time
    navigation_fn(lambda tp, d=delta: tp.move_page(d))


def forward_fn(main_frame, current_period, navigation_fn):
    delta = current_period.end_time - current_period.start_time  
    navigation_fn(lambda tp, d=delta: tp.move_page(d))
