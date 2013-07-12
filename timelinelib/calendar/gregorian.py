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


import timelinelib.time.timeline as timeline


class Gregorian(object):

    def __init__(self, year, month, day, hour, minute, second):
        if not is_valid(year, month, day):
            raise ValueError("Invalid gregorian date %s-%s-%s" % (year, month, day))
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

    def replace(self, year=None, month=None):
        if year is None:
            year = self.year
        if month is None:
            month = self.month
        return Gregorian(year, month, self.day,
                         self.hour, self.minute, self.second)

    def days_in_month(self):
        return days_in_month(self.year, self.month)

    def to_tuple(self):
        return (self.year, self.month, self.day, self.hour, self.minute,
                self.second)

    def to_time(self):
        days = to_julian_day(self.year, self.month, self.day)
        seconds = self.hour * 60 * 60 + self.minute * 60 + self.second
        return timeline.Time(days, seconds)

    def __eq__(self, other):
        return (isinstance(other, Gregorian) and
                self.to_tuple() == other.to_tuple())

    def __repr__(self):
        return "Gregorian<%d-%02d-%02d %02d:%02d:%02d>" % self.to_tuple()


def is_valid(year, month, day):
    return (month >= 1
       and  month <= 12
       and  day >= 1
       and  day <= days_in_month(year, month))


def days_in_month(year, month):
    if month in [4, 6, 9, 11]:
        return 30
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    if is_leap_year(year):
        return 29
    return 28


def is_leap_year(year):
    return year % 4 == 0 and (year % 400 == 0 or not year % 100 == 0)


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


def to_julian_day(year, month, day):
    a = (14-month)/12
    y = year+4800-a
    m = month + 12*a - 3
    return day + (153*m+2)/5 + y*365 + y/4 - y/100 + y/400 - 32045


def gregorian_week(timeline_date_time):
    # TODO: Test this.
    return 27


def from_time(time):
    (year, month, day) = from_julian_day(time.julian_day)
    (hour, minute, second) = time.get_time_of_day()
    return Gregorian(year, month, day, hour, minute, second)


def from_date(year, month, day):
    return Gregorian(year, month, day, 0, 0, 0)
