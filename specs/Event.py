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


from specs.utils import a_category_with
from specs.utils import an_event
from specs.utils import gregorian_period
from specs.utils import human_time_to_gregorian
from specs.utils import TestCase
from timelinelib.data import Event
from timelinelib.time.gregoriantime import GregorianTimeType
from timelinelib.time.numtime import NumTimeType


class describe_event(TestCase):

    def test_can_get_values(self):
        event = Event(time_type=GregorianTimeType(),
                      start_time=human_time_to_gregorian("11 Jul 2014"),
                      end_time=human_time_to_gregorian("12 Jul 2014"),
                      text="a day in my life")
        self.assertEqual(event.get_id(), None)
        self.assertEqual(event.get_time_period(),
                         gregorian_period("11 Jul 2014", "12 Jul 2014"))
        self.assertEqual(event.get_text(), "a day in my life")
        self.assertEqual(event.get_category(), None)
        self.assertEqual(event.get_time_type(), GregorianTimeType())
        self.assertEqual(event.get_fuzzy(), False)
        self.assertEqual(event.get_locked(), False)
        self.assertEqual(event.get_ends_today(), False)
        self.assertEqual(event.get_description(), None)
        self.assertEqual(event.get_icon(), None)
        self.assertEqual(event.get_hyperlink(), None)

    def test_can_set_values(self):
        self.assertEqual(
            self.an_event.set_id(15).get_id(),
            15)
        self.assertEqual(
            self.an_event.set_time_period(gregorian_period("1 Jan 2014", "1 Jan 2015")).get_time_period(),
            gregorian_period("1 Jan 2014", "1 Jan 2015"))
        self.assertEqual(
            self.an_event.set_text("cool").get_text(),
            "cool")
        self.assertEqual(
            self.an_event.set_category(self.a_category).get_category(),
            self.a_category)
        self.assertEqual(
            self.an_event.set_time_type(NumTimeType()).get_time_type(),
            NumTimeType())
        self.assertEqual(
            self.an_event.set_fuzzy(True).get_fuzzy(),
            True)
        self.assertEqual(
            self.an_event.set_locked(True).get_locked(),
            True)
        self.assertEqual(
            self.an_event.set_ends_today(True).get_ends_today(),
            True)
        self.assertEqual(
            self.an_event.set_description("cool").get_description(),
            "cool")
        self.assertEqual(
            self.an_event.set_icon(self.an_icon).get_icon(),
            self.an_icon)
        self.assertEqual(
            self.an_event.set_hyperlink("http://google.com").get_hyperlink(),
            "http://google.com")

    def setUp(self):
        self.an_event = an_event()
        self.a_category = a_category_with(name="work")
        self.an_icon = "really not an icon"
