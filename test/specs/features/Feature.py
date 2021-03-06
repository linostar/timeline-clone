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

from timelinelib.feedback.featuredialogcontoller import FeatureDialogController
from timelinelib.features.installed.installedfeatures import InstalledFeatures
from timelinelib.features.feature import Feature
from timelinelib.wxgui.dialogs.feature import FeatureDialog


DISPLAY_NAME = "Display name"
DESCRIPTION = "Display description"
        

class FeedbackFormSpec(unittest.TestCase):

    def test_shows_parts_in_dialog(self):
        key = InstalledFeatures().get_all_features()[0]
        self.form.populate(key)
        self.dialog.set_feature_name.assert_called_with(key.get_display_name())
        self.dialog.set_feature_description.assert_called_with(key.get_description())

    def setUp(self):
        self.dialog = Mock(FeatureDialog)
        self.form = FeatureDialogController(self.dialog)
        

class describe_feature(unittest.TestCase):
    
    def test_has_a_display_name(self):
        self.assertEqual(DISPLAY_NAME, self.feature.get_display_name())
    
    def test_has_a_description(self):
        self.assertEqual(DESCRIPTION, self.feature.get_description())
    
    def setUp(self):
        self.feature = Feature(DISPLAY_NAME, DESCRIPTION)
