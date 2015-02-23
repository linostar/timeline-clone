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


import datetime
import unittest

from specs.utils import a_category_with
from specs.utils import gregorian_period
from specs.utils import human_time_to_gregorian
from timelinelib.data.db import MemoryDB
from timelinelib.data import Event
from timelinelib.drawing.scene import TimelineScene
from timelinelib.drawing.viewproperties import ViewProperties


class SceneSpec(unittest.TestCase):

    def test_has_no_hidden_events_when_all_events_belong_to_visible_categories(self):
        self.given_displayed_period("1 Jan 2010", "10 Jan 2010")
        self.given_visible_event_at("5 Jan 2010")
        self.when_scene_is_created()
        self.assertEqual(0, self.scene.get_hidden_event_count())

    def test_has_hidden_events_for_all_events_belonging_to_hidden_categories(self):
        self.given_displayed_period("1 Jan 2010", "10 Jan 2010")
        self.given_visible_event_at("5 Jan 2010")
        self.given_hidden_event_at("5 Jan 2010")
        self.when_scene_is_created()
        self.assertEqual(1, self.scene.get_hidden_event_count())

    def test_considers_events_outside_screen_hidden(self):
        self.given_displayed_period("1 Jan 2010", "10 Jan 2010")
        self.given_number_of_events_stackable_is(5)
        for i in range(6):
            self.given_visible_event_at("5 Jan 2010")
        self.when_scene_is_created()
        self.assertEqual(1, self.scene.get_hidden_event_count())

    def test_point_events_on_same_date_has_different_y_positions(self):
        self.given_displayed_period("1 Jan 2010", "10 Jan 2010")
        self.given_visible_event_at("5 Jan 2010")
        self.given_visible_event_at("5 Jan 2010")
        self.when_scene_is_created()
        self.assertTrue(self.scene.event_data[0][1].Y >
                        self.scene.event_data[1][1].Y)

    def test_point_events_on_different_dates_has_same_y_positions(self):
        self.given_displayed_period("1 Jan 2010", "10 Jan 2010")
        self.given_visible_event_at("2 Jan 2010")
        self.given_visible_event_at("9 Jan 2010")
        self.when_scene_is_created()
        self.assertEqual(self.scene.event_data[0][1].Y,
                         self.scene.event_data[1][1].Y)

    def test_period_events_with_same_period_has_different_y_positions(self):
        self.given_displayed_period("1 Jan 2010", "12 Jan 2010")
        self.given_visible_event_at("2 Jan 2010", "10 Jan 2010")
        self.given_visible_event_at("2 Jan 2010", "10 Jan 2010")
        self.when_scene_is_created()
        self.assertTrue(self.scene.event_data[0][1].Y <
                        self.scene.event_data[1][1].Y)

    def test_period_events_with_different_periods_has_same_y_positions(self):
        self.given_displayed_period("1 Jan 2010", "12 Jan 2010")
        self.given_visible_event_at("2 Jan 2010", "3 Jan 2010")
        self.given_visible_event_at("8 Jan 2010", "10 Jan 2010")
        self.when_scene_is_created()
        self.assertEqual(self.scene.event_data[0][1].Y,
                         self.scene.event_data[1][1].Y)

    def test_long_periods_are_not_drawn_very_far_outside_screen(self):
        self.given_displayed_period("1 Jan 50 12:00", "1 Jan 50 13:00")
        self.given_visible_event_at("1 Jan 0", "1 Jan 1000")
        self.when_scene_is_created()
        event_x = self.scene.event_data[0][1].X
        event_width = self.scene.event_data[0][1].Width
        event_right_x = event_x + event_width
        window_width = self.size[0]
        self.assertTrue(event_x > -self.MAX_OUTSIDE_SCREEN)
        self.assertTrue(event_x < 0)
        self.assertTrue(event_right_x < window_width + self.MAX_OUTSIDE_SCREEN)
        self.assertTrue(event_right_x > window_width)

    def test_scene_must_be_created_at_last_century(self):
        self.given_displayed_period("1 Jan 9890", "1 Jan 9990")
        try:
            self.when_scene_is_created()
            self.assertTrue(self.scene != None)
        except:
            self.assertTrue(False)

    def setUp(self):
        self.db = MemoryDB()
        self.view_properties = ViewProperties()
        self.given_number_of_events_stackable_is(5)
        self.MAX_OUTSIDE_SCREEN = 20

    def get_text_size_fn(self, text):
        return (len(text), self.event_height)

    def given_number_of_events_stackable_is(self, number):
        self.event_height = 10
        self.size = (1000, 2 * self.event_height * number)
        self.view_properties.divider_position = 0.5
        self.outer_padding = 0
        self.inner_padding = 0
        self.baseline_padding = 0

    def given_displayed_period(self, start, end):
        self.view_properties.displayed_period = gregorian_period(start, end)

    def given_visible_event_at(self, start_time, end_time=None):
        self.given_event_at(start_time, end_time, visible=True)

    def given_hidden_event_at(self, time):
        self.given_event_at(time, visible=False)

    def given_event_at(self, start_time, end_time=None, visible=True):
        category = self.get_unique_category()
        if end_time is None:
            end_time = start_time
        event = Event(self.db.get_time_type(), human_time_to_gregorian(start_time),
                      human_time_to_gregorian(end_time), "event-text", category)
        self.db.save_category(category)
        self.db.save_event(event)
        self.view_properties.set_category_visible(category, visible)

    def get_unique_category(self):
        number = 1
        while True:
            name = "category %d" % number
            if self.db.get_category_by_name(name) is None:
                return a_category_with(name=name)
            else:
                number += 1

    def when_scene_is_created(self):
        self.scene = TimelineScene(
            self.size, self.db, self.view_properties, self.get_text_size_fn,
            None)
        self.scene.set_outer_padding(self.outer_padding)
        self.scene.set_inner_padding(self.inner_padding)
        self.scene.set_baseline_padding(self.baseline_padding)
        self.scene.create()
