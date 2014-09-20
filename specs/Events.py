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


from specs.utils import a_category_with
from specs.utils import TestCase
from timelinelib.data import Events
from timelinelib.data.db import InvalidOperationError


class EventsTestCase(TestCase):

    def setUp(self):
        self.events = Events()


class describe_cloning(EventsTestCase):

    def test_categories_are_cloned(self):
        self.events.save_category(a_category_with(name="work"))
        self.events.save_category(a_category_with(name="football"))
        self.events.save_category(a_category_with(
            name="meetings",
            parent=self.events.get_category_by_name("work")))
        clone = self.events.clone()
        self.assertListIsCloneOf(clone.get_categories(),
                                 self.events.get_categories())
        self.assertIsCloneOf(clone.get_category_by_name("meetings").parent,
                             self.events.get_category_by_name("work"))


class describe_saving_categories(EventsTestCase):

    def test_can_save(self):
        category = a_category_with(name="work")
        self.events.save_category(category)
        self.assertEqual(self.events.get_categories(), [category])

    def test_can_update(self):
        self.events.save_category(a_category_with(name="work"))
        updated_category = self.events.get_categories()[0]
        updated_category.color = (50, 100, 150)
        self.events.save_category(updated_category)
        self.assertEqual(self.events.get_categories(), [updated_category])

    def test_fails_if_new_category_has_existing_name(self):
        self.events.save_category(a_category_with(name="work"))
        self.assertRaises(InvalidOperationError,
                          self.events.save_category,
                          a_category_with(name="work"))

    def test_fails_if_category_has_existing_name(self):
        self.events.save_category(a_category_with(name="work"))
        self.events.save_category(a_category_with(name="sports"))
        updated_category = self.events.get_categories()[0]
        updated_category.set_name("sports")
        self.assertRaises(InvalidOperationError,
                          self.events.save_category, updated_category)
