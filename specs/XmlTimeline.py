# Copyright (C) 2009, 2010  Rickard Lindberg, Roger Lindberg
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

from timelinelib.db.backends.xmlfile import XmlTimeline
from timelinelib.time import WxTimeType


class XmlTimelineSpec(unittest.TestCase):

    def testUseWxTimeTypeWhenUseWideDateRangeIsTrue(self):
        timeline = XmlTimeline(None, load=False, use_wide_date_range=True)
        self.assertTrue(isinstance(timeline.time_type, WxTimeType))
        