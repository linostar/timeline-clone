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

from mock import Mock

from timelinelib.time import NumTimeType
from timelinelib.db.objects import TimePeriod


class NumTimeTypeSpec(unittest.TestCase):

    def setUp(self):
        self.time_type = NumTimeType()

    def testReturnsHalfDelta(self):
        delta = 126
        half_delta = self.time_type.half_delta(delta)
        self.assertEquals(63, half_delta) 

    def testReturnsMarginDelta(self):
        delta = 24 * 12345
        margin_delta = self.time_type.margin_delta(delta)
        self.assertEquals(12345, margin_delta) 
