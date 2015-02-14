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

import timelinelib.calendar
from timelinelib.features.experimental.experimentalfeatures import LOCALE_DATE


YEAR = "3333"
MONTH = "11"
DAY = "22"


class describe_experimental_feature_date_formatting(unittest.TestCase):
    
    def test_big_endian_can_be_formatted(self):
        self.given_sample_date("%s-%s-%s" % (YEAR, MONTH, DAY))
        self.assertEqual("2014-11-02", self.ef.format(2014, 11, 2))
    
    def test_middle_endian_can_be_formatted(self):
        self.given_sample_date("%s/%s/%s" % (MONTH, DAY, YEAR))
        self.assertEqual("11/02/2014", self.ef.format(2014, 11, 2))
    
    def test_little_endian_can_be_formatted(self):
        self.given_sample_date("%s.%s.%s" % (DAY, MONTH, YEAR))
        self.assertEqual("02.11.2014", self.ef.format(2014, 11, 2))
    
    def test_big_endian_format_can_be_parsed(self):
        self.given_sample_date("%s-%s-%s" % (YEAR, MONTH, DAY))
        self.assertEqual((2014,11,2), self.ef.parse("2014-11-02"))

    def test_middle_endian_format_can_be_parsed(self):
        self.given_sample_date("%s/%s/%s" % (MONTH, DAY, YEAR))
        self.assertEqual((2014,11,2), self.ef.parse("11/02/2014"))
    
    def test_little_endian_format_can_be_parsed(self):
        self.given_sample_date("%s.%s.%s" % (DAY, MONTH, YEAR))
        self.assertEqual((2014,11,2), self.ef.parse("02.11.2014"))
        
    def given_sample_date(self, sample_date):
        self.ef._construct_format(sample_date)
        
    def setUp(self):
        self.ef = LOCALE_DATE
