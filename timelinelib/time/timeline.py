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


SECONDS_IN_DAY = 24 * 60 * 60


class TimelineDateTime(object):

    def __init__(self, julian_day, seconds):
        self.julian_day = julian_day
        self.seconds = seconds

    def __eq__(self, dt):
        return self.julian_day == dt.julian_day and self.seconds == dt.seconds
    
    def __add__(self, delta):
        seconds = self.seconds + delta.seconds
        return TimelineDateTime(self.julian_day + seconds / SECONDS_IN_DAY, seconds % SECONDS_IN_DAY)
    
    def __sub__(self, dt):
        if isinstance(dt, TimelineDelta):
            seconds = self.seconds - dt.seconds
            if seconds < 0:
                if seconds % SECONDS_IN_DAY  == 0:
                    days = abs(seconds) / SECONDS_IN_DAY
                    seconds = 0
                else:
                    days = abs(seconds) / SECONDS_IN_DAY + 1
                    seconds = SECONDS_IN_DAY - abs(seconds) % SECONDS_IN_DAY
                return TimelineDateTime(self.julian_day - days, seconds)
            else:
                return TimelineDateTime(self.julian_day, seconds)
        else:
            return TimelineDelta((self.julian_day - dt.julian_day) * SECONDS_IN_DAY)
    
    def __gt__(self, dt):
        return (self.julian_day, self.seconds) > (dt.julian_day, dt.seconds)
        
    def __lt__(self, dt):
        return (self.julian_day, self.seconds) < (dt.julian_day, dt.seconds)

    def __repr__(self):
        return "TimelineDateTime[%s, %s]" % (self.julian_day, self.seconds)
    
    def get_time_of_day(self):
        hours = self.seconds / 3600
        minutes = (self.seconds / 60) % 60 
        seconds = self.seconds % 60
        return (hours, minutes, seconds)

    def get_day_of_week(self):
        return  (self.julian_day + 1) %  7 
    
    
class TimelineDelta(object):
    
    def __init__(self, seconds):
        self.seconds = seconds
        
    def __div__(self, value):
        if isinstance(value, TimelineDelta):
            return float(self.seconds) / float(value.seconds)
        else:
            return TimelineDelta(self.seconds / value)

    def __mul__(self, value):
        return TimelineDelta(int(self.seconds * value))

    def __eq__(self, d):
        return self.seconds == d.seconds
    
    def __gt__(self, d):
        return self.seconds > d.seconds

    def __lt__(self, d):
        return self.seconds < d.seconds
    
    def get_days(self):
        return self.seconds / SECONDS_IN_DAY
    
    def get_hours(self):
        return (self.seconds / (60 * 60)) % 24
    
    def get_minutes(self):
        return (self.seconds / 60) % 60
