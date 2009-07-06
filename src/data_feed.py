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
Implementation of a read-only Timeline that gets its information from a feed.
"""


import feedparser
from datetime import datetime
from datetime import timedelta

from data import Timeline
from data import Event
from data import time_period_center


class FeedTimeline(Timeline):

    def __init__(self, feed_path):
        Timeline.__init__(self)
        self.data = feedparser.parse(feed_path)

    def get_events(self, time_period):
        res = []
        for entry in self.data.entries:
            date = datetime(*entry.date_parsed[0:6])
            text = entry.title
            e = Event(date, date, text)
            if e.inside_period(time_period):
                res.append(e)
        return res

    def add_event(self, event):
        # Not supported because read-only
        pass

    def event_edited(self, event):
        # Not supported because read-only
        pass

    def select_event(self, event, selected=True):
        # Not supported because read-only
        pass

    def delete_selected_events(self):
        # Not supported because read-only
        pass

    def reset_selected_events(self):
        # Not supported because read-only
        pass

    def get_categories(self):
        return []

    def add_category(self, category):
        # Not supported because read-only
        pass

    def category_edited(self, category):
        # Not supported because read-only
        pass

    def delete_category(self, category):
        # Not supported because read-only
        pass

    def get_preferred_period(self):
        return time_period_center(datetime.now(), timedelta(days=10))

    def set_preferred_period(self, period):
        # Not supported because read-only
        pass
