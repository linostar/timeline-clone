"""
Custom data types.
"""


from datetime import timedelta
from datetime import datetime as dt


# To save computation power (used by `delta_to_microseconds`)
US_PER_SEC = 1000000
US_PER_DAY = 24 * 60 * 60 * US_PER_SEC


class Timeline(object):
    """
    Base class that represents the interface for a timeline.

    A possible implementation could be for a timeline stored in a flat file or
    in a SQL database.

    In order to get an implementation, the `get_timeline` factory method should
    be used.

    All methods that modify the timeline should automatically save it.
    """

    def get_events(self, time_period):
        """Return a list of all events visible within the time period."""
        raise NotImplementedError()

    def add_event(self, event):
        """Add `event` to the timeline."""
        raise NotImplementedError()

    def event_edited(self, event):
        """Notify that `event` has been modified so that it can be saved."""
        raise NotImplementedError()

    def delete_selected_events(self):
        """Delete all events whose selected flag is True."""
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

    def reset_selection(self):
        """Reset any selection on the timeline."""
        raise NotImplementedError()


class Event(object):
    """Represents an event on a timeline."""

    def __init__(self, start_time, end_time, text, category=None):
        """
        Create an event.

        `start_time` and `end_time` should be of the type datetime.
        """
        self.selected = False
        self.update(start_time, end_time, text, category)

    def update(self, start_time, end_time, text, category=None):
        """Change the event data."""
        self.time_period = TimePeriod(start_time, end_time)
        self.text = text
        self.category = category

    def inside_period(self, time_period):
        """Wrapper for time period method."""
        return self.time_period.overlap(time_period)

    def is_period(self):
        """Wrapper for time period method."""
        return self.time_period.is_period()

    def mean_time(self):
        """Wrapper for time period method."""
        return self.time_period.mean_time()


class Category(object):
    """Represents a category that an event belongs to."""

    def __init__(self, name, color):
        """
        Create a category with the given name and color.

        name = string
        color = (r, g, b)
        """
        self.name = name
        self.color = color


class TimePeriod(object):
    """
    Represents a period in time using a start and end time.

    This is used both to store the time period for an event and for storing the
    currently displayed time period in the GUI.
    """

    def __init__(self, start_time, end_time):
        """
        Create a time period.

        `start_time` and `end_time` should be of the type datetime.
        """
        self.update(start_time, end_time)

    def update(self, start_time, end_time):
        """
        Change the time period data.

        If data is invalid, it will not be set, and a ValueError will be raised
        instead.
        """
        if start_time > end_time:
            raise ValueError("Start time can't be after end time")
        if start_time.year < 10:
            raise ValueError("Start time can't be before year 10")
        self.start_time = start_time
        self.end_time = end_time

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
        return self.start_time + self.delta() / 2

    def zoom(self, times):
        MAX_ZOOM_DELTA = timedelta(days=120*365)
        MIN_ZOOM_DELTA = timedelta(hours=1)
        delta = mult_timedelta(self.delta(), times / 10.0)
        new_delta = self.delta() - 2 * delta
        if new_delta > MAX_ZOOM_DELTA:
            raise ValueError("Can't zoom wider than 120 years")
        if new_delta < MIN_ZOOM_DELTA:
            raise ValueError("Can't zoom deeper than 1 hour")
        self.update(self.start_time + delta, self.end_time - delta)

    def move(self, dir):
        delta = mult_timedelta(self.delta(), dir / 10.0)
        self.move_delta(delta)

    def move_delta(self, delta):
        self.update(self.start_time + delta, self.end_time + delta)

    def delta(self):
        """Return the length of this time period as a timedelta object."""
        return self.end_time - self.start_time

    def center(self, time):
        """Center time period around time keeping the length."""
        self.move_delta(time - self.mean_time())

    def fit_year(self):
        mean = self.mean_time()
        start = dt(mean.year, 1, 1)
        end = dt(mean.year + 1, 1, 1)
        self.update(start, end)

    def fit_month(self):
        mean = self.mean_time()
        start = dt(mean.year, mean.month, 1)
        end = dt(mean.year, mean.month + 1, 1)
        self.update(start, end)

    def fit_day(self):
        mean = self.mean_time()
        start = dt(mean.year, mean.month, mean.day)
        end = dt(mean.year, mean.month, mean.day + 1)
        self.update(start, end)


def delta_to_microseconds(delta):
    """Return the number of microseconds that the timedelta represents."""
    return (delta.days * US_PER_DAY +
            delta.seconds * US_PER_SEC +
            delta.microseconds)


def microseconds_to_delta(microsecs):
    """Return a timedelta representing the given number of microseconds."""
    return timedelta(microseconds=microsecs)


def mult_timedelta(delta, num):
    """Return a new timedelta that is `num` times larger than `delta`."""
    days = delta.days * num
    seconds = delta.seconds * num
    microseconds = delta.microseconds * num
    return timedelta(days, seconds, microseconds)


def div_timedeltas(delta1, delta2):
    """Return how many times delta2 fit in delta1."""
    # Since Python can handle infinitely large numbers, this solution works. It
    # might however not be optimal. If you are clever, you should be able to
    # treat the different parts individually. But this is simple.
    total_us1 = delta_to_microseconds(delta1)
    total_us2 = delta_to_microseconds(delta2)
    # Make sure that the result is a floating point number
    return total_us1 / float(total_us2)


def time_period_center(time, length):
    """
    TimePeriod factory method.

    Return a time period with the given length (represented as a timedelta)
    centered around `time`.
    """
    half_length = mult_timedelta(length, 0.5)
    start_time = time - half_length
    end_time = time + half_length
    return TimePeriod(start_time, end_time)


def get_timeline(input_file):
    """
    Timeline factory method.

    Return a specific timeline depending on the input_file.
    """
    if input_file.endswith(".timeline"):
        from data_file import FileTimeline
        return FileTimeline(input_file)
    elif input_file.endswith(".db2timeline"):
        from data_db2 import Db2Timeline
        return Db2Timeline(input_file)
    else:
        raise Exception("Unknown format")
