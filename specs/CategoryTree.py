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
from timelinelib.wxgui.components.categorytree import CustomCategoryTreeModel


class CategoryTreeModelSpec(unittest.TestCase):

    def test_no_categories(self):
        self.assert_update_gives_entries([])

    def test_one_category_visible(self):
        self.given_category("Work", (255, 0, 100), (0, 0, 0), True)
        self.assert_update_gives_entries([
            {
                "name": "Work",
                "visible": True,
                "color": (255, 0, 100),
            },
        ])

    def test_one_category_hidden(self):
        self.given_category("Work", (255, 0, 100), (0, 0, 0), False)
        self.assert_update_gives_entries([
            {
                "name": "Work",
                "visible": False,
                "color": (255, 0, 100),
            },
        ])

    def test_one_category_multiple_updates(self):
        self.given_category("Work", (255, 0, 100), (0, 0, 0), False)
        self.model.update_from_timeline_view(self.timeline_view)
        self.model.update_from_timeline_view(self.timeline_view)
        self.assertEqual(len(self.model.entries), 1)

    def setUp(self):
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

    def given_category(self, name, bg_color, fg_color, visible):
        work_category = Category(name, bg_color, fg_color, True)
        self.categories.append(work_category)
        if visible:
            self.visible_categories.append(work_category)

    def assert_update_gives_entries(self, expected_entries):
        self.model.update_from_timeline_view(self.timeline_view)
        self.assertEqual(self.model.entries, expected_entries)
