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
Implementation of read-only timeline database whose data is files in a
directory and their modification times.
"""


import os
import os.path
import colorsys
from datetime import datetime
from datetime import timedelta
import time

import wx

from timelinelib.db.interface import TimelineIOError
from timelinelib.db.interface import TimelineDB
from timelinelib.db.interface import STATE_CHANGE_CATEGORY
from timelinelib.db.objects import Event
from timelinelib.db.objects import Category
from timelinelib.db.objects import time_period_center
from timelinelib.db.utils import IdCounter
from timelinelib.db.utils import generic_event_search
from timelinelib.version import get_version


class DirTimeline(TimelineDB):
    """
    Implements the timeline database interface.

    The comments in the TimelineDB class describe what the public methods do.

    The class is a read-only timeline database, where each event represents a
    file found in a given directory. The directory is given at construction
    time. The time for an event is the files 'last modified' time.
    
    Every public method (including the constructor) can raise a TimelineIOError
    if there was a problem reading data from a directory.
    """

    def __init__(self, path):
        TimelineDB.__init__(self, path)
        self.event_id_counter = IdCounter()
        self.category_id_counter = IdCounter()
        self._load_data()

    def is_read_only(self):
        return True

    def supported_event_data(self):
        pass

    def search(self, search_string):
        return generic_event_search(self.events, search_string)
    
    def get_events(self, time_period):
        def include_event(event):
            if not event.inside_period(time_period):
                return False
            return True
        return [event for event in self.events if include_event(event)]

    def get_first_event(self):
        if len(self.events) == 0:
            return None
        return min(self.events, key=lambda e: e.time_period.start_time)

    def get_last_event(self):
        if len(self.events) == 0:
            return None
        return max(self.events, key=lambda e: e.time_period.end_time)

    def save_event(self, event):
        pass
    
    def delete_event(self, event_or_id):
        pass
                
    def get_categories(self):
        # Make sure the original list can't be modified
        return self.categories[:]
        
    def save_category(self, category):
        pass

    def delete_category(self, category_or_id):
        pass

    def load_view_properties(self, view_properties):
        for cat in self.categories:
            view_properties.set_category_visible(cat, cat.visible)

    def save_view_properties(self, period):
        pass

    def _load_data(self):
        """
        Load timeline data from the directory that this timeline points to.

        This should only be done once when this class is created.

        The data can never be saved.

        If an error occurs, the error_flag will be set to either ERROR_READ if
        we failed to read from the directory or ERROR_CORRUPT if the data we 
        read was not valid. A TimelineIOError will also be raised.
        """
        self.categories = []
        self.events = []
        if not os.path.exists(self.path): 
            # Nothing to load
            return
        if not os.path.isdir(self.path): 
            # Nothing to load
            return
        try:
            color_ranges = {}
            color_ranges[self.path] = (0.0, 1.0, 1.0)
            for (dirpath, dirnames, filenames) in os.walk(self.path):
                # Assign color ranges
                range = (rstart, rend, b) = color_ranges[dirpath]
                step = (rend - rstart) / (len(dirnames) + 1)
                next_start = rstart + step
                new_b = b - 0.2
                if new_b < 0:
                    new_b = 0
                for dir in dirnames:
                    next_end = next_start + step
                    color_ranges[os.path.join(dirpath, dir)] = (next_start,
                                                                next_end, new_b)
                    next_start = next_end
                # Create the stuff
                cat = Category(dirpath, (233, 233, 233), False)
                cat.set_id(self.category_id_counter.get_next())
                self.categories.append(cat)
                for file in filenames:
                    path = os.path.join(dirpath, file)
                    evt = self._event_from_path(path)
                    evt.set_id(self.event_id_counter.get_next())
                    self.events.append(evt)
            self.categories[0].visible = True
            # Set colors and remove prefix
            prefix_len = len(self.path)
            for cat in self.categories:
                cat.color = self._color_from_range(color_ranges[cat.name])
                cat.name = "." + cat.name[prefix_len:]
        except Exception, e:
            msg = _("Unable to read from file '%s'.") % self.path
            whole_msg = "%s\n\n%s" % (msg, e)
            raise TimelineIOError(whole_msg)

    def _event_from_path(self, path):
        stat = os.stat(path)
        # st_atime (time of most recent access), 
        # st_mtime (time of most recent content modification), 
        # st_ctime (platform dependent; time of most recent metadata change on
        #           Unix, or the time of creation on Windows):
        start_time = datetime.fromtimestamp(int(stat.st_mtime))
        end_time = start_time
        if start_time > end_time:
            start_time, end_time = end_time, start_time
        text = os.path.basename(path)
        category = self._category_from_path(path)
        evt = Event(start_time, end_time, text, category)
        return evt

    def _category_from_path(self, path):
        for cat in self.categories:
            if cat.name == os.path.dirname(path):
                return cat
        return None

    def _category_from_name(self, name):
        for cat in self.categories:
            if cat.name == name:
                return cat
        return None

    def _color_from_range(self, range):
        (rstart, rend, b) = range
        (r, g, b) = colorsys.hsv_to_rgb(rstart, b, 1)
        return (r*255, g*255, b*255)
