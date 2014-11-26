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


EVENT_DONE = 0
CONTAINERS_DISPLAY = 1

FEATURES = (EVENT_DONE, CONTAINERS_DISPLAY)


class ExperimentalFeatures(object):
    
    def __init__(self):
        self.enabled_features = []
        #self.enable_all()
        
    def enabled(self, feature):
        return feature in self.enabled_features

    def enable(self, feature):
        if feature in FEATURES and feature not in self.enabled_features:
            self.enabled_features.append(feature)

    def enable_all(self):
        self.enabled_features = list(FEATURES)
                
    def disable(self, feature):
        if feature in FEATURES and feature in self.enabled_features:
            self.enabled_features.remove(feature)
            
    def disable_all(self):
        self.enabled_features = []
                
    def get_enabled_features(self):
        return self.enabled_features
    
    def get_all_features(self):
        return FEATURES
    
    
def experimental_feature_enabled(feature):
    return ExperimentalFeatures().enabled(feature)
