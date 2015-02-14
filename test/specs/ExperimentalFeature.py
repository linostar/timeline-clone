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

from timelinelib.features.experimental.experimentalfeature import ExperimentalFeature


DISPLAY_NAME = "Display name"
DESCRIPTION = "Display description"


class describe_experimental_feature(unittest.TestCase):
    
    def test_has_a_display_name(self):
        self.assertEqual(DISPLAY_NAME, self.feature.get_display_name())
    
    def test_has_a_description(self):
        self.assertEqual(DESCRIPTION, self.feature.get_description())
    
    def test_is_not_activated_by_default(self):
        self.assertFalse(self.feature.enabled())
    
    def test_can_be_activated(self):
        self.feature.set_active(True)
        self.assertTrue(self.feature.enabled())
        
    def test_can_be_deactivated(self):
        self.feature.set_active(True)
        self.feature.set_active(False)
        self.assertFalse(self.feature.enabled())
        
    def test_can_format_config_string(self):
        self.assertEqual("%s=False;" % DISPLAY_NAME, self.feature.get_config())
    
    def setUp(self):
        self.feature = ExperimentalFeature(DISPLAY_NAME, DESCRIPTION)
