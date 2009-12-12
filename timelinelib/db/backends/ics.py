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
Implementation of timeline database that reads and writes (todo) ICS files.
"""


import re
import codecs
import shutil
import os.path
from os.path import abspath
from datetime import date
from datetime import datetime
from datetime import timedelta

from icalendar import Calendar

from timelinelib.db.interface import TimelineIOError
from timelinelib.db.interface import TimelineDB
from timelinelib.db.interface import STATE_CHANGE_ANY
from timelinelib.db.interface import STATE_CHANGE_CATEGORY
from timelinelib.db.objects import TimePeriod
from timelinelib.db.objects import Event
from timelinelib.db.objects import Category
from timelinelib.db.objects import time_period_center
from timelinelib.db.utils import IdCounter
from timelinelib.db.utils import safe_write
from timelinelib.version import get_version


class IcsTimeline(TimelineDB):

    def __init__(self, path):
        TimelineDB.__init__(self, path)
        self.event_id_counter = IdCounter()
        self._load_data()

    def is_read_only(self):
        return True

    def supported_event_data(self):
        return ["description"]

    def get_events(self, time_period):
        events = []
        for event in self.cal.walk("VEVENT"):
            start, end = extract_start_end(event)
            txt = ""
            if event.has_key("summary"):
                txt = event["summary"]
            e = Event(start, end, txt)
            if e.inside_period(time_period):
                e.set_id(event["timeline_id"])
                events.append(e)
        return events

    def save_event(self, event):
        pass

    def delete_event(self, event_or_id):
        pass

    def get_categories(self):
        return []

    def save_category(self, category):
        pass

    def delete_category(self, category_or_id):
        pass

    def get_preferred_period(self):
        return time_period_center(datetime.now(), timedelta(days=30))

    def set_preferred_period(self, period):
        pass

    def _load_data(self):
        self.cal = Calendar()
        if not os.path.exists(self.path): 
            # Nothing to load. Will create a new timeline on save.
            return
        try:
            file = open(self.path, "rb")
            try:
                file_contents = file.read()
                try:
                    self.cal = Calendar.from_string(file_contents)
                    for event in self.cal.walk("VEVENT"):
                        event["timeline_id"] = self.event_id_counter.get_next()
                except Exception, pe:
                    msg1 = _("Unable to read timeline data from '%s'.")
                    msg2 = "\n\n" + pe.message
                    raise TimelineIOError((msg1 % abspath(self.path)) + msg2)
            finally:
                file.close()
        except IOError, e:
            msg = _("Unable to read from file '%s'.")
            whole_msg = (msg + "\n\n%s") % (abspath(self.path), e)
            raise TimelineIOError(whole_msg)

    def _save_data(self):
        #def save(file):
        #    file.write(self.cal.as_string())
        #safe_write(self.path, NONE, save)
        pass


def extract_start_end(vevent):
    """Return (start_time, end_time)."""
    start = ensure_datetime(vevent.decoded("dtstart"))
    if vevent.has_key("dtend"):
        end = ensure_datetime(vevent.decoded("dtend"))
    else:
        end = start + vevent.decoded("duration")
    return (start, end)


def ensure_datetime(d):
    if isinstance(d, datetime):
        return datetime(d.year, d.month, d.day, d.hour, d.minute, d.second)
    elif isinstance(d, date):
        return datetime(d.year, d.month, d.day)
    else:
        raise Exception("Unknown date")
