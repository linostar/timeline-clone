# Copyright (C) 2009  Rickard Lindberg, Roger Lindberg
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

from timelinelib.gui.dialogs.categoryeditor import CategoryEditorController
from timelinelib.db.interface import TimelineIOError
from timelinelib.db.objects import Category


class TestCategoryEditorController(unittest.TestCase):

    def setUp(self):
        # Setup mock for db (we want one existing category in there named foo)
        self.db = Mock()
        existing_categories = [Category("foo", (0, 0, 0), True)]
        self.db.get_categories.return_value = existing_categories
        # Setup mock for view
        self.view = Mock()
        # Setup example new category
        self.ex_cat = Category("bar", (255, 0, 0), True)

    def testInitFromCategory(self):
        controller = CategoryEditorController(self.view, self.db, self.ex_cat)
        controller.initialize()
        self.view.set_name.assert_called_with("bar")
        self.view.set_color.assert_called_with((255, 0, 0))

    def testInitFromNone(self):
        controller = CategoryEditorController(self.view, self.db, None)
        controller.initialize()
        # Default values when creating a new category
        self.view.set_name.assert_called_with("")
        self.view.set_color.assert_called_with((255, 0, 0))

    def testSaveNew(self):
        controller = CategoryEditorController(self.view, self.db, None)
        # Simulate entering this in gui
        self.view.get_name.return_value = "new_cat"
        self.view.get_color.return_value = (255, 44, 0)
        controller.save()
        # Assert that controller fetched data from view
        self.assertTrue(self.view.get_name.called)
        self.assertTrue(self.view.get_color.called)
        # Assert that category was saved to db
        self.assertTrue(self.db.save_category.called)
        # Assert that controller closed dialog
        self.assertTrue(self.view.close.called)
        # Assert that the controller has a category (the one created)
        self.assertEquals(controller.category.name, "new_cat")

    def testSaveExisting(self):
        controller = CategoryEditorController(self.view, self.db, self.ex_cat)
        # Simulate that gui is populated from ex_cat
        self.view.get_name.return_value = self.ex_cat.name
        self.view.get_color.return_value = self.ex_cat.color
        controller.save()
        # Assert that controller fetched data from view
        self.assertTrue(self.view.get_name.called)
        self.assertTrue(self.view.get_color.called)
        # Assert that category was saved to db
        self.assertTrue(self.db.save_category.called)
        # Assert that controller closed dialog
        self.assertTrue(self.view.close.called)

    def testInvalidName(self):
        controller = CategoryEditorController(self.view, self.db, self.ex_cat)
        # Simulate a blank name which is invalid
        self.view.get_name.return_value = ""
        controller.save()
        # Assert that category was not saved to db
        self.assertFalse(self.db.save_category.called)
        # Assert that controller let view handle error
        self.assertTrue(self.view.handle_invalid_name.called)
        # Assert that controller did not close view
        self.assertFalse(self.view.close.called)

    def testUsedName(self):
        controller = CategoryEditorController(self.view, self.db, self.ex_cat)
        # Simulate name foo which is already in use
        self.view.get_name.return_value = "foo"
        controller.save()
        # Assert that category was not saved to db
        self.assertFalse(self.db.save_category.called)
        # Assert that controller let view handle error
        self.assertTrue(self.view.handle_used_name.called)
        # Assert that controller did not close view
        self.assertFalse(self.view.close.called)

    def testDbError(self):
        controller = CategoryEditorController(self.view, self.db, self.ex_cat)
        # Simulate TimelineIOError when we try to save a valid category
        self.db.save_category.side_effect = TimelineIOError
        self.view.get_name.return_value = "foobar"
        controller.save()
        # Assert that controller let view handle error
        self.assertTrue(self.view.handle_db_error.called)
        # Assert that controller did not close view
        self.assertFalse(self.view.close.called)
        # Assert that controller did not close view
        self.assertFalse(self.view.close.called)
