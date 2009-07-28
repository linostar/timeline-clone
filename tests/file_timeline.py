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

from data_file import FileTimeline


class TestFileTimeline(unittest.TestCase):
    
    def _error_fn(self, msg):
        self.error_fn_called += 1

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
        self.error_fn_called = 0
        HEADER_030 = "# Written by Timeline 0.3.0 on 2009-7-23 9:40:33"
        HEADER_030_DEV = "# Written by Timeline 0.3.0dev on 2009-7-23 9:40:33"
        HEADER_021 = "# Written by Timeline 0.2.1 on 2009-7-23 9:40:33"
        self._write_timeline("readonly.timeline", [HEADER_030, "# END"])
        self._write_timeline("writeonly.timeline", [HEADER_030, "# END"])
        self._write_timeline("corrupt.timeline", ["corrupt data here"])
        self._write_timeline("missingeof.timeline", ["# valid data"])
        self._write_timeline("030dev.timeline", [HEADER_030_DEV])
        self._write_timeline("021.timeline", [HEADER_021])
        self._set_read_only("readonly.timeline")
        self._set_write_only("writeonly.timeline")

    def tearDown(self):
        self._silent_remove("readonly.timeline")
        self._silent_remove("readonly.timeline~")
        self._silent_remove("writeonly.timeline")
        self._silent_remove("writeonly.timeline~")
        self._silent_remove("corrupt.timeline")
        self._silent_remove("corrupt.timeline~")
        self._silent_remove("missingeof.timeline")
        self._silent_remove("missingeof.timeline~")
        self._silent_remove("030dev.timeline")
        self._silent_remove("030dev.timeline~")
        self._silent_remove("021.timeline")
        self._silent_remove("021.timeline~")

    def testWriteError(self):
        """
        Scenario: You open a timeline and everything is fine. When you do
        something that causes a save it fails to save your data.

        Expected result: You get an error message and subsequent tries to save
        will be disabled. The first save attempt will create a backup
        even though the save itself will fail. Subsequent saves should not
        create backups.

        The write error is simulated with a read-only file.
        """
        timeline = FileTimeline("readonly.timeline", self._error_fn)
        self.assertFalse(os.path.exists("readonly.timeline~"))
        timeline._save_data()
        self.assertEqual(self.error_fn_called, 1)
        self.assertEqual(timeline.error_flag, FileTimeline.ERROR_WRITE)
        self.assertTrue(os.path.exists("readonly.timeline~"))
        modified_time = os.stat("readonly.timeline~").st_mtime
        timeline._save_data()
        self.assertEqual(self.error_fn_called, 2)
        self.assertEqual(timeline.error_flag, FileTimeline.ERROR_WRITE)
        self.assertEqual(modified_time, os.stat("readonly.timeline~").st_mtime)

    def testReadError(self):
        """
        Scenario: You open a timeline and the application fails to read from
        the file.

        Expected result: You get an error message and subsequent tries to save
        will be disabled. No backup file will be created.

        The read error is simulated with a write-only file.
        """
        timeline = FileTimeline("writeonly.timeline", self._error_fn)
        self.assertEqual(self.error_fn_called, 1)
        self.assertEqual(timeline.error_flag, FileTimeline.ERROR_READ)
        self.assertFalse(os.path.exists("writeonly.timeline~"))
        timeline._save_data()
        self.assertEqual(self.error_fn_called, 2)
        self.assertEqual(timeline.error_flag, FileTimeline.ERROR_READ)
        self.assertFalse(os.path.exists("writeonly.timeline~"))

    def testCorruptData(self):
        """
        Scenario: You open a timeline that contains corrupt data.

        Expected result: You get an error message and subsequent attempts to
        save the timeline will fail with an error message. No backup file will
        be created either.
        """
        timeline = FileTimeline("corrupt.timeline", self._error_fn)
        self.assertEqual(self.error_fn_called, 1)
        self.assertEqual(timeline.error_flag, FileTimeline.ERROR_CORRUPT)
        timeline._save_data()
        self.assertEqual(self.error_fn_called, 2)
        self.assertFalse(os.path.exists("corrupt.timeline~"))
        self.assertEqual(timeline.error_flag, FileTimeline.ERROR_CORRUPT)
        timeline._save_data()
        self.assertEqual(self.error_fn_called, 3)
        self.assertFalse(os.path.exists("corrupt.timeline~"))
        self.assertEqual(timeline.error_flag, FileTimeline.ERROR_CORRUPT)

    def testMissingEOF(self):
        """
        Scenario: A timeline is opened that contains no corrupt data. However,
        no end of file marker is found.

        Expected result: The timeline should be treated as corrupt.
        """
        timeline = FileTimeline("missingeof.timeline", self._error_fn)
        self.assertEqual(self.error_fn_called, 1)
        self.assertEqual(timeline.error_flag, FileTimeline.ERROR_CORRUPT)

    def testAddingEOF(self):
        """
        Scenario: You open an old timeline < 0.3.0 with a client >= 0.3.0.

        Expected result: The timeline does not contain the EOF marker but since
        it is an old file, no error messages should be sent.
        """
        timeline = FileTimeline("030dev.timeline", self._error_fn)
        self.assertEqual(self.error_fn_called, 0)
        timeline = FileTimeline("021.timeline", self._error_fn)
        self.assertEqual(self.error_fn_called, 0)
