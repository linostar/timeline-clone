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
Implementation of Timeline with flat file storage.

The class FileTimeline implements the Timeline interface.
"""


import re
import codecs
import shutil
import os.path
from os.path import abspath
from datetime import datetime
from datetime import timedelta

from data import TimelineIOError
from data import Timeline
from data import TimePeriod
from data import Event
from data import Category
from data import time_period_center
from data import get_event_data_plugins
from data import get_event_data_plugin
from version import get_version


ENCODING = "utf-8"


class ParseException(Exception):
    """Thrown if parsing of data read from file fails."""
    pass


class FileTimeline(Timeline):
    """
    Implements the Timeline interface.

    The comments in the Timeline class describe what the public methods do.

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

    # Errors caused by loading and saving timeline data to file
    ERROR_NONE    = 0
    ERROR_READ    = 1 # Unable to read from file
    ERROR_CORRUPT = 2 # Able to read from file but content corrupt
    ERROR_WRITE   = 3 # Unable to write to file

    def __init__(self, path):
        """
        Create a new timeline and read data from file.

        If the file does not exist a new timeline will be created.
        """
        Timeline.__init__(self, path)
        self._load_data()

    def get_events(self, time_period):
        def include_event(event):
            if not event.inside_period(time_period):
                return False
            if event.category != None and event.category.visible == False:
                return False
            return True
        return [event for event in self.events if include_event(event)]

    def add_event(self, event):
        self.events.append(event)
        self._save_data()

    def event_edited(self, event):
        self._save_data()

    def select_event(self, event, selected=True):
        event.selected = selected
        self._notify(Timeline.STATE_CHANGE_ANY)

    def delete_selected_events(self):
        self.events = [event for event in self.events if not event.selected]
        self._save_data()

    def reset_selected_events(self):
        for event in self.events:
            event.selected = False
        self._notify(Timeline.STATE_CHANGE_ANY)

    def get_categories(self):
        # Make sure the original list can't be modified
        return tuple(self.categories)

    def add_category(self, category):
        self.categories.append(category)
        self._save_data()
        self._notify(Timeline.STATE_CHANGE_CATEGORY)

    def category_edited(self, category):
        self._save_data()
        self._notify(Timeline.STATE_CHANGE_CATEGORY)

    def delete_category(self, category):
        if category in self.categories:
            self.categories.remove(category)
        for event in self.events:
            if event.category == category:
                event.category = None
        self._save_data()
        self._notify(Timeline.STATE_CHANGE_CATEGORY)

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

        If an error occurs, the error_flag will be set to either ERROR_READ if
        we failed to read from the file or ERROR_CORRUPT if the data we read
        was not valid. A TimelineIOError will also be raised.
        """
        self.preferred_period = None
        self.categories = []
        self.events = []
        self.error_flag = FileTimeline.ERROR_NONE
        if not os.path.exists(self.path): 
            # Nothing to load. Will create a new timeline on save.
            return
        try:
            file = codecs.open(self.path, "r", ENCODING)
            try:
                try:
                    self._load_from_lines(file)
                except ParseException, pe:
                    self.error_flag = FileTimeline.ERROR_CORRUPT
                    msg1 = _("Unable to read timeline data from '%s'.")
                    msg2 = "\n\n" + pe.message
                    raise TimelineIOError((msg1 % abspath(self.path)) + msg2)
            finally:
                file.close()
        except IOError, e:
            self.error_flag = FileTimeline.ERROR_READ
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
            self.categories.append(Category(name, color, visible))
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
                self.events.append(Event(start_time, end_time, text, category))
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

        It is extremely important to ensure that we never loose data. We can
        only loose data when we write. Here is how we try to minimize data
        loss:

          * Before we write the timeline we take a backup of the original
            * A backup can only be taken if the original file is healthy
            * If we encountered problems while reading the original file, it is
              not healthy (error_flag != ERROR_NONE)
            * If we read a file correctly and encounter error while writing new
              data, the error flag is also set to prevent further writes
        """
        if self.error_flag != FileTimeline.ERROR_NONE:
            raise TimelineIOError(_("Save function has been disabled because there was a problem reading or writing the timeline before. This to ensure that your data will not be overwritten."))
        self._create_backup()
        try:
            file = codecs.open(self.path, "w", ENCODING)
            try:
                self._write_header(file)
                self._write_preferred_period(file)
                self._write_categories(file)
                self._write_events(file)
                self._write_footer(file)
                self._notify(Timeline.STATE_CHANGE_ANY)
            finally:
                file.close()
        except IOError, e:
            self.error_flag = FileTimeline.ERROR_WRITE
            msg_part1 = _("Unable to save timeline data.")
            msg_part2 = _("If data was corrupted, check out the backed up file that was created when the timeline was last saved.")
            msg = msg_part1 + "\n\n" + msg_part2 + "\n\n%s" % e
            raise TimelineIOError(msg)

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
        for cat in self.categories:
            r, g, b = cat.color
            file.write("CATEGORY:%s;%s,%s,%s;%s\n" % (quote(cat.name),
                                                      r, g, b,
                                                      cat.visible))

    def _write_events(self, file):
        for event in self.events:
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
    map = {"n": "\n",
           "r": "\r"}
    res = ""
    dequote_next = False
    for char in text:
        if dequote_next:
            res += map.get(char, char)
            dequote_next = False
        else:
            if char == "\\":
                dequote_next = True
            else:
                res += char
    return res


def quote(text):
    map = {";": "\\;",
           "\n": "\\n",
           "\r": "\\r",
           "\\": "\\\\"}
    res = ""
    for char in text:
        res += map.get(char, char)
    return res
