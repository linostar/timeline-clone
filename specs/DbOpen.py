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


import codecs

from specs.utils import a_category_with
from specs.utils import TmpDirTestCase
from timelinelib.calendar.gregorian import Gregorian
from timelinelib.db.exceptions import TimelineIOError
from timelinelib.db import db_open
from timelinelib.drawing.viewproperties import ViewProperties

import wx


CONTENT_010 = u"""
# Written by Timeline 0.1.0 on 2009-11-15 19:28:7
PREFERRED-PERIOD:2009-10-17 22:38:32;2009-12-2 16:22:4
CATEGORY:Category 1;188,129,224;True
CATEGORY:Category 2;255,165,0;True
CATEGORY:Category 3;173,216,230;False
EVENT:2009-11-4 22:52:0;2009-11-11 22:52:0;Event 1;Category 1
""".strip()

CONTENT_0100 = u"""
<?xml version="1.0" encoding="utf-8"?>
<timeline>
    <version>0.10.0</version>
    <categories>
        <category>
            <name>Category 1</name>
            <color>188,129,224</color>
        </category>
        <category>
            <name>Category 2</name>
            <color>255,165,0</color>
            <parent>Category 1</parent>
        </category>
        <category>
            <name>Category 3</name>
            <color>173,216,230</color>
            <parent>Category 2</parent>
        </category>
    </categories>
    <events>
        <event>
            <start>2009-11-4 22:52:0</start>
            <end>2009-11-11 22:52:0</end>
            <text>Event 1</text>
            <category>Category 1</category>
            <description>The first event.</description>
        </event>
    </events>
    <view>
        <displayed_period>
            <start>2009-10-17 22:38:32</start>
            <end>2009-12-2 16:22:4</end>
        </displayed_period>
        <hidden_categories>
            <name>Category 3</name>
        </hidden_categories>
    </view>
</timeline>
""".strip()


class DbOpenSpec(TmpDirTestCase):

    def test_raises_error_when_reading_non_xml_file(self):
        self.writeContentToTmpFile(CONTENT_010)
        try:
            db_open(self.tmp_path)
        except TimelineIOError, e:
            self.assertTrue("old file with a new version" in str(e))

    def testRead0100File(self):
        self.writeContentToTmpFile(CONTENT_0100)
        db = db_open(self.tmp_path)
        # Assert event correctly loaded
        events = db.get_all_events()
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertTrue(event.has_id())
        self.assertEqual(event.text, "Event 1")
        self.assertEqual(event.time_period.start_time,
                          Gregorian(2009, 11, 4, 22, 52, 0).to_time())
        self.assertEqual(event.time_period.end_time,
                          Gregorian(2009, 11, 11, 22, 52, 0).to_time())
        self.assertEqual(event.category.get_name(), "Category 1")
        self.assertEqual(event.get_data("description"), "The first event.")
        self.assertEqual(event.get_data("icon"), None)
        # Assert that correct view properties are loaded (category visibility
        # checked later)
        vp = ViewProperties()
        db.load_view_properties(vp)
        self.assertEqual(vp.displayed_period.start_time,
                          Gregorian(2009, 10, 17, 22, 38, 32).to_time())
        self.assertEqual(vp.displayed_period.end_time,
                          Gregorian(2009, 12, 2, 16, 22, 4).to_time())
        # Assert categories correctly loaded
        categories = db.get_categories()
        self.assertEqual(len(categories), 3)
        for cat in categories:
            self.assertTrue(cat.has_id())
            if cat.get_name() == "Category 1":
                self.assertEqual(cat.get_color(), (188, 129, 224))
                self.assertTrue(vp.is_category_visible(cat))
                self.assertEqual(cat.get_parent(), None)
            elif cat.get_name() == "Category 2":
                self.assertEqual(cat.get_color(), (255, 165, 0))
                self.assertTrue(vp.is_category_visible(cat))
                self.assertEqual(cat.get_parent().get_name(), "Category 1")
            elif cat.get_name() == "Category 3":
                self.assertEqual(cat.get_color(), (173, 216, 230))
                self.assertFalse(vp.is_category_visible(cat))
                self.assertEqual(cat.get_parent().get_name(), "Category 2")
            else:
                self.fail("Unknown category.")

    def test_creates_new_xml_file(self):
        new_db = db_open(self.tmp_path)
        new_db.save_category(a_category_with(name="work"))
        re_read_db = db_open(self.tmp_path)
        self.assertEqual(len(re_read_db.get_categories()), 1)
        self.assertEqual(re_read_db.get_categories()[0].get_name(), "work")

    def setUp(self):
        TmpDirTestCase.setUp(self)
        self.tmp_path = self.get_tmp_path("test.timeline")

    def writeContentToTmpFile(self, content):
        f = codecs.open(self.tmp_path, "w", "utf-8")
        f.write(content)
        f.close()
