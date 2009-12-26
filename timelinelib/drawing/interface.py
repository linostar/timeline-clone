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
Defines the interface that drawers should adhere to.
"""


class Drawer(object):
    """
    Draw timeline onto a device context and provide information about drawing.
    """

    def draw(self, dc, time_period, timeline, event_runtime_data):
        """
        Draw a representation of a timeline.

        - dc: used to do the actual drawing
        - time_period: what period of the timeline should be visible
        - timeline: which timeline to visualize
        - event_runtime_data: ViewProperties

        When the dc is temporarily stored in a class variable such as self.dc,
        this class variable must be deleted before the draw method ends.
        """

    def event_is_period(self, time_period):
        """
        Return True if the event time_period will make the event appear
        below the center line, as a period event.
        """
        return None
     
    def snap(self, time, snap_region=10):
        """Snap time to minor strip if within snap_region pixels."""
        return time

    def snap_selection(self, period_selection):
        """
        Return a tuple where the selection has been stretched to fit to minor
        strip.

        period_selection: (start, end)
        Return: (new_start, new_end)
        """
        return period_selection

    def event_at(self, x, y):
        """
        Return the event at pixel coordinate (x, y) or None if no event there.
        """
        return None

    def event_with_rect_at(self, x, y):
        """
        Return the event at pixel coordinate (x, y) and its rect in a tuple
        (event, rect) or None if no event there.
        """
        return None

    def event_rect_at(self, event):
        """
        Return the rect for the given event or None if no event isn't found.
        """
        return None
    
    def notify_events(self, notification, data):
        """
        Send notification to all visible events
        """
        

class ViewProperties(object):
    """
    Store non-persistent information about events.

    TODO: how to handle a method like `get_selected`? Should it return a list
          of id numbers or a list of events?
    """

    SELECTED_KEY = 0
    BALLOON_KEY = 1
    CATEGORY_VISIBLE_KEY = 2

    def __init__(self):
        self.data = {}
        self.period_selection = None
        self.draw_legend = True
        self.divider_position = 0.5
        self.preferred_period = None

    def is_selected(self, event):
        return self._id_in_list(event.id, ViewProperties.SELECTED_KEY)

    def clear_selected(self):
        self._clear_key(ViewProperties.SELECTED_KEY)

    def set_selected(self, event, is_selected=True):
        if is_selected:
            self._append_id_to_list(event.id, ViewProperties.SELECTED_KEY)
        else:
            self._remove_id_from_list(event.id, ViewProperties.SELECTED_KEY)

    def get_selected_event_ids(self):
        if self.data.has_key(ViewProperties.SELECTED_KEY):
            return self.data[ViewProperties.SELECTED_KEY]
        else:
            return []
        
    def has_balloon(self, event):
        return self._id_in_list(event.id, ViewProperties.BALLOON_KEY)

    def clear_balloons(self):
        self._clear_key(ViewProperties.BALLOON_KEY)

    def set_balloon(self, event, has_balloon=True):
        if has_balloon:
            self._append_id_to_list(event.id, ViewProperties.BALLOON_KEY)
        else:
            self._remove_id_from_list(event.id, ViewProperties.BALLOON_KEY)
        
    def category_visible(self, category):
        return self._id_in_list(category.id, 
                                ViewProperties.CATEGORY_VISIBLE_KEY)
    
    def set_category_visible(self, category, is_visible=True):
        if is_visible:
            self._append_id_to_list(category.id, 
                                    ViewProperties.CATEGORY_VISIBLE_KEY)
        else:
            self._remove_id_from_list(category.id, 
                                      ViewProperties.CATEGORY_VISIBLE_KEY)
        
    def _append_id_to_list(self, id, list_key):
        if self.data.has_key(list_key):
            if not id in self.data[list_key]:
                self.data[list_key].append(id)
        else:        
            self.data[list_key] = [id]

    def _remove_id_from_list(self, id, list_key):
        if self.data.has_key(list_key) and id in self.data[list_key]:
            self.data[list_key].remove(id)

    def _id_in_list(self, id, list_key):
        if self.data.has_key(list_key):
            return id in self.data[list_key]
        return False

    def _clear_key(self, key):
        try:
            del (self.data[key])
        except:
            pass
