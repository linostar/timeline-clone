# Copyright (C) 2009, 2010  Rickard Lindberg, Roger Lindberg
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
        # Setup mock for db with this category configuration:
        # foo
        #   foofoo
        # bar
        self.db = Mock()
        self.foo = Category("foo", (255, 0, 0), True, parent=None)
        self.foofoo = Category("foofoo", (255, 0, 0), True, parent=self.foo)
        self.bar = Category("bar", (255, 0, 0), True, parent=None)
        self.db.get_categories.return_value = [self.foo, self.foofoo, self.bar]
        # Setup mock for view
        self.view = Mock()

    def testInitFromCategory(self):
        controller = CategoryEditorController(self.view, self.db, self.foofoo)
        controller.initialize()
        self.view.set_category_tree.assert_called_with([
            (self.bar, []),
            (self.foo, [])
            # foofoo should not be included since it is being edited
        ])
        self.view.set_name.assert_called_with("foofoo")
        self.view.set_color.assert_called_with((255, 0, 0))
        self.view.set_parent.assert_called_with(self.foo)

    def testInitFromNone(self):
        controller = CategoryEditorController(self.view, self.db, None)
        controller.initialize()
        # Default values when creating a new category
        self.view.set_category_tree.assert_called_with([
            (self.bar, []),
            (self.foo, [
                (self.foofoo, [])
            ])
        ])
        self.view.set_name.assert_called_with("")
        self.view.set_color.assert_called_with((255, 0, 0))
        self.view.set_parent.assert_called_with(None)

    def testSaveNew(self):
        controller = CategoryEditorController(self.view, self.db, None)
        # Simulate entering this in gui
        self.view.get_name.return_value = "new_cat"
        self.view.get_color.return_value = (255, 44, 0)
        self.view.get_parent.return_value = self.foo
        controller.save()
        # Assert that controller fetched data from view
        self.assertTrue(self.view.get_name.called)
        self.assertTrue(self.view.get_color.called)
        self.assertTrue(self.view.get_parent.called)
        # Assert that category was saved to db with correct attributes
        saved_cats = self.db.save_category.call_args_list
        self.assertEquals(len(saved_cats), 1)
        # first arg, ordered args, first ordered arg
        saved_cat = saved_cats[0][0][0]
        self.assertEquals(saved_cat.name, "new_cat")
        self.assertEquals(saved_cat.color, (255, 44, 0))
        self.assertEquals(saved_cat.parent, self.foo)
        # Assert that controller closed dialog
        self.assertTrue(self.view.close.called)

    def testSaveExisting(self):
        controller = CategoryEditorController(self.view, self.db, self.foo)
        # Simulate that gui is populated from foo
        self.view.get_name.return_value = self.foo.name
        self.view.get_color.return_value = self.foo.color
        self.view.get_parent.return_value = self.foo.parent
        controller.save()
        # Assert that controller fetched data from view
        self.assertTrue(self.view.get_name.called)
        self.assertTrue(self.view.get_color.called)
        self.assertTrue(self.view.get_parent.called)
        # Assert that category was saved to db with correct attributes
        saved_cats = self.db.save_category.call_args_list
        self.assertEquals(len(saved_cats), 1)
        # first arg, ordered args, first ordered arg
        saved_cat = saved_cats[0][0][0]
        self.assertEquals(saved_cat.name, self.foo.name)
        self.assertEquals(saved_cat.color, self.foo.color)
        self.assertEquals(saved_cat.parent, self.foo.parent)
        # Assert that controller closed dialog
        self.assertTrue(self.view.close.called)

    def testInvalidName(self):
        controller = CategoryEditorController(self.view, self.db, None)
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
        controller = CategoryEditorController(self.view, self.db, None)
        # Simulate name foo which is already in use
        self.view.get_name.return_value = "foo"
        controller.save()
        # Assert that category was not saved to db
        self.assertFalse(self.db.save_category.called)
        # Assert that controller let view handle error
        self.assertTrue(self.view.handle_used_name.called)
        # Assert that controller did not close view
        self.assertFalse(self.view.close.called)

    def testDbErrorOnInit(self):
        controller = CategoryEditorController(self.view, self.db, None)
        # Simulate TimelineIOError when we try to get categories from db
        self.db.get_categories.side_effect = TimelineIOError
        controller.initialize()
        # Assert that controller let view handle error
        self.assertTrue(self.view.handle_db_error.called)
        # Assert that controller did not close view
        self.assertFalse(self.view.close.called)

    def testDbErrorOnSave(self):
        controller = CategoryEditorController(self.view, self.db, None)
        # Simulate TimelineIOError when we try to save a valid category
        self.db.save_category.side_effect = TimelineIOError
        self.view.get_name.return_value = "foobar"
        controller.save()
        # Assert that controller let view handle error
        self.assertTrue(self.view.handle_db_error.called)
        # Assert that controller did not close view
        self.assertFalse(self.view.close.called)
