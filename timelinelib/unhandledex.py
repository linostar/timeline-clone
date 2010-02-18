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
Code for reporting exceptions that aren't handled anywhere else.
"""


import traceback

from timelinelib.gui.dialogs.textdisplay import TextDisplayDialog


def unhandled_exception_hook(type, value, tb):
    """
    The handling of top-level exceptions can be customized by assigning a
    three-argument function to sys.excepthook.
    
    This is the method assigned to sys.excepthook.
    The assignment is made in the main method in the main module.
    """
    lines = traceback.format_exception(type, value, tb)
    title = "Unhandled Exception Report"
    TextDisplayDialog(title, "\n".join(lines)).ShowModal()