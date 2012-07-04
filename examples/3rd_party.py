#!/usr/bin/env python


# Make sure timelinelib can be imported
import os.path
import sys
root_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(root_dir, ".."))


import wx

from timelinelib.wxgui.component import TimelineComponent


class MainFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, style=wx.DEFAULT_FRAME_STYLE)
        timeline_component = TimelineComponent(self)


if __name__ == "__main__":
    app = wx.PySimpleApp()
    main_frame = MainFrame()
    main_frame.Show()
    app.MainLoop()
