"""
Implementation of `Timeline` with DB2 storage.

The class `Db2Timeline` implements the `Timeline` interface.
"""


import re
import codecs
from logging import error as logerror
from logging import info as loginfo
from logging import debug as logdebug
from datetime import datetime
from datetime import timedelta

import DB2

from data import Timeline
from data import TimePeriod
from data import Event
from data import Category
from data import time_period_center
from gui import display_error_message


class ParseException(Exception):
    """Thrown if loading of data read from database fails."""
    pass

class LoadException(Exception):
    """Thrown if loading of data read from database fails."""
    pass


class Db2Timeline(Timeline):
    """
    Implements the `Timeline` interface.

    The comments in the `Timeline` class describes what the public methods
    should do.
    """

    def __init__(self, database):
        """
        Create a new timeline and read data from file.

        The usage of a DB2 database is recognized by investigation of the
        file argument given to the application. If the file extension
        = .db2timeline then DB2 will be used and the datebase to use is the
        filename. So if the follwoing filename is given:
           timeline.db2timeline
        DB2 is used and the database to use is 'timeline'.
        """

        self.database = database.split('.')[0]
        self.__load_data()

    def get_events(self, time_period):
        return [event for event in self.events
                if event.inside_period(time_period)]

    def add_event(self, event):
        self.events.append(event)
        self.__save_data()

    def event_edited(self, event):
        self.__save_data()

    def delete_selected_events(self):
        self.events = [event for event in self.events if not event.selected]
        self.__save_data()

    def get_categories(self):
        # Make sure the original list can't be modified
        return tuple(self.categories)

    def add_category(self, category):
        self.categories.append(category)
        self.__save_data()

    def category_edited(self, category):
        self.__save_data()

    def delete_category(self, category):
        if category in self.categories:
            self.categories.remove(category)
        for event in self.events:
            if event.category == category:
                event.category = None
        self.__save_data()

    def get_preferred_period(self):
        if self.preferred_period:
            return self.preferred_period
        return time_period_center(datetime.now(), timedelta(days=30))

    def set_preferred_period(self, period):
        self.preferred_period = period
        self.__save_data()

    def reset_selected_events(self):
        for event in self.events:
            event.selected = False

    def __get_login_info(self):
        """Ask for, and return the user name and password"""
        return ('roger', 'roglin50')

    def __save_data(self):
        """Save timeline data to the database that this timeline points to."""

    def __execute_query(self, query):
        """ Issue a query to the database and return the result set """
        db2_connection = None
        db2_cursor = None
        try:
            try:
                db2_connection = DB2.connect(dsn=self.database,
                                             uid=self._username,
                                             pwd=self._password)
                db2_cursor = db2_connection.cursor()
                db2_cursor.execute(query)
                table = db2_cursor.fetchall()
                return table
            except Exception, ex:
                display_error_message("Database query failed\n\n%s" % ex)
                return None
        finally:
            if db2_cursor:
                db2_cursor.close()
            if db2_connection:
                db2_connection.close()

    def __load_data(self):
        """Load timeline data from the database."""
        self.preferred_period = None
        self.categories = []
        self.events = []
        (self._username, self._password) = self.__get_login_info()
        self.__load_categories()
        self.__load_events()
        self.__load_preferred_period()
        self.disable_save_due_to_corrupt_data = False

    def __load_categories(self):
        """Load categoreis info from DB"""
        table = self.__execute_query("SELECT NAME "
                                     ",      RCOLOR "
                                     ",      GCOLOR "
                                     ",      BCOLOR "
                                     "FROM   DB2ADMIN.CATEGORIES ")
        if table:
            for row in table:
                self.__load_category(row)

    def __load_events(self):
        table = self.__execute_query("SELECT START "
                                     ",      END "
                                     ",      TEXT "
                                     ",      CATEGORY "
                                     ",      SELECTED "
                                     "FROM   DB2ADMIN.EVENTS ")
        if table:
            for row in table:
                if not self.__load_event(row):
                    data_corrupt = True

    def __load_preferred_period(self):
        """Expected format 'start_time;end_time'."""
        table = self.__execute_query("SELECT NAME  "
                                     ",      VALUE "
                                     "FROM   DB2ADMIN.PROPERTIES "
                                     "WHERE  NAME IN ('START', 'END') ")
        start_time = None
        end_time = None

        if table:
            for row in table:
                if row[0] == 'START':
                    start_time = parse_time(row[1])
                elif row[0] == 'END':
                    end_time = parse_time(row[1])

        if start_time and end_time:
            self.preferred_period = TimePeriod(start_time,end_time)

    def __load_category(self, category_specification):
        """
        Create a category from a datbase record (category_specification).

        The created category is added to the categories list.

        The database record contains the following fields:
            0   The category name
            1   The R color value
            2   The G color value
            3   The B color value
        """

        name = category_specification[0]
        color = (category_specification[1], category_specification[2],
                 category_specification[3])
        self.categories.append(Category(name, color))

    def __load_event(self, event_specification):
        """
        Create an event from a datbase record (event_specification).

        The created event is added to the events list.

        The database record contains the following fields:
            0   Start timestamp value as a string 'yyyy-mm-dd-hh.mm.ss.tttttt'
            1   End   timestamp value as a string 'yyyy-mm-dd-hh.mm.ss.tttttt'
            2   The event text
            3   The name of a category
        """

        try:
            start_time = parse_time(event_specification[0])
            end_time = parse_time(event_specification[1])
            event_text = event_specification[2]
            cat_name = event_specification[3]
            category = self.__get_category(cat_name)
            self.events.append(Event(start_time, end_time, event_text,
                                     category))
            return True
        except ParseException, ex:
            logerror("Unable to parse event from database record:\n\n%s",
                     exc_info=ex)
            return False

    def __get_category(self, name):
        for category in self.categories:
            if category.name == name:
                return category
        return None



def parse_time(time_string):
    """
    Return a DateTime or raise exception.

    Expected format 'year-month-day-hour.minute.second.millseconds'.
    """
    match = re.search(r"^(\d+)-(\d+)-(\d+)-(\d+).(\d+).(\d+).(\d+)$", time_string)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        hour = int(match.group(4))
        minute = int(match.group(5))
        second = int(match.group(6))
        try:
            return datetime(year, month, day, hour, minute, second)
        except ValueError:
            raise ParseException("Invalid time, time string = '%s'" % time_string)
    else:
        raise ParseException("Time not on correct format = '%s'" % time_string)


def time_string(time):
    """
    Return time formatted for writing to file.
    """
    return "%s-%s-%s %s.%s.%s.000" % (time.year, time.month, time.day,
                                      time.hour, time.minute, time.second)

