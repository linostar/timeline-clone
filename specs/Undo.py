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


import random
import subprocess

from specs.utils import TmpDirTestCase
from specs.utils import EVENT_MODIFIERS
from timelinelib.dataexport.timelinexml import export_db_to_timeline_xml
from timelinelib.dataimport.tutorial import create_in_memory_tutorial_db


class describe_undo(TmpDirTestCase):

    def test_a_series_of_operations_can_be_undone(self):
        db_operations = DBOperations(self.get_tmp_path("original.timeline"),
                                     self.get_tmp_path("after_undo.timeline"))
        db = create_in_memory_tutorial_db()
        db.loaded()
        names = []
        for fn in db_operations.get():
            names.append(fn(db))
        if self.read("original.timeline") != self.read("after_undo.timeline"):
            self.fail_with_diff(names)

    def read(self, path):
        return open(self.get_tmp_path(path)).read()

    def fail_with_diff(self, names):
        lines = ["Operations could not be undone:"]
        lines.append("")
        for name in names:
            lines.append("- %s" % name)
        lines.append("")
        lines.append("Diff (original -> after undo):")
        lines.append("")
        for line in self.get_diff().split("\n"):
            lines.append("%s" % line.strip())
        self.fail("\n".join(lines))

    def get_diff(self):
        try:
            process = subprocess.Popen([
                "diff",
                self.get_tmp_path("original.timeline"),
                self.get_tmp_path("after_undo.timeline")],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            return process.communicate()[0]
        except:
            return "no diff program found"


class DBOperations(object):

    def __init__(self, original_path, after_undo_path):
        self._original_path = original_path
        self._after_undo_path = after_undo_path

    def operation_change_progress(self, db):
        event = random.choice(db.get_all_events())
        while True:
            new_progress = random.randint(0, 100)
            if new_progress != event.get_progress():
                event.set_progress(new_progress)
                break
        db.save_event(event)
        return "change progress to %s (event %d)" % (new_progress, event.get_id())

    def get(self):
        operations = []
        for _ in range(random.randint(0, 3)):
            operations.append(self._get_single())
        operations.append(self._operation_save_original)
        num_operations = random.randint(1, 5)
        for _ in range(num_operations):
            operations.append(self._get_single())
        for _ in range(num_operations):
            operations.append(self._operation_undo)
        operations.append(self._operation_save_after_undo)
        return operations

    def _operation_save_original(self, db):
        export_db_to_timeline_xml(db, self._original_path)
        return "save original"

    def _operation_undo(self, db):
        db.undo()
        return "undo"

    def _operation_save_after_undo(self, db):
        export_db_to_timeline_xml(db, self._after_undo_path)
        return "save after undo"

    def _get_single(self):
        return random.choice([
            getattr(self, name)
            for name in dir(self)
            if name.startswith("operation_")
        ])
