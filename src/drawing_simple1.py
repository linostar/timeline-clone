"""
Implements a prototype algorithm for drawing a timeline.

The drawing interface is implemented in the `SimpleDrawingAlgorithm1` class in
the `draw` method.
"""


import logging
import calendar
from datetime import timedelta
from datetime import datetime

import wx

import drawing
from drawing import DrawingAlgorithm
from drawing import Metrics
from data import TimePeriod


OUTER_PADDING = 5      # Space between event boxes
INNER_PADDING = 3      # Space inside event box to text
THRESHOLD_PIX = 20     # Periods smaller than this are considered events
BASELINE_PADDING = 15  # Extra space to move events away from baseline


class Strip(object):
    """
    Represent a strip (month or day for example).

    The timeline is divided in major and minor strips. The minor strip might
    for example be days, and the major strip month. Major strips are divided
    with a solid line and minor strips with dotted lines. Typically maximum
    three major strips should be shown and the rest will be minor strips.
    """

    def use_as_minor(self, time_period):
        """
        Return if this strip should be used as minor strip for the given time
        period.

        The strip before this one in `strips` will then be used as major.

        Strips are always checked in order larger to smaller (year strip is
        tested before month strip for example). So if the time period is larger
        than 2 days, maybe we would like to use the day strip.

        This method is used in `__choose_strip`. Have a look there for details
        on how strips are chosen.
        """

    def label(self, time, major=False):
        """Return the label for this strip at the given time."""

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

    def use_as_minor(self, time_period):
        return time_period.delta() > timedelta(365*15)

    def label(self, time, major=False):
        if major:
            # TODO: This only works for English. Possible to localize?
            return str(self.__decade_start_year(time.year)) + "s"
        return ""

    def start(self, time):
        return datetime(self.__decade_start_year(time.year), 1, 1)

    def increment(self, time):
        return time.replace(year=time.year+10)

    def __decade_start_year(self, year):
        return (year / 10) * 10


class StripYear(Strip):

    def use_as_minor(self, time_period):
        return time_period.delta() > timedelta(365*2)

    def label(self, time, major=False):
        return time.strftime("%Y")

    def start(self, time):
        return datetime(time.year, 1, 1)

    def increment(self, time):
        return time.replace(year=time.year+1)


class StripMonth(Strip):

    def use_as_minor(self, time_period):
        return time_period.delta() > timedelta(40)

    def label(self, time, major=False):
        if major:
            return time.strftime("%b %Y")
        return time.strftime("%b")

    def start(self, time):
        return datetime(time.year, time.month, 1)

    def increment(self, time):
        return time + timedelta(calendar.monthrange(time.year, time.month)[1])


class StripDay(Strip):

    def use_as_minor(self, time_period):
        return time_period.delta() > timedelta(2)

    def label(self, time, major=False):
        if major:
            return time.strftime("%d %b %Y")
        return str(time.day)

    def start(self, time):
        return datetime(time.year, time.month, time.day)

    def increment(self, time):
        return time + timedelta(1)


class StripHour(Strip):

    def use_as_minor(self, time_period):
        return time_period.delta() > timedelta(0, 60)

    def label(self, time, major=False):
        if major:
            return time.strftime("%b %d %Y %h")
        return str(time.hour)

    def start(self, time):
        return datetime(time.year, time.month, time.day, time.hour)

    def increment(self, time):
        return time + timedelta(hours=1)


