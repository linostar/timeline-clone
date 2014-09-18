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


MAX_BUFFER_SIZE = 10


class UndoHandler(object):

    def __init__(self, db):
        self._db = db
        self._undo_buffer = []
        self._enabled = False
        self._pos = -1
        self._report_enabled = False
        self._max_buffer_size = MAX_BUFFER_SIZE
        self.report("After Init---------------------")

    def enable(self, value):
        self._enabled = value

    def undo(self):
        if len(self._undo_buffer) == 0:
            return False
        if self._pos == 0:
            return False
        self._pos -= 1
        self.enable(False)
        self.report("After Undo---------------------")
        return True

    def redo(self):
        if len(self._undo_buffer) == 0:
            return False
        if self._pos >= len(self._undo_buffer) - 1:
            return False
        self._pos += 1
        self.enable(False)
        self.report("After Redo---------------------")
        return True

    def get_data(self):
        if len(self._undo_buffer) > 0:
            return self._undo_buffer[self._pos].clone()
        else:
            return []

    def save(self):
        if self._enabled:
            del (self._undo_buffer[self._pos + 1:])
            if self._max_buffer_size == len(self._undo_buffer):
                del(self._undo_buffer[0])
                self._pos -= 1
            self.report("After  delete---------------------")
            self._undo_buffer.append(self._db._events.clone())
            self._pos += 1
            self.report("After Save---------------------")

    def _reset_buffer(self):
        self._pos = -1
        self._undo_buffer = []

    def report(self, msg=""):
        if self._report_enabled:
            print msg
            print "Size: %d  pos: %d" % (len(self._undo_buffer), self._pos)
            i = 0
            for list in self._undo_buffer:
                print "List ", i
                i += 1
                for event in list:
                    print "   %s" % event.text
                    print "   %s" % event.category.name
