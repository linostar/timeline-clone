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
        self.timeline = None
        self.Bind(wx.EVT_CHECKLISTBOX, self._checklistbox_on_checklistbox, self)

    def set_timeline(self, timeline):
        if self.timeline != None:
            self.timeline.unregister(self._timeline_changed)
        self.timeline = timeline
        if self.timeline:
            self.timeline.register(self._timeline_changed)
            self._update_categories()
        else:
            self.Clear()

    def _checklistbox_on_checklistbox(self, e):
        i = e.GetSelection()
        self.categories[i].visible = self.IsChecked(i)
        try:
            self.timeline.save_category(self.categories[i])
        except TimelineIOError, e:
            wx.GetTopLevelParent(self).handle_timeline_error(e)

    def _timeline_changed(self, state_change):
        if state_change == STATE_CHANGE_CATEGORY:
            self._update_categories()

    def _update_categories(self):
        try:
            self.categories = sort_categories(self.timeline.get_categories())
        except TimelineIOError, e:
            wx.GetTopLevelParent(self).handle_timeline_error(e)
        else:
            self.Clear()
            self.AppendItems([category.name for category in self.categories])
            for i in range(0, self.Count):
                if self.categories[i].visible:
                    self.Check(i)
                self.SetItemBackgroundColour(i, self.categories[i].color)
