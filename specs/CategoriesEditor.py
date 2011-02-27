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

from timelinelib.gui.dialogs.categorieseditor import CategoriesEditor
from timelinelib.gui.dialogs.categorieseditor import CategoriesEditorController
from timelinelib.db.interface import TimelineDB
from timelinelib.db.objects import Category


class CategoriesTreeSpec(unittest.TestCase):

    def testCategoriesArePopulatedFromDbWhenInitializingFromDb(self):
        self.controller.initialize(self.db)
        self.view.initialize.assert_called_with(self.db)

    def setUp(self):
        self.db = Mock(TimelineDB)
        self.view = Mock(CategoriesEditor)
        self.controller = CategoriesEditorController(self.view, self.db)
