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


import locale
import datetime
import re

from timelinelib.features.experimental.experimentalfeature import ExperimentalFeature
from timelinelib.calendar.dateformatter import DateFormatter


DISPLAY_NAME = "Locale date formats"
DESCRIPTION = """
              Use a date format specific for the locale setting of the host.
              """  
YEAR = "3333"
MONTH = "11"
DAY = "22"


class ExperimentalFeatureDateFormatting(ExperimentalFeature, DateFormatter):
    
    def __init__(self):
        ExperimentalFeature.__init__(self, DISPLAY_NAME, DESCRIPTION)
        locale.setlocale(locale.LC_TIME, "")
        dt = datetime.datetime(int(YEAR), int(MONTH), int(DAY)).strftime('%x')
        self._construct_format(dt)
        
    def format(self, year, month, day):
        lst = self._get_data_list(year, month, day)
        return self._format % lst
    
    def parse(self, dt):
        fields = dt.split(self._separator)
        year = int(fields[self._fields[YEAR]])
        month = int(fields[self._fields[MONTH]])
        day = int(fields[self._fields[DAY]])
        return year, month, day    

    def _construct_format(self, dt):
        self._separator = self._find_separator(dt)
        self._fields = self._get_fields(dt)
        self._format = self._get_format(dt)
        
    def _find_separator(self, dt):
        return re.search('\D', dt).group()
    
    def _get_fields(self, dt):
        keys = dt.split(self._separator)
        return {keys[0]:0, keys[1]:1, keys[2]:2}

    def _get_format(self, dt):
        dt = dt.replace(YEAR, "%04d")
        dt = dt.replace(MONTH, "%02d")
        dt = dt.replace(DAY, "%02d")
        return dt

    def _get_data_list(self, year, month, day):
        result = [0, 0, 0]
        result[self._fields[YEAR]] = year
        result[self._fields[MONTH]] = month
        result[self._fields[DAY]] = day
        return tuple(result)
