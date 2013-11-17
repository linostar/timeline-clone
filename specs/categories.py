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

from timelinelib.db.backends.memory import MemoryDB
from timelinelib.db.objects import Category
from timelinelib.drawing.viewproperties import ViewProperties
from timelinelib.repositories.categories import CategoriesFacade


class queries(unittest.TestCase):

    def test_get_all(self):
        self.assertEqual(self.categories.get_all(),
                         self.category_list)

    def test_get_immediate_children(self):
        self.assertEqual(self.categories.get_immediate_children(self.work),
                         [self.report])

    def test_get_all_children(self):
        self.assertEqual(self.categories.get_all_children(self.work),
                         [self.report, self.monthly_report, self.yearly_report])

    def test_get_parents(self):
        self.assertEqual(set(self.categories.get_parents(self.monthly_report)),
                         set([self.work, self.report]))
        
    def test_get_parents_for_checked_childs(self):
        self.checked_categories = (self.monthly_report,)
        self.assertEqual(set(self.categories.get_parents_for_checked_childs()),
                         set([self.work, self.report]))

    def setUp(self):
        self.category_list = []
        self.view_properties = Mock(ViewProperties)
        self.view_properties.is_category_visible.side_effect = self._is_category_visible
        self.db = Mock(MemoryDB)
        self.db.get_categories.return_value = self.category_list
        self.categories = CategoriesFacade(self.db, self.view_properties)
        self._create_example_tree()

    def _is_category_visible(self, category):
        return category in self.checked_categories
        
    def _create_example_tree(self):
        self.work = self.add_category("Work")
        self.report = self.add_category("Report", parent=self.work)
        self.monthly_report = self.add_category("Monthly report", parent=self.report)
        self.yearly_report = self.add_category("Yearly report", parent=self.report)
        self.play = self.add_category("Play")
        self.football = self.add_category("Football", parent=self.play)

    def add_category(self, name, parent=None):
        category = Category(name, color=(0, 0, 0), font_color=(0, 0, ),
                            visible=True, parent=parent)
        self.category_list.append(category)
        return category
