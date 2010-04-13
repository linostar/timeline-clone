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
Definition of interface that timeline databases should adhere to.

Actual implementations of timeline databases are in the backends package.
"""


from timelinelib.observer import Observable


# A category was added, edited, or deleted
STATE_CHANGE_CATEGORY = 1
# Something happened that changed the state of the timeline
STATE_CHANGE_ANY = 2


class TimelineDB(Observable):
    """
    Read (and write) timeline data from persistent storage.

    All methods that modify timeline data should automatically write it to
    persistent storage.

    A TimelineIOError should be raised if reading or writing fails. After such
    a failure the database it not guarantied to return correct data. (Read and
    write errors are however very rare.)

    A timeline database is observable so that GUI components can update
    themselves when data changes. The two types of state changes are given as
    constants above.

    Future considerations: If databases get large it might be inefficient to
    save to persistent storage every time we modify the database. A solution is
    to add an explicit save method and have all the other methods just modify
    the database in memory.
    """

    def __init__(self, path):
        Observable.__init__(self)
        self.path = path

    def is_read_only(self):
        """
        Return True if you can only read from this database and False if you
        can both read and write.
        """
        raise NotImplementedError()

    def supported_event_data(self):
        """
        Return a list of event data that we can write.

        Event data is represented by a string id. See Event.set_data for
        information what string id map to what data.

        Not required if is_read_only returns True.
        """
        raise NotImplementedError()

    def search(self, search_string):
        """
        Return a list of events matching the search string.
        """
        raise NotImplementedError()

    def get_events(self, time_period):
        """
        Return a list of events within the time period.
        """
        raise NotImplementedError()

    def get_all_events(self, time_period):
        """
        Return a list of all events in the database.
        """
        raise NotImplementedError()

    def get_first_event(self):
        """Return the event with the earliest start time."""
        raise NotImplementedError()
        
    def get_last_event(self):
        """Return the event with the latest end time."""
        raise NotImplementedError()
        
    def save_event(self, event):
        """
        Make sure that the given event is saved to persistent storage.

        If the event is new it is given a new unique id. Otherwise the
        information in the database is just updated.

        Not required if is_read_only returns True.
        """
        raise NotImplementedError()

    def delete_event(self, event_or_id):
        """
        Delete the event (or the event with the given id) from the database.

        Not required if is_read_only returns True.
        """
        raise NotImplementedError()

    def get_categories(self):
        """
        Return a list of all available categories.
        """
        raise NotImplementedError()

    def save_category(self, category):
        """
        Make sure that the given category is saved to persistent storage.

        If the category is new it is given a new unique id. Otherwise the
        information in the database is just updated.

        Not required if is_read_only returns True.
        """
        raise NotImplementedError()

    def delete_category(self, category_or_id):
        """
        Delete the category (or the category with the given id) from the
        database.

        Not required if is_read_only returns True.
        """
        raise NotImplementedError()
    
    def load_view_properties(self, view_properties):
        """
        Load saved view properties from persistent storage into view_properties
        object.
        """
        raise NotImplementedError()

    def save_view_properties(self, view_properties):
        """
        Save subset of view properties to persistent storage.

        Not required if is_read_only returns True.
        """
        raise NotImplementedError()

    def find_event_with_id(self, id):
        """
        Return the event associated with the given event id.
        """
        raise NotImplementedError()


class TimelineIOError(Exception):
    """
    Raised from a TimelineDB if a read/write error occurs.

    The constructor and any of the public methods can raise this exception.

    Also raised by the get_timeline method if loading of a timeline failed.
    """
    pass
