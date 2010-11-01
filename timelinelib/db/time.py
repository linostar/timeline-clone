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


import re
import datetime

import wx


class TimeType(object):

    def time_string(self, time):
        raise NotImplementedError("time_string not implemented.")

    def parse_time(self, time_string):
        raise NotImplementedError("parse_time not implemented.")

    def create_time_picker(self, parent):
        raise NotImplementedError("create_time_picker not implemented.")

    def get_navigation_functions(self):
        raise NotImplementedError("get_navigation_functions not implemented.")


class PyTimeType(TimeType):

    def time_string(self, time):
        return "%s-%s-%s %s:%s:%s" % (time.year, time.month, time.day,
                                      time.hour, time.minute, time.second)

    def parse_time(self, time_string):
        match = re.search(r"^(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)$", time_string)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            hour = int(match.group(4))
            minute = int(match.group(5))
            second = int(match.group(6))
            try:
                return datetime.datetime(year, month, day, hour, minute, second)
            except ValueError:
                raise ValueError("Invalid time, time string = '%s'" % time_string)
        else:
            raise ValueError("Time not on correct format = '%s'" % time_string)

    def create_time_picker(self, parent):
        from timelinelib.gui.components.pydatetimepicker import PyDateTimePicker
        return PyDateTimePicker(parent)

    def get_navigation_functions(self):
        return [
            (_("Go to &Today\tCtrl+T"), go_to_today_fn),
            (_("Go to D&ate...\tCtrl+G"), go_to_date_fn),
            ("SEP", None),
            (_("Backward\tPgUp"), backward_fn),
            (_("Forward\tPgDn"), forward_fn),
            (_("Forward One Wee&k\tCtrl+K"), forward_one_week_fn),
            (_("Back One &Week\tCtrl+W"), backward_one_week_fn),
            (_("Forward One Mont&h\tCtrl+h"), forward_one_month_fn),
            (_("Back One &Month\tCtrl+M"), backward_one_month_fn),
            (_("Forward One Yea&r\tCtrl+R"), forward_one_year_fn),
            (_("Back One &Year\tCtrl+Y"), backward_one_year_fn),
            ("SEP", None),
            (_("Fit Millennium"), fit_millennium_fn),
            (_("Fit Century"), fit_century_fn),
            (_("Fit Decade"), fit_decade_fn),
            (_("Fit Year"), fit_year_fn),
            (_("Fit Month"), fit_month_fn),
            (_("Fit Day"), fit_day_fn),
        ]


def go_to_today_fn(main_frame, current_period, navigation_fn):
    navigation_fn(lambda tp: tp.center(datetime.datetime.now()))


def go_to_date_fn(main_frame, current_period, navigation_fn):
    from timelinelib.gui.dialogs.gotodate import GotoDateDialog
    dialog = GotoDateDialog(main_frame, current_period.mean_time())
    if dialog.ShowModal() == wx.ID_OK:
        navigation_fn(lambda tp: tp.center(dialog.time))
    dialog.Destroy()


def backward_fn(main_frame, current_period, navigation_fn):
    navigation_fn(lambda tp: tp.move_page_smart(-1))


def forward_fn(main_frame, current_period, navigation_fn):
    navigation_fn(lambda tp: tp.move_page_smart(1))


def forward_one_week_fn(main_frame, current_period, navigation_fn):
    wk = datetime.timedelta(days=7)
    navigation_fn(lambda tp: tp.move_delta(wk))


def backward_one_week_fn(main_frame, current_period, navigation_fn):
    wk = datetime.timedelta(days=7)
    navigation_fn(lambda tp: tp.move_delta(-1*wk))


def navigate_month_step(current_period, navigation_fn, direction):
    """
    Currently does notice leap years.
    """
    tm = current_period.mean_time()
    if direction > 0:
        if tm.month == 2:
            d = 28
        elif tm.month in (4,6,9,11):
            d = 30
        else:
            d = 31
    else:
        if tm.month == 3:
            d = 28
        elif tm.month in (5,7,10,12):
            d = 30
        else:
            d = 31
    mv = datetime.timedelta(days=d)
    navigation_fn(lambda tp: tp.move_delta(direction*mv))


def forward_one_month_fn(main_frame, current_period, navigation_fn):
    navigate_month_step(current_period, navigation_fn, 1)


def backward_one_month_fn(main_frame, current_period, navigation_fn):
    navigate_month_step(current_period, navigation_fn, -1)


def forward_one_year_fn(main_frame, current_period, navigation_fn):
    yr = datetime.timedelta(days=365)
    navigation_fn(lambda tp: tp.move_delta(yr))


def backward_one_year_fn(main_frame, current_period, navigation_fn):
    yr = datetime.timedelta(days=365)
    navigation_fn(lambda tp: tp.move_delta(-1*yr))


def fit_millennium_fn(main_frame, current_period, navigation_fn):
    navigation_fn(lambda tp: tp.fit_millennium())


def fit_century_fn(main_frame, current_period, navigation_fn):
    navigation_fn(lambda tp: tp.fit_century())


def fit_decade_fn(main_frame, current_period, navigation_fn):
    navigation_fn(lambda tp: tp.fit_decade())


def fit_year_fn(main_frame, current_period, navigation_fn):
    navigation_fn(lambda tp: tp.fit_year())


def fit_month_fn(main_frame, current_period, navigation_fn):
    navigation_fn(lambda tp: tp.fit_month())


def fit_day_fn(main_frame, current_period, navigation_fn):
    navigation_fn(lambda tp: tp.fit_day())
