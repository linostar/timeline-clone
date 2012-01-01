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
        def draw_fn(dc):
            view_properties = ViewProperties()
            period_length = self.play_frame.get_view_period_length()
            first_event_time = self.timeline.get_first_event().time_period.start_time
            start_time = first_event_time - period_length / 2
            end_time = first_event_time + period_length / 2
            start_period = TimePeriod(self.timeline.get_time_type(), start_time, end_time)
            view_properties.set_displayed_period(start_period)
            self.drawing_algorithm.draw(dc, self.timeline,
                    view_properties, self.config)
        self.play_frame.redraw_drawing_area(draw_fn)
