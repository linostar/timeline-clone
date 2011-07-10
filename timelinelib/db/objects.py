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


"""
Objects that can be read from and written to a timeline database.
"""


class Event(object):
    """
    Store persistent data about an event.

    The event's id is managed by the database. An event with id None is viewed
    as an event not saved to a database. After a successful save by a database,
    it will set the event id to a unique integer.
    """

    def __init__(self, db, start_time, end_time, text, category=None, 
                 fuzzy=False, locked=False, ends_today=False):
        self.db = db
        self.fuzzy = fuzzy
        self.locked = locked
        self.ends_today = ends_today
        self.id = None
        self.selected = False
        self.draw_ballon = False
        self.update(start_time, end_time, text, category)
        self.data = {}

    def has_id(self):
        return self.id is not None

    def set_id(self, id):
        self.id = id

    def update(self, start_time, end_time, text, category=None, fuzzy=None, 
               locked=None, ends_today=None):
        """Change the event data."""
        time_type = self.db.get_time_type()
        self.time_period = TimePeriod(time_type, start_time, end_time)
        self.text = text
        self.category = category
        if ends_today is not None:
            if not self.locked: 
                self.ends_today = ends_today
        if fuzzy is not None:
            self.fuzzy = fuzzy
        if locked is not None:
            self.locked = locked

    def update_period(self, start_time, end_time):
        """Change the event period."""
        self.time_period = TimePeriod(self.db.get_time_type(), start_time, 
                                      end_time)
        
    def update_start(self, start_time):
        """Change the event data."""
        if start_time <= self.time_period.end_time:
            self.time_period = TimePeriod(self.db.get_time_type(), start_time, 
                                          self.time_period.end_time)
            return True
        return False            

    def update_end(self, end_time):
        """Change the event data."""
        if end_time >= self.time_period.start_time:
            self.time_period = TimePeriod(self.db.get_time_type(), 
                                          self.time_period.start_time, end_time)
            return True
        return False            

    def inside_period(self, time_period):
        """Wrapper for time period method."""
        return self.time_period.overlap(time_period)

    def is_period(self):
        """Wrapper for time period method."""
        return self.time_period.is_period()

    def mean_time(self):
        """Wrapper for time period method."""
        return self.time_period.mean_time()

    def get_data(self, id):
        """
        Return data with the given id or None if no data with that id exists.

        See set_data for information how ids map to data.
        """
        return self.data.get(id, None)

    def set_data(self, id, data):
        """
        Set data with the given id.

        Here is how ids map to data:

            description - string
            icon - wx.Bitmap
        """
        self.data[id] = data

    def has_data(self):
        """Return True if the event has associated data, or False if not."""
        for id in self.data:
            if self.data[id] != None:
                return True
        return False

    def get_label(self):
        """Returns a unicode label describing the event."""
        return u"%s (%s)" % (self.text, self.time_period.get_label())

    def clone(self):
        # Objects of type datetime are immutable.
        new_event = Event(self.db, self.time_period.start_time, 
                          self.time_period.end_time, self.text, self.category)
        # Description is immutable
        new_event.set_data("description", self.get_data("description") )
        # Icon is immutable in the sense that it is never changed by our 
        # application.    
        new_event.set_data("icon", self.get_data("icon"))    
        return new_event

    
class Category(object):
    """
    Store persistent data about a category.

    Its id is managed in the same way as for events.

    NOTE: The visible flag of categories should not be used any longer.
    Visibility of categories are now managed in ViewProperties. However some
    timeline databases still use this flag to manage the saving. This flag
    should be removed when we can.
    """

    def __init__(self, name, color, visible, parent=None):
        """
        Create a category with the given name and color.

        name = string
        color = (r, g, b)
        """
        self.id = None
        self.name = name
        self.color = color
        self.visible = visible
        self.parent = parent

    def has_id(self):
        return self.id is not None

    def set_id(self, id):
        self.id = id


class TimeOutOfRangeLeftError(ValueError):
    pass


class TimeOutOfRangeRightError(ValueError):
    pass


class PeriodTooLongError(ValueError):
    pass


