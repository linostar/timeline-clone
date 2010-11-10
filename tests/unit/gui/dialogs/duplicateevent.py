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


import datetime
import unittest

from mock import Mock

from timelinelib.gui.dialogs.duplicateevent import DuplicateEventController
from timelinelib.gui.dialogs.duplicateevent import DAY
from timelinelib.gui.dialogs.duplicateevent import WEEK
from timelinelib.gui.dialogs.duplicateevent import MONTH
from timelinelib.gui.dialogs.duplicateevent import YEAR
from timelinelib.gui.dialogs.duplicateevent import FORWARD
from timelinelib.gui.dialogs.duplicateevent import BACKWARD
from timelinelib.gui.dialogs.duplicateevent import BOTH
from timelinelib.gui.dialogs.duplicateevent import repeat_period
from timelinelib.time import PyTimeType
from timelinelib.db.interface import TimelineIOError
from timelinelib.db.objects import Event
from timelinelib.db.objects import TimePeriod


class TestDuplicateEventController(unittest.TestCase):

    def setUp(self):
        self.db = Mock()
        self.view = Mock()
        self.db.get_time_type.return_value = PyTimeType()
        start_time = datetime.datetime(2010, 1, 1, 12, 0, 0)
        end_time = datetime.datetime(2010, 1, 1, 13, 0, 0)
        self.event = Event(self.db, start_time, end_time, "foo", category=None)

    def testInit(self):
        """Assert the initial settings in the view dialog."""
        controller = DuplicateEventController(self.view, self.db, self.event)
        controller.initialize()
        self.view.set_count.assert_called_with(1)
        self.view.set_period_type.assert_called_with(DAY)
        self.view.set_frequency.assert_called_with(1)
        self.view.set_direction.assert_called_with(FORWARD)

    def testCreateDuplicate(self):
        controller = DuplicateEventController(self.view, self.db, self.event)
        # Simulate entering this in gui
        self.view.get_count.return_value = 1
        self.view.get_period_type.return_value = DAY
        self.view.get_frequency.return_value = 1
        self.view.get_direction.return_value = FORWARD
        controller.create_duplicates_and_save()
        # Assert that controller fetched data from view
        self.assertTrue(self.view.get_count.called)
        self.assertTrue(self.view.get_period_type.called)
        self.assertTrue(self.view.get_direction.called)
        self.assertTrue(self.view.get_frequency.called)
        # Assert that the saved event is a clone
        event = self.db.save_event.call_args[0][0]
        self.assertTrue(event != self.event)

    def testDbError(self):
        """Assert correct handling of TimelineIOError."""
        controller = DuplicateEventController(self.view, self.db, self.event)
        # Simulate TimelineIOError when we try to save a valid event
        self.db.save_event.side_effect = TimelineIOError
        # Simulate return values from view
        self.view.get_count.return_value = 1
        self.view.get_period_type.return_value = YEAR
        self.view.get_frequency.return_value = 1
        self.view.get_direction.return_value = FORWARD
        controller.create_duplicates_and_save()
        # Assert that controller let view handle error
        self.assertTrue(self.view.handle_db_error.called)
        # Assert that controller did not close view
        self.assertFalse(self.view.close.called)


