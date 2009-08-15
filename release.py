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
Script that generates a source archive and does some checks.

Can be run from anywhere and will create a file xyz.zip in the directory from
which it is run.

The zipfile will contain a single directory, xyz, corresponding to the
directory in which this file exists.
"""

import sys
import glob
import os
import os.path
import shutil
from subprocess import call

# The root of the source archive corresponds to the directory in which this
# file is
ROOT_DIR = os.path.dirname(__file__)

# Make sure that we can import modules from the src directory
sys.path.insert(0, os.path.join(ROOT_DIR, "src"))

import about
import version

REL_NAME_ZIP = "%s-%s.zip" % (about.APPLICATION_NAME.lower(),
                              version.get_version())

if os.path.exists(REL_NAME_ZIP):
    print("Error: Archive '%s' already exists" % REL_NAME_ZIP)
    sys.exit()

print("Exporting from Mercurial")
cmd = ["hg", "archive",
       "-R", ROOT_DIR,
       "-t", "zip",
       "--exclude", ".hg*",
       REL_NAME_ZIP]
if call(cmd) != 0:
    print("Error: Could not export from Mercurial")
    sys.exit()

print("-----")

f = open(os.path.join(ROOT_DIR, "README"))
redme_first_line = f.readline()
f.close()
if not version.get_version() in redme_first_line:
    print("Warning: Version mismatch between README and version module")

if version.DEV:
    print("Warning: This is a development version")
