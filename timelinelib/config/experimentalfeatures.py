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


from timelinelib.config.experimentalfeaturedone import ExperimentalFeatureDone
from timelinelib.config.experimentalfeaturecontainersize import ExperimentalFeatureContainerSize


EVENT_DONE = ExperimentalFeatureDone()
EXTENDED_CONTAINER_HEIGHT = ExperimentalFeatureContainerSize()
FEATURES = (EVENT_DONE, EXTENDED_CONTAINER_HEIGHT)


class ExperimentalFeatures(object):
    
    def __str__(self):
        collector = []
        for feature in FEATURES:
            collector.append("%s=" % feature.get_display_name())
            if feature.enabled():
                collector.append("1")
            else:
                collector.append("0")
            collector.append(";")
        return "".join(collector)
    
    def set_from_string(self, cfg_string):
        for item in cfg_string.split(";"):
            if "=" in item:
                name, value = item.split("=")
                self.set_value_on_feature_by_name(name.strip(), value.strip() == "1")
        
    def set_value_on_feature_by_name(self, name, value):
        for feature in FEATURES:
            if feature.get_display_name() == name:
                feature.set_value(value)
                return
            
    def set_value_on_feature(self, feature_index, value):
        if value:
            FEATURES[feature_index].enable()
        else:
            FEATURES[feature_index].disable()
            
    def get_all_features(self):
        return FEATURES


def experimental_feature(foo):
    return foo
