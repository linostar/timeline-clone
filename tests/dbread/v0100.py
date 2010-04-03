# -*- coding: utf-8 -*-
# Copyright (C) 2009, 2010  Rickard Lindberg, Roger Lindberg
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


"""
Tests that files written with v0.10.0 of Timeline can be read and that the data
is correctly converted if needed.
"""


import codecs
import tempfile
import shutil
import os
import os.path
import unittest
from datetime import datetime

from timelinelib.drawing.interface import ViewProperties
from timelinelib.db import db_open


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
        </category>
        <category>
            <name>Category 3</name>
            <color>173,216,230</color>
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


class TestRead0100File(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="timeline-test")
        self.tmp_path = os.path.join(self.tmp_dir, "test.timeline")
        f = codecs.open(self.tmp_path, "w", "utf-8")
        f.write(CONTENT_0100)
        f.close()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def testRead010DB(self):
        db = db_open(self.tmp_path)
        # Assert event correctly loaded
        events = db.get_all_events()
        self.assertEquals(len(events), 1)
        event = events[0]
        self.assertTrue(event.has_id())
        self.assertEquals(event.text, "Event 1")
        self.assertEquals(event.time_period.start_time,
                          datetime(2009, 11, 4, 22, 52, 0))
        self.assertEquals(event.time_period.end_time,
                          datetime(2009, 11, 11, 22, 52, 0))
        self.assertEquals(event.category.name, "Category 1")
        self.assertEquals(event.get_data("description"), "The first event.")
        self.assertEquals(event.get_data("icon"), None)
        # Assert that correct view properties are loaded (category visibility
        # checked later)
        vp = ViewProperties()
        db.load_view_properties(vp)
        self.assertEquals(vp.displayed_period.start_time,
                          datetime(2009, 10, 17, 22, 38, 32))
        self.assertEquals(vp.displayed_period.end_time,
                          datetime(2009, 12, 2, 16, 22, 4))
        # Assert categories correctly loaded
        categories = db.get_categories()
        self.assertEquals(len(categories), 3)
        for cat in categories:
            self.assertTrue(cat.has_id())
            if cat.name == "Category 1":
                self.assertEquals(cat.color, (188, 129, 224))
                self.assertTrue(vp.category_visible(cat))
            elif cat.name == "Category 2":
                self.assertEquals(cat.color, (255, 165, 0))
                self.assertTrue(vp.category_visible(cat))
            elif cat.name == "Category 3":
                self.assertEquals(cat.color, (173, 216, 230))
                self.assertFalse(vp.category_visible(cat))
            else:
                self.fail("Unknown category.")
