# Copyright (C) 2009, 2010, 2011  Rickard Lindberg, Roger Lindberg
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


import unittest
import os
import sys


def get_po_files(path):
    return [f for f in os.listdir(path) 
            if f[-3:] == ".po" ]


def parse_translations(lines):
    translations = []
    BEFORE = 0
    START = 1
    MSGID = 2
    MSGSTR = 3
    state = BEFORE
    sourceline = None
    msgid = None
    msgstr = None
    for line in lines:
        line = line.strip()
        if state == BEFORE:
            if line.startswith("#: "):
                state = START
                sourceline = line

        elif state == START:
            if line.startswith("msgid "):
                state = MSGID
                msgid = line[7:-1]
        elif state == MSGID:
            if line.startswith("msgstr "):
                state = MSGSTR
                msgstr = line[8:-1]
            else:
                msgid = msgid + line[1:-1]
        elif state == MSGSTR:
            if len(line) == 0:
                translations.append((sourceline, msgid, msgstr))
                state = BEFORE
                msgid = None
                msgstr = None
                sourceline = None
        
    return translations
    
    
def get_translations(po_file):
    f = open(po_file, "r")
    lines = f.read().split("\n")
    f.close()
    return parse_translations(lines)
    

def validate_translations(translations):
    errors = []
    for sourceline, msgid, msgstr in translations:
        if len(msgstr) > 0:
            if msgid.count("%s") != msgstr.count("%s"):
                errors.append((sourceline, msgid, msgstr))
    return errors
    
    
def get_invalid_translations(path):
    errors = []
    po_files = get_po_files(path)
    for po_file in po_files:
        translations = get_translations(os.path.join(path,po_file))
        err = validate_translations(translations)
        if len(err) > 0:
            errors.append((po_file, err))
    return errors
    

def report(errors):
    if len(errors) > 0:
        print "------------------------------------"
        print "!!!! Invalid translations found !!!!"
        print "------------------------------------"
        for po_file, errs in errors:
            print "PO file:", po_file
            print " "
            for sourceline, msgid, msgstr in errs:
                print "Src:", sourceline
                print "Id: ", msgid
                print "Str:", msgstr
                print " "
    else:
        print "No errors found"
    return len(errors) 
        

class TranslationsSpec(unittest.TestCase):

    def test_string_replacemnts_are_conserved(self):
        self.assertEqual(0, len(get_invalid_translations("po")))


if __name__ == '__main__':
    invalid_translations = get_invalid_translations("..\\po")
    report(invalid_translations)
    print "Press any key to continue:",
    raw_input()
    sys.exit(len(invalid_translations))
