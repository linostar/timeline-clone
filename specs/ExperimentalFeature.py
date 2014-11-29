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

from timelinelib.config.experimentalfeaturedone import ExperimentalFeatureDone


class describe_experimental_feature(unittest.TestCase):
    
    def test_can_be_enabled(self):
        self.ef.set_active(True)
        self.assertTrue(self.ef.enabled())
        
    def test_can_be_disabled(self):
        self.ef.set_active(False)
        self.assertFalse(self.ef.enabled())
        
    def setUp(self):
        self.ef = ExperimentalFeatureDone()
        