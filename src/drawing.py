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
Defines the interface for drawing algorithms and provides common utilities for
drawing.
"""


import wx

from data import div_timedeltas
from data import microseconds_to_delta
from data import delta_to_microseconds


class DrawingAlgorithm(object):
    """
    Base class for timeline drawing algorithms.

    In order to get an implementation, the `get_algorithm` factory method
    should be used.
    """

    def draw(self, dc, time_period, events, period_selection=None,
             legend=False, divider_line_slider=None):
        """
        This is the interface.

        - dc: used to do the actual drawing
        - time_period: what period of the timeline should be visible
        - events: events inside time_period that should be drawn
        - period_selection: tuple with start and end time indicating selection
        - legend: draw a legend for the categories

        When the dc is temporarily stored in a class variable such as self.dc,
        this class variable must be deleted before the draw method ends.
        """
        pass

    def snap(self, time, snap_region=10):
        """Snap time to minor strip if within snap_region pixels."""
        return time

    def snap_selection(self, period_selection):
        """
        Return a tuple where the selection has been stretched to fit to minor
        strip.

        period_selection: (start, end)
        Return: (new_start, new_end)
        """
        return period_selection

    def event_at(self, x, y):
        """
        Return the event at pixel coordinate (x, y) or None if no event there.
        """
        return None


class Metrics(object):
    """Helper class that can calculate coordinates."""

    def __init__(self, dc, time_period, divider_line_slider):
        self.width, self.height = dc.GetSizeTuple()
        self.half_width = self.width / 2
        self.half_height = self.height / 2
        self.half_height = divider_line_slider.GetValue() * self.height / 100
        self.time_period = time_period

    def calc_exact_x(self, time):
        """Return the x position in pixels as a float for the given time."""
        delta1 = div_timedeltas(time - self.time_period.start_time,
                                self.time_period.delta())
        float_res = self.width * delta1
        return float_res

    def calc_x(self, time):
        """Return the x position in pixels as an integer for the given time."""
        return int(round(self.calc_exact_x(time)))

    def calc_exact_width(self, time_period):
        """Return the with in pixels as a float for the given time_period."""
        return (self.calc_exact_x(time_period.end_time) -
                self.calc_exact_x(time_period.start_time))

    def calc_width(self, time_period):
        """Return the with in pixels as an integer for the given time_period."""
        return (self.calc_x(time_period.end_time) -
                self.calc_x(time_period.start_time)) + 1

    def get_time(self, x):
        """Return the time at pixel `x`."""
        microsecs = delta_to_microseconds(self.time_period.delta())
        microsecs = microsecs * float(x) / self.width
        return self.time_period.start_time + microseconds_to_delta(microsecs)


def get_default_font(size, bold=False):
    if bold:
        weight = wx.FONTWEIGHT_BOLD
    else:
        weight = wx.FONTWEIGHT_NORMAL
    return wx.Font(size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, weight)


def darken_color(color, factor=0.7):
    r, g, b = color
    new_r = int(r * factor)
    new_g = int(g * factor)
    new_b = int(b * factor)
    return (new_r, new_g, new_b)


def get_algorithm():
    """
    Factory method.

    Return the drawing algorithm that should be used by the application.
    """
    from drawing_default import DefaultDrawingAlgorithm
    return DefaultDrawingAlgorithm()
