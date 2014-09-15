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


class Events(object):

    def __init__(self):
        self.categories = []
        self.events = []

    def get_all(self):
        return list(self.events)

    def search(self, search_string):
        return _generic_event_search(self.events, search_string)


def _generic_event_search(events, search_string):
    def match(event):
        target = search_string.lower()
        description = event.get_data("description")
        if description is None:
            description = ""
        else:
            description = description.lower()
        return target in event.text.lower() or target in description
    def mean_time(event):
        return event.mean_time()
    matches = [event for event in events if match(event)]
    matches.sort(key=mean_time)
    return matches
