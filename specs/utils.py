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


import datetime

import wx

from timelinelib.db.objects import TimePeriod
from timelinelib.monthnames import ABBREVIATED_ENGLISH_MONTH_NAMES
from timelinelib.time.pytime import PyTimeType
from timelinelib.time.wxtime import WxTimeType


def py_period(start, end):
    return TimePeriod(PyTimeType(), human_time_to_py(start), human_time_to_py(end))


def wx_period(start, end):
    return TimePeriod(WxTimeType(), human_time_to_wx(start), human_time_to_wx(end))


def human_time_to_py(human_time):
    (year, month, day) = human_time_to_ymd(human_time)
    return py_time(year, month, day)


def human_time_to_wx(human_time):
    (year, month, day) = human_time_to_ymd(human_time)
    return wx_time(year, month, day)


def human_time_to_ymd(human_time):
    day_part, month_part, year_part = human_time.split(" ")
    day = int(day_part)
    month = ABBREVIATED_ENGLISH_MONTH_NAMES.index(month_part) + 1
    year = int(year_part)
    return (year, month, day)


def py_time(year, month, day, hour=0, minute=0, second=0):
    return datetime.datetime(year, month, day, hour, minute, second)


def wx_time(year, month, day, hour=0, minute=0, second=0):
    return wx.DateTimeFromDMY(day, month-1, year, hour, minute, second)
