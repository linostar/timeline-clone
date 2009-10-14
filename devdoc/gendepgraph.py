"""
Writes a module dependency graph as a Graphviz (http://www.graphviz.org/) graph
on STDOUT.

Usage:

    python gendepgraph.py > depgraph.gv
    fdp -Tpng -odepgraph.png depgraph.gv
    eog depgraph.png

fdp is a program from the Graphviz package
eog is an image viewer on the GNOME platform

Instead of fdp you can try neato or twopi.
"""

import re
import os.path
import glob

MODULES = glob.glob("../src/*.py")
IMPORT_RE = r'^import ([^ \r\n]+)'
FROM_IMPORT_RE = r'^from ([^ ]+) import ([^ \r\n]+)'

COLORS = [
    "lightskyblue",
    "yellowgreen",
    "orange",
    "crimson",
    "cyan2",
    "goldenrod2",
    "green1",
    "hotpink3",
    "red",
    "blue",
    "maroon",
    "grey",
]

COLOR_ID = 0
def get_next_color():
    global COLOR_ID
    if COLOR_ID < len(COLORS):
        c = COLORS[COLOR_ID]
        COLOR_ID += 1
        return c
    return COLORS[-1]

cross_ref = {}

for module_name in MODULES:
    file = open(module_name)
    m = os.path.basename(module_name)[:-3]
    for line in file:
        match = re.search(IMPORT_RE, line)
        if match:
            mm = match.group(1)
            if cross_ref.has_key(m):
                cross_ref[m].append((mm, ""))
            else:
                cross_ref[m] = [(mm, "")]
        match = re.search(FROM_IMPORT_RE, line)
        if match:
            mm = match.group(1)
            mm2 = match.group(2)
            if cross_ref.has_key(m):
                cross_ref[m].append((mm, mm2))
            else:
                cross_ref[m] = [(mm, mm2)]
    file.close()

print "digraph"
print "{"
print "overlap=false;"
print "splines=true;"
for module in cross_ref.keys():
    c = get_next_color()
    print 'edge [color=%s]' % (c)
    for dep in cross_ref[module]:
        (mm, l) = dep
        if l:
            l = " [label=\"%s\"]" % l
            l = ""
        print '"%s" -> "%s"%s' % (module, mm, l)
for module in MODULES:
    m = os.path.basename(module)[:-3]
    print '"%s" [fillcolor=lightblue2, style=filled]' % (m)
print "}"
