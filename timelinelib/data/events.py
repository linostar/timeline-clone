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


from timelinelib.data.category import clone_categories_list
from timelinelib.data.event import clone_event_list
from timelinelib.data.idnumber import get_process_unique_id


class Events(object):

    def __init__(self, categories=None, events=None):
        if categories is None:
            self.categories = []
        else:
            self.categories = categories
        if events is None:
            self.events = []
        else:
            self.events = events

    def get_all(self):
        return list(self.events)

    def get_first(self):
        if len(self.get_all()) == 0:
            return None
        return min(self.get_all(), key=lambda e: e.time_period.start_time)

    def get_last(self):
        if len(self.get_all()) == 0:
            return None
        return max(self.get_all(), key=lambda e: e.time_period.end_time)

    def get_in_period(self, time_period):
        def include_event(event):
            if not event.inside_period(time_period):
                return False
            return True
        return [e for e in self.events if include_event(e)]

    def search(self, search_string):
        return _generic_event_search(self.events, search_string)

    def get_categories(self):
        return list(self.categories)

    def get_category_by_name(self, name):
        for category in self.categories:
            if category.name == name:
                return category

    def save_category(self, category):
        from timelinelib.data.db import InvalidOperationError
        if (category.parent is not None and
            category.parent not in self.categories):
            raise InvalidOperationError("Parent category not in db.")
        self._ensure_no_circular_parent(category)
        if not category in self.categories:
            self._append_category(category)

    def _ensure_no_circular_parent(self, cat):
        from timelinelib.data.db import InvalidOperationError
        parent = cat.parent
        while parent is not None:
            if parent == cat:
                raise InvalidOperationError("Circular category parent.")
            else:
                parent = parent.parent

    def _append_category(self, category):
        from timelinelib.data.db import InvalidOperationError
        if category.has_id():
            raise InvalidOperationError("Category with id %s not found in db." % category.id)
        self.categories.append(category)
        category.set_id(get_process_unique_id())

    def clone(self):
        (categories, events) = clone_data(self.categories, self.events)
        return Events(categories, events)


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


def clone_data(categories, events):
    categories, catclones = clone_categories_list(categories)
    events = clone_event_list(events)
    for event in events:
        try:
            event.category = catclones[event.category]
        except KeyError:
            event.category = None
    return categories, events
