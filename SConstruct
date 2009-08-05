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

def docbookhtml_builder(env):
    env["XMLTO"] = WhereIs("xmlto")
    if not env["XMLTO"]:
        print("xmlto not found. You will not be able to convert docbook files to html files.")
    convert_action = "$XMLTO" \
                     " -vv" \
                     " --stringparam chunker.output.encoding=UTF-8" \
                     " html-nochunks" \
                     " -o ${SOURCE.dir}" \
                     " $SOURCE"
    # -o option specified output directory. There is no way to specify output
    # file with the xmlto command. We therefore have to move the file in place
    # as a last step.
    move_action = Move("$TARGET", "${SOURCE.base}.html")
    env["BUILDERS"]["DocBookHtml"] = Builder(action=[convert_action,
                                                     move_action])

def pot_builder(env):
    env["XGETTEXT"] = WhereIs("xgettext")
    if not env["XGETTEXT"]:
        print("xgettext not found. You will not be able to extract pot files from source code.")
    env["XGETTEXTFLAGS"] = ""
    extract_action = "$XGETTEXT" \
                     " -o $TARGET" \
                     " $XGETTEXTFLAGS" \
                     " $SOURCES"
    env["BUILDERS"]["Pot"] = Builder(action=extract_action)

def mo_builder(env):
    env["MSGFMT"] = WhereIs("msgfmt")
    if not env["MSGFMT"]:
        print("msgfmt not found. You will not be able to create mo files.")
    convert_action = "$MSGFMT -o $TARGET $SOURCE"
    env["BUILDERS"]["Mo"] = Builder(action=convert_action)

def vimtags_builder(env):
    env["CTAGS"] = WhereIs("ctags")
    if not env["CTAGS"]:
        print("ctags not found. You will not be able to create vim tags file.")
    generate_action = "$CTAGS -f $TARGET $SOURCES"
    env["BUILDERS"]["VimTags"] = Builder(action=generate_action)

env = Environment(tools=["default", docbookhtml_builder, pot_builder,
                         mo_builder, vimtags_builder])

Export("env")

SConscript("manual/SConscript")
SConscript("po/SConscript")
SConscript("src/SConscript")
