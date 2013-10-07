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

from timelinelib.db.objects import Category
from timelinelib.db.utils import IdCounter
from timelinelib.drawing.viewproperties import ViewProperties
from timelinelib.wxgui.components.categorytree import CustomCategoryTreeModel


class Base(unittest.TestCase):

    def setUp(self):
        self.id_counter = IdCounter()
        self.view_properties = ViewProperties()

    def create_category(self, name, parent=None):
        category = Category(name, (0, 0, 0), (0, 0, 0), True, parent=parent)
        category.set_id(self.id_counter.get_next())
        return category


class category_visibility(Base):

    def test_visible_by_default(self):
        work = self.create_category("Work", parent=None)
        self.assertTrue(self.view_properties.category_visible(work))

    def test_can_set_visibility(self):
        work = self.create_category("Work", parent=None)
        self.view_properties.set_category_visible(work, True)
        self.assertTrue(self.view_properties.category_visible(work))
        self.view_properties.set_category_visible(work, False)
        self.assertFalse(self.view_properties.category_visible(work))


class actual_category_visiblity(Base):

    def setUp(self):
        Base.setUp(self)
        self.work = self.create_category("Work", parent=None)
        self.meetings = self.create_category("Meetings", parent=self.work)
        self.fun_meetings = self.create_category("Fun meetings", parent=self.meetings)
        self.boring_meetings = self.create_category("Boring meetings", parent=self.meetings)

    def assert_actually_visible(self, category):
        self.assertTrue(self.view_properties.category_actually_visible(category))

    def assert_actually_hidden(self, category):
        self.assertFalse(self.view_properties.category_actually_visible(category))

    def test_visible_by_default(self):
        self.assert_actually_visible(self.boring_meetings)

    def test_children_hidden_if_parent_hidden(self):
        self.view_properties.set_category_visible(self.work, False)
        self.assert_actually_hidden(self.boring_meetings)

    def test_children_visible_if_parent_hidden_and_individual_view(self):
        self.view_properties.view_cats_individually = True
        self.view_properties.set_category_visible(self.work, False)
        self.assert_actually_visible(self.boring_meetings)
