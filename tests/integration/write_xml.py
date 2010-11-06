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
Tests that xml files are correctly written.
"""


import codecs
import tempfile
import shutil
import os
import os.path
import unittest
from datetime import datetime

from timelinelib.db.objects import Event
from timelinelib.db import db_open
from timelinelib.version import get_version


class TestWriteXml(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="timeline-test")
        self.tmp_path = os.path.join(self.tmp_dir, "test.timeline")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def testDisplayedPeriodTagNotWrittenIfNotSet(self):
        # Create a new db and add one event
        db = db_open(self.tmp_path)
        db.save_event(Event(db, datetime(2010, 8, 31, 0, 0, 0),
                            datetime(2010, 8, 31, 0, 0, 0),
                            "test"))
        # Read the file content from disk
        f = codecs.open(self.tmp_path, "r", "utf-8")
        content = f.read()
        f.close()
        # Assert that displayed_period tag is not written
        self.assertEquals(content, """<?xml version="1.0" encoding="utf-8"?>
<timeline>
  <version>%s</version>
  <categories>
  </categories>
  <events>
    <event>
      <start>2010-8-31 0:0:0</start>
      <end>2010-8-31 0:0:0</end>
      <text>test</text>
    </event>
  </events>
  <view>
    <hidden_categories>
    </hidden_categories>
  </view>
</timeline>
""" % get_version())
