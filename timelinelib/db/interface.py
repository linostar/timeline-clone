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
    Read (and write) timeline data to persistent storage.

    All methods that modify the timeline should automatically save it.

    A TimelineDB is observable so that GUI components can update themselves
    when it changes. The two types of state changes are given as constants
    below.
    """

    def __init__(self, path):
        Observable.__init__(self)
        self.path = path

    def get_events(self, time_period):
        """Return a list of all events visible within the time period whose
        category is visible."""
        raise NotImplementedError()

    def add_event(self, event):
        """Add `event` to the timeline."""
        raise NotImplementedError()

    def event_edited(self, event):
        """Notify that `event` has been modified so that it can be saved."""
        raise NotImplementedError()

    def select_event(self, event, selected=True):
        """
        Notify that event should be marked as selected.

        Must ensure that subsequent calls to get_events maintains this selected
        state.
        """
        raise NotImplementedError()

    def delete_selected_events(self):
        """Delete all events that have been marked as selected."""
        raise NotImplementedError()

    def reset_selected_events(self):
        """Mark all selected events as unselected."""
        raise NotImplementedError()

    def get_categories(self):
        """Return a list of all available categories."""
        raise NotImplementedError()

    def add_category(self, category):
        """Add `category` to the timeline."""
        raise NotImplementedError()

    def category_edited(self, category):
        """Notify that `category` has been modified so that it can be saved."""
        raise NotImplementedError()

    def delete_category(self, category):
        """Delete `category` and remove it from all events."""
        raise NotImplementedError()

    def get_preferred_period(self):
        """Return the preferred period to display of this timeline."""
        raise NotImplementedError()

    def set_preferred_period(self, period):
        """Set the preferred period to display of this timeline."""
        raise NotImplementedError()


class TimelineIOError(Exception):
    """
    Raised from a TimelineDB if a read/write error occurs.

    The constructor and any of the public methods can raise this exception.

    Also raised by the get_timeline method if loading of a timeline failed.
    """
    pass
