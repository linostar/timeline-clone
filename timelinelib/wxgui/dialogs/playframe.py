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


import wx

from timelinelib.play.playcontroller import PlayController


class PlayFrame(wx.Dialog):

    def __init__(self, timeline):
        self.controller = PlayController(self, timeline)
        wx.Dialog.__init__(self, None, style=wx.DEFAULT_FRAME_STYLE)
        self.close_button = wx.Button(self, wx.ID_ANY, label="knapp")
        self.Bind(wx.EVT_BUTTON, self.on_close_clicked, self.close_button)

    def on_close_clicked(self, e):
        self.controller.on_close_clicked()

    def close(self):
        self.EndModal(wx.ID_OK) 
