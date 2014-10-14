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

from specs.utils import a_category_with
from specs.utils import TmpDirTestCase
from timelinelib.dataexport.timelinexml import export_db_to_timeline_xml
from timelinelib.dataimport.tutorial import create_in_memory_tutorial_db


class describe_undo(TmpDirTestCase):

    DIFF_PROGRAM = "diff"

    def test_a_series_of_operations_can_be_undone(self):
        db_operations = DBOperations(self.original_path, self.after_undo_path)
        db = create_in_memory_tutorial_db()
        db.loaded()
        names = []
        for fn in db_operations.get():
            names.append(fn(db))
        if self.read(self.original_path) != self.read(self.after_undo_path):
            self.fail_with_diff(names)

    def setUp(self):
        TmpDirTestCase.setUp(self)
        self.original_path = self.get_tmp_path("original.timeline")
        self.after_undo_path = self.get_tmp_path("after_undo.timeline")

    def read(self, path):
        f = open(path)
        try:
            return f.read()
        finally:
            f.close()

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
            cmd = [self.DIFF_PROGRAM, self.original_path, self.after_undo_path]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            output = process.communicate()[0]
        except:
            return "no diff program found"
        else:
            return output


class DBOperations(object):

    def __init__(self, original_path, after_undo_path):
        self.original_path = original_path
        self.after_undo_path = after_undo_path

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
        export_db_to_timeline_xml(db, self.original_path)
        return "save original"

    def _operation_undo(self, db):
        db.undo()
        return "undo"

    def _operation_save_after_undo(self, db):
        export_db_to_timeline_xml(db, self.after_undo_path)
        return "save after undo"

    def _get_single(self):
        return random.choice([
            self._operation_change_progress,
            self._operation_change_category,
            self._operation_add_category,
            self._operation_change_fuzzy,
            self._operation_change_ends_today,
            self._operation_change_locked,
            self._operation_change_text,
            self._operation_change_description,
        ])

    def _operation_change_progress(self, db):
        event = self._get_random_event(db)
        while True:
            new_progress = random.randint(0, 100)
            if new_progress != event.get_progress():
                event.set_progress(new_progress)
                break
        db.save_event(event)
        return "change progress to %s %r" % (new_progress, event)

    def _operation_change_category(self, db):
        event = self._get_random_event(db)
        while True:
            category = random.choice(db.get_categories())
            if category != event.get_category():
                break
        event.set_category(category)
        db.save_event(event)
        return "change category to %r %r" % (category, event)

    def _operation_add_category(self, db):
        counter = 0
        while True:
            counter += 1
            name = "new category %d" % counter
            if db.get_category_by_name(name) is None:
                category = a_category_with(name=name)
                break
        db.save_category(category)
        return "save category %r" % category

    def _operation_change_fuzzy(self, db):
        event = self._get_random_event(db)
        event.set_fuzzy(not event.get_fuzzy())
        db.save_event(event)
        return "change fuzzy to %s %r" % (event.get_fuzzy(), event)
        
    def _operation_change_ends_today(self, db):
        event = self._get_random_event(db)
        if (event.is_subevent() or event.is_container()):
            event.set_text(self._get_random_string(4, 16))
            db.save_event(event)
            return "change text to %s %r" % (event.get_text(), event)
        event.set_ends_today(not event.get_ends_today())
        db.save_event(event)
        return "change ends-today to %s %r" % (event.get_ends_today(), event)

    def _operation_change_locked(self, db):
        event = self._get_random_event(db)
        if (event.is_subevent() or event.is_container()):
            event.set_text(self._get_random_string(4, 16))
            db.save_event(event)
            return "change text to %s %r" % (event.get_text(), event)
        event.set_locked(not event.get_locked())
        db.save_event(event)
        return "change locked to %s %r" % (event.get_locked(), event)

    def _operation_change_text(self, db):
        event = self._get_random_event(db)
        event.set_text(self._get_random_string(4, 16))
        db.save_event(event)
        return "change text to %s %r" % (event.get_text(), event)

    def _operation_change_description(self, db):
        event = self._get_random_event(db)
        event.set_description(self._get_random_string(24, 36))
        db.save_event(event)
        return "change description to %s %r" % (event.get_description(), event)

    def _get_random_string(self, min_length, max_length):
        import string
        return ''.join(random.choice(string.ascii_lowercase + "     ") for _ in range(random.randint(min_length, max_length)))

    def _get_random_event(self, db):
        while True:
            event = random.choice(db.get_all_events())
            if not event.is_container():
                return event
