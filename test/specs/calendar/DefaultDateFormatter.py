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


import unittest

from timelinelib.calendar.defaultdateformatter import DefaultDateFormatter


class describe_date_formatter(unittest.TestCase):
    
    def test_format_return_yyyy_mm_dd(self):
        self.assertEquals("2014-11-30", self.formatter.format(2014,11, 30))
    
    def test_parse_return_year_mont_day(self):
        self.assertEquals((2014, 11, 30), self.formatter.parse("2014-11-30"))
    
    def setUp(self):
        self.formatter = DefaultDateFormatter()