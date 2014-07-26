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

from specs.utils import TmpDirTestCase
from timelinelib.db.backends.ics import IcsTimeline
from timelinelib.db.backends.memory import MemoryDB
from timelinelib.db.objects import Category
from timelinelib.db.objects import Event


class BackendTest(object):

    # These tests should work for any backend. They are tested with different
    # backends below.

    def test_get_all_events_returns_a_list(self):
        all_events = self.backend.get_all_events()
        self.assertTrue(isinstance(all_events, list))

    def test_has_time_type_method(self):
        self.backend.get_time_type()


class MemoryBackendTest(unittest.TestCase, BackendTest):

    def setUp(self):
        self.backend = MemoryDB()


class IcsBackendTest(TmpDirTestCase, BackendTest):

    def setUp(self):
        TmpDirTestCase.setUp(self)
        self.backend = IcsTimeline(self.write_ics_content())

    def write_ics_content(self):
        tmp_path = self.get_tmp_path("test.ics")
        f = open(tmp_path, "w")
        f.write(ICS_EXAMPLE)
        f.close()
        return tmp_path


ICS_EXAMPLE = """
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal//NONSGML v1.0//EN
BEGIN:VEVENT
UID:uid1@example.com
DTSTAMP:19970714T170000Z
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
DTSTART:19970714T170000Z
DTEND:19970715T035959Z
SUMMARY:Bastille Day Party
END:VEVENT
END:VCALENDAR
"""

class CloningTest(unittest.TestCase):
    """
    An Event can be associated with a category.
    When the backend event-list and category-list are cloned this association must be maintained.
    """
    
    def test_when_db_data_is_cloned_category_event_relasionship_is_preserved(self):
        self.given_event_and_category_lists()
        self.when_cloning()
        self.assertTrue(self.new_category != self.old_category)
        self.assertTrue(self.new_event != self.old_event)
        self.assertTrue(self.db.events[0].category != self.old_category)
        self.assertEquals(self.new_event.category.name, self.old_category.name)

    def when_cloning(self):
        self.db.clone_data()
        self.new_category = self.db.categories[0]
        self.new_event = self.db.events[0]
    
    def given_event_and_category_lists(self):
        self.db.categories = [Category("cat1", None, None, True, parent=None)]
        self.db.events = [Event(self.db.get_time_type(), self.now, self.now, "evt", category=self.db.categories[0])]
        self.old_category = self.db.categories[0]
        self.old_event = self.db.events[0]
         
    def setUp(self):
        self.db = MemoryDB()
        self.now = self.db.get_time_type().now()
    