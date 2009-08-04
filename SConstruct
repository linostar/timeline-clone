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
    convert_action = "xmlto" \
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
    extract_action = "xgettext" \
                     " -o $TARGET" \
                     " --copyright-holder='Rickard Lindberg'" \
                     " --package-name=Timeline" \
                     " --package-version=0.4.0" \
                     " $SOURCES"
    env["BUILDERS"]["Pot"] = Builder(action=extract_action)

def mo_builder(env):
    convert_action = "msgfmt -o $TARGET $SOURCE"
    env["BUILDERS"]["Mo"] = Builder(action=convert_action)

env = Environment(tools=[docbookhtml_builder, pot_builder, mo_builder])
Export("env")

SConscript("manual/SConscript")
SConscript("po/SConscript")
