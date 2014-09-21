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


class InvalidOperationError(Exception):
    pass


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
        return min(self.get_all(), key=lambda e: e.get_time_period().start_time)

    def get_last(self):
        if len(self.get_all()) == 0:
            return None
        return max(self.get_all(), key=lambda e: e.get_time_period().end_time)

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
            if category.get_name() == name:
                return category

    def save_category(self, category):
        self._ensure_category_exists_for_update(category)
        self._ensure_category_name_available(category)
        self._ensure_parent_exists(category)
        self._ensure_no_circular_parent(category)
        if not self._does_category_exists(category):
            category.set_id(get_process_unique_id())
            self.categories.append(category)

    def _ensure_category_exists_for_update(self, category):
        message = "Updating a category that does not exist."
        if category.has_id():
            if not self._does_category_exists(category):
                raise InvalidOperationError(message)

    def _ensure_category_name_available(self, category):
        message = "A category with name %r already exists." % category.get_name()
        ids = self._get_ids_with_name(category.get_name())
        if self._does_category_exists(category):
            if ids != [category.get_id()]:
                raise InvalidOperationError(message)
        else:
            if ids != []:
                raise InvalidOperationError(message)

    def _get_ids_with_name(self, name):
        ids = []
        for category in self.get_categories():
            if category.get_name() == name:
                ids.append(category.get_id())
        return ids

    def _does_category_exists(self, a_category):
        for stored_category in self.get_categories():
            if stored_category.get_id() == a_category.get_id():
                return True
        return False

    def _ensure_parent_exists(self, category):
        message = "Parent category not in db."
        if (category.get_parent() is not None and
            category.get_parent() not in self.categories):
            raise InvalidOperationError(message)

    def _ensure_no_circular_parent(self, category):
        message = "Circular category parent."
        parent = category.get_parent()
        while parent is not None:
            if parent == category:
                raise InvalidOperationError(message)
            else:
                parent = parent.get_parent()

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
        return target in event.get_text().lower() or target in description
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
            event.set_category(catclones[event.get_category()])
        except KeyError:
            event.set_category(None)
    return categories, events
