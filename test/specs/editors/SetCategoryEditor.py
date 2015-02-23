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
from timelinelib.data.db import MemoryDB
from timelinelib.data.event import Event
from timelinelib.editors.setcategory import SetCategoryEditor
from timelinelib.time.gregoriantime import GregorianTimeType
from timelinelib.wxgui.dialogs.setcategoryeditor import SetCategoryEditorDialog
import timelinelib.calendar.gregorian as gregorian


class set_category_editor_spec_base(unittest.TestCase):

    def setUp(self, view_properties):
        self.time_type = GregorianTimeType()
        self._create_category1()
        self._create_category2()
        self._create_event1()
        self._create_event2()
        self._create_db_mock()
        self.controller = SetCategoryEditor(
            self._create_view_mock(), self.db, view_properties)

    def _create_view_mock(self):
        self.view = Mock(SetCategoryEditorDialog)
        self.view.get_category.return_value = self.category1
        return self.view

    def _create_db_mock(self):
        def get_all_events():
            return [self.event1, self.event2]
        self.db = Mock(MemoryDB)
        self.db.get_time_type.return_value = self.time_type
        self.db.get_all_events = get_all_events
        return self.db

    def _create_category1(self):
        self.category1 = a_category_with(name="category-name-1")

    def _create_category2(self):
        self.category2 = a_category_with(name="category-name-2")

    def _create_event1(self):
        self.event1 = self._create_event(None)

    def _create_event2(self):
        self.event2 = self._create_event(self.category2)

    def _create_event(self, category):
        return Event(
            self.time_type,
            gregorian.from_date(2010, 1, 1).to_time(),
            gregorian.from_date(2010, 1, 1).to_time(),
            "foo",
            category)


class a_newly_initialized_dialog(set_category_editor_spec_base):

    def setUp(self):
        set_category_editor_spec_base.setUp(self, [])

    def test_category_can_be_set_on_all_events_without_category(self):
        self.controller.save()
        self.view.close.assert_called()
        self.assertTrue(self.event1.get_category() == self.category1)
        self.assertTrue(self.event2.get_category() == self.category2)

    def test_category_can_be_set_when_all_events_has_catageroies(self):
        self.event1.set_category(self.category2)
        self.controller.save()
        self.view.close.assert_called()
        self.assertTrue(self.event1.get_category() == self.category2)
        self.assertTrue(self.event2.get_category() == self.category2)
