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
Utility functions used by unit tests.
"""


import tempfile
import codecs


def create_tmp_file(content, suffix):
    """
    Write unicode content to a temporary file (using utf-8 encoding) with the
    given suffix. Path to temporary file is returned.
    """
    (handle, path) = tempfile.mkstemp(suffix=suffix)
    f = codecs.open(path, "w", "utf-8")
    f.write(content)
    f.close()
    return path
