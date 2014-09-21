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


from xml.sax.saxutils import escape as xmlescape
import base64
import StringIO

import wx

from timelinelib.db.utils import safe_write
from timelinelib.meta.version import get_version


ENCODING = "utf-8"
INDENT1 = "  "
INDENT2 = "    "
INDENT3 = "      "


def export_db_to_timeline_xml(db, path):
    Exporter(db).export(path)


def wrap_in_tag(func, name, indent=""):
    def wrapper(*args, **kwargs):
        file = args[1] # 1st argument is self, 2nd argument is file
        file.write(indent)
        file.write("<")
        file.write(name)
        file.write(">\n")
        func(*args, **kwargs)
        file.write(indent)
        file.write("</")
        file.write(name)
        file.write(">\n")
    return wrapper


class Exporter(object):

    def __init__(self, db):
        self.db = db

    def export(self, path):
        safe_write(path, ENCODING, self._write_xml_doc)

    def _time_string(self, time):
        return self.db.get_time_type().time_string(time)

    def _write_xml_doc(self, file):
        file.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
        self._write_timeline(file)

    def _write_timeline(self, file):
        write_simple_tag(file, "version", get_version(), INDENT1)
        write_simple_tag(file, "timetype", self.db.get_time_type().get_name(), INDENT1)
        self._write_categories(file)
        self._write_events(file)
        self._write_view(file)
    _write_timeline = wrap_in_tag(_write_timeline, "timeline")

    def _write_categories(self, file):
        def write_with_parent(categories, parent):
            for cat in categories:
                if cat.get_parent() == parent:
                    self._write_category(file, cat)
                    write_with_parent(categories, cat)
        write_with_parent(self.db.get_categories(), None)
    _write_categories = wrap_in_tag(_write_categories, "categories", INDENT1)

    def _write_category(self, file, cat):
        write_simple_tag(file, "name", cat.get_name(), INDENT3)
        write_simple_tag(file, "color", color_string(cat.get_color()), INDENT3)
        write_simple_tag(file, "font_color", color_string(cat.get_font_color()), INDENT3)
        if cat.get_parent():
            write_simple_tag(file, "parent", cat.get_parent().get_name(), INDENT3)
    _write_category = wrap_in_tag(_write_category, "category", INDENT2)

    def _write_events(self, file):
        all_events = self.db.get_all_events()
        subevents = [event for event in all_events if event.is_subevent()]
        events = [event for event in all_events if not event.is_subevent()]
        events.extend(subevents)
        for evt in events:
            self._write_event(file, evt)
    _write_events = wrap_in_tag(_write_events, "events", INDENT1)

    def _write_event(self, file, evt):
        write_simple_tag(file, "start",
                         self._time_string(evt.get_time_period().start_time), INDENT3)
        write_simple_tag(file, "end",
                         self._time_string(evt.get_time_period().end_time), INDENT3)
        if evt.is_container():
            write_simple_tag(file, "text", "[%d]%s " % (evt.cid(), evt.text), INDENT3)
        elif evt.is_subevent():
            write_simple_tag(file, "text", "(%d)%s " % (evt.cid(), evt.text), INDENT3)
        else:
            text = evt.text
            if self._text_starts_with_container_tag(evt.text):
                text = self._add_leading_space_to_text(evt.text)
            write_simple_tag(file, "text", text, INDENT3)
        if evt.get_data("progress") is not None:
            write_simple_tag(file, "progress", "%s" % evt.get_data("progress"), INDENT3)
        write_simple_tag(file, "fuzzy", "%s" % evt.get_fuzzy(), INDENT3)
        write_simple_tag(file, "locked", "%s" % evt.get_locked(), INDENT3)
        write_simple_tag(file, "ends_today", "%s" % evt.get_ends_today(), INDENT3)
        if evt.category is not None:
            write_simple_tag(file, "category", evt.category.get_name(), INDENT3)
        if evt.get_data("description") is not None:
            write_simple_tag(file, "description", evt.get_data("description"), INDENT3)
        alert = evt.get_data("alert")
        if alert is not None:
            write_simple_tag(file, "alert", alert_string(self.db.get_time_type(), alert),
                             INDENT3)
        hyperlink = evt.get_data("hyperlink")
        if hyperlink is not None:
            write_simple_tag(file, "hyperlink", hyperlink, INDENT3)
        if evt.get_data("icon") is not None:
            icon_text = icon_string(evt.get_data("icon"))
            write_simple_tag(file, "icon", icon_text, INDENT3)
    _write_event = wrap_in_tag(_write_event, "event", INDENT2)

    def _text_starts_with_container_tag(self, text):
        return text[0] in ('(', '[')

    def _add_leading_space_to_text(self, text):
        return " %s" % text

    def _write_view(self, file):
        if self.db.get_displayed_period() is not None:
            self._write_displayed_period(file)
        self._write_hidden_categories(file)
    _write_view = wrap_in_tag(_write_view, "view", INDENT1)

    def _write_displayed_period(self, file):
        period = self.db.get_displayed_period()
        write_simple_tag(file, "start",
                         self._time_string(period.start_time), INDENT3)
        write_simple_tag(file, "end",
                         self._time_string(period.end_time), INDENT3)
    _write_displayed_period = wrap_in_tag(_write_displayed_period,
                                          "displayed_period", INDENT2)

    def _write_hidden_categories(self, file):
        for cat in self.db.get_hidden_categories():
            write_simple_tag(file, "name", cat.get_name(), INDENT3)
    _write_hidden_categories = wrap_in_tag(_write_hidden_categories,
                                           "hidden_categories", INDENT2)


def write_simple_tag(file, name, content, indent=""):
    file.write(indent)
    file.write("<")
    file.write(name)
    file.write(">")
    file.write(xmlescape(content))
    file.write("</")
    file.write(name)
    file.write(">\n")


def color_string(color):
    return "%i,%i,%i" % color


def icon_string(bitmap):
    output = StringIO.StringIO()
    image = wx.ImageFromBitmap(bitmap)
    image.SaveStream(output, wx.BITMAP_TYPE_PNG)
    return base64.b64encode(output.getvalue())


def alert_string(time_type, alert):
    time, text = alert
    time_string = time_type.time_string(time)
    return "%s;%s" % (time_string, text)
