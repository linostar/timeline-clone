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
import time

from timelinelib.db.objects import TimePeriod
from timelinelib.time.pytime import PyTimeType
from timelinelib.drawing.viewproperties import ViewProperties


class PlayController(object):

    def __init__(self, play_frame, timeline, drawing_algorithm,
            config):
        self.play_frame = play_frame
        self.timeline = timeline
        self.drawing_algorithm = drawing_algorithm
        self.config = config

    def on_close_clicked(self):
        self.play_frame.close()

    def start_movie(self):
        period_length = self.play_frame.get_view_period_length()

        first_event_time = self.timeline.get_first_event().time_period.start_time
        start_time = first_event_time - period_length / 2
        end_time = first_event_time + period_length / 2
        self.start_period = TimePeriod(self.timeline.get_time_type(), start_time, end_time)

        second_period = self.start_period.move(1)

        last_event_time = self.timeline.get_last_event().time_period.end_time
        start_time = last_event_time - period_length / 2
        end_time = last_event_time + period_length / 2
        end_period = TimePeriod(self.timeline.get_time_type(), start_time, end_time)

        self.animations = []
        self.animations.append((2.5, second_period))
        self.animations.append((10.5, end_period))

        self.current_period = self.start_period

        self.last_time = time.time()

        self.current_animation = Animation(
            self.timeline,
            self.start_period, self.animations[0][0], self.animations[0][1])

        self.play_frame.start_timer(50)

    def tick(self):
        new_time = time.time()
        self.delta = new_time - self.last_time
        self.last_time = new_time
        print self.delta
        self.play_frame.redraw_drawing_area(self.draw_fn)

    def draw_fn(self, dc):
        view_properties = ViewProperties()
        view_properties.set_displayed_period(self.get_period())
        self.drawing_algorithm.draw(
            dc, self.timeline, view_properties, self.config)

    def get_period(self):
        self.current_animation.change_current_period(self.delta)

        if self.current_animation.is_done():
            (speed, period) = self.animations.pop(0)
            if len(self.animations) == 0:
                self.play_frame.stop_timer()
                return period
            else:
                self.current_animation = Animation(
                    self.timeline,
                    period, self.animations[0][0], self.animations[0][1])

        return self.current_animation.current_period


class Animation(object):

    def __init__(self, timeline, start_period, duration_in_seconds, end_period):
        self.timeline = timeline
        self.start_period = start_period
        self.duration_in_seconds = duration_in_seconds
        self.end_period = end_period
        self.current_period = start_period
        self.total_animation_delta = TimePeriod(self.timeline.get_time_type(),
                self.start_period.start_time, self.end_period.start_time).delta()
        self.total_animation_time = 0

    def is_done(self):
        return self.current_period.end_time >= self.end_period.end_time

    def change_current_period(self, delta):
        self.total_animation_time += delta

        delta_to_move = self.timeline.get_time_type().mult_timedelta(
            self.total_animation_delta,
            min(1, self.total_animation_time/self.duration_in_seconds))

        self.current_period = self.start_period.move_delta(delta_to_move)
