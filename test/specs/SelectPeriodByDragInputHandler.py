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


import mock
import unittest

from timelinelib.calendar.gregorian import from_date
from timelinelib.dataimport.tutorial import TutorialTimelineCreator
from timelinelib.time.timeline import Time
from timelinelib.view.periodbase import SelectPeriodByDragInputHandler


class SelectperiodByDragInputHandler(unittest.TestCase):

    def test_no_exception_when_julian_day_lt_0(self):
        try:
            self.simulate_drag_where_julian_day_becomes_lt_zero()
            self.when_mouse_moved()
            self.assert_(True)
        except ValueError:
            self.assert_(False)

    def when_mouse_moved(self):
        self.handler.mouse_moved(10, 10)

    def simulate_drag_where_julian_day_becomes_lt_zero(self):
        controller = RaiseValueErrorController()
        controller.get_timeline.return_value = TutorialTimelineCreator().db
        controller.get_drawer.return_value = Snap()
        self.handler = SelectPeriodByDragInputHandler(controller, from_date(2013, 12, 31))

    def setUp(self):
        pass


class Snap(object):

    def snap(self, time):
        return from_date(2013, 12, 1).to_time()


class RaiseValueErrorController(mock.Mock):

    def get_time(self, x):
        raise ValueError()
