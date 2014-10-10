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


from specs.utils import a_category
from specs.utils import a_category_with
from specs.utils import CATEGORY_MODIFIERS
from specs.utils import TestCase
from timelinelib.data import Category


class describe_category(TestCase):

    def test_can_get_values(self):
        category = Category("work", (50, 100, 150), (0, 0, 0))
        self.assertEqual(category.get_id(), None)
        self.assertEqual(category.get_name(), "work")
        self.assertEqual(category.get_color(), (50, 100, 150))
        self.assertEqual(category.get_font_color(), (0, 0, 0))
        self.assertEqual(category.get_parent(), None)

    def test_can_set_values(self):
        self.assertEqual(
            a_category().set_id(15).get_id(),
            15)
        self.assertEqual(
            a_category().set_name("fun").get_name(),
            "fun")
        self.assertEqual(
            a_category().set_color((33, 66, 99)).get_color(),
            (33, 66, 99))
        self.assertEqual(
            a_category().set_font_color((11, 12, 13)).get_font_color(),
            (11, 12, 13))
        a_parent = a_category_with(name="parent")
        self.assertEqual(
            a_category().set_parent(a_parent).get_parent(),
            a_parent)

    def test_clone_eq_ne(self):
        self.assertCloneEqNe(a_category, CATEGORY_MODIFIERS)

    def test_can_be_compared(self):
        self.assertEqNeImplementationIsCorrect(a_category, CATEGORY_MODIFIERS)
