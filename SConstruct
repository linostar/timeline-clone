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

# The builders instruct scons how to build the documentation and the language
# related stuff. These commands might differ on different platforms. This is
# the place to change them with a check like if "win32" in sys.platform: ..."

def docbooksinglehtml_builder(env):
    env["XMLLINT"] = WhereIs("xmllint")
    env["XSLTPROC"] = WhereIs("xsltproc")
    verify_action = "$XMLLINT --xinclude --postvalid --nonet --noent --noout" \
                    " $SOURCE"
    convert_action = "$XSLTPROC $XSLTPROCFLAGS --nonet --xinclude -o $TARGET" \
                     " http://docbook.sourceforge.net/release/xsl/current/html/docbook.xsl" \
                     " $SOURCE"
    env["BUILDERS"]["DocBookSingleHtml"] = Builder(action=[verify_action,
                                                           convert_action])

def pot_builder(env):
    env["XGETTEXT"] = WhereIs("xgettext")
    env["XGETTEXTFLAGS"] = ""
    extract_action = "$XGETTEXT -o $TARGET $XGETTEXTFLAGS $SOURCES"
    env["BUILDERS"]["Pot"] = Builder(action=extract_action)

def mo_builder(env):
    env["MSGFMT"] = WhereIs("msgfmt")
    convert_action = "$MSGFMT -o $TARGET $SOURCE"
    env["BUILDERS"]["Mo"] = Builder(action=convert_action)

def vimtags_builder(env):
    env["CTAGS"] = WhereIs("ctags")
    generate_action = "$CTAGS --tag-relative=yes -f $TARGET $SOURCES"
    env["BUILDERS"]["VimTags"] = Builder(action=generate_action)

env = Environment(tools=["default", docbooksinglehtml_builder, pot_builder,
                         mo_builder, vimtags_builder])

Export("env")

SConscript("po/SConscript")
SConscript("timelinelib/SConscript")

### devdoc

def devdoc_convert(target, source, env):
    import markdown
    import codecs
    import re
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

### api doc

src = env.Glob("timelinelib/*.py") + env.Glob("timelinelib/*/*.py") + env.Glob("timelinelib/*/*/*.py")

api = env.Command("dummy", src,
                  "epydoc -o devdoc/api $SOURCES")
env.Clean("api", api)
env.Alias("api", api)

# vim: syntax=python
