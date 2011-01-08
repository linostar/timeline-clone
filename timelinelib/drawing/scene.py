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


import wx

from timelinelib.drawing.utils import Metrics
from timelinelib.drawing.utils import get_default_font
from timelinelib.db.objects import TimePeriod


OUTER_PADDING = 5      # Space between event boxes (pixels)
INNER_PADDING = 3      # Space inside event box to text (pixels)
BASELINE_PADDING = 15  # Extra space to move events away from baseline (pixels)
PERIOD_THRESHOLD = 20  # Periods smaller than this are drawn as events (pixels)
DATA_INDICATOR_SIZE = 10


class TimelineScene(object):

    def __init__(self, size, db, view_properties, get_text_size_fn):
        self.size = size
        self.db = db
        self.view_properties = view_properties
        self._get_text_size = get_text_size_fn

        self.metrics = Metrics(self.size, self.db.get_time_type(), 
                               self.view_properties.displayed_period, 
                               self.view_properties.divider_position)
        
        self.width, self.height = self.size
        self.divider_y = self.metrics.half_height

        self.event_data = []
        self.major_strip = None
        self.minor_strip = None
        self.major_strip_data = []
        self.minor_strip_data = []

    def create(self):
        self._calc_event_positions(self.view_properties)
        self._calc_strips()

    def x_pos_for_time(self, time):
        return self.metrics.calc_x(time)

    def distance_between_times(self, time1, time2):
        time1_x = self.metrics.calc_exact_x(time1)
        time2_x = self.metrics.calc_exact_x(time2)
        distance = abs(time1_x - time2_x)
        return distance

    def width_of_period(self, time_period):
        return self.metrics.calc_width(time_period)

    def _calc_event_positions(self, view_properties):
        events_from_db = self.db.get_events(self.view_properties.displayed_period)
        visible_events = view_properties.filter_events(events_from_db)
        self._calc_rects(visible_events)
        
    def _calc_rects(self, events):
        self.event_data = []
        for event in events:
            rect = self._create_rectangle_for_event(event)
            self.event_data.append((event, rect))
        for (event, rect) in self.event_data:
            rect.Deflate(OUTER_PADDING, OUTER_PADDING)

    def _create_rectangle_for_event(self, event):
        rect = self._create_ideal_rect_for_event(event)
        self._ensure_rect_is_not_far_outisde_screen(rect)
        self._prevent_overlap(rect, self._get_y_move_direction(event))
        return rect
        
    def _get_y_move_direction(self, event):
        if self._display_as_period(event):
            return 1
        else:
            return -1

    def _create_ideal_rect_for_event(self, event):
        if self._display_as_period(event):
            return self._create_ideal_rect_for_period_event(event)
        else:
            return self._create_ideal_rect_for_non_period_event(event)

    def _display_as_period(self, event):
        event_width = self.metrics.calc_width(event.time_period)
        return event_width > PERIOD_THRESHOLD

    def _create_ideal_rect_for_period_event(self, event):
        tw, th = self._get_text_size(event.text)
        ew = self.metrics.calc_width(event.time_period)
        rw = ew + 2 * OUTER_PADDING
        rh = th + 2 * INNER_PADDING + 2 * OUTER_PADDING
        rx = (self.metrics.calc_x(event.time_period.start_time) -
              OUTER_PADDING)
        ry = self.metrics.half_height + BASELINE_PADDING
        rect = wx.Rect(rx, ry, rw, rh)
        return rect

    def _create_ideal_rect_for_non_period_event(self, event):
        tw, th = self._get_text_size(event.text)
        rw = tw + 2 * INNER_PADDING + 2 * OUTER_PADDING
        rh = th + 2 * INNER_PADDING + 2 * OUTER_PADDING
        if event.has_data():
            rw += DATA_INDICATOR_SIZE / 3
        rx = self.metrics.calc_x(event.mean_time()) - rw / 2
        ry = self.metrics.half_height - rh - BASELINE_PADDING
        rect = wx.Rect(rx, ry, rw, rh)
        return rect

    def _ensure_rect_is_not_far_outisde_screen(self, rect):
        # Drawing stuff on huge x-coordinates causes drawing to fail.
        # MARGIN must be big enough to hide outer padding, borders, and
        # selection markers.
        rx = rect.GetX()
        rw = rect.GetWidth()
        MARGIN = 50
        if rx < -MARGIN:
            distance_beyond_left_margin = -rx - MARGIN
            rx += distance_beyond_left_margin
            rw -= distance_beyond_left_margin
        right_edge_x = rx + rw
        if right_edge_x > self.metrics.width + MARGIN:
            rw -= right_edge_x - self.metrics.width - MARGIN
        rect.SetX(rx)
        rect.SetWidth(rw)

    def _prevent_overlap(self, rect, y_move_direction):
        while True:
            intersection_height = self._intersection_height(rect)
            rect.Y += y_move_direction * intersection_height
            if intersection_height == 0:
                break
            if self._rect_above_or_below_screen(rect):
                # Optimization: Don't prevent overlap if rect is pushed
                # outside screen
                break

    def _rect_above_or_below_screen(self, rect):
        return rect.Y > self.metrics.height or (rect.Y + rect.Height) < 0

    def _intersection_height(self, rect):
        for (event, r) in self.event_data:
            if rect.Intersects(r):
                r_copy = wx.Rect(*r) # Because `Intersect` modifies rect
                intersection = r_copy.Intersect(rect)
                return intersection.Height
        return 0

    def _calc_strips(self):
        """Fill the two arrays `minor_strip_data` and `major_strip_data`."""
        def fill(list, strip):
            """Fill the given list with the given strip."""
            current_start = strip.start(self.view_properties.displayed_period.start_time)
            while current_start < self.view_properties.displayed_period.end_time:
                next_start = strip.increment(current_start)
                list.append(TimePeriod(self.db.get_time_type(), current_start, next_start))
                current_start = next_start
        self.major_strip_data = [] # List of time_period
        self.minor_strip_data = [] # List of time_period
        self.major_strip, self.minor_strip = self.db.get_time_type().choose_strip(self.metrics)
        fill(self.major_strip_data, self.major_strip)
        fill(self.minor_strip_data, self.minor_strip)
