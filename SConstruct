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
SCons configuration file.
"""

import os

env = Environment()

# Help

env.Help("""
Targets:

  mo      - compiled translations
  pot     - translation template
  tags    - tags file for the Vim text editor
  hacking - html version of HACKING
  api     - source code API documentation
""")

# Import environment variables

for env_var in ["PYTHONPATH"]:
    if os.environ.has_key(env_var):
        env["ENV"][env_var] = os.environ[env_var]

# Find paths to programs and print warning messages if not found

env["MSGFMT"] = WhereIs("msgfmt")
env["XGETTEXT"] = WhereIs("xgettext")
env["CTAGS"] = WhereIs("ctags")
env["EPYDOC"] = WhereIs("epydoc")

if not env["MSGFMT"]:
    print "Warning: msgfmt not found, can't generate mo files"

if not env["XGETTEXT"]:
    print "Warning: xgettext not found, can't generate pot file"

if not env["CTAGS"]:
    print "Warning: ctags not found, can't generate tags file"

if not env["EPYDOC"]:
    print "Warning: epydoc not found, can't generate api documentation"

# Import modules that we need

try:
    import markdown
except ImportError:
    print "Warning: markdown Python module not found, can't generate developer documentation"

import os
import os.path
import codecs
import re

# Helper functions

def find_py_files_in(path):
    py_files = []
    for root, dirs, files in os.walk(path):
        py_files += [os.path.join(root, f) for f in files if f.endswith(".py")]
    return py_files

# Gather a list with all source files

sources = find_py_files_in("timelinelib")

# Target: mo

languages = [os.path.basename(x)[:-3] for x in env.Glob("po/*.po", strings=True)]
for language in languages:
    target = "po/%s/LC_MESSAGES/timeline.mo" % language
    env.Alias("mo", env.Command(target, "po/%s.po" % language,
                                '"$MSGFMT" -o $TARGET $SOURCE'))
    env.Clean(target, "po/"+language) # Removed the folder

# Target: pot

env["XGETTEXTFLAGS"] = " --copyright-holder=\"Rickard Lindberg\"" \
                       " --package-name=Timeline" \
                       " --add-comments=TRANSLATORS"
pot = env.Command("po/timeline.pot", sources,
                  '"$XGETTEXT" -o $TARGET $XGETTEXTFLAGS $SOURCES')
env.Alias("pot", pot)

# Target: tags

tags = env.Command("tags",
                   sources + find_py_files_in("specs") + find_py_files_in("tests"),
                   "$CTAGS --python-kinds=-i --tag-relative=yes --extra=+f -f $TARGET $SOURCES")
env.Alias("tags", tags)

# Target: hacking

def markdown_convert(target, source, env):
    html_body = markdown.markdown(codecs.open(source[0].abspath, "r", "utf-8").read())
    title = str(target[0])
    html_template = """
    <html>
    <head>
    <title>%s</title>
    </head>
    <body>
    %s
    </body>
    </html>
    """
    html = html_template % (title, html_body)
    codecs.open(target[0].abspath, "w", "utf-8").write(html)

html = env.Command("HACKING.html", "HACKING", markdown_convert)
env.Alias("hacking", html)

# Target: api

env["EPYDOCFLAGS"] = "--name Timeline --no-private --no-sourcecode"
api = env.Command("api/index.html", sources,
                  "$EPYDOC $EPYDOCFLAGS -o $TARGET.dir $SOURCES")
env.Clean(api, "api") # remove the whole directory
env.Alias("api", api)

# vim: syntax=python
