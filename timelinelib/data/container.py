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


class Container(Event):

    def __init__(self, time_type, start_time, end_time, text, category=None,
                 cid=-1):
        Event.__init__(self, time_type, start_time, end_time, text, category,
                       False, False, False)
        self.container_id = cid
        self.events = []
        import timelinelib.db.strategies
        self.strategy = timelinelib.db.strategies.DefaultContainerStrategy(self)

    def is_container(self):
        return True

    def is_subevent(self):
        return False

    def cid(self):
        return self.container_id

    def set_cid(self, cid):
        self.container_id = cid

    def register_subevent(self, subevent):
        self.strategy.register_subevent(subevent)

    def unregister_subevent(self, subevent):
        self.strategy.unregister_subevent(subevent)

    def update_container(self, subevent):
        self.strategy.update(subevent)

    def update_properties(self, text, category=None):
        self.text = text
        self.category = category

    def clone(self):
        # Objects of type datetime are immutable.
        new_event = Container(self.get_time_type(), self.time_period.start_time,
                          self.time_period.end_time, self.text, self.category,
                          self.container_id)
        # Description is immutable
        new_event.set_data("description", self.get_data("description") )
        # Icon is immutable in the sense that it is never changed by our
        # application.
        new_event.set_data("icon", self.get_data("icon"))
        new_event.set_data("hyperlink", self.get_data("hyperlink"))
        return new_event
