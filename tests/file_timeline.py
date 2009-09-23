# Copyright (C) 2009  Rickard Lindberg, Roger Lindberg
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
import os
import stat
import datetime

from data import TimelineIOError
from data import TimePeriod
from data_file import FileTimeline
from data_file import quote
from data_file import dequote
from data_file import split_on_semicolon


class TestFileTimeline(unittest.TestCase):
    
    def _silent_remove(self, path):
        if os.path.exists(path):
            os.remove(path)

    def _write_timeline(self, path, lines):
        f = file(path, "w")
        f.write("\n".join(lines))
        f.close()

    def _set_read_only(self, path):
        os.chmod(path, stat.S_IREAD)

    def _set_write_only(self, path):
        os.chmod(path, stat.S_IWRITE)

    def setUp(self):
        HEADER_030 = "# Written by Timeline 0.3.0 on 2009-7-23 9:40:33"
        HEADER_030_DEV = "# Written by Timeline 0.3.0dev on 2009-7-23 9:40:33"
        HEADER_021 = "# Written by Timeline 0.2.1 on 2009-7-23 9:40:33"
        self._write_timeline("readonly.timeline", [HEADER_030, "# END"])
        self._write_timeline("writeonly.timeline", [HEADER_030, "# END"])
        self._write_timeline("corrupt.timeline", ["corrupt data here"])
        self._write_timeline("missingeof.timeline", ["# valid data"])
        self._write_timeline("021.timeline", [HEADER_021])
        self._set_read_only("readonly.timeline")
        self._set_write_only("writeonly.timeline")
        invalid_time_period = [
            "# Written by Timeline 0.5.0dev785606221dc2 on 2009-9-22 19:1:10",
            "PREFERRED-PERIOD:2008-12-9 11:32:26;2008-12-9 11:32:26",
            "CATEGORY:Work;173,216,230;True",
            "CATEGORY:Private;200,200,200;True",
            "EVENT:2009-7-13 0:0:0;2009-7-18 0:0:0;Programming course;Work",
            "EVENT:2009-7-10 14:30:0;2009-7-10 14:30:0;Go to dentist;Private",
            "EVENT:2009-7-20 0:0:0;2009-7-27 0:0:0;Vacation;Private",
            "# END",
        ]
        self._write_timeline("invalid_time_period.timeline",
                             invalid_time_period)
        valid = [
            "# Written by Timeline 0.5.0 on 2009-9-22 19:1:10",
            "# END",
        ]
        self._write_timeline("valid.timeline", valid)

    def tearDown(self):
        self._silent_remove("readonly.timeline")
        self._silent_remove("readonly.timeline~")
        self._silent_remove("writeonly.timeline")
        self._silent_remove("writeonly.timeline~")
        self._silent_remove("corrupt.timeline")
        self._silent_remove("corrupt.timeline~")
        self._silent_remove("missingeof.timeline")
        self._silent_remove("missingeof.timeline~")
        self._silent_remove("021.timeline")
        self._silent_remove("021.timeline~")
        self._silent_remove("invalid_time_period.timeline")
        self._silent_remove("invalid_time_period.timeline~")
        self._silent_remove("valid.timeline")
        self._silent_remove("valid.timeline~")

    def testWriteError(self):
        """
        Scenario: You open a timeline without errors. When you do something
        that causes a save it fails to save your data.

        Expected result: You get an exception and subsequent tries to save will
        not have any effect. The first save attempt will create a backup even
        though the save itself will fail. Subsequent saves should not create
        backups.

        The write error is simulated with a read-only file.
        """
        timeline = FileTimeline("readonly.timeline")
        self.assertFalse(os.path.exists("readonly.timeline~"))
        self.assertRaises(TimelineIOError, timeline._save_data)
        self.assertTrue(os.path.exists("readonly.timeline~"))
        modified_time = os.stat("readonly.timeline").st_mtime
        backup_modified_time = os.stat("readonly.timeline~").st_mtime
        self.assertRaises(TimelineIOError, timeline._save_data)
        self.assertEqual(modified_time, os.stat("readonly.timeline").st_mtime)
        self.assertEqual(backup_modified_time, os.stat("readonly.timeline~").st_mtime)

    def testReadError(self):
        """
        Scenario: You open a timeline and the application fails to read from
        the file.

        Expected result: You get an exception and you can not use the timeline.

        The read error is simulated with a write-only file.
        """
        self.assertRaises(TimelineIOError, FileTimeline, "writeonly.timeline")
        self.assertFalse(os.path.exists("writeonly.timeline~"))

    def testCorruptData(self):
        """
        Scenario: You open a timeline that contains corrupt data.

        Expected result: You get an exception and you can not use the timeline.
        """
        self.assertRaises(TimelineIOError, FileTimeline, "corrupt.timeline")

    def testMissingEOF(self):
        """
        Scenario: A timeline is opened that contains no corrupt data. However,
        no end of file marker is found.

        Expected result: The timeline should be treated as corrupt.
        """
        self.assertRaises(TimelineIOError, FileTimeline, "missingeof.timeline")

    def testAddingEOF(self):
        """
        Scenario: You open an old timeline < 0.3.0 with a client >= 0.3.0.

        Expected result: The timeline does not contain the EOF marker but since
        it is an old file, no exception should be raised.
        """
        FileTimeline("021.timeline")

    def testInvalidTimePeriod(self):
        """
        Scenario: You open a timeline that has a PREFERRED-PERIOD of length 0.

        Expected result: Even if this is a valid value for a TimePeriod it
        should not be a valid PREFERRED-PERIOD. The length must be > 0. So we
        should get an error when trying to read this.
        """
        self.assertRaises(TimelineIOError, FileTimeline,
                          "invalid_time_period.timeline")

    def testSettingInvalidPreferredPeriod(self):
        """
        Scenario: You try to assign a preferred period whose length is 0.

        Expected result: You should get an error.
        """
        timeline = FileTimeline("valid.timeline")
        now = datetime.datetime.now()
        zero_tp = TimePeriod(now, now)
        self.assertRaises(TimelineIOError, timeline.set_preferred_period,
                          zero_tp)

class TestHelperFunctions(unittest.TestCase):

    def testQuote(self):
        # None
        self.assertEqual(quote("plain"), "plain")
        # Single
        self.assertEqual(quote("foo;bar"), "foo\\;bar")
        self.assertEqual(quote("foo\nbar"), "foo\\nbar")
        self.assertEqual(quote("foo\\bar"), "foo\\\\bar")
        self.assertEqual(quote("foo\\nbar"), "foo\\\\nbar")
        self.assertEqual(quote("\\;"), "\\\\\\;")
        # Mixed
        self.assertEqual(quote("foo\nbar\rbaz\\n;;"),
                         "foo\\nbar\\rbaz\\\\n\\;\\;")

    def testDequote(self):
        self.assertEqual(dequote("\\\\n"), "\\n")

    def testQuoteDequote(self):
        for s in ["simple string", "with; some;; semicolons",
                  "with\r\n some\n\n newlines\n"]:
            self.assertEqual(s, dequote(quote(s)))

    def testSplit(self):
        self.assertEqual(split_on_semicolon("one;two\\;;three"),
                         ["one", "two\\;", "three"])
