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

from timelinelib.feedback.feature import FeatureForm
from timelinelib.feedback.feature import FEATURES
from timelinelib.wxgui.dialogs.feature import FeatureDialog


class FeedbackFormSpec(unittest.TestCase):

    def test_shows_parts_in_dialog(self):
        key = FEATURES.keys()[0]
        self.form.populate(key)
        self.dialog.set_feature_name.assert_called_with(key)
        self.dialog.set_feature_description.assert_called_with(FEATURES[key])

    def setUp(self):
        self.dialog = Mock(FeatureDialog)
        self.form = FeatureForm(self.dialog)
