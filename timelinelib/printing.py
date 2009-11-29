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
Printing framework.
"""


import wx
import logging


class TimelinePrintout(wx.Printout):
    """
    This class has the functionality of printing out a Timeline document.
    Responds to calls such as OnPrintPage and HasPage.
    Instances of this class are passed to wx.Printer.Print() or a
    wx.PrintPreview object to initiate printing or previewing.
    """

    def __init__(self, panel, preview=False):
        wx.Printout.__init__(self)
        self.panel   = panel
        self.preview = preview

    def OnBeginDocument(self, start, end):
        logging.debug("TimelinePrintout.OnBeginDocument")
        return super(TimelinePrintout, self).OnBeginDocument(start, end)

    def OnEndDocument(self):
        logging.debug("TimelinePrintout.OnEndDocument")
        super(TimelinePrintout, self).OnEndDocument()

    def OnBeginPrinting(self):
        logging.debug("TimelinePrintout.OnBeginPrinting")
        super(TimelinePrintout, self).OnBeginPrinting()

    def OnEndPrinting(self):
        logging.debug("TimelinePrintout.OnEndPrinting")
        super(TimelinePrintout, self).OnEndPrinting()

    def OnPreparePrinting(self):
        logging.debug("TimelinePrintout.OnPreparePrinting")
        super(TimelinePrintout, self).OnPreparePrinting()

    def HasPage(self, page):
        logging.debug("TimelinePrintout.HasPage")
        if page <= 1:
            return True
        else:
            return False

    def GetPageInfo(self):
        logging.debug("TimelinePrintout.GetPageInfo")
        minPage  = 1
        maxPage  = 1
        pageFrom = 1
        pageTo   = 1
        return (minPage, maxPage, pageFrom, pageTo)

    def OnPrintPage(self, page):

        def SetScaleAndDeviceOrigin(dc):
            (panel_width, panel_height) = self.panel.GetSize()
            # Let's have at least 50 device units margin
            x_margin = 50
            y_margin = 50
            # Add the margin to the graphic size
            x_max = panel_width  + (2 * x_margin)
            y_max = panel_height + (2 * y_margin)
            # Get the size of the DC in pixels
            (dc_width, dc_heighth) = dc.GetSizeTuple()
            # Calculate a suitable scaling factor
            x_scale = float(dc_width) / x_max
            y_scale = float(dc_heighth) / y_max
            # Use x or y scaling factor, whichever fits on the DC
            scale = min(x_scale, y_scale)
            # Calculate the position on the DC for centering the graphic
            x_pos = (dc_width - (panel_width  * scale)) / 2.0
            y_pos = (dc_heighth - (panel_height * scale)) / 2.0
            dc.SetUserScale(scale, scale)
            dc.SetDeviceOrigin(int(x_pos), int(y_pos))

        logging.debug("TimelinePrintout.OnPrintPage: %d\n" % page)
        dc = self.GetDC()
        SetScaleAndDeviceOrigin(dc)
        dc.BeginDrawing()
        dc.DrawBitmap(self.panel.bgbuf, 0, 0, True)
        dc.EndDrawing()
        return True