class TimePeriod(object):
    """
    Represents a period in time using a start and end time.

    This is used both to store the time period for an event and for storing the
    currently displayed time period in the GUI.
    """

    def __init__(self, time_type, start_time, end_time):
        """
        Create a time period.

        `start_time` and `end_time` should be of a type that can be handled
        by the time_type object.
        """
        self.time_type = time_type
        self.start_time, self.end_time = self._update(start_time, end_time)

    def clone(self):
        return TimePeriod(self.time_type, self.start_time, self.end_time)

    def __eq__(self, other):
        if isinstance(other, TimePeriod):
            return (self.start_time == other.start_time and
                    self.end_time == other.end_time)
        return False

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return "TimePeriod<%s, %s>" % (self.start_time, self.end_time)

    def update(self, start_time, end_time,
               start_delta=None, end_delta=None):
        new_start, new_end = self._update(start_time, end_time, start_delta, end_delta)
        return TimePeriod(self.time_type, new_start, new_end)

    def _update(self, start_time, end_time,
               start_delta=None, end_delta=None):
        """
        Change the time period data.

        Optionally add the deltas to the times like this: time + delta.

        If data is invalid, it will not be set, and a ValueError will be raised
        instead.

        Data is invalid if time + delta is not within the range 
        [self.time_type.get_min_time(), self.time_type.get_max_time()] or if 
        the start time is larger than the end time.
        """
        new_start = self._ensure_within_range(start_time, start_delta, 
                                              _("Start time "))
        new_end = self._ensure_within_range(end_time, end_delta,
                                            _("End time "))
        self._assert_period_is_valid(new_start, new_end)
        return (new_start, new_end)

    def _assert_period_is_valid(self, new_start, new_end):
        self._assert_start_gt_end(new_start, new_end)
        self._assert_period_lt_max(new_start, new_end)
        
    def _assert_start_gt_end(self, new_start, new_end):
        if new_start > new_end:
            raise ValueError(_("Start time can't be after end time"))

    def _assert_period_lt_max(self, new_start, new_end):
        MAX_ZOOM_DELTA, max_zoom_error_text = self.time_type.get_max_zoom_delta()
        if MAX_ZOOM_DELTA and (new_end - new_start > MAX_ZOOM_DELTA):
            raise PeriodTooLongError(max_zoom_error_text)
        
    def inside(self, time):
        """
        Return True if the given time is inside this period or on the border,
        otherwise False.
        """
        return time >= self.start_time and time <= self.end_time

    def overlap(self, time_period):
        """Return True if this time period has any overlap with the given."""
        return not (time_period.end_time < self.start_time or
                    time_period.start_time > self.end_time)

    def is_period(self):
        """
        Return True if this time period is longer than just a point in time,
        otherwise False.
        """
        return self.start_time != self.end_time

    def mean_time(self):
        """
        Return the time in the middle if this time period is longer than just a
        point in time, otherwise the point in time for this time period.
        """
        return self.start_time + self.time_type.half_delta(self.delta())

    def zoom(self, times):
        MAX_ZOOM_DELTA, max_zoom_error_text = self.time_type.get_max_zoom_delta()
        MIN_ZOOM_DELTA, min_zoom_error_text = self.time_type.get_min_zoom_delta()
        start_delta = self.time_type.mult_timedelta(self.delta(), times / 10.0)
        end_delta = self.time_type.mult_timedelta(self.delta(), -times / 10.0)
        new_delta = self.delta() - 2 * start_delta
        if MAX_ZOOM_DELTA and new_delta > MAX_ZOOM_DELTA:
            raise ValueError(max_zoom_error_text)
        if new_delta < MIN_ZOOM_DELTA:
            raise ValueError(min_zoom_error_text)
        return self.update(self.start_time, self.end_time, start_delta, end_delta)

    def move(self, direction):
        """
        Move this time period one 10th to the given direction.

        Direction should be -1 for moving to the left or 1 for moving to the
        right.
        """
        delta = self.time_type.mult_timedelta(self.delta(), direction / 10.0)
        return self.move_delta(delta)

    def move_delta(self, delta):
        return self.update(self.start_time, self.end_time, delta, delta)

    def delta(self):
        """Return the length of this time period as a timedelta object."""
        return self.end_time - self.start_time

    def center(self, time):
        """
        Center time period around time keeping the length.

        If we can't center because we are on the edge, we do as good as we can.
        """
        delta = time - self.mean_time()
        start_overflow = self._calculate_overflow(self.start_time, delta)[1]
        end_overflow = self._calculate_overflow(self.end_time, delta)[1]
        if start_overflow == -1:
            delta = self.time_type.get_min_time()[0] - self.start_time
        elif end_overflow == 1:
            delta = self.time_type.get_max_time()[0] - self.end_time
        return self.move_delta(delta)

    def _ensure_within_range(self, time, delta, error_prefix):
        """
        Return new time (time + delta) or raise ValueError if it is not within
        the range [self.time_type.get_min_time(), 
        self.time_type.get_max_time()].
        """
        if delta == None:
            delta = self.time_type.get_zero_delta()
        new_time, overflow, error_text = self._calculate_overflow(time, delta)
        if overflow != 0:
            error_text = "%s %s" % (error_prefix, error_text)
            raise ValueError(error_text)
        else:
            return new_time

    def _calculate_overflow(self, time, delta):
        """
        Return a tuple (new time, overflow flag).

        Overflow flag can be -1 (overflow to the left), 0 (no overflow), or 1
        (overflow to the right).

        If overflow flag is 0 new time is time + delta, otherwise None.
        """
        try:
            min_time, min_error_text = self.time_type.get_min_time()
            max_time, max_error_text = self.time_type.get_max_time()
            new_time = time + delta
            if min_time and new_time < min_time:
                return (None, -1, min_error_text)
            if max_time and new_time > max_time:
                return (None, 1, max_error_text)
            return (new_time, 0, "")
        except OverflowError:
            if delta > self.time_type.get_zero_delta():
                return (None, 1, max_error_text)
            else:
                return (None, -1, min_error_text)

    def get_label(self):
        """Returns a unicode string describing the time period."""
        return self.time_type.format_period(self)

    def has_nonzero_time(self):
        return self.time_type.time_period_has_nonzero_time(self)


def time_period_center(time_type, time, length):
    """
    TimePeriod factory method.

    Return a time period with the given length (represented as a timedelta)
    centered around `time`.
    """
    half_length = time_type.mult_timedelta(length, 0.5)
    start_time = time - half_length
    end_time = time + half_length
    return TimePeriod(time_type, start_time, end_time)
