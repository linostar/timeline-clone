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

REL_NAME = "%s-%s" % (about.APPLICATION_NAME.lower(), version.get_version())
REL_NAME_ZIP = "%s.zip" % REL_NAME

if os.path.exists(REL_NAME):
    print("Error: Path already exists %s" % REL_NAME)
    sys.exit()

if os.path.exists(REL_NAME_ZIP):
    print("Error: Package already exists %s" % REL_NAME_ZIP)
    sys.exit()

print("Exporting from SVN")
if call(["svn", "export", ROOT_DIR, REL_NAME]) != 0:
    print("Error: Could not export from SVN")
    sys.exit()

print("Making manual")
if call(["make", "-C", os.path.join(ROOT_DIR, "manual")]) != 0:
    print("Error: Could not make manual")
    sys.exit()

# The html version of the manual is not versioned controlled, but we would like
# to include it in the source release anyway so that users running from source
# do not need to make it themselves.
print("Copying manual to release")
if call(["cp", os.path.join(ROOT_DIR, "manual", "manual.html"),
         os.path.join(REL_NAME, "manual")]) != 0:
    print("Error: Could not copy manual")
    sys.exit()

print("Creating file %s" % REL_NAME_ZIP)
if call(["zip", "-r", REL_NAME_ZIP, REL_NAME]) != 0:
    print("Error: Could not create archive")
    sys.exit()

print("Deleting directory %s" % REL_NAME)
shutil.rmtree(REL_NAME)

print("-----")

if version.DEV:
    print("Warning: This is a development version")