class SimpleDrawingAlgorithm1(DrawingAlgorithm):

    def __init__(self):
        # Fonts and pens we use when drawing
        self.header_font = drawing.get_default_font(12, True)
        self.event_font = drawing.get_default_font(8)
        self.solid_pen = wx.Pen(wx.Color(0, 0, 0), 1, wx.SOLID)
        self.dashed_pen = wx.Pen(wx.Color(200, 200, 200), 1, wx.USER_DASH)
        self.dashed_pen.SetDashes([2, 2])
        self.dashed_pen.SetCap(wx.CAP_BUTT)
        self.solid_pen2 = wx.Pen(wx.Color(200, 200, 200), 1, wx.SOLID)
        self.solid_brush = wx.Brush(wx.Color(0, 0, 0), wx.SOLID)
        # Init the list of strips in the order larger to smaller
        self.strips = []
        self.strips.append(StripDecade())
        self.strips.append(StripYear())
        self.strips.append(StripMonth())
        self.strips.append(StripDay())
        self.strips.append(StripHour())

    def draw(self, dc, time_period, events):
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
        self.__calc_rects(events)
        self.__calc_strips()
        # Perform the actual drawing
        self.__draw_bg()
        self.__draw_events()
        # Make sure to delete this one
        del self.dc

    def __calc_rects(self, events):
        """
        Calculate rectangles for all events.

        The rectangles define the areas in which the events can draw
        themselves.
        """
        self.dc.SetFont(self.event_font)
        for event in events:
            tw, th = self.dc.GetTextExtent(event.text)
            ew = self.metrics.calc_width(event.time_period)
            if ew > THRESHOLD_PIX:
                # Treat as period (periods are placed below the baseline, with
                # indicates length of period)
                rw = ew + 2 * OUTER_PADDING
                rh = th + 2 * INNER_PADDING + 2 * OUTER_PADDING
                rx = self.metrics.calc_x(event.mean_time()) - rw / 2
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
            self.__prevent_overlap(rect, movedir)
            self.event_data.append((event, rect))
        # Remove outer padding
        for (event, rect) in self.event_data:
            rect.Deflate(OUTER_PADDING, OUTER_PADDING)

    def __prevent_overlap(self, rect, movedir):
        """
        Prevent rect from overlapping with any rectangle by moving it.
        """
        while True:
            h = self.__intersection_height(rect)
            if h > 0:
                rect.Y += movedir * h
            else:
                break

    def __intersection_height(self, rect):
        """
        Calculate height of first intersection with rectangle.
        """
        for (event, r) in self.event_data:
            r_copy = wx.Rect(*r) # Because `Intersect` modifies rect
            intersection = r_copy.Intersect(rect)
            if not intersection.IsEmpty():
                return intersection.Height
        return 0

    def __calc_strips(self):
        """Fill the two arrays `minor_strip_data` and `major_strip_data`."""
        def fill(list, strip):
            """Fill the given list with the given strip."""
            current_start = strip.start(self.time_period.start_time)
            while current_start < self.time_period.end_time:
                next_start = strip.increment(current_start)
                list.append(TimePeriod(current_start, next_start))
                current_start = next_start
        major_strip, minor_strip = self.__choose_strip()
        fill(self.major_strip_data, major_strip)
        fill(self.minor_strip_data, minor_strip)

    def __choose_strip(self):
        """
        Return a tuple (major_strip, minor_strip) for current time period.
        """
        prev_strip = None
        for strip in self.strips:
            if strip.use_as_minor(self.time_period):
                if prev_strip == None:
                    # Use the same strip for major and minor
                    return (strip, strip)
                return (prev_strip, strip)
            prev_strip = strip
        # Zoom level is high, resort to last one
        return (self.strips[-2], self.strips[-1])

    def __draw_bg(self):
        """
        Draw major and minor strips, lines to all event boxes and baseline.

        Both major and minor strips have divider lines and labels.
        """
        major_strip, minor_strip = self.__choose_strip()
        # Minor strips
        self.dc.SetFont(self.event_font)
        self.dc.SetPen(self.dashed_pen)
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
        self.dc.SetPen(self.solid_pen2)
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
            elif x + tw / 2 + INNER_PADDING > self.metrics.width:
                x = self.metrics.width - tw - INNER_PADDING
                left = self.metrics.calc_x(tp.start_time)
                if x < left:
                    x = left + INNER_PADDING
            self.dc.DrawText(label, x, INNER_PADDING)
        # Main divider line
        self.dc.SetPen(self.solid_pen)
        self.dc.DrawLine(0, self.metrics.half_height,
                         self.metrics.width, self.metrics.half_height)
        # Lines to all events
        self.dc.SetBrush(self.solid_brush)
        for (event, rect) in self.event_data:
            if rect.Y < self.metrics.half_height:
                x = rect.X + rect.Width / 2
                y = rect.Y + rect.Height / 2
                self.dc.DrawLine(x, y, x, self.metrics.half_height)
                self.dc.DrawCircle(x, self.metrics.half_height, 2)

    def __draw_events(self):
        """Draw all event boxes and the text inside them."""
        self.dc.SetFont(self.event_font)
        self.dc.SetPen(self.solid_pen)
        for (event, rect) in self.event_data:
            # Ensure that we can't draw outside rectangle
            self.dc.DestroyClippingRegion()
            self.dc.SetClippingRect(rect)
            self.dc.SetBrush(wx.Brush(wx.Color(200, 200, 0), wx.SOLID))
            self.dc.DrawRectangleRect(rect)
            self.dc.DrawText(event.text,
                             rect.X + INNER_PADDING,
                             rect.Y + INNER_PADDING)
