# Copyright (C) 2009, 2010  Rickard Lindberg, Roger Lindberg
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

    def draw(self, dc, timeline, view_properties):
        """
        Draw a representation of a timeline.

        The dc is used to do the actual drawing. The timeline is used to get
        the events to visualize. The view properties contains information like
        which events are selected in the view we are drawing for and what
        period is currently displayed.

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

    def is_balloon_at(self, event, x, y):
        """
        Return True if a balloon for event is drawn at (x, y), otherwise False.
        """

    
class ViewProperties(object):
    """
    Store properties of a view.

    Some timeline databases support storing some of these view properties
    together with the data.
    """

    def __init__(self):
        self.sticky_balloon_event_ids = []
        self.hovered_event = None
        self.selected_event_ids = []
        self.hidden_categories = []
        self.period_selection = None
        self.show_legend = True
        self.divider_position = 0.5
        self.displayed_period = None

    def clear_db_specific(self):
        self.sticky_balloon_event_ids = []
        self.hovered_event = None
        self.selected_event_ids = []
        self.hidden_categories = []
        self.period_selection = None
        self.displayed_period = None

    def filter_events(self, events):
        def category_visible(cat):
            if cat is None:
                return True
            elif self.category_visible(cat) == True:
                return category_visible(cat.parent)
            else:
                return False
        return [e for e in events if category_visible(e.category)]

    def is_selected(self, event):
        return event.id in self.selected_event_ids

    def clear_selected(self):
        self.selected_event_ids = []

    def event_is_hovered(self, event):
        return (self.hovered_event is not None and
                event.id == self.hovered_event.id)

    def event_has_sticky_balloon(self, event):
        return event.id in self.sticky_balloon_event_ids

    def set_event_has_sticky_balloon(self, event, has_sticky=True):
        if has_sticky == True and not event.id in self.sticky_balloon_event_ids:
            self.sticky_balloon_event_ids.append(event.id)
        elif has_sticky == False and event.id in self.sticky_balloon_event_ids:
            self.sticky_balloon_event_ids.remove(event.id)

    def set_selected(self, event, is_selected=True):
        if is_selected == True and not event.id in self.selected_event_ids:
            self.selected_event_ids.append(event.id)
        elif is_selected == False and event.id in self.selected_event_ids:
            self.selected_event_ids.remove(event.id)

    def get_selected_event_ids(self):
        return self.selected_event_ids[:]
        
    def category_visible(self, category):
        return not category.id in self.hidden_categories
    
    def set_category_visible(self, category, is_visible=True):
        if is_visible == True and category.id in self.hidden_categories:
            self.hidden_categories.remove(category.id)
        elif is_visible == False and not category.id in self.hidden_categories:
            self.hidden_categories.append(category.id)
