# Copyright (C) 2009  Rickard Lindberg, Roger Lindberg
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
Implements the default algorithm for drawing a timeline.

The drawing interface is implemented in the `DefaultDrawingAlgorithm` class in
the `draw` method.
"""


import logging
import calendar
from datetime import timedelta
from datetime import datetime
from gui import sort_categories

import wx

import drawing
from drawing import DrawingAlgorithm
from drawing import Metrics
from data import TimePeriod


OUTER_PADDING = 5      # Space between event boxes (pixels)
INNER_PADDING = 3      # Space inside event box to text (pixels)
BASELINE_PADDING = 15  # Extra space to move events away from baseline (pixels)
PERIOD_THRESHOLD = 20  # Periods smaller than this are drawn as events (pixels)


class Strip(object):
    """
    An interface for strips.

    The different strips are implemented in subclasses below.

    The timeline is divided in major and minor strips. The minor strip might
    for example be days, and the major strip months. Major strips are divided
    with a solid line and minor strips with dotted lines. Typically maximum
    three major strips should be shown and the rest will be minor strips.
    """

    def label(self, time, major=False):
        """
        Return the label for this strip at the given time when used as major or
        minor strip.
        """

    def start(self, time):
        """
        Return the start time for this strip and the given time.

        For example, if the time is 2008-08-31 and the strip is month, the
        start would be 2008-08-01.
        """

    def increment(self, time):
        """
        Increment the given time so that it points to the start of the next
        strip.
        """


class StripDecade(Strip):

    def label(self, time, major=False):
        if major:
            # TODO: This only works for English. Possible to localize?
            return str(self._decade_start_year(time.year)) + "s"
        return ""

    def start(self, time):
        return datetime(self._decade_start_year(time.year), 1, 1)

    def increment(self, time):
        return time.replace(year=time.year+10)

    def _decade_start_year(self, year):
        return (int(year) / 10) * 10


class StripYear(Strip):

    def label(self, time, major=False):
        return str(time.year)

    def start(self, time):
        return datetime(time.year, 1, 1)

    def increment(self, time):
        return time.replace(year=time.year+1)


class StripMonth(Strip):

    def label(self, time, major=False):
        if major:
            return "%s %s" % (calendar.month_abbr[time.month], time.year)
        return calendar.month_abbr[time.month]

    def start(self, time):
        return datetime(time.year, time.month, 1)

    def increment(self, time):
        return time + timedelta(calendar.monthrange(time.year, time.month)[1])


class StripWeek(Strip):

    def label(self, time, major=False):
        if major:
            # Example: Week 23 (1-7 Jan 2009)
            first_weekday = self.start(time)
            next_first_weekday = self.increment(first_weekday)
            last_weekday = next_first_weekday - timedelta(days=1)
            range_string = self._time_range_string(first_weekday, last_weekday)
            return (_("Week") + " %s (%s)") % (time.isocalendar()[1], range_string)
        # This strip should never be used as minor
        return ""

    def start(self, time):
        stripped_date = datetime(time.year, time.month, time.day)
        return stripped_date - timedelta(stripped_date.weekday())

    def increment(self, time):
        return time + timedelta(7)

    def _time_range_string(self, time1, time2):
        """
        Examples:

        * 1-7 Jun 2009
        * 28 Jun-3 Jul 2009
        * 28 Jun 08-3 Jul 2009
        """
        if time1.year == time2.year:
            if time1.month == time2.month:
                return "%s-%s %s %s" % (time1.day, time2.day,
                                        calendar.month_abbr[time1.month],
                                        time1.year)
            return "%s %s-%s %s %s" % (time1.day,
                                       calendar.month_abbr[time1.month],
                                       time2.day,
                                       calendar.month_abbr[time2.month],
                                       time1.year)
        return "%s %s %s-%s %s %s" % (time1.day,
                                      calendar.month_abbr[time1.month],
                                      time1.year,
                                      time2.day,
                                      calendar.month_abbr[time2.month],
                                      time2.year)


class StripDay(Strip):

    def label(self, time, major=False):
        if major:
            return "%s %s %s" % (time.day, calendar.month_abbr[time.month],
                                 time.year)
        return str(time.day)

    def start(self, time):
        return datetime(time.year, time.month, time.day)

    def increment(self, time):
        return time + timedelta(1)


class StripWeekday(Strip):

    def label(self, time, major=False):
        if major:
            return "%s %s %s %s" % (calendar.day_abbr[time.weekday()],
                                    time.day, calendar.month_abbr[time.month],
                                    time.year)
        return str(calendar.day_abbr[time.weekday()])

    def start(self, time):
        return datetime(time.year, time.month, time.day)

    def increment(self, time):
        return time + timedelta(1)


class StripHour(Strip):

    def label(self, time, major=False):
        if major:
            return "%s %s %s %s" % (time.day, calendar.month_abbr[time.month],
                                    time.year, time.hour)
        return str(time.hour)

    def start(self, time):
        return datetime(time.year, time.month, time.day, time.hour)

    def increment(self, time):
        return time + timedelta(hours=1)


class DefaultDrawingAlgorithm(DrawingAlgorithm):

    def __init__(self):
        # Fonts and pens we use when drawing
        self.header_font = drawing.get_default_font(12, True)
        self.small_text_font = drawing.get_default_font(8)
        self.red_solid_pen = wx.Pen(wx.Color(255,0, 0), 1, wx.SOLID)
        self.black_solid_pen = wx.Pen(wx.Color(0, 0, 0), 1, wx.SOLID)
        self.darkred_solid_pen = wx.Pen(wx.Color(200, 0, 0), 1, wx.SOLID)
        self.black_dashed_pen = wx.Pen(wx.Color(200, 200, 200), 1, wx.USER_DASH)
        self.black_dashed_pen.SetDashes([2, 2])
        self.black_dashed_pen.SetCap(wx.CAP_BUTT)
        self.grey_solid_pen = wx.Pen(wx.Color(200, 200, 200), 1, wx.SOLID)
        self.white_solid_brush = wx.Brush(wx.Color(255, 255, 255), wx.SOLID)
        self.black_solid_brush = wx.Brush(wx.Color(0, 0, 0), wx.SOLID)
        self.lightgrey_solid_brush = wx.Brush(wx.Color(230, 230, 230), wx.SOLID)

    def draw(self, dc, time_period, events, period_selection=None,
             legend=False):
        """
        Implement the drawing interface.

        The drawing is done in a number of steps: First positions of all events
        and strips are calculated and then they are drawn. Positions can also
        be used later to answer questions like what event is at position (x, y).
        """
        # Store data so we can use it in other functions
        self.dc = dc
        self.time_period = time_period
        self.metrics = Metrics(dc, time_period)
        # Data
        self.event_data = []       # List of tuples (event, rect)
        self.major_strip_data = [] # List of time_period
        self.minor_strip_data = [] # List of time_period
        # Calculate stuff later used for drawing
        self._calc_rects(events)
        self._calc_strips()
        # Perform the actual drawing
        if period_selection:
            self._draw_period_selection(period_selection)
        self._draw_bg()
        if legend:
            self._draw_legend(self._extract_categories(events))
        self._draw_events()
        # Make sure to delete this one
        del self.dc

    def snap_selection(self, period_selection):
        major_strip, minor_strip = self._choose_strip()
        start, end = period_selection
        new_start = minor_strip.start(start)
        new_end = minor_strip.increment(minor_strip.start(end))
        return (new_start, new_end)

    def event_at(self, x, y):
        for (event, rect) in self.event_data:
            if rect.Contains(wx.Point(x, y)):
                return event
        return None

    def _calc_rects(self, events):
        """
        Calculate rectangles for all events.

        The rectangles define the areas in which the events can draw
        themselves.

        During the calculations, the outer padding is part of the rectangles to
        make the calculations easier. Outer padding is removed in the end.
        """
        self.dc.SetFont(self.small_text_font)
        for event in events:
            tw, th = self.dc.GetTextExtent(event.text)
            ew = self.metrics.calc_width(event.time_period)
            if ew > PERIOD_THRESHOLD:
                # Treat as period (periods are placed below the baseline, with
                # indicates length of period)
                rw = ew + 2 * OUTER_PADDING
                rh = th + 2 * INNER_PADDING + 2 * OUTER_PADDING
                rx = (self.metrics.calc_x(event.time_period.start_time) -
                      OUTER_PADDING)
                ry = self.metrics.half_height + BASELINE_PADDING
                movedir = 1
            else:
                # Treat as event (events are placed above the baseline, with
                # indicates length of text)
                rw = tw + 2 * INNER_PADDING + 2 * OUTER_PADDING
                rh = th + 2 * INNER_PADDING + 2 * OUTER_PADDING
                rx = self.metrics.calc_x(event.mean_time()) - rw / 2
                ry = self.metrics.half_height - rh - BASELINE_PADDING
                movedir = -1
            rect = wx.Rect(rx, ry, rw, rh)
            self._prevent_overlap(rect, movedir)
            self.event_data.append((event, rect))
        for (event, rect) in self.event_data:
            # Remove outer padding
            rect.Deflate(OUTER_PADDING, OUTER_PADDING)
            # Make sure rectangle are not far outside the screen
            if rect.X < -1:
                move = -rect.X - 1
                rect.X += move
                rect.Width -= move
            if rect.Width > self.metrics.width:
                rect.Width = self.metrics.width + 2

    def _prevent_overlap(self, rect, movedir):
        """
        Prevent rect from overlapping with any rectangle by moving it.
        """
        while True:
            h = self._intersection_height(rect)
            if h > 0:
                rect.Y += movedir * h
            else:
                break

    def _intersection_height(self, rect):
        """
        Calculate height of first intersection with rectangle.
        """
        for (event, r) in self.event_data:
            if rect.Intersects(r):
                # Calculate height of intersection only if there is any
                r_copy = wx.Rect(*r) # Because `Intersect` modifies rect
                intersection = r_copy.Intersect(rect)
                return intersection.Height
        return 0

    def _calc_strips(self):
        """Fill the two arrays `minor_strip_data` and `major_strip_data`."""
        def fill(list, strip):
            """Fill the given list with the given strip."""
            current_start = strip.start(self.time_period.start_time)
            while current_start < self.time_period.end_time:
                next_start = strip.increment(current_start)
                list.append(TimePeriod(current_start, next_start))
                current_start = next_start
        major_strip, minor_strip = self._choose_strip()
        fill(self.major_strip_data, major_strip)
        fill(self.minor_strip_data, minor_strip)

    def _choose_strip(self):
        """
        Return a tuple (major_strip, minor_strip) for current time period and
        window size.
        """
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        day_period = TimePeriod(today, tomorrow)
        one_day_width = self.metrics.calc_exact_width(day_period)
        if one_day_width > 600:
            return (StripDay(), StripHour())
        elif one_day_width > 45:
            return (StripWeek(), StripWeekday())
        elif one_day_width > 25:
            return (StripMonth(), StripDay())
        elif one_day_width > 1.5:
            return (StripYear(), StripMonth())
        elif one_day_width > 0.12:
            return (StripDecade(), StripYear())
        else:
            return (StripDecade(), StripDecade())

    def _draw_period_selection(self, period_selection):
        start, end = period_selection
        start_x = self.metrics.calc_x(start)
        end_x = self.metrics.calc_x(end)
        self.dc.SetBrush(self.lightgrey_solid_brush)
        self.dc.SetPen(wx.TRANSPARENT_PEN)
        self.dc.DrawRectangle(start_x, 0,
                              end_x - start_x + 1, self.metrics.height)

    def _draw_bg(self):
        """
        Draw major and minor strips, lines to all event boxes and baseline.

        Both major and minor strips have divider lines and labels.
        """
        major_strip, minor_strip = self._choose_strip()
        # Minor strips
        self.dc.SetFont(self.small_text_font)
        self.dc.SetPen(self.black_dashed_pen)
        for tp in self.minor_strip_data:
            # Divider line
            x = self.metrics.calc_x(tp.end_time)
            self.dc.DrawLine(x, 0, x, self.metrics.height)
            # Label
            label = minor_strip.label(tp.start_time)
            (tw, th) = self.dc.GetTextExtent(label)
            middle = self.metrics.calc_x(tp.mean_time())
            middley = self.metrics.half_height
            self.dc.DrawText(label, middle - tw / 2, middley - th)
        # Major strips
        self.dc.SetFont(self.header_font)
        self.dc.SetPen(self.grey_solid_pen)
        for tp in self.major_strip_data:
            # Divider line
            x = self.metrics.calc_x(tp.end_time)
            self.dc.DrawLine(x, 0, x, self.metrics.height)
            # Label
            label = major_strip.label(tp.start_time, True)
            (tw, th) = self.dc.GetTextExtent(label)
            x = self.metrics.calc_x(tp.mean_time()) - tw / 2
            # If the label is not visible when it is positioned in the middle
            # of the period, we move it so that as much of it as possible is
            # visible without crossing strip borders.
            if x - INNER_PADDING < 0:
                x = INNER_PADDING
                right = self.metrics.calc_x(tp.end_time)
                if x + tw + INNER_PADDING > right:
                    x = right - tw - INNER_PADDING
            elif x + tw + INNER_PADDING > self.metrics.width:
                x = self.metrics.width - tw - INNER_PADDING
                left = self.metrics.calc_x(tp.start_time)
                if x < left:
                    x = left + INNER_PADDING
            self.dc.DrawText(label, x, INNER_PADDING)
        # Main divider line
        self.dc.SetPen(self.black_solid_pen)
        self.dc.DrawLine(0, self.metrics.half_height,
                         self.metrics.width, self.metrics.half_height)
        # Lines to all events
        self.dc.SetBrush(self.black_solid_brush)
        for (event, rect) in self.event_data:
            if rect.Y < self.metrics.half_height:
                x = self.metrics.calc_x(event.mean_time())
                y = rect.Y + rect.Height / 2
                self.dc.DrawLine(x, y, x, self.metrics.half_height)
                self.dc.DrawCircle(x, self.metrics.half_height, 2)
        # Now line
        now_time = datetime.now()
        if self.time_period.inside(now_time):
            self.dc.SetPen(self.darkred_solid_pen)
            x = self.metrics.calc_x(now_time)
            self.dc.DrawLine(x, 0, x, self.metrics.height)

    def _extract_categories(self, events):
        categories = []
        for event in events:
            cat = event.category
            if cat and not cat in categories:
                categories.append(cat)
        return sort_categories(categories)

    def _draw_legend(self, categories):
        """
        Draw legend for the given categories.

        Box in lower left corner:

          +----------+
          | Name   O |
          | Name   O |
          +----------+
        """
        num_categories = len(categories)
        if num_categories == 0:
            return
        def calc_sizes(dc):
            """Return (width, height, item_height)."""
            width = 0
            height = INNER_PADDING
            item_heights = 0
            for cat in categories:
                tw, th = self.dc.GetTextExtent(cat.name)
                height = height + th + INNER_PADDING
                item_heights += th
                if tw > width:
                    width = tw
            item_height = item_heights / num_categories
            return (width + 4 * INNER_PADDING + item_height, height,
                    item_height)
        self.dc.SetFont(self.small_text_font)
        self.dc.SetTextForeground((0, 0, 0))
        width, height, item_height = calc_sizes(self.dc)
        # Draw big box
        self.dc.SetBrush(self.white_solid_brush)
        self.dc.SetPen(self.black_solid_pen)
        box_rect = (OUTER_PADDING,
                    self.metrics.height - height - OUTER_PADDING,
                    width, height)
        self.dc.DrawRectangleRect(box_rect)
        # Draw text and color boxes
        cur_y = self.metrics.height - height - OUTER_PADDING + INNER_PADDING
        for cat in categories:
            base_color = cat.color
            border_color = drawing.darken_color(base_color)
            self.dc.SetBrush(wx.Brush(base_color, wx.SOLID))
            self.dc.SetPen(wx.Pen(border_color, 1, wx.SOLID))
            color_box_rect = (OUTER_PADDING + width - item_height -
                              INNER_PADDING,
                              cur_y, item_height, item_height)
            self.dc.DrawRectangleRect(color_box_rect)
            self.dc.DrawText(cat.name, OUTER_PADDING + INNER_PADDING, cur_y)
            cur_y = cur_y + item_height + INNER_PADDING

    def _draw_events(self):
        """Draw all event boxes and the text inside them."""
        self.dc.SetFont(self.small_text_font)
        self.dc.SetTextForeground((0, 0, 0))
        for (event, rect) in self.event_data:
            # Ensure that we can't draw outside rectangle
            self.dc.DestroyClippingRegion()
            self.dc.SetClippingRect(rect)
            # Draw the box
            base_color = (200, 200, 200)
            if event.category:
                base_color = event.category.color
            border_color = drawing.darken_color(base_color)
            self.dc.SetBrush(wx.Brush(base_color, wx.SOLID))
            self.dc.SetPen(wx.Pen(border_color, 1, wx.SOLID))
            self.dc.DrawRectangleRect(rect)
            if event.selected:
                self.dc.SetBrush(wx.Brush(border_color, wx.BDIAGONAL_HATCH))
                self.dc.SetPen(wx.TRANSPARENT_PEN)
                self.dc.DrawRectangleRect(rect)
            # Draw the text
            self.dc.DrawText(event.text,
                             rect.X + INNER_PADDING,
                             rect.Y + INNER_PADDING)
