# -*- coding: utf-8 -*-
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
import os.path

from specs.utils import a_category_with
from specs.utils import TmpDirTestCase
from timelinelib.dataexport.timelinexml import alert_string
from timelinelib.dataexport.timelinexml import export_db_to_timeline_xml
from timelinelib.data import Event
from timelinelib.dataimport.timelinexml import import_db_from_timeline_xml
from timelinelib.dataimport.timelinexml import parse_alert_string
from timelinelib.data import TimePeriod
from timelinelib.db import db_open
from timelinelib.drawing.viewproperties import ViewProperties
from timelinelib.meta.version import get_version
from timelinelib.time.gregoriantime import GregorianTimeType
import timelinelib.calendar.gregorian as gregorian


class XmlTimelineSpec(TmpDirTestCase):

    def test_backs_up_pre_1_0_0_files(self):
        contents = """<?xml version="1.0" encoding="utf-8"?>
<timeline>
  <version>0.21.1</version>
  <categories>
  </categories>
  <events>
  </events>
  <view>
    <hidden_categories>
    </hidden_categories>
  </view>
</timeline>
"""
        self.write(self.tmp_path, contents)
        import_db_from_timeline_xml(self.tmp_path)
        self.assertEqual(self.read(self.tmp_path + ".pre100bak1"), contents)

    def test_does_not_back_up_1_0_0_files(self):
        contents = """<?xml version="1.0" encoding="utf-8"?>
<timeline>
  <version>1.0.0</version>
  <categories>
  </categories>
  <events>
  </events>
  <view>
    <hidden_categories>
    </hidden_categories>
  </view>
</timeline>
"""
        self.write(self.tmp_path, contents)
        import_db_from_timeline_xml(self.tmp_path)
        self.assertFalse(os.path.exists(self.tmp_path + ".pre100bak1"))

    def testAlertStringParsingGivesAlertData(self):
        time, text = parse_alert_string(GregorianTimeType(), "2012-11-11 00:00:00;Now is the time")
        self.assertEqual("Now is the time", text)
        self.assertEqual("2012-11-11 00:00:00", "%s" % GregorianTimeType().time_string(time))

    def testAlertDataConversionGivesAlertString(self):
        alert = (gregorian.from_date(2010, 8, 31).to_time(), "Hoho")
        alert_text = alert_string(GregorianTimeType(), alert)
        self.assertEqual("2010-08-31 00:00:00;Hoho", alert_text)

    def testDisplayedPeriodTagNotWrittenIfNotSet(self):
        # Create a new db and add one event
        db = db_open(self.tmp_path)
        db.save_event(Event(db.get_time_type(), gregorian.from_date(2010, 8, 31).to_time(),
                            gregorian.from_date(2010, 8, 31).to_time(),
                            "test"))
        # Read the file content from disk
        f = codecs.open(self.tmp_path, "r", "utf-8")
        content = f.read()
        f.close()
        # Assert that displayed_period tag is not written
        self.assertEqual(content, """<?xml version="1.0" encoding="utf-8"?>
<timeline>
  <version>%s</version>
  <timetype>gregoriantime</timetype>
  <categories>
  </categories>
  <events>
    <event>
      <start>2010-08-31 00:00:00</start>
      <end>2010-08-31 00:00:00</end>
      <text>test</text>
      <fuzzy>False</fuzzy>
      <locked>False</locked>
      <ends_today>False</ends_today>
    </event>
  </events>
  <view>
    <hidden_categories>
    </hidden_categories>
  </view>
</timeline>
""" % get_version())

    def testWriteReadCycle(self):
        self._create_db()
        db_re_read = import_db_from_timeline_xml(self.tmp_path)
        self._assert_re_read_db_same(db_re_read)

    def _create_db(self):
        db = db_open(self.tmp_path)
        # Create categories
        cat1 = a_category_with(name="Category 1", color=(255, 0, 0),
                               font_color=(0, 0, 255))
        db.save_category(cat1)
        cat2 = a_category_with(name="Category 2", color=(0, 255, 0),
                               font_color=None, parent=cat1)
        db.save_category(cat2)
        cat3 = a_category_with(name="Category 3", color=(0, 0, 255),
                               font_color=None, parent=cat2)
        db.save_category(cat3)
        # Create events
        ev1 = Event(db.get_time_type(), gregorian.from_date(2010, 3, 3).to_time(), gregorian.from_date(2010, 3, 6).to_time(),
                    "Event 1", cat1)
        ev1.set_data("description", u"The <b>first</b> event åäö.")
        ev1.set_data("alert", (gregorian.from_date(2012, 12, 31).to_time(), "Time to go"))
        db.save_event(ev1)
        # Create view properties
        vp = ViewProperties()
        start = gregorian.from_date(2010, 3, 1).to_time()
        end = gregorian.from_date(2010, 4, 1).to_time()
        vp.displayed_period = TimePeriod(db.get_time_type(), start, end)
        vp.set_category_visible(cat3, False)
        db.save_view_properties(vp)
        export_db_to_timeline_xml(db, self.tmp_path)

    def _assert_re_read_db_same(self, db):
        # Assert event correctly loaded
        events = db.get_all_events()
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event.get_text(), "Event 1")
        self.assertEqual(event.get_time_period().start_time, gregorian.from_date(2010, 3, 3).to_time())
        self.assertEqual(event.get_time_period().end_time, gregorian.from_date(2010, 3, 6).to_time())
        self.assertEqual(event.category.get_name(), "Category 1")
        self.assertEqual(event.get_data("description"), u"The <b>first</b> event åäö.")
        self.assertEqual(event.get_data("alert"), (gregorian.from_date(2012, 12, 31).to_time(), "Time to go"))
        self.assertEqual(event.get_data("icon"), None)
        # Assert that correct view properties are loaded (category visibility
        # checked later)
        vp = ViewProperties()
        db.load_view_properties(vp)
        self.assertEqual(vp.displayed_period.start_time, gregorian.from_date(2010, 3, 1).to_time())
        self.assertEqual(vp.displayed_period.end_time, gregorian.from_date(2010, 4, 1).to_time())
        # Assert categories correctly loaded
        categories = db.get_categories()
        self.assertEqual(len(categories), 3)
        for cat in categories:
            self.assertTrue(cat.has_id())
            if cat.get_name() == "Category 1":
                self.assertEqual(cat.get_color(), (255, 0, 0))
                self.assertEqual(cat.get_font_color(), (0, 0, 255))
                self.assertTrue(vp.is_category_visible(cat))
                self.assertEqual(cat.get_parent(), None)
            elif cat.get_name() == "Category 2":
                self.assertEqual(cat.get_color(), (0, 255, 0))
                self.assertTrue(vp.is_category_visible(cat))
                self.assertEqual(cat.get_parent().get_name(), "Category 1")
            elif cat.get_name() == "Category 3":
                self.assertEqual(cat.get_color(), (0, 0, 255))
                self.assertFalse(vp.is_category_visible(cat))
                self.assertEqual(cat.get_parent().get_name(), "Category 2")
            else:
                self.fail("Unknown category.")

    def setUp(self):
        TmpDirTestCase.setUp(self)
        self.tmp_path = self.get_tmp_path("test.timeline")

    def read(self, path):
        f = codecs.open(path, "r", "utf-8")
        contents = f.read()
        f.close()
        return contents

    def write(self, path, contents):
        f = codecs.open(path, "w", "utf-8")
        content = f.write(contents)
        f.close()
