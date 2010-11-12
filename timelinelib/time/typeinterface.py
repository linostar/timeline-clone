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


class TimeType(object):

    def time_string(self, time):
        raise NotImplementedError("time_string not implemented.")

    def parse_time(self, time_string):
        raise NotImplementedError("parse_time not implemented.")

    def create_time_picker(self, parent):
        raise NotImplementedError("create_time_picker not implemented.")

    def get_navigation_functions(self):
        raise NotImplementedError("get_navigation_functions not implemented.")

    def is_date_time_type(self):
        raise NotImplementedError("is_date_time_type not implemented.")

    def format_period(self, time_period):
        raise NotImplementedError("format_period not implemented.")

    def get_min_time(self):
        raise NotImplementedError("return the min time for this time type.")

    def get_max_time(self):
        raise NotImplementedError("return the max time for this time type.")

    def choose_strip(self, metrics):
        raise NotImplementedError("choose_strip not implemented.")
    
    def get_metrics(self, size, time_period, divider_position):
        raise NotImplementedError("get_metrics not implemented.")

    def mult_timedelta(self, delta, num):
        raise NotImplementedError("mult_timedelta not implemented.")

    def get_default_time_period(self):
        raise NotImplementedError("get_default_time_period not implemented.")

    def now(self):
        raise NotImplementedError("now not implemented.")

            
class Metrics(object):
    """
    Convert between pixel coordinates and time coordinates.
    """

    def __init__(self, size, time_period, divider_line_slider_position):
        self.width, self.height = size
        self.half_width = self.width / 2
        self.half_height = self.height / 2
        self.half_height = int(round(divider_line_slider_position * self.height))
        self.time_period = time_period

    def calc_exact_x(self, time):
        raise NotImplementedError("calc_exact_x not implemented.")

    def calc_x(self, time):
        raise NotImplementedError("calc_x not implemented.")

    def calc_exact_width(self, time_period):
        raise NotImplementedError("calc_exact_width not implemented.")

    def calc_width(self, time_period):
        raise NotImplementedError("calc_width not implemented.")

    def get_time(self, x):
        raise NotImplementedError("get_time not implemented.")

    def get_difftime(self, x1, x2):
        raise NotImplementedError("get_difftime not implemented.")
