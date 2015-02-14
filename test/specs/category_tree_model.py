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

from specs.utils import a_category_with
from timelinelib.data.idnumber import get_process_unique_id
from timelinelib.wxgui.components.categorytree import CategoriesFacade
from timelinelib.wxgui.components.categorytree import CustomCategoryTreeModel


class Base(unittest.TestCase):

    def setUp(self):
        self.categories = []
        self.visible_categories = []
        self.actually_visible_categories = []

        self.categories_facade = Mock(CategoriesFacade)
        self.categories_facade.get_all.return_value = self.categories
        self.categories_facade.is_visible.side_effect = self._category_visible
        self.categories_facade.is_event_with_category_visible.side_effect = self._event_with_category_visible

        self.model = CustomCategoryTreeModel()

    def _category_visible(self, category):
        return category in self.visible_categories

    def _event_with_category_visible(self, category):
        return category in self.actually_visible_categories

    def add_category(self, name, color=(0, 0, 0), visible=True, actually_visible=True, parent=None):
        category = a_category_with(name=name, color=color, parent=parent)
        category.set_id(get_process_unique_id())
        if visible:
            self.visible_categories.append(category)
        if actually_visible:
            self.actually_visible_categories.append(category)
        self.categories.append(category)
        return category

    def assert_model_has_itmes_matching(self, expected_entries):
        self.assertEqual(len(self.model.get_items()), len(expected_entries))
        for i in range(len(self.model.get_items())):
            for key in expected_entries[i]:
                self.assertEqual(self.model.get_items()[i][key],
                                 expected_entries[i][key])

    def assert_model_has_item_names(self, expected_names):
        self.assertEqual([x["name"] for x in self.model.get_items()], expected_names)


class setting_categories(Base):

    def test_has_no_items_when_no_timeline_view_set(self):
        self.assert_model_has_itmes_matching([])

    def test_has_no_items_when_no_categories_available(self):
        self.model.set_categories(self.categories_facade)
        self.assert_model_has_itmes_matching([])

    def test_has_items_for_each_category(self):
        self.add_category("Play")
        self.add_category("Work")
        self.model.set_categories(self.categories_facade)
        self.assert_model_has_item_names(["Play", "Work"])

    def test_can_set_view_multiple_times_without_items_duplicating(self):
        self.add_category("Work")
        self.model.set_categories(self.categories_facade)
        self.model.set_categories(self.categories_facade)
        self.assertEqual(len(self.model.get_items()), 1)


class item_properties(Base):

    def test_has_items_for_categories(self):
        play_category = self.add_category(
            "Play", (255, 0, 100), visible=False, actually_visible=True)
        work_category = self.add_category(
            "Work", (88, 55, 22), visible=True, actually_visible=False)
        self.model.set_categories(self.categories_facade)
        self.assert_model_has_itmes_matching([
            {
                "id": play_category.get_id(),
                "name": "Play",
                "visible": False,
                "actually_visible": True,
                "color": (255, 0, 100),
                "category": play_category,
            },
            {
                "id": work_category.get_id(),
                "name": "Work",
                "visible": True,
                "actually_visible": False,
                "color": (88, 55, 22),
                "category": work_category,
            },
        ])

    def test_has_child_attribute(self):
        play_category = self.add_category("Play")
        work_category = self.add_category("Work", parent=play_category)
        self.model.set_categories(self.categories_facade)
        self.assert_model_has_itmes_matching([
            {
                "name": "Play",
                "has_children": True,
            },
            {
                "name": "Work",
                "has_children": False,
            },
        ])


class bounding_box(Base):

    def test_includes_bounding_box_information_for_items(self):
        self.model.ITEM_HEIGHT_PX = 20
        self.add_category("Play")
        self.add_category("Work")
        self.model.set_categories(self.categories_facade)
        self.model.set_view_size(200, 900)
        self.assert_model_has_itmes_matching([
            {
                "name": "Play",
                "x": 0,
                "y": 0,
                "width": 200,
            },
            {
                "name": "Work",
                "x": 0,
                "y": 20,
                "width": 200,
            },
        ])

    def test_has_indented_bounding_box_for_child_categories(self):
        self.model.INDENT_PX = 10
        work_category = self.add_category("Work")
        self.add_category("Reading", parent=work_category)
        self.model.set_view_size(200, 900)
        self.model.set_categories(self.categories_facade)
        self.assert_model_has_itmes_matching([
            {
                "name": "Work",
                "x": 0,
                "width": 200,
            },
            {
                "name": "Reading",
                "x": 10,
                "width": 190,
            },
        ])


class sorting(Base):

    def test_sorts_categories_at_same_level(self):
        self.add_category("Work")
        self.add_category("Reading")
        self.model.set_categories(self.categories_facade)
        self.assert_model_has_item_names(["Reading", "Work"])


class hit_test(Base):

    def test_can_get_category(self):
        reading = self.add_category("Reading")
        work = self.add_category("Work")
        self.model.set_categories(self.categories_facade)
        self.assertEqual(self.model.hit(0, 0).get_category(), reading)
        self.assertEqual(self.model.hit(0, 25).get_category(), work)
        self.assertEqual(self.model.hit(0, 45).get_category(), None)

    def test_can_check_if_hit_arrow(self):
        reading = self.add_category("Reading")
        self.model.set_categories(self.categories_facade)
        self.assertEqual(self.model.hit(5, 10).is_on_arrow(), True)
        self.assertEqual(self.model.hit(0, 25).is_on_arrow(), False)

    def test_can_check_if_hit_checkbox(self):
        reading = self.add_category("Reading")
        self.model.set_categories(self.categories_facade)
        self.assertEqual(self.model.hit(25, 10).is_on_checkbox(), True)
        self.assertEqual(self.model.hit(0, 25).is_on_checkbox(), False)

    def setUp(self):
        Base.setUp(self)
        self.model.ITEM_HEIGHT_PX = 20


class expandedness(Base):

    def test_can_toggle(self):
        reading = self.add_category("Reading")
        work = self.add_category("Work")
        self.model.set_categories(self.categories_facade)
        self.assert_model_has_itmes_matching([
            { "name": "Reading", "expanded": True, },
            { "name": "Work",    "expanded": True, },
        ])
        self.model.toggle_expandedness(work)
        self.assert_model_has_itmes_matching([
            { "name": "Reading", "expanded": True, },
            { "name": "Work",    "expanded": False, },
        ])
        self.model.toggle_expandedness(work)
        self.assert_model_has_itmes_matching([
            { "name": "Reading", "expanded": True, },
            { "name": "Work",    "expanded": True, },
        ])

    def test_hides_subtrees_if_parent_not_expanded(self):
        work_category = self.add_category("Work")
        self.add_category("Reading", parent=work_category)
        self.model.set_categories(self.categories_facade)
        self.assert_model_has_item_names(["Work", "Reading"])
        self.model.toggle_expandedness(work_category)
        self.assert_model_has_item_names(["Work"])
