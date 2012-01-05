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


from timelinelib.db.interface import ContainerStrategy


class DefaultContainerStrategy(ContainerStrategy):
    
    def __init__(self, container):
        ContainerStrategy.__init__(self, container)
        
    def register_subevent(self, subevent):
        if subevent not in self.container.events:
            self.container.events.append(subevent)
            subevent.register_container(self.container)
            if len(self.container.events) == 1:
                self._set_time_period()
            else:
                self._adjust_time_period(subevent)

    def unregister_subevent(self, subevent):
        if subevent not in self.container.events:
            return
        self.container.events.remove(subevent)
        self._set_time_period()

    def update(self, subevent):
        self.unregister_subevent(subevent)
        self.register_subevent(subevent)
        self._set_time_period()
        
    def _set_time_period(self):
        """
        The container time period starts where the subevent with the earliest
        start time, starts, and it ends where the subevent whith the latest end 
        time ends.
           Subevents   +------+  +--------+    +--+
           Container   +--------------------------+
        """
        if len(self.container.events) == 0:
            return
        self._set_start_time(self.container.events[0]) 
        self._set_end_time(self.container.events[0])
        for event in self.container.events:
            if self._container_starts_after_event(event):
                self._set_start_time(event)
            if self._container_ends_before_event(event):
                self._set_end_time(event)

    def _container_starts_after_event(self, subevent):
        return (self.container.time_period.start_time > 
                subevent.time_period.start_time)

    def _container_ends_before_event(self, event):
        return (self.container.time_period.end_time < 
                event.time_period.end_time)
        
    def _set_start_time(self, event):
        self.container.time_period.start_time = event.time_period.start_time

    def _set_end_time(self, event):
        self.container.time_period.end_time = event.time_period.end_time
         
    def _adjust_time_period(self, subevent):
        """
        If the event to be added to the container overlaps any other
        event in the container or if the new event is outside of the 
        container time period the container time period must be adjusted.
        """
        delta = self._subevent_start_overlaps_other_event(subevent) 
        if delta:
            self._adjust_front_events(subevent, delta)

        delta = self._subevent_totally_overlaps_other_event(subevent) 
        if delta:
            self._adjust_back_events(subevent, delta)
        else:
            delta = self._subevent_end_overlaps_other_event(subevent) 
            if delta:
                self._adjust_back_events(subevent, delta)
        if subevent.time_period.start_time < self.container.time_period.start_time:
            self._set_start_time(subevent)
        if subevent.time_period.end_time > self.container.time_period.end_time:
            self._set_end_time(subevent)

    def _subevent_totally_overlaps_other_event(self, subevent):
        delta = None
        delta_start = None
        for event in self.container.events:
            if event == subevent:
                continue
            if ((event.time_period.start_time > subevent.time_period.start_time and
                 event.time_period.end_time < subevent.time_period.end_time) or 
                (event.time_period.start_time == subevent.time_period.start_time)):
                if delta == None or delta_start < event.time_period.start_time: 
                    delta = subevent.time_period.end_time - event.time_period.start_time
                    delta_start = event.time_period.start_time 
        return delta
             
    def _subevent_start_overlaps_other_event(self, subevent):
        for event in self.container.events:
            if event == subevent:
                continue
            if (event.time_period.start_time < subevent.time_period.start_time and
                event.time_period.end_time > subevent.time_period.start_time):
                delta = event.time_period.end_time - subevent.time_period.start_time 
                return delta
        return None

    def _subevent_end_overlaps_other_event(self, subevent):
        for event in self.container.events:
            if event == subevent:
                continue
            if (event.time_period.start_time < subevent.time_period.end_time and
                event.time_period.end_time > subevent.time_period.end_time):
                delta = subevent.time_period.end_time - event.time_period.start_time 
                return delta
        return None

    def _adjust_front_events(self, subevent, delta):
        for event in self.container.events:
            if event == subevent:
                continue
            if event.time_period.start_time < subevent.time_period.start_time:
                start = event.time_period.start_time - delta
                end = event.time_period.end_time - delta
                event.time_period.start_time = start
                event.time_period.end_time = end
                if self.container.time_period.start_time > start:
                    self.container.time_period.start_time = start
                    
    def _adjust_back_events(self, subevent, delta):
        for event in self.container.events:
            if event == subevent:
                continue
            if event.time_period.start_time >= subevent.time_period.start_time:
                start = event.time_period.start_time + delta
                end = event.time_period.end_time + delta
                event.time_period.start_time = start
                event.time_period.end_time = end
                if self.container.time_period.end_time < end:
                    self.container.time_period.end_time = end
