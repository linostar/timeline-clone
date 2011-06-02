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

from timelinelib.wxgui.dialogs.categoryeditor import CategoryEditor
from timelinelib.wxgui.dialogs.categoryeditor import CategoryEditorController
from timelinelib.db.interface import TimelineDB
from timelinelib.db.interface import TimelineIOError
from timelinelib.db.objects import Category


class CategoryEditorBaseFixture(unittest.TestCase):

    def setUp(self):
        # Category configuration:
        # foo
        #   foofoo
        # bar
        self.db = Mock(TimelineDB)
        self.foo = Category("foo", (255, 0, 0), True, parent=None)
        self.foofoo = Category("foofoo", (255, 0, 0), True, parent=self.foo)
        self.bar = Category("bar", (255, 0, 0), True, parent=None)
        self.db.get_categories.return_value = [self.foo, self.foofoo, self.bar]
        self.view = Mock(CategoryEditor)

    def _initializeControllerWith(self, category):
        self.controller = CategoryEditorController(self.view, self.db, category)
        self.controller.initialize()


class WhenEditingANewCategory(CategoryEditorBaseFixture):

    def setUp(self):
        CategoryEditorBaseFixture.setUp(self)
        self._initializeControllerWith(None)

    def testAllCategoriesInDbAreListedAsPossibleParents(self):
        self.view.set_category_tree.assert_called_with([
            (self.bar, []),
            (self.foo, [
                (self.foofoo, [])
            ])
        ])

    def testNameIsInitializedToEmptyString(self):
        self.view.set_name.assert_called_with("")

    def testColorIsInitialixedToRed(self):
        self.view.set_color.assert_called_with((255, 0, 0))

    def testParentIsInitializedToNone(self):
        self.view.set_parent.assert_called_with(None)


class WhenEditingAnExistingCategory(CategoryEditorBaseFixture):

    def setUp(self):
        CategoryEditorBaseFixture.setUp(self)
        self._initializeControllerWith(self.foofoo)

    def testAllCategoriesInDbExceptTheOneBeingEditedArePossibleParents(self):
        self.view.set_category_tree.assert_called_with([
            (self.bar, []),
            (self.foo, [])
        ])

    def testNameIsInitializedFromEditedCategory(self):
        self.view.set_name.assert_called_with("foofoo")

    def testColorIsInitialixedFromEditedCategory(self):
        self.view.set_color.assert_called_with((255, 0, 0))

    def testParentIsInitializedFromEditedCategory(self):
        self.view.set_parent.assert_called_with(self.foo)


class WhenTryingToEditACategoryButDbRaisesException(CategoryEditorBaseFixture):

    def setUp(self):
        CategoryEditorBaseFixture.setUp(self)
        self.db.get_categories.side_effect = TimelineIOError
        self._initializeControllerWith(None)

    def testErrorIsHandledByView(self):
        self.assertTrue(self.view.handle_db_error.called)

    def testTheDialogIsNotClosed(self):
        self.assertFalse(self.view.close.called)


class WhenSavingACategory(CategoryEditorBaseFixture):

    def setUp(self):
        CategoryEditorBaseFixture.setUp(self)
        self._initializeControllerWith(None)
        self.view.get_name.return_value = "new_cat"
        self.view.get_color.return_value = (255, 44, 0)
        self.view.get_parent.return_value = self.foo
        self.controller.save()

    def _getSavedCategory(self):
        if not self.db.save_category.called:
            self.fail("No category was saved.")
        return self.db.save_category.call_args_list[0][0][0]

    def testSavedCategoryHasNameFromView(self):
        self.assertEquals("new_cat", self._getSavedCategory().name)

    def testSavedCategoryHasColorFromView(self):
        self.assertEquals((255, 44, 0), self._getSavedCategory().color)

    def testSavedCategoryHasParentFromView(self):
        self.assertEquals(self.foo, self._getSavedCategory().parent)

    def testTheDialogIsClosed(self):
        self.assertTrue(self.view.close.called)


class WhenTryingToSaveACategoryButDbRaisesException(CategoryEditorBaseFixture):

    def setUp(self):
        CategoryEditorBaseFixture.setUp(self)
        self._initializeControllerWith(None)
        self.view.get_name.return_value = "foobar"
        self.db.save_category.side_effect = TimelineIOError
        self.controller.save()

    def testErrorIsHandledByView(self):
        self.assertTrue(self.view.handle_db_error.called)

    def testTheDialogIsNotClosed(self):
        self.assertFalse(self.view.close.called)


class WhenSavingACategoryWithAnInvalidName(CategoryEditorBaseFixture):

    def setUp(self):
        CategoryEditorBaseFixture.setUp(self)
        self._initializeControllerWith(None)
        self.view.get_name.return_value = ""
        self.controller.save()

    def testTheCategoryIsNotSavedToDb(self):
        self.assertFalse(self.db.save_category.called)

    def testTheViewShowsAnErrorMessage(self):
        self.assertTrue(self.view.handle_invalid_name.called)

    def testTheDialogIsNotClosed(self):
        self.assertFalse(self.view.close.called)


class WhenSavingACategoryWithAUsedName(CategoryEditorBaseFixture):

    def setUp(self):
        CategoryEditorBaseFixture.setUp(self)
        self._initializeControllerWith(None)
        self.view.get_name.return_value = "foo"
        self.controller.save()

    def testTheCategoryIsNotSavedToDb(self):
        self.assertFalse(self.db.save_category.called)

    def testTheViewShowsAnErrorMessage(self):
        self.assertTrue(self.view.handle_used_name.called)

    def testTheDialogIsNotClosed(self):
        self.assertFalse(self.view.close.called)
