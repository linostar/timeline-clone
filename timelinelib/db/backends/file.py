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


"""
Implementation of timeline database with flat file storage using our own custom
format.
"""


import re
import codecs
import shutil
import os.path
from os.path import abspath
from datetime import datetime
from datetime import timedelta

from timelinelib.db.interface import TimelineIOError
from timelinelib.db.interface import TimelineDB
from timelinelib.db.interface import STATE_CHANGE_ANY
from timelinelib.db.interface import STATE_CHANGE_CATEGORY
from timelinelib.db.objects import TimePeriod
from timelinelib.db.objects import Event
from timelinelib.db.objects import Category
from timelinelib.db.objects import time_period_center
from timelinelib.db.objects import get_event_data_plugins
from timelinelib.db.objects import get_event_data_plugin
from timelinelib.db.utils import safe_write
from timelinelib.version import get_version


ENCODING = "utf-8"


class IdCounter(object):

    def __init__(self, initial_id=0):
        self.id = initial_id

    def get_next(self):
        self.id += 1
        return self.id


class ParseException(Exception):
    """Thrown if parsing of data read from file fails."""
    pass


class FileTimeline(TimelineDB):
    """
    Implements the timeline database interface.

    The comments in the TimelineDB class describe what the public methods do.

    Every public method (including the constructor) can raise a TimelineIOError
    if there was a problem reading or writing from file.

    The general format of the file looks like this for version >= 0.3.0:

      # Written by Timeline 0.3.0 on 2009-7-23 9:40:33
      PREFERRED-PERIOD:...
      CATEGORY:...
      ...
      EVENT:...
      ...
      # END
    
    Only the first and last line are required. See comments in _load_*
    functions for information how the format looks like for the different
    parts.
    """

    def __init__(self, path):
        """
        Create a new timeline and read data from file.

        If the file does not exist a new timeline will be created.
        """
        TimelineDB.__init__(self, path)
        self.new_events = []
        self.event_id_counter = IdCounter()
        self.new_categories = []
        self.category_id_counter = IdCounter()
        self._load_data()

    def is_read_only(self):
        return False

    def get_events(self, time_period):
        def include_event(event):
            if not event.inside_period(time_period):
                return False
            if event.category != None and event.category.visible == False:
                return False
            return True
        return [event for event in self.events if include_event(event)]

    def save_event(self, event):
        if not event.has_id():
            self.new_events.append(event)
        self._save_data()

    def delete_event(self, event_or_id):
        def find_event():
            for e in self.events:
                if e == event_or_id or e.id == event_or_id:
                    return e
            return None
        e = find_event()
        if e is not None:
            self.events.remove(e)
            e.set_id(None)
            self._save_data()

    def get_categories(self):
        # Make sure the original list can't be modified
        return tuple(self.categories)

    def save_category(self, category):
        if not category.has_id():
            self.new_categories.append(category)
        self._save_data()
        self._notify(STATE_CHANGE_CATEGORY)

    def delete_category(self, category_or_id):
        def find_category():
            for c in self.categories:
                if c == category_or_id or c.id == category_or_id:
                    return c
            return None
        category = find_category()
        if category is not None:
            self.categories.remove(category)
            category.set_id(None)
            for event in self.events:
                if event.category == category:
                    event.category = None
            self._save_data()
            self._notify(STATE_CHANGE_CATEGORY)

    def get_preferred_period(self):
        if self.preferred_period != None:
            return self.preferred_period
        return time_period_center(datetime.now(), timedelta(days=30))

    def set_preferred_period(self, period):
        if not period.is_period():
            raise TimelineIOError(_("Preferred period must be > 0."))
        self.preferred_period = period
        self._save_data()

    def _load_data(self):
        """
        Load timeline data from the file that this timeline points to.

        This should only be done once when this class is created.

        The data is stored internally until we do a save.

        If a read error occurs a TimelineIOError will be raised.
        """
        self.preferred_period = None
        self.categories = []
        self.events = []
        if not os.path.exists(self.path): 
            # Nothing to load. Will create a new timeline on save.
            return
        try:
            file = codecs.open(self.path, "r", ENCODING)
            try:
                try:
                    self._load_from_lines(file)
                except Exception, pe:
                    # This should always be a ParseException, but if we made a
                    # mistake somewhere we still would like to mark the file as
                    # corrupt so we don't overwrite it later.
                    msg1 = _("Unable to read timeline data from '%s'.")
                    msg2 = "\n\n" + pe.message
                    raise TimelineIOError((msg1 % abspath(self.path)) + msg2)
            finally:
                file.close()
        except IOError, e:
            msg = _("Unable to read from file '%s'.")
            whole_msg = (msg + "\n\n%s") % (abspath(self.path), e)
            raise TimelineIOError(whole_msg)

    def _load_from_lines(self, file):
        current_line = file.readline()
        # Load header
        self._load_header(current_line.rstrip("\r\n"))
        current_line = file.readline()
        # Load preferred period
        if current_line.startswith("PREFERRED-PERIOD:"):
            self._load_preferred_period(current_line[17:].rstrip("\r\n"))
            current_line = file.readline()
        # Load categories
        while current_line.startswith("CATEGORY:"):
            self._load_category(current_line[9:].rstrip("\r\n"))
            current_line = file.readline()
        # Load events
        while current_line.startswith("EVENT:"):
            self._load_event(current_line[6:].rstrip("\r\n"))
            current_line = file.readline()
        # Check for footer if version >= 0.3.0 (version read by _load_header)
        if self.file_version >= (0, 3, 0):
            self._load_footer(current_line.rstrip("\r\n"))
            current_line = file.readline()
            # Ensure no more data
            if current_line:
                raise ParseException("File continues after EOF marker.")

    def _load_header(self, header_text):
        """
        Expected format '# Written by Timeline <version> on <date>'.
        
        Expected format of <version> '0.3.0[dev<revision>]'.
        
        We are just interested in the first part of the version.
        """
        match = re.search(r"^# Written by Timeline (\d+)\.(\d+)\.(\d+)",
                          header_text)
        if match:
            major = int(match.group(1))
            minor = int(match.group(2))
            tiny = int(match.group(3))
            self.file_version = (major, minor, tiny)
        else:
            raise ParseException("Unable to load header from '%s'." % header_text)

    def _load_preferred_period(self, period_text):
        """Expected format 'start_time;end_time'."""
        times = split_on_semicolon(period_text)
        try:
            if len(times) != 2:
                raise ParseException("Unexpected number of components.")
            self.preferred_period = TimePeriod(parse_time(times[0]),
                                               parse_time(times[1]))
            if not self.preferred_period.is_period():
                raise ParseException("Length not > 0.")
        except ParseException, e:
            raise ParseException("Unable to parse preferred period from '%s': %s" % (period_text, e.message))

    def _load_category(self, category_text):
        """
        Expected format 'name;color;visible'.
        
        Visible attribute added in version 0.2.0. If it is not found (we read
        an older file), we automatically set it to True.
        """
        category_data = split_on_semicolon(category_text)
        try:
            if len(category_data) != 2 and len(category_data) != 3:
                raise ParseException("Unexpected number of components.")
            name = dequote(category_data[0])
            color = parse_color(category_data[1])
            visible = True
            if len(category_data) == 3:
                visible = parse_bool(category_data[2])
            cat = Category(name, color, visible)
            cat.set_id(self.category_id_counter.get_next())
            self.categories.append(cat)
        except ParseException, e:
            raise ParseException("Unable to parse category from '%s': %s" % (category_text, e.message))

    def _load_event(self, event_text):
        """
        Expected format 'start_time;end_time;text;category[;id:data]*'.

        Changed in version 0.4.0: made category compulsory and added support
        for additional data. Format for version < 0.4.0 looked like this:
        'start_time;end_time;text[;category]'.
        
        If an event does not have a category the empty string will be written
        as category name. Since category names can not be the empty string
        there will be no confusion.
        """
        event_specification = split_on_semicolon(event_text)
        try:
            if self.file_version < (0, 4, 0):
                if (len(event_specification) != 3 and
                    len(event_specification) != 4):
                    raise ParseException("Unexpected number of components.")
                start_time = parse_time(event_specification[0])
                end_time = parse_time(event_specification[1])
                text = dequote(event_specification[2])
                cat_name = None
                if len(event_specification) == 4:
                    cat_name = dequote(event_specification[3])
                category = self._get_category(cat_name)
                evt = Event(start_time, end_time, text, category)
                evt.set_id(self.event_id_counter.get_next())
                self.events.append(evt)
                return True
            else:
                if len(event_specification) < 4:
                    raise ParseException("Unexpected number of components.")
                start_time = parse_time(event_specification[0])
                end_time = parse_time(event_specification[1])
                text = dequote(event_specification[2])
                category = self._get_category(dequote(event_specification[3]))
                event = Event(start_time, end_time, text, category)
                for item in event_specification[4:]:
                    id, data = item.split(":", 1)
                    plugin = get_event_data_plugin(id)
                    if plugin == None:
                        raise ParseException("Can't find event data plugin '%s'." % id)
                    event.set_data(id, plugin.decode(dequote(data)))
                event.set_id(self.event_id_counter.get_next())
                self.events.append(event)
        except ParseException, e:
            raise ParseException("Unable to parse event from '%s': %s" % (event_text, e.message))

    def _load_footer(self, footer_text):
        """Expected format '# END'."""
        if not footer_text == "# END":
            raise ParseException("Unable to load footer from '%s'." % footer_text)

    def _get_category(self, name):
        for category in self.categories:
            if category.name == name:
                return category
        return None

    def _save_data(self):
        """
        Save timeline data to the file that this timeline points to.

        If we have read corrupt data from a file it is not possible to still
        have an instance of this database. So it is always safe to write.
        """
        def write_fn(file):
            self._write_header(file)
            self._write_preferred_period(file)
            self._write_categories(file)
            self._write_events(file)
            self._write_footer(file)
        safe_write(self.path, ENCODING, write_fn)
        self._notify(STATE_CHANGE_ANY)

    def _create_backup(self):
        if os.path.exists(self.path):
            backup_path = self.path + "~"
            try:
                shutil.copy(self.path, backup_path)
            except IOError, e:
                msg = _("Unable to create backup to '%s'.")
                whole_msg = (msg + "\n\n%s") % (abspath(backup_path), e)
                raise TimelineIOError(whole_msg)

    def _write_header(self, file):
        file.write("# Written by Timeline %s on %s\n" % (
            get_version(),
            time_string(datetime.now())))

    def _write_preferred_period(self, file):
        if self.preferred_period:
            file.write("PREFERRED-PERIOD:%s;%s\n" % (
                time_string(self.preferred_period.start_time),
                time_string(self.preferred_period.end_time)))

    def _write_categories(self, file):
        def save(category):
            r, g, b = cat.color
            file.write("CATEGORY:%s;%s,%s,%s;%s\n" % (quote(cat.name),
                                                      r, g, b,
                                                      cat.visible))
        for cat in self.categories:
            save(cat)
        while self.new_categories:
            cat = self.new_categories.pop()
            save(cat)
            cat.set_id(self.category_id_counter.get_next())
            self.categories.append(cat)

    def _write_events(self, file):
        def save(event):
            file.write("EVENT:%s;%s;%s" % (
                time_string(event.time_period.start_time),
                time_string(event.time_period.end_time),
                quote(event.text)))
            if event.category:
                file.write(";%s" % quote(event.category.name))
            else:
                file.write(";")
            for plugin in get_event_data_plugins():
                data = event.get_data(plugin.get_id())
                if data != None:
                    file.write(";%s:%s" % (plugin.get_id(),
                                           quote(plugin.encode(data))))
            file.write("\n")
        for event in self.events:
            save(event)
        while self.new_events:
            event = self.new_events.pop()
            save(event)
            event.set_id(self.event_id_counter.get_next())
            self.events.append(event)

    def _write_footer(self, file):
        file.write(u"# END\n")


