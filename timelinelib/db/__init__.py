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
Functionality for reading and writing timeline data from and to persistent
storage.
"""


import os.path

from timelinelib.db.interface import TimelineIOError


def open(path):
    """
    Create timeline database that can read and write timeline data from and to
    persistent storage identified by path.

    Throw a TimelineIOError exception if not able to read from the given path.

    Valid values for path:

      - string with suffix .timeline
      - string with suffix .ics
      - string denoting a directory
    """
    if os.path.isdir(path):
        from timelinelib.db.backends.dir import DirTimeline
        return DirTimeline(path)
    elif path.endswith(".timeline"):
        from timelinelib.db.backends.file import FileTimeline
        return FileTimeline(path)
    elif path.endswith(".ics"):
        try:
            import icalendar
        except ImportError:
            raise TimelineIOError(_("Could not find iCalendar Python package. It is required for working with ICS files. See the Timeline website or the INSTALL file for instructions how to install it."))
        else:
            from timelinelib.db.backends.ics import IcsTimeline
            return IcsTimeline(path)
    else:
        msg_template = (_("Unable to open timeline '%s'.") + "\n\n" +
                        _("Unknown format."))
        raise TimelineIOError(msg_template % path)
