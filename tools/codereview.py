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
