# Copyright (C) 2009, 2010  Rickard Lindberg, Roger Lindberg
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
Implementation of timeline database that stores all data in memory.

MemoryDB can be used as a base class for other timeline databases that wish to
store all data in memory and also want to save the data to persistent storage
whenever it changes in memory. Initially data can be read from persistent
storage into memory.

MemoryDB is not suitable as a base class for timeline databases that need to
query persistent storage to retrieve data.
"""


from timelinelib.db.interface import TimelineIOError
from timelinelib.db.interface import TimelineDB
from timelinelib.db.interface import STATE_CHANGE_ANY
from timelinelib.db.interface import STATE_CHANGE_CATEGORY
from timelinelib.db.objects import Event
from timelinelib.db.objects import Category
from timelinelib.db.utils import IdCounter
from timelinelib.db.utils import generic_event_search


class MemoryDB(TimelineDB):

    def __init__(self):
        TimelineDB.__init__(self, "")
        self.categories = []
        self.category_id_counter = IdCounter()
        self.events = []
        self.event_id_counter = IdCounter()
        self.displayed_period = None
        self.hidden_categories = []
        self.save_disabled = False

    def is_read_only(self):
        return False

    def supported_event_data(self):
        return ["description", "icon"]

    def search(self, search_string):
        return generic_event_search(self.events, search_string)

    def get_events(self, time_period):
        def include_event(event):
            if not event.inside_period(time_period):
                return False
            return True
        return [e for e in self.events if include_event(e)]

    def get_all_events(self):
        return list(self.events)

    def get_first_event(self):
        if len(self.events) == 0:
            return None
        e = min(self.events, key=lambda e: e.time_period.start_time)
        return e

    def get_last_event(self):
        if len(self.events) == 0:
            return None
        e = max(self.events, key=lambda e: e.time_period.end_time)
        return e
        
    def save_event(self, event):
        if (event.category is not None and
            event.category not in self.categories):
            raise TimelineIOError("Event's category not in db.")
        if event not in self.events:
            if event.has_id():
                raise TimelineIOError("Event with id %s not found in db." %
                                      event.id)
            self.events.append(event)
            event.set_id(self.event_id_counter.get_next())
        self._save_if_not_disabled()
        self._notify(STATE_CHANGE_ANY)

    def delete_event(self, event_or_id):
        if isinstance(event_or_id, Event):
            event = event_or_id
        else:
            event = self.find_event_with_id(event_or_id)
        if event in self.events:
            self.events.remove(event)
            event.set_id(None)
            self._save_if_not_disabled()
            self._notify(STATE_CHANGE_ANY)
        else:
            raise TimelineIOError("Event not in db.")

    def get_categories(self):
        return list(self.categories)

    def save_category(self, category):
        if (category.parent is not None and
            category.parent not in self.categories):
            raise TimelineIOError("Parent category not in db.")
        self._ensure_no_circular_parent(category)
        if not category in self.categories:
            if category.has_id():
                raise TimelineIOError("Category with id %s not found in db." %
                                      category.id)
            self.categories.append(category)
            category.set_id(self.event_id_counter.get_next())
        self._save_if_not_disabled()
        self._notify(STATE_CHANGE_CATEGORY)

    def delete_category(self, category_or_id):
        if isinstance(category_or_id, Category):
            category = category_or_id
        else:
            category = self._find_category_with_id(category_or_id)
        if category in self.categories:
            if category in self.hidden_categories:
                self.hidden_categories.remove(category)
            self.categories.remove(category)
            category.set_id(None)
            # Loop to update parent attribute on children
            for cat in self.categories:
                if cat.parent == category:
                    cat.parent = category.parent
            self._save_if_not_disabled()
            self._notify(STATE_CHANGE_CATEGORY)
        else:
            raise TimelineIOError("Category not in db.")

    def load_view_properties(self, view_properties):
        view_properties.displayed_period = self.displayed_period
        for cat in self.categories:
            visible = cat not in self.hidden_categories
            view_properties.set_category_visible(cat, visible)

    def save_view_properties(self, view_properties):
        if view_properties.displayed_period is not None:
            if not view_properties.displayed_period.is_period():
                raise TimelineIOError(_("Displayed period must be > 0."))
            self.displayed_period = view_properties.displayed_period
        self.hidden_categories = []
        for cat in self.categories:
            if not view_properties.category_visible(cat):
                self.hidden_categories.append(cat)
        self._save_if_not_disabled()

    def disable_save(self):
        self.save_disabled = True

    def enable_save(self, call_save=True):
        if self.save_disabled == True:
            self.save_disabled = False
            if call_save == True:
                self._save_if_not_disabled()

    def _ensure_no_circular_parent(self, cat):
        parent = cat.parent
        while parent is not None:
            if parent == cat:
                raise TimelineIOError("Circular category parent.")
            else:
                parent = parent.parent
    
    def find_event_with_id(self, id):
        for e in self.events:
            if e.id == id:
                return e
        return None

    def _find_category_with_id(self, id):
        for c in self.categories:
            if c.id == id:
                return c
        return None

    def _save_if_not_disabled(self):
        if self.save_disabled == False:
            self._save()

    def _get_displayed_period(self):
        """
        Inheritors can call this method to get the displayed period used in
        load_view_properties and save_view_properties.
        """
        return self.displayed_period

    def _set_displayed_period(self, period):
        """
        Inheritors can call this method to set the displayed period used in
        load_view_properties and save_view_properties.
        """
        self.displayed_period = period

    def _get_hidden_categories(self):
        """
        Inheritors can call this method to get the hidden categories used in
        load_view_properties and save_view_properties.
        """
        return self.hidden_categories

    def _set_hidden_categories(self, hidden_categories):
        """
        Inheritors can call this method to set the hidden categories used in
        load_view_properties and save_view_properties.
        """
        self.hidden_categories = []
        for cat in hidden_categories:
            if cat not in self.categories:
                raise ValueError("Category '%s' not in db." % cat.name)
            self.hidden_categories.append(cat)

    def _save(self):
        """
        Inheritors can override this method to save this db to persistent
        storage.

        Called whenever this db changes.
        """
        pass
