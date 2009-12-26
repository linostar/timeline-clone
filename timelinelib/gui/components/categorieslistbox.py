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


import wx

from timelinelib.gui.utils import sort_categories
from timelinelib.db.interface import TimelineIOError
from timelinelib.db.interface import STATE_CHANGE_CATEGORY


class CategoriesVisibleCheckListBox(wx.CheckListBox):
    # ClientData can not be used in this control
    # (see http://docs.wxwidgets.org/stable/wx_wxchecklistbox.html)
    # This workaround will not work if items are reordered

    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent)
        self.view = None
        self.Bind(wx.EVT_CHECKLISTBOX, self._checklistbox_on_checklistbox, self)

    def set_view(self, view):
        if self.view is not None:
            self.view.timeline.unregister(self._timeline_changed)
        self.view = view
        if self.view:
            self.view.timeline.register(self._timeline_changed)
            self._update_categories()
        else:
            self.Clear()
        
    def _checklistbox_on_checklistbox(self, e):
        i = e.GetSelection()
        self.view.event_rt_data.set_category_visible(self.categories[i], 
                                                     self.IsChecked(i))
        self.view.redraw_timeline()

    def _timeline_changed(self, state_change):
        if state_change == STATE_CHANGE_CATEGORY:
            self._update_categories()

    def _update_categories(self):
        try:
            self.categories = sort_categories(self.view.timeline.get_categories())
        except TimelineIOError, e:
            wx.GetTopLevelParent(self).handle_timeline_error(e)
        else:
            self.Clear()
            self.AppendItems([category.name for category in self.categories])
            for i in range(0, self.Count):
                if self.view.event_rt_data.category_visible(self.categories[i]):    
                    self.Check(i)
                self.SetItemBackgroundColour(i, self.categories[i].color)
