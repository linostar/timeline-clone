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


"""
Implements a Drawer that draws the default timeline view.
"""


import math
import calendar
import os.path

import wx

from timelinelib.drawing.interface import Drawer
from timelinelib.drawing.utils import get_default_font
from timelinelib.drawing.utils import Metrics
from timelinelib.drawing.utils import darken_color
from timelinelib.gui.utils import sort_categories
from timelinelib.db.objects import TimePeriod
from timelinelib.paths import ICONS_DIR
import timelinelib.config as config


OUTER_PADDING = 5      # Space between event boxes (pixels)
INNER_PADDING = 3      # Space inside event box to text (pixels)
BASELINE_PADDING = 15  # Extra space to move events away from baseline (pixels)
PERIOD_THRESHOLD = 20  # Periods smaller than this are drawn as events (pixels)
BALLOON_RADIUS = 12
DATA_INDICATOR_SIZE = 10


class DefaultDrawingAlgorithm(Drawer):

    def __init__(self):
        self._create_fonts()
        self._create_pens()
        self._create_brushes()
        self.db = None
        
    def _create_fonts(self):
        self.header_font = get_default_font(12, True)
        self.small_text_font = get_default_font(8)
        self.small_text_font_bold = get_default_font(8, True)

    def _create_pens(self):
        self.red_solid_pen = wx.Pen(wx.Color(255,0, 0), 1, wx.SOLID)
        self.black_solid_pen = wx.Pen(wx.Color(0, 0, 0), 1, wx.SOLID)
        self.darkred_solid_pen = wx.Pen(wx.Color(200, 0, 0), 1, wx.SOLID)
        self.black_dashed_pen = wx.Pen(wx.Color(200, 200, 200), 1, wx.USER_DASH)
        self.black_dashed_pen.SetDashes([2, 2])
        self.black_dashed_pen.SetCap(wx.CAP_BUTT)
        self.grey_solid_pen = wx.Pen(wx.Color(200, 200, 200), 1, wx.SOLID)
        self.red_solid_pen = wx.Pen(wx.Color(255, 0, 0), 1, wx.SOLID)
        
    def _create_brushes(self):
        self.white_solid_brush = wx.Brush(wx.Color(255, 255, 255), wx.SOLID)
        self.black_solid_brush = wx.Brush(wx.Color(0, 0, 0), wx.SOLID)
        self.red_solid_brush = wx.Brush(wx.Color(255, 0, 0), wx.SOLID)
        self.lightgrey_solid_brush = wx.Brush(wx.Color(230, 230, 230), wx.SOLID)

    def event_is_period(self, time_period):
        period_width_in_pixels = self.metrics.calc_width(time_period)
        return period_width_in_pixels > PERIOD_THRESHOLD

    def draw(self, dc, timeline, view_properties):
        self.dc = dc
        self.time_period = view_properties.displayed_period
        self.db = timeline
        self.time_type = self.db.get_time_type()
        self.metrics = Metrics(dc.GetSizeTuple(), self.time_type, 
                               self.time_period, 
                               view_properties.divider_position)
        self._calc_event_positions(view_properties)
        self._calc_strips()
        self._perform_drawing(view_properties)
        del self.dc # Program crashes if we don't delete the dc reference.

    def _perform_drawing(self, view_properties):
        self._draw_period_selection(view_properties)
        self._draw_bg(view_properties)
        self._draw_events(view_properties)
        self._draw_legend(view_properties, self._extract_categories())
        self._draw_ballons(view_properties)
        
    def _calc_event_positions(self, view_properties):
        events_from_db = self.db.get_events(self.time_period)
        visible_events = view_properties.filter_events(events_from_db)
        self._calc_rects(visible_events)
        
    def snap(self, time, snap_region=10):
        if self._distance_to_left_border(time) < snap_region:
            return self._get_time_at_left_border(time)
        elif self._distance_to_right_border(time)  < snap_region:
            return self._get_time_at_right_border(time)
        else:
            return time

    def _distance_to_left_border(self, time):
        left_strip_time, right_strip_time = self._snap_region(time)
        return self._distance_between_times(time, left_strip_time)
        
    def _distance_to_right_border(self, time):
        left_strip_time, right_strip_time = self._snap_region(time)
        return self._distance_between_times(time, right_strip_time)

    def _get_time_at_left_border(self, time):
        left_strip_time, right_strip_time = self._snap_region(time)
        return left_strip_time
        
    def _get_time_at_right_border(self, time):
        left_strip_time, right_strip_time = self._snap_region(time)
        return right_strip_time
        
    def _distance_between_times(self, time1, time2):
        time1_x = self.metrics.calc_exact_x(time1)
        time2_x = self.metrics.calc_exact_x(time2)
        distance = abs(time1_x - time2_x)
        return distance
        
    def _snap_region(self, time): 
        major_strip, minor_strip = self._choose_strip()
        time_x = self.metrics.calc_exact_x(time)
        left_strip_time = minor_strip.start(time)
        right_strip_time = minor_strip.increment(left_strip_time)
        return (left_strip_time, right_strip_time)
    
    def snap_selection(self, period_selection):
        start, end = period_selection
        return (self.snap(start), self.snap(end))

    def event_at(self, x, y):
        for (event, rect) in self.event_data:
            if rect.Contains(wx.Point(x, y)):
                return event
        return None

    def event_with_rect_at(self, x, y):
        for (event, rect) in self.event_data:
            if rect.Contains(wx.Point(x, y)):
                return (event, rect)
        return None

    def event_rect(self, evt):
        for (event, rect) in self.event_data:
            if evt == event:
                return rect
        return None

    def balloon_at(self, x, y):
        event = None
        for (event_in_list, rect) in self.balloon_data:
            if rect.Contains(wx.Point(x, y)):
                event = event_in_list
        return event

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
        self.dc.SetFont(self.small_text_font)
        tw, th = self.dc.GetTextExtent(event.text)
        ew = self.metrics.calc_width(event.time_period)
        rw = ew + 2 * OUTER_PADDING
        rh = th + 2 * INNER_PADDING + 2 * OUTER_PADDING
        rx = (self.metrics.calc_x(event.time_period.start_time) -
              OUTER_PADDING)
        ry = self.metrics.half_height + BASELINE_PADDING
        rect = wx.Rect(rx, ry, rw, rh)
        return rect

    def _create_ideal_rect_for_non_period_event(self, event):
        self.dc.SetFont(self.small_text_font)
        tw, th = self.dc.GetTextExtent(event.text)
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
            current_start = strip.start(self.time_period.start_time)
            while current_start < self.time_period.end_time:
                next_start = strip.increment(current_start)
                list.append(TimePeriod(self.db.get_time_type(), current_start, next_start))
                current_start = next_start
        self.major_strip_data = [] # List of time_period
        self.minor_strip_data = [] # List of time_period
        major_strip, minor_strip = self.time_type.choose_strip(self.metrics)
        fill(self.major_strip_data, major_strip)
        fill(self.minor_strip_data, minor_strip)

    def _choose_strip(self):
        """
        Return a tuple (major_strip, minor_strip) for current time period and
        window size.
        """
        return self.time_type.choose_strip(self.metrics)
     
    def _draw_period_selection(self, view_properties):
        if not view_properties.period_selection:
            return
        start, end = view_properties.period_selection
        start_x = self.metrics.calc_x(start)
        end_x = self.metrics.calc_x(end)
        self.dc.SetBrush(self.lightgrey_solid_brush)
        self.dc.SetPen(wx.TRANSPARENT_PEN)
        self.dc.DrawRectangle(start_x, 0,
                              end_x - start_x + 1, self.metrics.height)

    def _draw_bg(self, view_properties):
        self._draw_minor_strips()
        self._draw_major_strips()
        self._draw_divider_line()
        self._draw_lines_to_non_period_events(view_properties)
        self._draw_now_line()

    def _draw_minor_strips(self):
        for strip_period in self.minor_strip_data:
            self._draw_minor_strip_divider_line_at(strip_period.end_time)
            self._draw_minor_strip_label(strip_period)

    def _draw_minor_strip_divider_line_at(self, time):
        x = self.metrics.calc_x(time)
        self.dc.SetPen(self.black_dashed_pen)
        self.dc.DrawLine(x, 0, x, self.metrics.height)

    def _draw_minor_strip_label(self, strip_period):
        major_strip, minor_strip = self._choose_strip()
        label = minor_strip.label(strip_period.start_time)
        (tw, th) = self.dc.GetTextExtent(label)
        middle = self.metrics.calc_x(strip_period.mean_time())
        middley = self.metrics.half_height
        self.dc.SetFont(minor_strip.get_font(strip_period))
        self.dc.DrawText(label, middle - tw / 2, middley - th)
        
    def _draw_major_strips(self):
        major_strip, minor_strip = self._choose_strip()
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
        
    def _draw_divider_line(self):
        self.dc.SetPen(self.black_solid_pen)
        self.dc.DrawLine(0, self.metrics.half_height, self.metrics.width,
                         self.metrics.half_height)
        
    def _draw_lines_to_non_period_events(self, view_properties):
        self.dc.SetBrush(self.black_solid_brush)
        for (event, rect) in self.event_data:
            if rect.Y < self.metrics.half_height:
                x = self.metrics.calc_x(event.mean_time())
                y = rect.Y + rect.Height / 2
                if view_properties.is_selected(event):
                    self.dc.SetPen(self.red_solid_pen)
                    self.dc.SetBrush(self.red_solid_brush)
                else:
                    self.dc.SetBrush(self.black_solid_brush)
                    self.dc.SetPen(self.black_solid_pen)
                self.dc.DrawLine(x, y, x, self.metrics.half_height)
                self.dc.DrawCircle(x, self.metrics.half_height, 2)
        
    def _draw_now_line(self):
        now_time = self.time_type.now()
        if self.time_period.inside(now_time):
            self.dc.SetPen(self.darkred_solid_pen)
            x = self.metrics.calc_x(now_time)
            self.dc.DrawLine(x, 0, x, self.metrics.height)
                
    def _extract_categories(self):
        categories = []
        for (event, rect) in self.event_data:
            cat = event.category
            if cat and not cat in categories:
                categories.append(cat)
        return sort_categories(categories)

    def _draw_legend(self, view_properties, categories):
        """
        Draw legend for the given categories.

        Box in lower left corner:

          +----------+
          | Name   O |
          | Name   O |
          +----------+
        """
        if not view_properties.show_legend:
            return
        if len(categories) == 0:
            return
        self.dc.SetFont(self.small_text_font)
        rect = self._calculate_legend_rect(categories)
        self._draw_legend_box(rect)
        self._draw_legend_items(rect, categories)

    def _calculate_legend_rect(self, categories):
        max_width = 0
        height = INNER_PADDING
        for cat in categories:
            tw, th = self.dc.GetTextExtent(cat.name)
            height = height + th + INNER_PADDING
            if tw > max_width:
                max_width = tw
        item_height = self._text_height_with_current_font()
        width = max_width + 4 * INNER_PADDING + item_height
        return wx.Rect(OUTER_PADDING,
                       self.metrics.height - height - OUTER_PADDING,
                       width,
                       height)

    def _draw_legend_box(self, rect):
        self.dc.SetBrush(self.white_solid_brush)
        self.dc.SetPen(self.black_solid_pen)
        self.dc.DrawRectangleRect(rect)

    def _text_height_with_current_font(self):
        STRING_WITH_MIXED_CAPITALIZATION = "jJ"
        tw, th = self.dc.GetTextExtent(STRING_WITH_MIXED_CAPITALIZATION)
        return th

    def _draw_legend_items(self, rect, categories):
        item_height = self._text_height_with_current_font()
        cur_y = rect.Y + INNER_PADDING
        for cat in categories:
            base_color = cat.color
            border_color = darken_color(base_color)
            self.dc.SetBrush(wx.Brush(base_color, wx.SOLID))
            self.dc.SetPen(wx.Pen(border_color, 1, wx.SOLID))
            color_box_rect = (OUTER_PADDING + rect.Width - item_height -
                              INNER_PADDING,
                              cur_y, item_height, item_height)
            self.dc.DrawRectangleRect(color_box_rect)
            self.dc.SetTextForeground((0, 0, 0))
            self.dc.DrawText(cat.name, OUTER_PADDING + INNER_PADDING, cur_y)
            cur_y = cur_y + item_height + INNER_PADDING

    def _draw_events(self, view_properties):
        """Draw all event boxes and the text inside them."""
        self.dc.SetFont(self.small_text_font)
        self.dc.SetTextForeground((0, 0, 0))
        for (event, rect) in self.event_data:
            # Ensure that we can't draw outside rectangle
            self.dc.DestroyClippingRegion()
            self.dc.SetClippingRect(rect)
            # Draw the box
            self.dc.SetBrush(self._get_box_brush(event))
            self.dc.SetPen(self._get_box_pen(event))
            self.dc.DrawRectangleRect(rect)
            # Ensure that we can't draw content outside inner rectangle
            self.dc.DestroyClippingRegion()
            rect_copy = wx.Rect(*rect)
            rect_copy.Deflate(INNER_PADDING, INNER_PADDING)
            self.dc.SetClippingRect(rect_copy)
            if rect_copy.Width > 0:
                # Draw the text (if there is room for it)
                text_x = rect.X + INNER_PADDING
                text_y = rect.Y + INNER_PADDING
                if text_x < INNER_PADDING:
                    text_x = INNER_PADDING
                self.dc.DrawText(event.text, text_x, text_y)
            # Draw data contents indicator
            self.dc.DestroyClippingRegion()
            self.dc.SetClippingRect(rect)
            if event.has_data():
                self._draw_contents_indicator(event, rect)
            # Draw selection and handles
            if view_properties.is_selected(event):
                small_rect = wx.Rect(*rect)
                small_rect.Deflate(1, 1)
                border_color = self._get_border_color(event)
                border_color = darken_color(border_color)
                pen = wx.Pen(border_color, 1, wx.SOLID)
                self.dc.SetBrush(wx.TRANSPARENT_BRUSH)
                self.dc.SetPen(pen)
                self.dc.DrawRectangleRect(small_rect)
                self._draw_handles(rect)
        # Reset this when we are done
        self.dc.DestroyClippingRegion()

    def _draw_handles(self, rect):
        SIZE = 4
        big_rect = wx.Rect(rect.X - SIZE, rect.Y - SIZE, rect.Width + 2 * SIZE, rect.Height + 2 * SIZE)
        self.dc.DestroyClippingRegion()
        self.dc.SetClippingRect(big_rect)
        y = rect.Y + rect.Height/2 - SIZE/2
        x = rect.X - SIZE / 2
        west_rect   = wx.Rect(x + 1             , y, SIZE, SIZE)
        center_rect = wx.Rect(x + rect.Width / 2, y, SIZE, SIZE)
        east_rect   = wx.Rect(x + rect.Width - 1, y, SIZE, SIZE)
        self.dc.SetBrush(wx.Brush("BLACK", wx.SOLID))
        self.dc.SetPen(wx.Pen("BLACK", 1, wx.SOLID))
        self.dc.DrawRectangleRect(east_rect)
        self.dc.DrawRectangleRect(west_rect)
        self.dc.DrawRectangleRect(center_rect)

    def _draw_contents_indicator(self, event, rect):
        """
        The data contents indicator is a small triangle drawn in the upper
        right corner of the event rectangle.
        """
        corner_x = rect.X + rect.Width
        if corner_x > self.metrics.width:
            corner_x = self.metrics.width
        points = (
            wx.Point(corner_x - DATA_INDICATOR_SIZE, rect.Y),
            wx.Point(corner_x, rect.Y),
            wx.Point(corner_x, rect.Y + DATA_INDICATOR_SIZE),
        )
        self.dc.SetBrush(self._get_box_indicator_brush(event))
        self.dc.SetPen(wx.TRANSPARENT_PEN)
        self.dc.DrawPolygon(points)

    def _get_base_color(self, event):
        if event.category:
            base_color = event.category.color
        else:
            base_color = (200, 200, 200)
        return base_color

    def _get_border_color(self, event):
        base_color = self._get_base_color(event)
        border_color = darken_color(base_color)
        return border_color

    def _get_box_pen(self, event):
        border_color = self._get_border_color(event)
        pen = wx.Pen(border_color, 1, wx.SOLID)
        return pen

    def _get_box_brush(self, event):
        base_color = self._get_base_color(event)
        brush = wx.Brush(base_color, wx.SOLID)
        return brush

    def _get_box_indicator_brush(self, event):
        base_color = self._get_base_color(event)
        darker_color = darken_color(base_color, 0.6)
        brush = wx.Brush(darker_color, wx.SOLID)
        return brush

    def _get_selected_box_brush(self, event):
        border_color = self._get_border_color(event)
        brush = wx.Brush(border_color, wx.BDIAGONAL_HATCH)
        return brush

    def _draw_ballons(self, view_properties):
        """Draw ballons on selected events that has 'description' data."""
        self.balloon_data = []     # List of (event, rect)
        top_event = None
        top_rect = None
        for (event, rect) in self.event_data:
            if (event.get_data("description") != None or
                event.get_data("icon") != None):
                sticky = view_properties.event_has_sticky_balloon(event)
                if (view_properties.event_is_hovered(event) or sticky):
                    if not sticky:
                        top_event, top_rect = event, rect
                    self._draw_ballon(event, rect, sticky)
        # Make the unsticky balloon appear on top
        if top_event is not None:
            self._draw_ballon(top_event, top_rect, False)

    def _draw_ballon(self, event, event_rect, sticky):
        """Draw one ballon on a selected event that has 'description' data."""
        # Constants
        MAX_TEXT_WIDTH = 200
        MIN_WIDTH = 100
        inner_rect_w = 0
        inner_rect_h = 0
        # Icon
        (iw, ih) = (0, 0)
        icon = event.get_data("icon")
        if icon != None:
            (iw, ih) = icon.Size
            inner_rect_w = iw
            inner_rect_h = ih
        # Text
        self.dc.SetFont(get_default_font(8))
        font_h = self.dc.GetCharHeight()
        (tw, th) = (0, 0)
        description = event.get_data("description")
        lines = None
        if description != None:
            lines = break_text(description, self.dc, MAX_TEXT_WIDTH)
            th = len(lines) * self.dc.GetCharHeight()
            for line in lines:
                (lw, lh) = self.dc.GetTextExtent(line)
                tw = max(lw, tw)
            if icon != None:
                inner_rect_w += BALLOON_RADIUS
            inner_rect_w += min(tw, MAX_TEXT_WIDTH)
            inner_rect_h = max(inner_rect_h, th)
        inner_rect_w = max(MIN_WIDTH, inner_rect_w)
        bounding_rect, x, y = self._draw_balloon_bg(
            self.dc, (inner_rect_w, inner_rect_h),
            (event_rect.X + event_rect.Width / 2,
            event_rect.Y),
            True, sticky)
        if icon != None:
            self.dc.DrawBitmap(icon, x, y, False)
            x += iw + BALLOON_RADIUS
        if lines != None:
            ty = y
            for line in lines:
                self.dc.DrawText(line, x, ty)
                ty += font_h
            x += tw
        # Write data so we know where the balloon was drawn
        # Following two lines can be used when debugging the rectangle
        #self.dc.SetBrush(wx.TRANSPARENT_BRUSH)
        #self.dc.DrawRectangleRect(bounding_rect)
        self.balloon_data.append((event, bounding_rect))

    def _draw_balloon_bg(self, dc, inner_size, tip_pos, above, sticky):
        """
        Draw the balloon background leaving inner_size for content.

        tip_pos determines where the tip of the ballon should be.

        above determines if the balloon should be above the tip (True) or below
        (False). This is not currently implemented.

                    W
           |----------------|
             ______________           _
            /              \          |             R = Corner Radius
           |                |         |            AA = Left Arrow-leg angle
           |  W_ARROW       |         |  H     MARGIN = Text margin
           |     |--|       |         |             * = Starting point
            \____    ______/          _
                /  /                  |
               /_/                    |  H_ARROW
              *                       -
           |----|
           ARROW_OFFSET

        Calculation of points starts at the tip of the arrow and continues
        clockwise around the ballon.

        Return (bounding_rect, x, y) where x and y is at top of inner region.
        """
        # Prepare path object
        gc = wx.GraphicsContext.Create(self.dc)
        path = gc.CreatePath()
        # Calculate path
        R = BALLOON_RADIUS
        W = 1 * R + inner_size[0]
        H = 1 * R + inner_size[1]
        H_ARROW = 14
        W_ARROW = 15
        W_ARROW_OFFSET = R + 25
        AA = 20
        # Starting point at the tip of the arrow
        (tipx, tipy) = tip_pos
        p0 = wx.Point(tipx, tipy)
        path.MoveToPoint(p0.x, p0.y)
        # Next point is the left base of the arrow
        p1 = wx.Point(p0.x + H_ARROW * math.tan(math.radians(AA)),
                      p0.y - H_ARROW)
        path.AddLineToPoint(p1.x, p1.y)
        # Start of lower left rounded corner
        p2 = wx.Point(p1.x - W_ARROW_OFFSET + R, p1.y)
        bottom_y = p2.y
        path.AddLineToPoint(p2.x, p2.y)
        # The lower left rounded corner. p3 is the center of the arc
        p3 = wx.Point(p2.x, p2.y - R)
        path.AddArc(p3.x, p3.y, R, math.radians(90), math.radians(180))
        # The left side
        p4 = wx.Point(p3.x - R, p3.y - H + R)
        left_x = p4.x
        path.AddLineToPoint(p4.x, p4.y)
        # The upper left rounded corner. p5 is the center of the arc
        p5 = wx.Point(p4.x + R, p4.y)
        path.AddArc(p5.x, p5.y, R, math.radians(180), math.radians(-90))
        # The upper side
        p6 = wx.Point(p5.x + W - R, p5.y - R)
        top_y = p6.y
        path.AddLineToPoint(p6.x, p6.y)
        # The upper right rounded corner. p7 is the center of the arc
        p7 = wx.Point(p6.x, p6.y + R)
        path.AddArc(p7.x, p7.y, R, math.radians(-90), math.radians(0))
        # The right side
        p8 = wx.Point(p7.x + R , p7.y + H - R)
        right_x = p8.x
        path.AddLineToPoint(p8.x, p8.y)
        # The lower right rounded corner. p9 is the center of the arc
        p9 = wx.Point(p8.x - R, p8.y)
        path.AddArc(p9.x, p9.y, R, math.radians(0), math.radians(90))
        # The lower side
        p10 = wx.Point(p9.x - W + W_ARROW +  W_ARROW_OFFSET, p9.y + R)
        path.AddLineToPoint(p10.x, p10.y)
        path.CloseSubpath()
        # Draw sharp lines on GTK which uses Cairo
        # See: http://www.cairographics.org/FAQ/#sharp_lines
        gc.Translate(0.5, 0.5)
        # Draw the ballon
        BORDER_COLOR = wx.Color(127, 127, 127)
        BG_COLOR = wx.Color(255, 255, 231)
        PEN = wx.Pen(BORDER_COLOR, 1, wx.SOLID)
        BRUSH = wx.Brush(BG_COLOR, wx.SOLID)
        gc.SetPen(PEN)
        gc.SetBrush(BRUSH)
        gc.DrawPath(path)
        # Draw the pin
        if sticky:
            pin = wx.Bitmap(os.path.join(ICONS_DIR, "stickypin.png"))
        else:
            pin = wx.Bitmap(os.path.join(ICONS_DIR, "unstickypin.png"))
        self.dc.DrawBitmap(pin, p7.x -5, p6.y + 5, True)

        # Return
        bx = left_x
        by = top_y
        bw = W + R + 1
        bh = H + R + H_ARROW + 1
        bounding_rect = wx.Rect(bx, by, bw, bh)
        return (bounding_rect, left_x + BALLOON_RADIUS, top_y + BALLOON_RADIUS)