def parse_bool(bool_string):
    """
    Return True or False.

    Expected format 'True' or 'False'.
    """
    if bool_string == "True":
        return True
    elif bool_string == "False":
        return False
    else:
        raise ParseException("Unknown boolean '%s'" % bool_string)


def parse_color(color_string):
    """
    Return a tuple (r, g, b) or raise exception.
    
    Expected format 'r,g,b'.
    """
    def verify_255_number(num):
        if num < 0 or num > 255:
            raise ParseException("Color number not in range [0, 255], color string = '%s'" % color_string)
    match = re.search(r"^(\d+),(\d+),(\d+)$", color_string)
    if match:
        r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
        verify_255_number(r)
        verify_255_number(g)
        verify_255_number(b)
        return (r, g, b)
    else:
        raise ParseException("Color not on correct format, color string = '%s'" % color_string)


def parse_time(time_string):
    """
    Return a DateTime or raise exception.

    Expected format 'year-month-day hour:minute:second'.
    """
    match = re.search(r"^(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)$", time_string)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        hour = int(match.group(4))
        minute = int(match.group(5))
        second = int(match.group(6))
        try:
            return datetime(year, month, day, hour, minute, second)
        except ValueError:
            raise ParseException("Invalid time, time string = '%s'" % time_string)
    else:
        raise ParseException("Time not on correct format = '%s'" % time_string)


def time_string(time):
    """
    Return time formatted for writing to file.
    """
    return "%s-%s-%s %s:%s:%s" % (time.year, time.month, time.day,
                                  time.hour, time.minute, time.second)


def split_on_semicolon(text):
    """
    The delimiter is ; but only if not proceeded by backslash.

    Examples:

        'foo;bar' -> ['foo', 'bar']
        'foo\;bar;barfoo -> ['foo\;bar', 'barfoo']
    """
    return re.split(r"(?<!\\);", text)


def dequote(text):
    def repl(match):
        after_backslash = match.group(1)
        if after_backslash == "n":
            return "\n"
        elif after_backslash == "r":
            return "\r"
        else:
            return after_backslash
    return re.sub(r"\\(.)", repl, text)


def quote(text):
    def repl(match):
        match_char = match.group(0)
        if match_char == "\n":
            return "\\n"
        elif match_char == "\r":
            return "\\r"
        else:
            return "\\" + match_char
    return re.sub(";|\n|\r|\\\\", repl, text)
