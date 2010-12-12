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
Script that generates a source archive and does some checks.

Can be run from anywhere and will create a file timeline-x.y.z.zip in the
directory from which it is run.

The zip file contains a single directory, timeline-x.y.z, corresponding to the
root directory.
"""


import sys
import glob
import os
import os.path
import shutil
import re
from subprocess import call
from datetime import datetime
import time
import codecs

# The root of the source archive corresponds to the parent directory of the
# directory in which this file is
ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")

# Make sure that we can import timelinelib
sys.path.insert(0, ROOT_DIR)

import timelinelib.about as about
import timelinelib.version as version


VERSION_STR = version.get_version()
REL_NAME_ZIP = "%s-%s.zip" % (about.APPLICATION_NAME.lower(), VERSION_STR)
MANPAGE = os.path.join(ROOT_DIR, "man", "man1", "timeline.1")
README = os.path.join(ROOT_DIR, "README")
CHANGES = os.path.join(ROOT_DIR, "CHANGES")
AUTHORS = os.path.join(ROOT_DIR, "AUTHORS")


def text_in_file(file, text):
    f = codecs.open(file, "r", "utf-8")
    contents = f.read()
    f.close()
    return text in contents

def read_first_line(file):
    f = codecs.open(file, "r", "utf-8")
    first_line = f.readline()
    f.close()
    return first_line

def text_in_first_line(file, text):
    return text in read_first_line(file)

def version_in_first_line(file):
    return text_in_first_line(file, VERSION_STR)

def get_all_authors():
    def is_author(text):
        return text and ":" not in text
    def extract_author(text):
        first_left_paren_pos = text.find("(")
        if first_left_paren_pos == -1:
            return text.strip()
        return text[0:first_left_paren_pos-1].strip()
    source = about.DEVELOPERS + about.TRANSLATORS + about.ARTISTS
    return [extract_author(x) for x in source if is_author(x)]

def read_release_date():
    rel_line = read_first_line(CHANGES)
    bfr_str = "released on "
    date_str = rel_line[rel_line.find(bfr_str)+len(bfr_str):].strip()
    release_date = datetime.strptime(date_str, "%d %B %Y")
    return release_date


if os.path.exists(REL_NAME_ZIP):
    print("Error: Archive '%s' already exists" % REL_NAME_ZIP)
    sys.exit()

if not "check" in sys.argv:
    print("Exporting from Mercurial")
    cmd = ["hg", "archive",
           "-R", ROOT_DIR,
           "-t", "zip",
           "--exclude", "%s/.hgignore" % (ROOT_DIR or "."),
           "--exclude", "%s/.hgtags" % (ROOT_DIR or "."),
           "--exclude", "%s/.hg_archival.txt" % (ROOT_DIR or "."),
           REL_NAME_ZIP]
    if call(cmd) != 0:
        print("Error: Could not export from Mercurial")
        sys.exit()

print("Running unit tests")
unittest_ret = call(["python", "%s/tests/run.py" % (ROOT_DIR or "."), "quiet"])

print("Running specs")
spec_ret = call(["python", "%s/specs/execute.py" % (ROOT_DIR or "."), "quiet"])

print
print("Warnings:")

if unittest_ret != 0:
    print("* Failed unit test")

if spec_ret != 0:
    print("* Failed spec")

if version.DEV:
    print("* This is a development version")

if not version_in_first_line(README):
    print("* Version mismatch between README and version module")

if not version_in_first_line(CHANGES):
    print("* Version mismatch between CHANGES and version module")

if not version_in_first_line(MANPAGE):
    print("* Version mismatch between manpage and version module")

if not text_in_first_line(MANPAGE, read_release_date().strftime("%B %Y")):
    print("* Date mismatch between manpage and release date in CHANGES")

for author in get_all_authors():
    if not text_in_file(AUTHORS, author):
        print("* '%s' not in AUTHORS" % author)
