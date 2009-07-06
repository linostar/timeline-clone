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
Implementation of `Timeline` with file storage.

The class `FileTimeline` implements the `Timeline` interface.
"""


import re
import codecs
import shutil
import os.path
from logging import error as logerror
from logging import info as loginfo
from logging import warning as logwarning
from logging import debug as logdebug
from datetime import datetime
from datetime import timedelta

from data import Timeline
from data import TimePeriod
from data import Event
from data import Category
from data import time_period_center
from version import get_version
from gui import display_error_message


ENCODING = "utf-8"


class ParseException(Exception):
    """Thrown if parsing of data read from file fails."""
    pass


class FileTimeline(Timeline):
    """
    Implements the `Timeline` interface.

    The comments in the `Timeline` class describes what the public methods
    should do.
    """

    def __init__(self, file_path):
        """Create a new timeline and read data from file."""
        Timeline.__init__(self)
        self.file_path = file_path
        self.__load_data()

    def __load_data(self):
        """Load timeline data from the file that this timeline points to."""
        self.preferred_period = None
        self.categories = []
        self.events = []
        self.disable_save_due_to_corrupt_data = False
        if not os.path.exists(self.file_path): 
            # Nothing to load if file does not exist
            return
        self.__create_backup()
        loginfo("Opening file '%s'" % self.file_path)
        file = None
        try:
            try:
                file = codecs.open(self.file_path, "r", ENCODING)
            except IOError, e:
                display_error_message("Unable to read data from timeline.\n\n%s" % e)
            else:
                data_corrupt = False
                for line in file:
                    if not self.__load_object_from_line(line.rstrip("\r\n")):
                        data_corrupt = True
                if data_corrupt:
                    display_error_message("Timeline data corrupt. Enable logging and open the timeline again to get more information about the problem.")
                    self.disable_save_due_to_corrupt_data = True
        finally:
            if file:
                file.close()

    def __save_data(self):
        """Save timeline data to the file that this timeline points to."""
        if self.disable_save_due_to_corrupt_data:
            display_error_message("Save disabled because timeline data was corrupt.")
            return
        loginfo("Saving file '%s'" % self.file_path)
        file = None
        try:
            try:
                file = codecs.open(self.file_path, "w", ENCODING)
            except IOError, e:
                display_error_message("Unable to save timeline data.\n\nIf data was corrupted, check out the backed up file that was created when the timeline was opened.\n\n%s" % e)
            else:
                file.write("# Written by Timeline %s on %s\n" % (
                    get_version(),
                    time_string(datetime.now())))
                if self.preferred_period:
                    file.write("PREFERRED-PERIOD:%s;%s\n" % (
                        time_string(self.preferred_period.start_time),
                        time_string(self.preferred_period.end_time)))
                for cat in self.categories:
                    r, g, b = cat.color
                    file.write("CATEGORY:%s;%s,%s,%s;%s\n" % (quote(cat.name),
                                                              r, g, b,
                                                              cat.visible))
                for event in self.events:
                    file.write("EVENT:%s;%s;%s" % (
                        time_string(event.time_period.start_time),
                        time_string(event.time_period.end_time),
                        quote(event.text)))
                    if event.category:
                        file.write(";%s" % quote(event.category.name))
                    file.write("\n")
        finally:
            if file:
                file.close()
        self._notify(Timeline.STATE_CHANGE_ANY)

    def __create_backup(self):
        backup_path = self.file_path + "~"
        try:
            loginfo("Creating backup to '%s'" % backup_path)
            shutil.copy(self.file_path, backup_path)
        except IOError, e:
            logwarning("Unable to create backup to '%s'" % backup_path,
                       exc_info=e)

    def __load_object_from_line(self, line):
        """Return True if object successfully loaded, otherwise False."""
        logdebug("Processing line '%s'" % line)
        # Map prefixes to functions that handle the loading of those objects
        prefixes = (
            ("PREFERRED-PERIOD:", self.__load_preferred_period),
            ("CATEGORY:", self.__load_category),
            ("EVENT:", self.__load_event),
            ("#", self.__load_comment),
            # Catch all (make sure this function always return something)
            ("", self.__load_unknown),
        )
        for (prefix, loading_function) in prefixes:
            if line.startswith(prefix):
                return loading_function(line[len(prefix):])

    def __load_preferred_period(self, period_text):
        """Expected format 'start_time;end_time'."""
        times = split_on_semicolon(period_text)
        try:
            if len(times) != 2:
                raise ParseException("Unexpected number of components")
            self.preferred_period = TimePeriod(parse_time(times[0]),
                                               parse_time(times[1]))
            return True
        except ParseException, e:
            logerror("Unable to parse preferred period from '%s'" % (
                     period_text), exc_info=e)
            return False

    def __load_category(self, category_text):
        """
        Expected format 'name;color;visible'.
        
        File format for timeline version 0.1.0 did not have the visible
        attribute. If it is not found (we read an old file), we automatically
        set it to True.
        """
        category_data = split_on_semicolon(category_text)
        try:
            if len(category_data) != 2 and len(category_data) != 3:
                raise ParseException("Unexpected number of components")
            name = dequote(category_data[0])
            color = parse_color(category_data[1])
            visible = True
            if len(category_data) == 3:
                visible = parse_bool(category_data[2])
            self.categories.append(Category(name, color, visible))
            return True
        except ParseException, e:
            logerror("Unable to parse category from '%s'" % category_text,
                     exc_info=e)
            return False

    def __load_event(self, event_text):
        """Expected format 'start_time;end_time;text[;category]'."""
        event_specification = split_on_semicolon(event_text)
        try:
            if len(event_specification) != 3 and len(event_specification) != 4:
                raise ParseException("Unexpected number of components")
            start_time = parse_time(event_specification[0])
            end_time = parse_time(event_specification[1])
            text = dequote(event_specification[2])
            cat_name = None
            if len(event_specification) == 4:
                cat_name = dequote(event_specification[3])
            category = self.__get_category(cat_name)
            self.events.append(Event(start_time, end_time, text, category))
            return True
        except ParseException, e:
            logerror("Unable to parse event from '%s'" % event_text,
                     exc_info=e)
            return False

    def __load_comment(self, comment):
        # No processing of comments
        return True

    def __load_unknown(self, line):
        line_is_empty = line.strip() == ""
        if line_is_empty:
            return True
        else:
            logerror("Skipping unknown line: '%s'" % line)
            return False

    def __get_category(self, name):
        for category in self.categories:
            if category.name == name:
                return category
        return None

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
        self.__save_data()

    def event_edited(self, event):
        self.__save_data()

    def select_event(self, event, selected=True):
        event.selected = selected
        self._notify(Timeline.STATE_CHANGE_ANY)

    def delete_selected_events(self):
        self.events = [event for event in self.events if not event.selected]
        self.__save_data()

    def reset_selected_events(self):
        for event in self.events:
            event.selected = False
        self._notify(Timeline.STATE_CHANGE_ANY)

    def get_categories(self):
        # Make sure the original list can't be modified
        return tuple(self.categories)

    def add_category(self, category):
        self.categories.append(category)
        self.__save_data()
        self._notify(Timeline.STATE_CHANGE_CATEGORY)

    def category_edited(self, category):
        self.__save_data()
        self._notify(Timeline.STATE_CHANGE_CATEGORY)

    def delete_category(self, category):
        if category in self.categories:
            self.categories.remove(category)
        for event in self.events:
            if event.category == category:
                event.category = None
        self.__save_data()
        self._notify(Timeline.STATE_CHANGE_CATEGORY)

    def get_preferred_period(self):
        if self.preferred_period:
            return self.preferred_period
        return time_period_center(datetime.now(), timedelta(days=30))

    def set_preferred_period(self, period):
        self.preferred_period = period
        self.__save_data()


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
    return text.replace(r"\;", ";")


def quote(text):
    return text.replace(";", r"\;")
