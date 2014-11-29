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

from timelinelib.features.experimental.experimentalfeaturedone import ExperimentalFeatureDone
from timelinelib.features.experimental.experimentalfeaturedone import DISPLAY_NAME
from timelinelib.features.experimental.experimentalfeaturedone import DESCRIPTION


class describe_experimental_feature_done(unittest.TestCase):
    
    def test_has_displayname(self):
        self.assertEqual(DISPLAY_NAME, self.ef.get_display_name())
        
    def test_has_description(self):
        self.assertEqual(DESCRIPTION, self.ef.get_description())
        
    def setUp(self):
        self.ef = ExperimentalFeatureDone()

