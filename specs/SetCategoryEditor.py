import datetime
import unittest

from mock import Mock

from timelinelib.db.backends.memory import MemoryDB
from timelinelib.db.objects.category import Category
from timelinelib.db.objects.event import Event
from timelinelib.time import PyTimeType
from timelinelib.editors.setcategory import SetCategoryEditor
from timelinelib.wxgui.dialogs.setcategoryeditor import SetCategoryEditorDialog


class set_category_editor_spec_base(unittest.TestCase):

    def setUp(self, view_properties):
        self.time_type = PyTimeType()
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
        self.db = Mock(MemoryDB)
        self.db.get_time_type.return_value = self.time_type
        self.db.events = [self.event1, self.event2]
        return self.db

    def _create_category1(self):
        self.category1 = Category("category-name-1", None, None, False, None) 

    def _create_category2(self):
        self.category2 = Category("category-name-2", None, None, False, None) 

    def _create_event1(self):
        self.event1 = self._create_event(None)

    def _create_event2(self):
        self.event2 = self._create_event(self.category2)
    
    def _create_event(self, category):
        return Event(
            self.time_type,
            datetime.datetime(2010, 1, 1),
            datetime.datetime(2010, 1, 1),
            "foo",
            category)


class a_newly_initialized_dialog(set_category_editor_spec_base):

    def setUp(self):
        set_category_editor_spec_base.setUp(self, None)

    def test_category_can_be_set_on_all_events_without_category(self):
        self.controller.save()
        self.view.close.assert_called()
        self.assertTrue(self.event1.category == self.category1)
        self.assertTrue(self.event2.category == self.category2)

    def test_category_can_be_set_when_all_events_has_catageroies(self):
        self.event1.category = self.category2
        self.controller.save()
        self.view.close.assert_called()
        self.assertTrue(self.event1.category == self.category2)
        self.assertTrue(self.event2.category == self.category2)
