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
Script that generates a code review template.

Usage:
    cd path-to-my-hg-repo
    python tools/codereview.py rev [file]"

The code review is supposed to be sent as an email. The firs line contains the
subject line.

If file is not given, the template will be written to stdout.
"""

import sys
import os
import re
from subprocess import Popen, PIPE

def exit(msg):
    print msg
    raise SystemExit()

if len(sys.argv) != 2 and len(sys.argv) != 3:
    exit("Usage: python codereview.py rev [file]")

rev = sys.argv[1]

info_process = Popen(["hg", "log", "-r", rev], stdout=PIPE)
export_process = Popen(["hg", "export", rev], stdout=PIPE,
                       universal_newlines=True)

info = info_process.communicate()[0]
diff = export_process.communicate()[0]

if info_process.returncode != 0 or export_process.returncode != 0:
    exit("Error while exporting diff")

summary = re.search(r"^summary:\s+(.*)$", info, re.MULTILINE).group(1)

f = sys.stdout
if len(sys.argv) == 3:
    f = open(sys.argv[2], "w")
f.write("Code review: %s (rev %s)%s" % (summary, rev, "\n"))
f.write("\n")
for line in diff.split("\n"):
    f.write("> %s%s" % (line, "\n"))
f.close()
