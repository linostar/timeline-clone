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

from specs.utils import a_category_with
from timelinelib.data import sort_categories


class CategorySorter(unittest.TestCase):

    def test_sorts_categories_by_name(self):
        self.sort([
            a_category_with(name="b"),
            a_category_with(name="a")])
        self.assert_sorted_in_order(["a", "b"])

    def test_ignores_case(self):
        self.sort([
            a_category_with(name="Foo"),
            a_category_with(name="bar")])
        self.assert_sorted_in_order(["bar", "Foo"])

    def sort(self, categories):
        self.sorted_categories = sort_categories(categories)

    def assert_sorted_in_order(self, names):
        self.assertEqual(
            names,
            [category.get_name() for category in self.sorted_categories])
