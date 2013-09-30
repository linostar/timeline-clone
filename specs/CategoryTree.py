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

    def test_has_no_entries_when_no_categories(self):
        self.model.set_timeline_view(self.timeline_view)
        self.assert_model_has_entries([])

    def test_copies_event_properties_when_event_visible(self):
        self.add_category("Work", (255, 0, 100), True)
        self.model.set_timeline_view(self.timeline_view)
        self.assert_model_has_entries([
            {
                "id": 1,
                "name": "Work",
                "visible": True,
                "color": (255, 0, 100),
                "x": 0,
                "y": 0,
                "expanded": True,
            },
        ])

    def test_copies_event_properties_when_event_hidden(self):
        self.add_category("Work", (255, 0, 100), False)
        self.model.set_timeline_view(self.timeline_view)
        self.assert_model_has_entries([
            {
                "id": 1,
                "name": "Work",
                "visible": False,
                "color": (255, 0, 100),
                "x": 0,
                "y": 0,
                "expanded": True,
            },
        ])

    def test_flattens_category_hierarchy_with_indent_level(self):
        self.model.HEIGHT = 20
        self.model.INDENT_PX = 10
        work_category = self.add_category("Work", (255, 0, 100), False)
        self.add_category("Reading", (0, 255, 0), False, work_category)
        self.model.set_timeline_view(self.timeline_view)
        self.assert_model_has_entries([
            {
                "id": 1,
                "name": "Work",
                "visible": False,
                "color": (255, 0, 100),
                "x": 0,
                "y": 0,
                "expanded": True,
            },
            {
                "id": 2,
                "name": "Reading",
                "visible": False,
                "color": (0, 255, 0),
                "x": 10,
                "y": 20,
                "expanded": True,
            },
        ])

    def test_sorts_categories_at_same_level(self):
        self.add_category("Work", (255, 0, 100), False)
        self.add_category("Reading", (0, 255, 0), False)
        self.model.set_timeline_view(self.timeline_view)
        self.assert_model_has_names(["Reading", "Work"])

    def test_can_set_view_multiple_times_without_entries_duplicating(self):
        self.add_category("Work", (255, 0, 100), False)
        self.model.set_timeline_view(self.timeline_view)
        self.model.set_timeline_view(self.timeline_view)
        self.assertEqual(len(self.model.entries), 1)

    def test_toggles_expandedness(self):
        self.model.HEIGHT = 20
        self.add_category("Work", (255, 0, 100), False)
        self.add_category("Reading", (0, 255, 0), False)
        self.model.set_timeline_view(self.timeline_view)
        self.assertTrue(self.model.entries[1]["expanded"])
        self.model.toggle_expandedness(25)
        self.assertFalse(self.model.entries[1]["expanded"])
        self.model.toggle_expandedness(25)
        self.assertTrue(self.model.entries[1]["expanded"])

    def test_hides_subtrees_if_parent_not_expanded(self):
        self.model.HEIGHT = 20
        work_category = self.add_category("Work", (255, 0, 100), False)
        self.add_category("Reading", (0, 255, 0), False, work_category)
        self.model.set_timeline_view(self.timeline_view)
        self.assert_model_has_names(["Work", "Reading"])
        self.model.toggle_expandedness(5)
        self.assert_model_has_names(["Work"])

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

    def add_category(self, name, color, visible, parent=None):
        category = Category(name, color, (0, 0, 0), True, parent=parent)
        category.set_id(self.id_counter.get_next())
        if visible:
            self.visible_categories.append(category)
        self.categories.append(category)
        return category

    def assert_model_has_entries(self, expected_entries):
        self.assertEqual(self.model.entries, expected_entries)

    def assert_model_has_names(self, expected_names):
        self.assertEqual([x["name"] for x in self.model.entries], expected_names)
