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

from timelinelib.config.experimentalfeatures import ExperimentalFeatures
from timelinelib.config.experimentalfeatures import experimental_feature_enabled


class describe_experimental_features(unittest.TestCase):
    
    def test_has_a_list_of_enabled_features(self):
        enabled_features = self.ef.get_enabled_features()
        self.assertTrue(isinstance(enabled_features, (list, tuple)))
                
    def test_has_a_list_of_all_features(self):
        features = self.ef.get_all_features()
        self.assertTrue(isinstance(features, (list, tuple)))
        self.assertTrue(len(features) > 0)
                
    def test_a_feature_can_be_enabled(self):
        enabled_features = self.ef.get_all_features()
        self.ef.enable(enabled_features[0])
        self.assertTrue(self.ef.enabled(enabled_features[0]))
      
    def test_all_features_can_be_enabled(self):
        self.ef.enable_all()
        for feature in self.ef.get_all_features():
            self.assertTrue(self.ef.enabled(feature))
      
    def test_a_feature_can_be_disabled(self):
        enabled_features = self.ef.get_all_features()
        self.ef.disable(enabled_features[0])
        self.assertFalse(self.ef.enabled(enabled_features[0]))

    def test_all_features_can_be_disabled(self):
        self.ef.disable_all()
        for feature in self.ef.get_all_features():
            self.assertFalse(self.ef.enabled(feature))
      
    def test_feature_test_exists(self):
        self.assertFalse(experimental_feature_enabled(0))
    
    def setUp(self):  
        self.ef = ExperimentalFeatures()
        self.enabled_features = self.ef.get_enabled_features()
        