def break_text(text, dc, max_width_in_px):
    """ Break the text into lines so that they fits within the given width."""
    sentences = text.split("\n")
    lines = []
    for sentence in sentences:
        w, h = dc.GetTextExtent(sentence)
        if w <= max_width_in_px:
            lines.append(sentence)
        # The sentence is too long. Break it.
        else:
            break_sentence(dc, lines, sentence, max_width_in_px);
    return lines


def break_sentence(dc, lines, sentence, max_width_in_px):
    """Break a sentence into lines."""
    line = []
    max_word_len_in_ch = get_max_word_length(dc, max_width_in_px)
    words = break_line(dc, sentence, max_word_len_in_ch)
    for word in words:
        w, h = dc.GetTextExtent("".join(line) + word + " ")
        # Max line length reached. Start a new line
        if w > max_width_in_px:
            lines.append("".join(line))
            line = []
        line.append(word + " ")
        # Word edning with '-' is a broken word. Start a new line
        if word.endswith('-'):
            lines.append("".join(line))
            line = []
    if len(line) > 0:
        lines.append("".join(line))


def break_line(dc, sentence, max_word_len_in_ch):
    """Break a sentence into words."""
    words = sentence.split(" ")
    new_words = []
    for word in words:
        broken_words = break_word(dc, word, max_word_len_in_ch)
        for broken_word in broken_words:
            new_words.append(broken_word)
    return new_words


def break_word(dc, word, max_word_len_in_ch):
    """
    Break words if they are too long.

    If a single word is too long to fit we have to break it.
    If not we just return the word given.
    """
    words = []
    while len(word) > max_word_len_in_ch:
        word1 = word[0:max_word_len_in_ch] + "-"
        word =  word[max_word_len_in_ch:]
        words.append(word1)
    words.append(word)
    return words


def get_max_word_length(dc, max_width_in_px):
    TEMPLATE_CHAR = 'K'
    word = [TEMPLATE_CHAR]
    w, h = dc.GetTextExtent("".join(word))
    while w < max_width_in_px:
        word.append(TEMPLATE_CHAR)
        w, h = dc.GetTextExtent("".join(word))
    return len(word) - 1
