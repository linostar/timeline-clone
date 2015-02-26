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
        self.assertEqual((2014, 11, 2), self.ef.parse("2014-11-02"))

    def test_middle_endian_format_can_be_parsed(self):
        self.given_sample_date("%s/%s/%s" % (MONTH, DAY, YEAR))
        self.assertEqual((2014, 11, 2), self.ef.parse("11/02/2014"))

    def test_little_endian_format_can_be_parsed(self):
        self.given_sample_date("%s.%s.%s" % (DAY, MONTH, YEAR))
        self.assertEqual((2014, 11, 2), self.ef.parse("02.11.2014"))

    def test_all_endians_can_be_parsed(self):
        date_strings = [# year, month, day
                        ("2015-02-01", "3333-11-22"),
                        ("2015/02/01", "3333/11/22"),
                        ("2015.02.01", "3333.11.22"),
                        ("2015 02 01", "3333 11 22"),
                        ("2015-2-1", "3333-1-2"),
                        ("2015/2/1", "3333/1/2"),
                        ("2015.2.1", "3333.1.2"),
                        ("2015 2 1", "3333 1 2"),
                        # day, month, year
                        ("01-02-2015", "22-11-3333"),
                        ("01/02/2015", "22/11/3333"),
                        ("01.02.2015", "22.11.3333"),
                        ("01 02 2015", "22 11 3333"),
                        ("1-2-2015", "2-1-3333"),
                        ("1/2/2015", "2/1/3333"),
                        ("1.2.2015", "2.1.3333"),
                        ("1 2 2015", "2 1 3333"),
                        # month, day, year
                        ("02-01-2015", "11-22-3333"),
                        ("02/01/2015", "11/22/3333"),
                        ("02.01.2015", "11.22.3333"),
                        ("02 01 2015", "11 22 3333"),
                        ("2-1-2015", "1-2-3333"),
                        ("2/1/2015", "1/2/3333"),
                        ("2.1.2015", "1.2.3333"),
                        ("2 1 2015", "1 2 3333"),
                        ]
        for date_string, template in date_strings:
            self.given_sample_date(template)
            self.assertEqual((2015, 2, 1), self.ef.parse(date_string))

    def test_all_endians_with_2_digit_year_can_be_parsed(self):
        date_strings = [("15-02-01", "33-11-22"),
                        ("15/02/01", "33/11/22"),
                        ("15.02.01", "33.11.22"),
                        ("15 02 01", "33 11 22"),
                        ("15-2-1", "33-1-2"),
                        ("15/2/1", "33/1/2"),
                        ("15.2.1", "33.1.2"),
                        ("15 2 1", "33 1 2"),
                        # day, month, year
                        ("01-02-15", "22-11-33"),
                        ("01/02/15", "22/11/33"),
                        ("01.02.15", "22.11.33"),
                        ("01 02 15", "22 11 33"),
                        ("1-2-15", "2-1-33"),
                        ("1/2/15", "2/1/33"),
                        ("1.2.15", "2.1.33"),
                        ("1 2 15", "2 1 33"),
                        # month, day, year
                        ("02-01-15", "11-22-33"),
                        ("02/01/15", "11/22/33"),
                        ("02.01.15", "11.22.33"),
                        ("02 01 15", "11 22 33"),
                        ("2-1-15", "1-2-33"),
                        ("2/1/15", "1/2/33"),
                        ("2.1.15", "1.2.33"),
                        ("2 1 15", "1 2 33"),
                        ]
        for date_string, template in date_strings:
            self.given_sample_date(template)
            self.assertEqual((15, 2, 1), self.ef.parse(date_string))

    def given_sample_date(self, sample_date):
        self.ef._construct_format(sample_date)

    def setUp(self):
        self.ef = LOCALE_DATE

