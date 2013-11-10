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
from timelinelib.wxgui.components.categorytree import CustomCategoryTreeModel, CategoriesFacade


class Base(unittest.TestCase):

    def setUp(self):
        self.id_counter = IdCounter()

        self.categories = []
        self.visible_categories = []
        self.actually_visible_categories = []

        self.categories_facade = Mock(CategoriesFacade)
        self.categories_facade.get_all.return_value = self.categories
        self.categories_facade.is_visible.side_effect = self._category_visible
        self.categories_facade.is_event_with_category_visible.side_effect = self._event_with_category_visible
        self.categories_facade.set_visible.side_effect = self._set_visible

        self.model = CustomCategoryTreeModel()

    def _category_visible(self, category):
        return category in self.visible_categories

    def _event_with_category_visible(self, category):
        return category in self.actually_visible_categories

    def _set_visible(self, category_id, visible):
        def find_category_with_id(id):
            for category in self.categories:
                if category.id == id:
                    return category
        category = find_category_with_id(category_id)
        if visible:
            self.visible_categories.append(category)
        else:
            self.visible_categories.remove(category)
        self.categories_facade.listen_for_any.call_args[0][0]()

    def add_category(self, name, color=(0, 0, 0), visible=True, actually_visible=True, parent=None):
        category = Category(name, color, (0, 0, 0), True, parent=parent)
        category.set_id(self.id_counter.get_next())
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
        play_category = self.add_category("Play", (255, 0, 100), visible=False, actually_visible=True)
        work_category = self.add_category("Work", (88, 55, 22), visible=True, actually_visible=False)
        self.model.set_categories(self.categories_facade)
        self.assert_model_has_itmes_matching([
            {
                "id": play_category.id,
                "name": "Play",
                "visible": False,
                "actually_visible": True,
                "color": (255, 0, 100),
            },
            {
                "id": work_category.id,
                "name": "Work",
                "visible": True,
                "actually_visible": False,
                "color": (88, 55, 22),
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


class visibility(Base):

    def test_toggles_when_clicking_on_checkbox(self):
        self.model.ITEM_HEIGHT_PX = 20
        self.add_category("Reading")
        self.add_category("Work")
        self.model.set_categories(self.categories_facade)
        self.assert_model_has_itmes_matching([
            { "name": "Reading", "visible": True, },
            { "name": "Work",    "visible": True, },
        ])
        self.model.left_click(20, 25)
        self.assert_model_has_itmes_matching([
            { "name": "Reading", "visible": True, },
            { "name": "Work",    "visible": False, },
        ])
        self.model.left_click(20, 25)
        self.assert_model_has_itmes_matching([
            { "name": "Reading", "visible": True, },
            { "name": "Work",    "visible": True, },
        ])


class expandedness(Base):

    def test_toggles_when_clicking_on_arrow(self):
        self.model.ITEM_HEIGHT_PX = 20
        self.add_category("Reading")
        self.add_category("Work")
        self.model.set_categories(self.categories_facade)
        self.assert_model_has_itmes_matching([
            { "name": "Reading", "expanded": True, },
            { "name": "Work",    "expanded": True, },
        ])
        self.model.left_click(5, 25)
        self.assert_model_has_itmes_matching([
            { "name": "Reading", "expanded": True, },
            { "name": "Work",    "expanded": False, },
        ])
        self.model.left_click(5, 25)
        self.assert_model_has_itmes_matching([
            { "name": "Reading", "expanded": True, },
            { "name": "Work",    "expanded": True, },
        ])

    def test_does_not_toggle_if_clicking_outside_arrow(self):
        self.model.ITEM_HEIGHT_PX = 20
        self.add_category("Reading")
        self.add_category("Work")
        self.model.set_categories(self.categories_facade)
        before = [x["expanded"] for x in self.model.get_items()]
        self.model.left_click(50, 25)
        after = [x["expanded"] for x in self.model.get_items()]
        self.assertEqual(before, after)

    def test_does_not_toggle_if_clicking_outside_item(self):
        self.model.ITEM_HEIGHT_PX = 20
        self.add_category("Work")
        self.add_category("Reading")
        self.model.set_categories(self.categories_facade)
        before = [x["expanded"] for x in self.model.get_items()]
        self.model.left_click(5, 50)
        after = [x["expanded"] for x in self.model.get_items()]
        self.assertEqual(before, after)

    def test_hides_subtrees_if_parent_not_expanded(self):
        self.model.ITEM_HEIGHT_PX = 20
        work_category = self.add_category("Work")
        self.add_category("Reading", parent=work_category)
        self.model.set_categories(self.categories_facade)
        self.assert_model_has_item_names(["Work", "Reading"])
        self.model.left_click(5, 5)
        self.assert_model_has_item_names(["Work"])
