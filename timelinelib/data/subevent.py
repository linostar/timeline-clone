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


from timelinelib.data.event import Event


class Subevent(Event):

    def __init__(self, time_type, start_time, end_time, text, category=None,
                 container=None, cid=-1):
        Event.__init__(self, time_type, start_time, end_time, text, category,
                       False, False, False)
        self.container = container
        if self.container != None:
            self.container_id = self.container.cid()
        else:
            self.container_id = cid

    def is_container(self):
        """Overrides parent method."""
        return False

    def is_subevent(self):
        """Overrides parent method."""
        return True

    def update_period(self, start_time, end_time):
        """Overrides parent method."""
        Event.update_period(self, start_time, end_time)
        self.container.update_container(self)

    def update_period_o(self, new_period):
        """Overrides parent method."""
        Event.update_period(self, new_period.start_time, new_period.end_time)
        self.container.update_container(self)

    def cid(self):
        return self.container_id

    def register_container(self, container):
        self.container = container
        self.container_id = container.cid()

    def clone(self):
        # Objects of type datetime are immutable.
        new_event = Subevent(self.get_time_type(), self.time_period.start_time,
                          self.time_period.end_time, self.text, self.category,
                          None, self.container_id)
        # Description is immutable
        new_event.set_data("description", self.get_data("description") )
        # Icon is immutable in the sense that it is never changed by our
        # application.
        new_event.set_data("icon", self.get_data("icon"))
        new_event.set_data("hyperlink", self.get_data("hyperlink"))
        return new_event
