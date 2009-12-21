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
Implementation of Timeline for directories and readonly.

The class FileTimeline implements the Timeline interface.
"""


import re
import codecs
import shutil
import os
import os.path
from os.path import abspath
from datetime import datetime
from datetime import timedelta
import time
import wx

from timelinelib.db.interface  import TimelineIOError
from timelinelib.db.interface  import TimelineDB
from timelinelib.db.objects  import TimePeriod
from timelinelib.db.objects  import Event
from timelinelib.db.objects  import Category
from timelinelib.db.objects  import time_period_center
from timelinelib.db.utils import generic_event_search
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


class DirTimeline(TimelineDB):
    """
    Implements the timeline database interface.

    The comments in the TimelineDB class describe what the public methods do.

    The class is a read-only timeline database, where each event represents a 
    file found in a given parent directory. The parent directory is given
    at construction time. The time for an event is the files 'last modified' time.
    
    Every public method (including the constructor) can raise a TimelineIOError
    if there was a problem reading data from a directory.
    """

    # Errors caused by loading and saving timeline data to file
    ERROR_NONE    = 0
    ERROR_READ    = 1 # Unable to read from file
    ERROR_CORRUPT = 2 # Able to read from file but content corrupt
    ERROR_WRITE   = 3 # Unable to write to file

    def __init__(self, path):
        """
        Create a new timeline and read data from the given directory.
        """
        TimelineDB.__init__(self, path)
        self.event_id_counter = IdCounter()
        self._load_data()

    def is_read_only(self):
        return True

    def supported_event_data(self):
        return []

    def search(self, search_string):
        return generic_event_search(self.events, search_string)
    
    def get_events(self, time_period):
        def include_event(event):
            if not event.inside_period(time_period):
                return False
            if event.category != None and event.category.visible == False:
                return False
            return True
        return [event for event in self.events if include_event(event)]

    def get_first_event(self):
        if len(self.events) == 0:
            return None
        start_event = self.events[0]
        start_time = start_event.time_period.start_time
        for event in self.events[1:]:
            if event.time_period.start_time < start_time:
                start_event = event
                start_time = event.time_period.start_time
        return start_event

    def get_last_event(self):
        if len(self.events) == 0:
            return None
        end_event = self.events[0]
        end_time = end_event.time_period.end_time
        for event in self.events[1:]:
            if event.time_period.end_time > end_time:
                end_event = event
                end_time = event.time_period.end_time
        return end_event
    
    def add_event(self, event):
        self.events.append(event)

    def save_event(self, event):
        """Noop"""
    
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
                
    def get_categories(self):
        return tuple(self.categories)
        
    def save_category(self, category):
        if not category.has_id():
            self.new_categories.append(category)
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
            self._notify(STATE_CHANGE_CATEGORY)

    def get_preferred_period(self):
        if self.preferred_period != None:
            return self.preferred_period
        return time_period_center(datetime.now(), timedelta(days=30))

    def set_preferred_period(self, period):
        if not period.is_period():
            raise TimelineIOError(_("Preferred period must be > 0."))
        self.preferred_period = period

    def _load_data(self):
        """
        Load timeline data from the directory that this timeline points to.

        This should only be done once when this class is created.

        The data can never be saved.

        If an error occurs, the error_flag will be set to either ERROR_READ if
        we failed to read from the directory or ERROR_CORRUPT if the data we 
        read was not valid. A TimelineIOError will also be raised.
        """
        self.preferred_period = None
        self.categories = []
        self.events = []
        if not os.path.exists(self.path): 
            # Nothing to load
            return
        if not os.path.isdir(self.path): 
            # Nothing to load
            return
        dirlist = os.listdir(self.path)
        min_time = datetime.now()
        max_time = datetime.now()
        counter = 0
        for file_or_dir in dirlist:
            counter += 1
            if counter > 100:
                message = _("Max 100 events are displayed")
                dial = wx.MessageDialog(None, message, _("Warning"), wx.OK | wx.ICON_WARNING)
                dial.ShowModal()
                break    
            path = os.path.join(self.path, file_or_dir)
            if not os.path.isfile(path):
                continue
            stat = os.stat(path)
            # st_atime (time of most recent access), 
            # st_mtime (time of most recent content modification), 
            # st_ctime (platform dependent; time of most recent metadata change on Unix, 
            # or the time of creation on Windows):
            start_time = datetime.fromtimestamp(int(stat.st_mtime))
            end_time = start_time
            if start_time > end_time:
                start_time, end_time = end_time, start_time
            if not min_time:
                min_time = start_time
                max_time = start_time
            else:
                if start_time < min_time:
                    min_time = start_time
                elif start_time > max_time:
                    max_time = start_time        
            text = file_or_dir
            category = None
            evt = Event(start_time, end_time, text, category)
            evt.set_id(self.event_id_counter.get_next())
            self.events.append(evt)
        min_time -= timedelta(7)
        max_time += timedelta(7)
        td = max_time - min_time
        if td > timedelta(365):
            min_time = max_time - timedelta(365)
        self.preferred_period = TimePeriod(min_time, max_time)
