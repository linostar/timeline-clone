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

from timelinelib.db.utils import IdCounter
from timelinelib.db.objects import Category
from timelinelib.wxgui.components.categorytree import CustomCategoryTreeModel


class CategoryTreeModelSpec(unittest.TestCase):

    def test_has_no_items_when_no_timeline_view_set(self):
        self.assert_model_has_itmes_matching([])

    def test_has_no_items_when_no_categories_available(self):
        self.model.set_timeline_view(self.timeline_view)
        self.assert_model_has_itmes_matching([])

    def test_has_items_for_categories(self):
        play_category = self.add_category("Play", (255, 0, 100), False)
        work_category = self.add_category("Work", (88, 55, 22), True)
        self.model.set_timeline_view(self.timeline_view)
        self.assert_model_has_itmes_matching([
            {
                "id": play_category.id,
                "name": "Play",
                "visible": False,
                "color": (255, 0, 100),
            },
            {
                "id": work_category.id,
                "name": "Work",
                "visible": True,
                "color": (88, 55, 22),
            },
        ])

    def test_includes_bounding_box_information_for_items(self):
        self.model.ITEM_HEIGHT_PX = 20
        self.add_category("Play")
        self.add_category("Work")
        self.model.set_timeline_view(self.timeline_view)
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
        self.model.set_timeline_view(self.timeline_view)
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

    def test_sorts_categories_at_same_level(self):
        self.add_category("Work")
        self.add_category("Reading")
        self.model.set_timeline_view(self.timeline_view)
        self.assert_model_has_item_names(["Reading", "Work"])

    def test_can_set_view_multiple_times_without_items_duplicating(self):
        self.add_category("Work")
        self.model.set_timeline_view(self.timeline_view)
        self.model.set_timeline_view(self.timeline_view)
        self.assertEqual(len(self.model.get_items()), 1)

    def test_toggles_expandedness(self):
        self.model.ITEM_HEIGHT_PX = 20
        self.add_category("Reading")
        self.add_category("Work")
        self.model.set_timeline_view(self.timeline_view)
        self.assert_model_has_itmes_matching([
            { "name": "Reading", "expanded": True, },
            { "name": "Work",    "expanded": True, },
        ])
        self.model.toggle_expandedness(25)
        self.assert_model_has_itmes_matching([
            { "name": "Reading", "expanded": True, },
            { "name": "Work",    "expanded": False, },
        ])
        self.model.toggle_expandedness(25)
        self.assert_model_has_itmes_matching([
            { "name": "Reading", "expanded": True, },
            { "name": "Work",    "expanded": True, },
        ])

    def test_does_not_toggle_expandedness_if_doing_it_out_of_range(self):
        self.model.ITEM_HEIGHT_PX = 20
        self.add_category("Work")
        self.add_category("Reading")
        self.model.set_timeline_view(self.timeline_view)
        before = [x["expanded"] for x in self.model.get_items()]
        self.model.toggle_expandedness(50)
        after = [x["expanded"] for x in self.model.get_items()]
        self.assertEqual(before, after)

    def test_hides_subtrees_if_parent_not_expanded(self):
        self.model.ITEM_HEIGHT_PX = 20
        work_category = self.add_category("Work", (255, 0, 100), False)
        self.add_category("Reading", (0, 255, 0), False, work_category)
        self.model.set_timeline_view(self.timeline_view)
        self.assert_model_has_item_names(["Work", "Reading"])
        self.model.toggle_expandedness(5)
        self.assert_model_has_item_names(["Work"])

    def setUp(self):
        self.id_counter = IdCounter()

        self.categories = []
        self.visible_categories = []

        timeline = Mock()
        timeline.get_categories.return_value = self.categories

        def category_visible(category):
            return category in self.visible_categories
        view_properties = Mock()
        view_properties.category_visible.side_effect = category_visible

        timeline_view = Mock()
        timeline_view.get_timeline.return_value = timeline
        timeline_view.get_view_properties.return_value = view_properties

        self.timeline_view = timeline_view

        self.model = CustomCategoryTreeModel()

    def add_category(self, name, color=(0, 0, 0), visible=True, parent=None):
        category = Category(name, color, (0, 0, 0), True, parent=parent)
        category.set_id(self.id_counter.get_next())
        if visible:
            self.visible_categories.append(category)
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
