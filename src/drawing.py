"""
Contains algorithms for drawing a timeline.
"""

import logging
from datetime import timedelta

import wx

from data import div_timedeltas
from data import microseconds_to_delta
from data import delta_to_microseconds


class DrawingAlgorithm(object):
    """Base class for timeline drawing algorithms."""

    def draw(self, dc, time_period, events):
        """
        This is the interface.

        - dc: used to do the actual drawing
        - time_period: what period should of the timeline should be visible
        - events: events inside time_period that should be drawn

        When the dc is temporarily stored in a class variable such as self.dc,
        this class variable must be deleted before the draw method ends.
        """
        pass


class Metrics(object):
    """Helper class that can calculate coordinates."""

    def __init__(self, dc, time_period):
        self.width, self.height = dc.GetSizeTuple()
        self.half_width = self.width / 2
        self.half_height = self.height / 2
        self.time_period = time_period

    def calc_x(self, time):
        """Calculate the x position for the given time."""
        delta1 = div_timedeltas(time - self.time_period.start_time,
                                self.time_period.delta())
        return self.width * delta1

    def calc_width(self, time_period):
        """Calculate the with in pixels for the given time_period."""
        return (self.calc_x(time_period.end_time) -
                self.calc_x(time_period.start_time))

    def get_time(self, x):
        """Calculate the time at pixel `x`."""
        microsecs = delta_to_microseconds(self.time_period.delta())
        microsecs = microsecs * float(x) / self.width
        return self.time_period.start_time + microseconds_to_delta(microsecs)


def get_default_font(size, bold=False):
    if bold:
        weight = wx.FONTWEIGHT_BOLD
    else:
        weight = wx.FONTWEIGHT_NORMAL
    return wx.Font(size, wx.FONTFAMILY_DEFAULT,
                   wx.FONTSTYLE_NORMAL, weight)


def setup_drawing_algorithm(drawing_algorithm):
    global _drawing_algorithm
    _drawing_algorithm = drawing_algorithm


from drawing_simple1 import SimpleDrawingAlgorithm1
from drawing_simple2 import SimpleDrawingAlgorithm2


def get_algorithm():
    """Factory method."""
    return _drawing_algorithms.get(_drawing_algorithm, SimpleDrawingAlgorithm1)()


_drawing_algorithm  = None
_drawing_algorithms = {'simple1': SimpleDrawingAlgorithm1,
                       'simple2': SimpleDrawingAlgorithm2}
