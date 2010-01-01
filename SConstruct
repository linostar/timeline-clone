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
SCons configuration file.
"""

env = Environment()

# Help

env.Help("""
Targets:

  mo     - compiled translations
  pot    - translation template
  tags   - tags file for Vim
  devdoc - html versions of developer documentation
  api    - source code API documentation
""")

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

# Gather a list with all source files

sources = []
for root, dirs, files in os.walk("timelinelib"):
    sources.extend([os.path.join(root, f) for f in files if f.endswith(".py")])

# Target: mo

languages = ["sv", "es", "de", "pt_BR", "pt", "ru", "ca", "he"]
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

tags = env.Command("timelinelib/tags", sources,
                   "$CTAGS --tag-relative=yes -f $TARGET $SOURCES")
env.Alias("tags", tags)

# Target: devdoc

def devdoc_convert(target, source, env):
    html_body = markdown.markdown(codecs.open(source[0].abspath, "r", "utf-8").read())
    # replace txt links with html links for local pages
    html_body = re.sub(r'(<a href="(html){0}.*?\.)txt(".*?</a>)', r"\1html\3", html_body)
    title = str(target[0])
    title_match = re.search(r"<h1>(.*?)</h1>", html_body)
    if title_match:
        title = title_match.group(1)
    html_template = """
    <html>
    <head>
    <title>%s</title>
    </head>
    <body>
    %s
    <hr>
    <center>
    <a href="index.html">Home</a>
    </center>
    </body>
    </html>
    """
    html = html_template % (title, html_body)
    codecs.open(target[0].abspath, "w", "utf-8").write(html)

for f in env.Glob("devdoc/*.txt"):
    html = env.Command(f.abspath[:-3] + "html", f, devdoc_convert)
    env.Alias("devdoc", html)

# Target: api

env["EPYDOCFLAGS"] = "--name Timeline --no-private --no-sourcecode"
api = env.Command("devdoc/api/index.html", sources,
                  "$EPYDOC $EPYDOCFLAGS -o $TARGET.dir $SOURCES")
env.Clean(api, "devdoc/api") # remove the whole directory
env.Alias("api", api)

# vim: syntax=python
