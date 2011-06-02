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


from timelinelib.db.objects import Event
from timelinelib.db.objects import TimePeriod


class EventEditor(object):

    def __init__(self, view, db, start, end, event):
        self.view = view
        self.db = db
        self.event = event
        if self.event != None:
            self.start = self.event.time_period.start_time
            self.end = self.event.time_period.end_time
            self.name = self.event.text
            self.category = self.event.category
            self.fuzzy = self.event.fuzzy
            self.locked = self.event.locked
            self.ends_today = self.event.ends_today
        else:
            self.start = start
            self.end = end
            self.name = ""
            self.category = None
            self.fuzzy = False
            self.locked = False
            self.ends_today = False
        if start is None:
            start = self.db.get_time_type().now()
        if end is None:
            end = self.db.get_time_type().now()
        
    def initialize(self):
        if self.event != None:
            self.view.set_event_data(self.event.data)
        self.view.set_start(self.start)
        self.view.set_end(self.end)
        self.view.set_name(self.name)
        self.view.set_category(self.category)
        self.view.set_show_period(self.end > self.start)
        self.view.set_show_time(self._event_has_nonzero_time())
        self.view.set_show_add_more(self.event == None)
        self.view.set_fuzzy(self.fuzzy)
        self.view.set_locked(self.locked)
        self.view.set_ends_today(self.ends_today)
        if self.start != self.end:
            self.view.set_focus("text")
        else:
            self.view.set_focus("start")

    def create_or_update_event(self):
        try:
            self._get_and_verify_input()
            self._save_event()
            return True
        except ValueError, ex:
            return False
        
    def clear(self):
        self.name = ""
        self.event = None
        self.view.set_name(self.name)
        self.view.set_focus("start")

    def _get_and_verify_input(self):
        self.name = self._validate_and_save_name(self.view.get_name())
        self.fuzzy = self.view.get_fuzzy()
        self.locked = self.view.get_locked()
        self.ends_today = self.view.get_ends_today()
        self.category = self.view.get_category()
        start = self.view.get_start()
        if self._dialog_has_signalled_invalid_input(start):
            raise ValueError()
        end = self.view.get_end()
        if self._dialog_has_signalled_invalid_input(end):
            raise ValueError()
        if self.locked:
            self._verify_that_time_has_not_been_changed(start, end)
        self.start = self._validate_and_save_start(self.view.get_start())
        self.end = self._validate_and_save_end(self.view.get_end())
        
    def _dialog_has_signalled_invalid_input(self, time):
        return time == None 
   
    def _verify_that_time_has_not_been_changed(self, start, end):
        self._exception_if_start_has_changed(start)
        if not self.ends_today:
            self._exception_if_end_has_changed(end)
    
    def _exception_if_start_has_changed(self, start):
        if self.start != start:
            self.view.set_start(self.start)
            self._exception_when_start_or_end_has_changed()

    def _exception_if_end_has_changed(self, end):
        if self.end != end:
            self.view.set_end(self.end)
            self._exception_when_start_or_end_has_changed()

    def _exception_when_start_or_end_has_changed(self):
        error_message = _("You can't change time when the Event is locked")
        self.view.display_invalid_start(error_message)
        raise ValueError()
        
    def _save_event(self):
        if self.event == None:
            self.event = Event(self.db, self.start, self.end, self.name, 
                               self.category, self.fuzzy, self.locked, 
                               self.ends_today)
        else:
            self.event.update(self.start, self.end, self.name, 
                              self.category, self.fuzzy, self.locked, 
                              self.ends_today)
        self.event.data = self.view.get_event_data()
        self._save_event_to_db()
        
    def _validate_and_save_start(self, start):
        if start == None:
            raise ValueError()
        return start

    def _validate_and_save_end(self, end):
        if end == None:
            raise ValueError()
        if end < self.start:
            self.view.display_invalid_start(_("End must be > Start"))
            raise ValueError()
        return end

    def _validate_and_save_name(self, name):
        if name == "":
            msg = _("Field '%s' can't be empty.") % _("Text")
            self.view.display_invalid_name(msg)
            raise ValueError()
        return name
        
    def _save_event_to_db(self):
        try:
            self.db.save_event(self.event)
        except Exception, e:
            self.view.display_db_exception(e)
        
    def _event_has_nonzero_time(self):
        try:
            time_type = self.db.get_time_type()
            time_period = TimePeriod(time_type, self.start, self.end)
            return time_period.has_nonzero_time()
        except Exception:
            return False