class TestRepeatPeriod(unittest.TestCase):
    """
    testRepeatOfDayN:   period_type = DAY
    testRepeatOfWeekN:  period_type = WEEK
    testRepeatOfMonthN: period_type = MONTH
    testRepeatOfYearN:  period_type = YEAR

    N    count  frequency  direction
    --   -----  -----      ---------
    1      1      1        FORWARD
    2      2      1        FORWARD
    3      2      2        FORWARD
    4      1      1        BACKWARD
    5      2      1        BACKWARD
    6      2      2        BACKWARD
    7      1      1        BOTH
    8      2      1        BOTH
    9      2      2        BOTH

    """

    def setUp(self):
        start_time = datetime.datetime(2010, 1, 1, 12, 0, 0)
        end_time = datetime.datetime(2010, 1, 1, 13, 0, 0)
        self.period = TimePeriod(PyTimeType(), start_time, end_time)

    def testRepeatOfDay1(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, DAY, 1, 1,
                                                      FORWARD)
        self.assertEquals(len(periods), 1)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2010,1,2,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2010,1,2,13,0,0))

    def testRepeatOfDay2(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, DAY, 1, 2,
                                                      FORWARD)
        self.assertEquals(len(periods), 2)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2010,1,2,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2010,1,2,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2010,1,3,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2010,1,3,13,0,0))

    def testRepeatOfDay3(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, DAY, 2, 2,
                                                      FORWARD)
        self.assertEquals(len(periods), 2)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2010,1,3,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2010,1,3,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2010,1,5,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2010,1,5,13,0,0))

    def testRepeatOfDay4(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, DAY, 1, 1,
                                                      BACKWARD)
        self.assertEquals(len(periods), 1)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2009,12,31,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2009,12,31,13,0,0))

    def testRepeatOfDay5(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, DAY, 1, 2,
                                                      BACKWARD)
        self.assertEquals(len(periods), 2)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2009,12,31,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2009,12,31,13,0,0))
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2009,12,30,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2009,12,30,13,0,0))

    def testRepeatOfDay6(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, DAY, 2, 2,
                                                      BACKWARD)
        self.assertEquals(len(periods), 2)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2009,12,30,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2009,12,30,13,0,0))
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2009,12,28,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2009,12,28,13,0,0))

    def testRepeatOfDay7(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, DAY, 1, 1,
                                                      BOTH)
        self.assertEquals(len(periods), 2)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2009,12,31,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2009,12,31,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2010,1,2,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2010,1,2,13,0,0))

    def testRepeatOfDay8(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, DAY, 1, 2,
                                                      BOTH)
        self.assertEquals(len(periods), 4)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2009,12,30,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2009,12,30,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2009,12,31,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2009,12,31,13,0,0))
        self.assertEquals(periods[2].start_time,
                          datetime.datetime(2010,1,2,12,0,0))
        self.assertEquals(periods[2].end_time,
                          datetime.datetime(2010,1,2,13,0,0))
        self.assertEquals(periods[3].start_time,
                          datetime.datetime(2010,1,3,12,0,0))
        self.assertEquals(periods[3].end_time,
                          datetime.datetime(2010,1,3,13,0,0))

    def testRepeatOfDay9(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, DAY, 2, 2,
                                                      BOTH)
        self.assertEquals(len(periods), 4)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2009,12,28,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2009,12,28,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2009,12,30,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2009,12,30,13,0,0))
        self.assertEquals(periods[2].start_time,
                          datetime.datetime(2010,1,3,12,0,0))
        self.assertEquals(periods[2].end_time,
                          datetime.datetime(2010,1,3,13,0,0))
        self.assertEquals(periods[3].start_time,
                          datetime.datetime(2010,1,5,12,0,0))
        self.assertEquals(periods[3].end_time,
                          datetime.datetime(2010,1,5,13,0,0))

    def testRepeatOfWeek1(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, WEEK, 1, 1,
                                                      FORWARD)
        self.assertEquals(len(periods), 1)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2010,1,8,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2010,1,8,13,0,0))

    def testRepeatOfWeek2(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, WEEK, 1, 2,
                                                      FORWARD)
        self.assertEquals(len(periods), 2)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2010,1,8,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2010,1,8,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2010,1,15,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2010,1,15,13,0,0))

    def testRepeatOfWeek3(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, WEEK, 2, 2,
                                                      FORWARD)
        self.assertEquals(len(periods), 2)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2010,1,15,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2010,1,15,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2010,1,29,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2010,1,29,13,0,0))

    def testRepeatOfWeek4(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, WEEK, 1, 1,
                                                      BACKWARD)
        self.assertEquals(len(periods), 1)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2009,12,25,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2009,12,25,13,0,0))

    def testRepeatOfWeek5(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, WEEK, 1, 2,
                                                      BACKWARD)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(len(periods), 2)
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2009,12,25,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2009,12,25,13,0,0))
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2009,12,18,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2009,12,18,13,0,0))

    def testRepeatOfWeek6(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, WEEK, 2, 2,
                                                      BACKWARD)
        self.assertEquals(len(periods), 2)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2009,12,18,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2009,12,18,13,0,0))
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2009,12,4,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2009,12,4,13,0,0))

    def testRepeatOfWeek7(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, WEEK, 1, 1,
                                                      BOTH)
        self.assertEquals(len(periods), 2)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2009,12,25,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2009,12,25,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2010,1,8,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2010,1,8,13,0,0))

    def testRepeatOfWeek8(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, WEEK, 1, 2,
                                                      BOTH)
        self.assertEquals(len(periods), 4)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2009,12,18,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2009,12,18,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2009,12,25,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2009,12,25,13,0,0))
        self.assertEquals(periods[2].start_time,
                          datetime.datetime(2010,1,8,12,0,0))
        self.assertEquals(periods[2].end_time,
                          datetime.datetime(2010,1,8,13,0,0))
        self.assertEquals(periods[3].start_time,
                          datetime.datetime(2010,1,15,12,0,0))
        self.assertEquals(periods[3].end_time,
                          datetime.datetime(2010,1,15,13,0,0))

    def testRepeatOfWeek9(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, WEEK, 2, 2,
                                                      BOTH)
        self.assertEquals(len(periods), 4)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2009,12,4,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2009,12,4,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2009,12,18,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2009,12,18,13,0,0))
        self.assertEquals(periods[2].start_time,
                          datetime.datetime(2010,1,15,12,0,0))
        self.assertEquals(periods[2].end_time,
                          datetime.datetime(2010,1,15,13,0,0))
        self.assertEquals(periods[3].start_time,
                          datetime.datetime(2010,1,29,12,0,0))
        self.assertEquals(periods[3].end_time,
                          datetime.datetime(2010,1,29,13,0,0))

    def testRepeatOfMonth1(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, MONTH, 1, 1,
                                                      FORWARD)
        self.assertEquals(len(periods), 1)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2010,2,1,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2010,2,1,13,0,0))

    def testRepeatOfMonth2(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, MONTH, 1, 2,
                                                      FORWARD)
        self.assertEquals(len(periods), 2)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2010,2,1,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2010,2,1,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2010,3,1,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2010,3,1,13,0,0))

    def testRepeatOfMonth3(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, MONTH, 2, 2,
                                                      FORWARD)
        self.assertEquals(len(periods), 2)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2010,3,1,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2010,3,1,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2010,5,1,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2010,5,1,13,0,0))

    def testRepeatOfMonth4(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, MONTH, 1, 1,
                                                      BACKWARD)
        self.assertEquals(len(periods), 1)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2009,12,1,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2009,12,1,13,0,0))

    def testRepeatOfMonth5(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, MONTH, 1, 2,
                                                      BACKWARD)
        self.assertEquals(len(periods), 2)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2009,12,1,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2009,12,1,13,0,0))
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2009,11,1,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2009,11,1,13,0,0))

    def testRepeatOfMonth6(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, MONTH, 2, 2,
                                                      BACKWARD)
        self.assertEquals(len(periods), 2)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2009,11,1,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2009,11,1,13,0,0))
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2009,9,1,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2009,9,1,13,0,0))

    def testRepeatOfMonth7(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, MONTH, 1, 1,
                                                      BOTH)
        self.assertEquals(len(periods), 2)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2009,12,1,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2009,12,1,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2010,2,1,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2010,2,1,13,0,0))

    def testRepeatOfMonth8(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, MONTH, 1, 2,
                                                      BOTH)
        self.assertEquals(len(periods), 4)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2009,11,1,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2009,11,1,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2009,12,1,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2009,12,1,13,0,0))
        self.assertEquals(periods[2].start_time,
                          datetime.datetime(2010,2,1,12,0,0))
        self.assertEquals(periods[2].end_time,
                          datetime.datetime(2010,2,1,13,0,0))
        self.assertEquals(periods[3].start_time,
                          datetime.datetime(2010,3,1,12,0,0))
        self.assertEquals(periods[3].end_time,
                          datetime.datetime(2010,3,1,13,0,0))

    def testRepeatOfMonth9(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, MONTH, 2, 2,
                                                      BOTH)
        self.assertEquals(len(periods), 4)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2009,9,1,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2009,9,1,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2009,11,1,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2009,11,1,13,0,0))
        self.assertEquals(periods[2].start_time,
                          datetime.datetime(2010,3,1,12,0,0))
        self.assertEquals(periods[2].end_time,
                          datetime.datetime(2010,3,1,13,0,0))
        self.assertEquals(periods[3].start_time,
                          datetime.datetime(2010,5,1,12,0,0))
        self.assertEquals(periods[3].end_time,
                          datetime.datetime(2010,5,1,13,0,0))

    def testRepeatOfMonthLargeTimeSpan(self):
        """More than 12 months time span."""
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, MONTH, 15, 1,
                                                      BOTH)
        self.assertEquals(len(periods), 2)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2008,10,1,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2008,10,1,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2011,4,1,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2011,4,1,13,0,0))

    def testRepeatOfYear1(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, YEAR, 1, 1,
                                                      FORWARD)
        self.assertEquals(len(periods), 1)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2011,1,1,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2011,1,1,13,0,0))

    def testRepeatOfYear2(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, YEAR, 1, 2,
                                                      FORWARD)
        self.assertEquals(len(periods), 2)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2011,1,1,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2011,1,1,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2012,1,1,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2012,1,1,13,0,0))

    def testRepeatOfYear3(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, YEAR, 2, 2,
                                                      FORWARD)
        self.assertEquals(len(periods), 2)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2012,1,1,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2012,1,1,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2014,1,1,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2014,1,1,13,0,0))

    def testRepeatOfYear4(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, YEAR, 1, 1,
                                                      BACKWARD)
        self.assertEquals(len(periods), 1)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2009,1,1,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2009,1,1,13,0,0))

    def testRepeatOfYear5(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, YEAR, 1, 2,
                                                      BACKWARD)
        self.assertEquals(len(periods), 2)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2009,1,1,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2009,1,1,13,0,0))
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2008,1,1,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2008,1,1,13,0,0))

    def testRepeatOfYear6(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, YEAR, 2, 2,
                                                      BACKWARD)
        self.assertEquals(len(periods), 2)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2008,1,1,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2008,1,1,13,0,0))
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2006,1,1,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2006,1,1,13,0,0))

    def testRepeatOfYear7(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, YEAR, 1, 1,
                                                      BOTH)
        self.assertEquals(len(periods), 2)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2009,1,1,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2009,1,1,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2011,1,1,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2011,1,1,13,0,0))

    def testRepeatOfYear8(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, YEAR, 1, 2,
                                                      BOTH)
        self.assertEquals(len(periods), 4)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2008,1,1,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2008,1,1,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2009,1,1,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2009,1,1,13,0,0))
        self.assertEquals(periods[2].start_time,
                          datetime.datetime(2011,1,1,12,0,0))
        self.assertEquals(periods[2].end_time,
                          datetime.datetime(2011,1,1,13,0,0))
        self.assertEquals(periods[3].start_time,
                          datetime.datetime(2012,1,1,12,0,0))
        self.assertEquals(periods[3].end_time,
                          datetime.datetime(2012,1,1,13,0,0))

    def testRepeatOfYear9(self):
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      self.period, YEAR, 2, 2,
                                                      BOTH)
        self.assertEquals(len(periods), 4)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2006,1,1,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2006,1,1,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2008,1,1,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2008,1,1,13,0,0))
        self.assertEquals(periods[2].start_time,
                          datetime.datetime(2012,1,1,12,0,0))
        self.assertEquals(periods[2].end_time,
                          datetime.datetime(2012,1,1,13,0,0))
        self.assertEquals(periods[3].start_time,
                          datetime.datetime(2014,1,1,12,0,0))
        self.assertEquals(periods[3].end_time,
                          datetime.datetime(2014,1,1,13,0,0))

    def testRepeatOfFeb29_1(self):
        """Feb29 should only appear in leap years."""
        start_time = datetime.datetime(2004, 2, 29, 12, 0, 0)
        end_time = datetime.datetime(2004, 2, 29, 13, 0, 0)
        period = TimePeriod(PyTimeType(), start_time, end_time)
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      period, YEAR, 1, 4,
                                                      FORWARD)
        self.assertEquals(len(periods), 1)
        self.assertEquals(nbr_of_missing_dates, 3)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2008,2,29,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2008,2,29,13,0,0))

    def testRepeatOfFeb29_2(self):
        """Feb29 should only appear in leap years."""
        start_time = datetime.datetime(2004, 2, 29, 12, 0, 0)
        end_time = datetime.datetime(2004, 2, 29, 13, 0, 0)
        period = TimePeriod(PyTimeType(), start_time, end_time)
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      period, YEAR, 1, 4,
                                                      BOTH)
        self.assertEquals(len(periods), 2)
        self.assertEquals(nbr_of_missing_dates, 6)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2000,2,29,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2000,2,29,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2008,2,29,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2008,2,29,13,0,0))

    def testRepeatOfJan31_1(self):
        """Jan31 should only appears in 31-day months."""
        start_time = datetime.datetime(2010, 1, 31, 12, 0, 0)
        end_time = datetime.datetime(2010, 1, 31, 13, 0, 0)
        period = TimePeriod(PyTimeType(), start_time, end_time)
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      period, MONTH, 1, 12,
                                                      FORWARD)
        self.assertEquals(len(periods), 7)
        self.assertEquals(nbr_of_missing_dates, 5)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2010,3,31,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2010,3,31,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2010,5,31,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2010,5,31,13,0,0))
        self.assertEquals(periods[2].start_time,
                          datetime.datetime(2010,7,31,12,0,0))
        self.assertEquals(periods[2].end_time,
                          datetime.datetime(2010,7,31,13,0,0))
        self.assertEquals(periods[3].start_time,
                          datetime.datetime(2010,8,31,12,0,0))
        self.assertEquals(periods[3].end_time,
                          datetime.datetime(2010,8,31,13,0,0))
        self.assertEquals(periods[4].start_time,
                          datetime.datetime(2010,10,31,12,0,0))
        self.assertEquals(periods[4].end_time,
                          datetime.datetime(2010,10,31,13,0,0))
        self.assertEquals(periods[5].start_time,
                          datetime.datetime(2010,12,31,12,0,0))
        self.assertEquals(periods[5].end_time,
                          datetime.datetime(2010,12,31,13,0,0))
        self.assertEquals(periods[6].start_time,
                          datetime.datetime(2011,1,31,12,0,0))
        self.assertEquals(periods[6].end_time,
                          datetime.datetime(2011,1,31,13,0,0))

    def testRepeatOfMonthsBackwardOverYearBorder(self):
        """Backwards over year border."""
        start_time = datetime.datetime(2010, 3, 1, 12, 0, 0)
        end_time = datetime.datetime(2010, 3, 1, 13, 0, 0)
        period = TimePeriod(PyTimeType(), start_time, end_time)
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      period, MONTH, 1, 15,
                                                      BACKWARD)
        self.assertEquals(len(periods), 15)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2008,12,1,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2008,12,1,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2009,1,1,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2009,1,1,13,0,0))
        self.assertEquals(periods[2].start_time,
                          datetime.datetime(2009,2,1,12,0,0))
        self.assertEquals(periods[2].end_time,
                          datetime.datetime(2009,2,1,13,0,0))
        self.assertEquals(periods[3].start_time,
                          datetime.datetime(2009,3,1,12,0,0))
        self.assertEquals(periods[3].end_time,
                          datetime.datetime(2009,3,1,13,0,0))
        self.assertEquals(periods[4].start_time,
                          datetime.datetime(2009,4,1,12,0,0))
        self.assertEquals(periods[4].end_time,
                          datetime.datetime(2009,4,1,13,0,0))
        self.assertEquals(periods[5].start_time,
                          datetime.datetime(2009,5,1,12,0,0))
        self.assertEquals(periods[5].end_time,
                          datetime.datetime(2009,5,1,13,0,0))
        self.assertEquals(periods[6].start_time,
                          datetime.datetime(2009,6,1,12,0,0))
        self.assertEquals(periods[6].end_time,
                          datetime.datetime(2009,6,1,13,0,0))
        self.assertEquals(periods[7].start_time,
                          datetime.datetime(2009,7,1,12,0,0))
        self.assertEquals(periods[7].end_time,
                          datetime.datetime(2009,7,1,13,0,0))
        self.assertEquals(periods[8].start_time,
                          datetime.datetime(2009,8,1,12,0,0))
        self.assertEquals(periods[8].end_time,
                          datetime.datetime(2009,8,1,13,0,0))
        self.assertEquals(periods[9].start_time,
                          datetime.datetime(2009,9,1,12,0,0))
        self.assertEquals(periods[9].end_time,
                          datetime.datetime(2009,9,1,13,0,0))
        self.assertEquals(periods[10].start_time,
                          datetime.datetime(2009,10,1,12,0,0))
        self.assertEquals(periods[10].end_time,
                          datetime.datetime(2009,10,1,13,0,0))
        self.assertEquals(periods[11].start_time,
                          datetime.datetime(2009,11,1,12,0,0))
        self.assertEquals(periods[11].end_time,
                          datetime.datetime(2009,11,1,13,0,0))
        self.assertEquals(periods[12].start_time,
                          datetime.datetime(2009,12,1,12,0,0))
        self.assertEquals(periods[12].end_time,
                          datetime.datetime(2009,12,1,13,0,0))
        self.assertEquals(periods[13].start_time,
                          datetime.datetime(2010,1,1,12,0,0))
        self.assertEquals(periods[13].end_time,
                          datetime.datetime(2010,1,1,13,0,0))
        self.assertEquals(periods[14].start_time,
                          datetime.datetime(2010,2,1,12,0,0))
        self.assertEquals(periods[14].end_time,
                          datetime.datetime(2010,2,1,13,0,0))

    def testRepeatOfMonthsForwardOverYearBorder(self):
        """Backwards over year border."""
        start_time = datetime.datetime(2010, 11, 1, 12, 0, 0)
        end_time = datetime.datetime(2010, 11, 1, 13, 0, 0)
        period = TimePeriod(PyTimeType(), start_time, end_time)
        periods, nbr_of_missing_dates = repeat_period(PyTimeType(),
                                                      period, MONTH, 1, 15,
                                                      FORWARD)
        self.assertEquals(len(periods), 15)
        self.assertEquals(nbr_of_missing_dates, 0)
        self.assertEquals(periods[0].start_time,
                          datetime.datetime(2010,12,1,12,0,0))
        self.assertEquals(periods[0].end_time,
                          datetime.datetime(2010,12,1,13,0,0))
        self.assertEquals(periods[1].start_time,
                          datetime.datetime(2011,1,1,12,0,0))
        self.assertEquals(periods[1].end_time,
                          datetime.datetime(2011,1,1,13,0,0))
        self.assertEquals(periods[2].start_time,
                          datetime.datetime(2011,2,1,12,0,0))
        self.assertEquals(periods[2].end_time,
                          datetime.datetime(2011,2,1,13,0,0))
        self.assertEquals(periods[3].start_time,
                          datetime.datetime(2011,3,1,12,0,0))
        self.assertEquals(periods[3].end_time,
                          datetime.datetime(2011,3,1,13,0,0))
        self.assertEquals(periods[4].start_time,
                          datetime.datetime(2011,4,1,12,0,0))
        self.assertEquals(periods[4].end_time,
                          datetime.datetime(2011,4,1,13,0,0))
        self.assertEquals(periods[5].start_time,
                          datetime.datetime(2011,5,1,12,0,0))
        self.assertEquals(periods[5].end_time,
                          datetime.datetime(2011,5,1,13,0,0))
        self.assertEquals(periods[6].start_time,
                          datetime.datetime(2011,6,1,12,0,0))
        self.assertEquals(periods[6].end_time,
                          datetime.datetime(2011,6,1,13,0,0))
        self.assertEquals(periods[7].start_time,
                          datetime.datetime(2011,7,1,12,0,0))
        self.assertEquals(periods[7].end_time,
                          datetime.datetime(2011,7,1,13,0,0))
        self.assertEquals(periods[8].start_time,
                          datetime.datetime(2011,8,1,12,0,0))
        self.assertEquals(periods[8].end_time,
                          datetime.datetime(2011,8,1,13,0,0))
        self.assertEquals(periods[9].start_time,
                          datetime.datetime(2011,9,1,12,0,0))
        self.assertEquals(periods[9].end_time,
                          datetime.datetime(2011,9,1,13,0,0))
        self.assertEquals(periods[10].start_time,
                          datetime.datetime(2011,10,1,12,0,0))
        self.assertEquals(periods[10].end_time,
                          datetime.datetime(2011,10,1,13,0,0))
        self.assertEquals(periods[11].start_time,
                          datetime.datetime(2011,11,1,12,0,0))
        self.assertEquals(periods[11].end_time,
                          datetime.datetime(2011,11,1,13,0,0))
        self.assertEquals(periods[12].start_time,
                          datetime.datetime(2011,12,1,12,0,0))
        self.assertEquals(periods[12].end_time,
                          datetime.datetime(2011,12,1,13,0,0))
        self.assertEquals(periods[13].start_time,
                          datetime.datetime(2012,1,1,12,0,0))
        self.assertEquals(periods[13].end_time,
                          datetime.datetime(2012,1,1,13,0,0))
        self.assertEquals(periods[14].start_time,
                          datetime.datetime(2012,2,1,12,0,0))
        self.assertEquals(periods[14].end_time,
                          datetime.datetime(2012,2,1,13,0,0))
