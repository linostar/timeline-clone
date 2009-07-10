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
from subprocess import Popen
from subprocess import PIPE
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

def ignore(file):
    if os.path.basename(file).startswith("."):
        return True
    if os.path.basename(file).endswith(".pyc"):
        return True
    if os.path.basename(file).endswith(".zip"):
        return True
    return False

def generate_filelist(subpath=""):
    current_path = os.path.join(ROOT_DIR, subpath) or "."
    if not os.path.isdir(current_path):
        return [subpath]
    filelist = []
    for file in os.listdir(current_path):
        file_subpath = os.path.join(subpath, file)
        if not ignore(file_subpath):
            filelist.extend(generate_filelist(file_subpath))
        else:
            print("Ignoring %s" % file_subpath)
    return filelist

def copy_files(files):
    for path in files:
        dest = os.path.join(REL_NAME, os.path.dirname(path))
        if dest and not os.path.exists(dest):
            print("Creating directory %s" % dest)
            os.makedirs(dest)
        print("Copying %s" % path)
        shutil.copy(os.path.join(ROOT_DIR, path), dest)

if os.path.exists(REL_NAME):
    print("Error: Path already exists %s" % REL_NAME)
    sys.exit()

print("Making manual")
if call(["make", "-C", os.path.join(ROOT_DIR, "manual")]) != 0:
    print("Error: Could not make manual")
    sys.exit()

print("Creating directory %s" % REL_NAME)
os.mkdir(REL_NAME)

copy_files(generate_filelist())

print("Creating file %s" % REL_NAME_ZIP)
Popen(["zip", "-r", REL_NAME_ZIP, REL_NAME], stdout=PIPE).communicate()[0]

print("Deleting directory %s" % REL_NAME)
shutil.rmtree(REL_NAME)

print("-----")

if version.DEV:
    print("Warning: This is a development version")
