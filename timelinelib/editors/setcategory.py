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


from timelinelib.wxgui.utils import _display_error_message

 
class SetCategoryEditor(object):
    
    def __init__(self, view, timeline):
        self.view = view
        self.timeline = timeline

    def save(self):
        category = self.view.get_category()
        if self._category_is_given(category):
            self._save_category_in_events(category)
            self.view.close()
        else:
            _display_error_message(_("You must select a category!"))

    def _category_is_given(self, category):
        return category != None
    
    def _save_category_in_events(self, category):
        for event in self.timeline.events:
            if event.category == None:
                event.category = category

    def _events_without_category_exists(self):
        for event in self.timeline.events:
            if event.category == None:
                return True
        return False
    
        