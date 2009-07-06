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
Functionality and information for displaying the About dialog.

Much of this information is available in the source distribution files README,
COPYING, and AUTHORS. It is copied here to be available from Python code.
"""


import wx
from wx.lib.wordwrap import wordwrap

from version import get_version


APPLICATION_NAME = "Timeline"
COPYRIGHT_TEXT = "Copyright (C) 2009 The %s Developers" % APPLICATION_NAME
APPLICATION_DESCRIPTION = "Timeline is a cross-platform application for displaying and navigating information on a timeline."
WEBSITE = "http://sourceforge.net/apps/trac/thetimelineproj/"
DEVELOPERS = ["Rickard Lindberg", "Roger Lindberg"]
LICENSE = """Timeline is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Timeline is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Timeline.  If not, see <http://www.gnu.org/licenses/>."""

def display_about_dialog():
    info = wx.AboutDialogInfo()
    info.Name = APPLICATION_NAME
    info.Version = get_version()
    info.Copyright = COPYRIGHT_TEXT
    info.Description = APPLICATION_DESCRIPTION
    info.WebSite = (WEBSITE, "%s Website" % APPLICATION_NAME)
    info.Developers = DEVELOPERS
    info.License = LICENSE
    wx.AboutBox(info)
