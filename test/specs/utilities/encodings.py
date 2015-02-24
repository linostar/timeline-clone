

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
import os

from timelinelib.utilities.encodings import to_unicode


TESTFILE = "testdata.txt"


class describe_to_unicode_function(unittest.TestCase):

    def test_can_open_url(self):
        self.save_file_data()
        self.assertTrue(isinstance(to_unicode(self.read_file_data()), unicode))
        self.remove_file()

    def test_can_url(self):
        self.assertTrue(isinstance(to_unicode(u"123abc"), unicode))

    def save_file_data(self):
        f = open(TESTFILE, "w")
        for i in range(256):
            try:
                f.write(chr(i))
            except:
                pass
        f.close()

    def read_file_data(self):
        f = open(TESTFILE, "r")
        url = f.read()
        f.close()
        return url

    def remove_file(self):
        os.remove(TESTFILE)
