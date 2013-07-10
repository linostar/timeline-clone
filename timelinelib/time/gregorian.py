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


class Gregorian(object):

    def __init__(self, year, month, day, hour, minute, second):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

    def to_tuple(self):
        return (self.year, self.month, self.day, self.hour, self.minute,
                self.second)


def timeline_date_time_to_gregorian(timeline_date_time):
    (year, month, day) = from_julian_day(timeline_date_time.julian_day)
    (hour, minute, second) = (0, 0, 0)
    return Gregorian(year, month, day, hour, minute, second)


def from_julian_day(julian_day):
    a = julian_day + 32044
    b = (4*a+3)/146097
    c = a - (b*146097)/4
    d = (4*c+3)/1461
    e = c - (1461*d)/4
    m = (5*e+2)/153
    day   = e - (153*m+2)/5 + 1
    month = m + 3 - 12*(m/10)
    year  = b*100 + d - 4800 + m/10
    return (year, month, day)
