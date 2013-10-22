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
        self.hscroll_amount = 0
        self.view_cats_individually = False

    def clear_db_specific(self):
        self.sticky_balloon_event_ids = []
        self.hovered_event = None
        self.selected_event_ids = []
        self.hidden_categories = []
        self.period_selection = None
        self.displayed_period = None

    def get_displayed_period(self):
        return self.displayed_period

    def filter_events(self, events):
        return [event for event in events if self._is_event_visible(event)]

    def _is_event_visible(self, event):
        if event.is_subevent():
            return (self.is_event_with_category_visible(event.category) and
                    self.is_event_with_category_visible(event.container.category))
        else:
            return self.is_event_with_category_visible(event.category)

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

    def set_displayed_period(self, period):
        self.displayed_period = period

    def get_selected_event_ids(self):
        return self.selected_event_ids[:]

    def is_category_visible(self, category):
        return category.id not in self.hidden_categories

    def is_event_with_category_visible(self, category):
        if category is None:
            return True
        elif self.view_cats_individually:
            return self.is_category_visible(category)
        else:
            return self._is_category_recursively_visible(category)

    def _is_category_recursively_visible(self, category):
        if self.is_category_visible(category):
            if category.parent is None:
                return True
            else:
                return self._is_category_recursively_visible(category.parent)
        else:
            return False

    def set_category_visible(self, category, is_visible=True):
        self.set_category_with_id_visible(category.id, is_visible)

    def set_category_with_id_visible(self, id, is_visible=True):
        if is_visible == True and id in self.hidden_categories:
            self.hidden_categories.remove(id)
        elif is_visible == False and not id in self.hidden_categories:
            self.hidden_categories.append(id)
