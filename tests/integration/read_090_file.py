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
Tests that files written with v0.9.0 of Timeline can still be read and that the
data is correctly converted.
"""


import tempfile
import os
import os.path
import codecs
import shutil
import unittest
from datetime import datetime

from timelinelib.drawing.interface import ViewProperties
from timelinelib.db.backends.xmlfile import XmlTimeline
from timelinelib.db import db_open

import wx


CONTENT_090 = u"""
# Written by Timeline 0.9.0 on 2010-5-1 10:15:54
PREFERRED-PERIOD:2010-4-27 21:54:54;2010-5-13 6:33:18
CATEGORY:Hidden;0,0,0;False
CATEGORY:Work;255,0,0;True
CATEGORY:Private;0,0,255;True
EVENT:2010-5-2 9:0:0;2010-5-2 9:0:0;Tennis;Private;description:Med Kristoffer.
EVENT:2010-5-5 0:0:0;2010-5-8 0:0:0;Konferens;Work;icon:iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAgdJREFUOI11k8FLlGEQxn8z39pqmoq5FpQRdCgJk+gQ3ToHHeqQdaw/obOge+pQp45Bl04dO5cdKkgpgogCIYrSEgUjtzVdyW+eDu+364o1MLzzDs/MPDzzvra/+nLK3SazzMncyNzJMsM93d2NLHPcUuxuuBlmhhlVl5gEQLSsLfxPIiUlTZYA7l48xtWxyr9QO2yx/oc7s0s8+7qGMEC4ELeffwNgZr7O/TfLzC7UAZj+VOPB2xXmVjYAqG/mvP7+m5CISO4I5lcb3Hu1xPvldaaeLjBTNNhXznjyucalhx95NPeTuR8Nao28VRwhSpKQjInHXzg60IWknXoU0269WKS3s0SEMAMs4UoqQJIxv9ogc2/VS8lDYnVji1+bOQaQNlA0kAgZJqGASOq2K02EwEEBlupbVooAMxECkxVjtwERIiQocIZB86TQIIrO0VxOwaBJP0LI0uRtBgnjoTSh6bm0rUGTQS4iDy6PDDBx/hDdHU4eIg/hEUJta2lRLihIIo+gZ49z48wQI5Uurp+uEHkQeVCKaH+nQV9nBxeODwAw3Ffmyugg5470Mn5qkOG+MgC1jS1OVLr4sLxOKSIApynstbEhRg92pwb9Zcb7dz/xkwf2cvZwD+8W1zC7OS333b/NPf04N5o/Dyv2Z217dIlqRJA8aZAESrlmnIfI87YzD/KI6l8cNFR9AfhsJAAAAABJRU5ErkJggg==
# END
""".strip()


class TestRead010File(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="timeline-test")
        self.tmp_path = os.path.join(self.tmp_dir, "test.timeline")
        f = codecs.open(self.tmp_path, "w", "utf-8")
        f.write(CONTENT_090)
        f.close()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def testRead090DB(self):
        app = wx.PySimpleApp() # Needed for graphics functions to parse icon
        db = db_open(self.tmp_path)
        # Assert converted to xml db
        self.assertTrue(isinstance(db, XmlTimeline))
        # Assert events correctly loaded
        events = db.get_all_events()
        self.assertEquals(len(events), 2)
        for event in events:
            self.assertTrue(event.has_id())
            if event.text == "Tennis":
                self.assertEquals(event.time_period.start_time,
                                  datetime(2010, 5, 2, 9, 0, 0))
                self.assertEquals(event.time_period.end_time,
                                  datetime(2010, 5, 2, 9, 0, 0))
                self.assertEquals(event.category.name, "Private")
                self.assertEquals(event.get_data("description"), "Med Kristoffer.")
                self.assertEquals(event.get_data("icon"), None)
            elif event.text == "Konferens":
                self.assertEquals(event.time_period.start_time,
                                  datetime(2010, 5, 5, 0, 0, 0))
                self.assertEquals(event.time_period.end_time,
                                  datetime(2010, 5, 8, 0, 0, 0))
                self.assertEquals(event.category.name, "Work")
                self.assertEquals(event.get_data("description"), None)
                self.assertFalse(event.get_data("icon") is None)
            else:
                self.fail("Unknown event.")
        # Assert that correct view properties are loaded (category visibility
        # checked later)
        vp = ViewProperties()
        db.load_view_properties(vp)
        self.assertEquals(vp.displayed_period.start_time,
                          datetime(2010, 4, 27, 21, 54, 54))
        self.assertEquals(vp.displayed_period.end_time,
                          datetime(2010, 5, 13, 6, 33, 18))
        # Assert categories correctly loaded
        categories = db.get_categories()
        self.assertEquals(len(categories), 3)
        for cat in categories:
            self.assertTrue(cat.has_id())
            if cat.name == "Work":
                self.assertEquals(cat.color, (255, 0, 0))
                self.assertTrue(vp.category_visible(cat))
                self.assertEquals(cat.parent, None)
            elif cat.name == "Private":
                self.assertEquals(cat.color, (0, 0, 255))
                self.assertTrue(vp.category_visible(cat))
                self.assertEquals(cat.parent, None)
            elif cat.name == "Hidden":
                self.assertEquals(cat.color, (0, 0, 0))
                self.assertFalse(vp.category_visible(cat))
                self.assertEquals(cat.parent, None)
            else:
                self.fail("Unknown category.")
