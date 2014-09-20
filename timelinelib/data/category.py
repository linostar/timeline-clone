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


class Category(object):

    # NOTE: The visible flag of categories should not be used any longer.
    # Visibility of categories are now managed in ViewProperties. However some
    # timeline databases still use this flag to manage the saving. This flag
    # should be removed when we can.

    def __init__(self, name, color, font_color, visible, parent=None):
        self.id = None
        self.name = name
        self.color = color
        if font_color is None:
            self.font_color = (0, 0, 0)
        else:
            self.font_color = font_color
        self.visible = visible
        self.parent = parent

    def has_id(self):
        return self.id is not None

    def set_id(self, id):
        self.id = id

    def clone(self):
        clone = Category(self.name, self.color, self.font_color, self.visible,
                         self.parent)
        return clone

    def __repr__(self):
        return "Category<id=%r, name=%r, color=%r, font_color=%r, visible=%r>" % (
            self.id, self.name, self.color, self.font_color, self.visible)

    def __eq__(self, other):
        return (isinstance(other, Category) and
                self.id == other.id and
                self.name == other.name and
                self.color == other.color and
                self.font_color == other.font_color and
                self.visible == other.visible)

    def __nq__(self, other):
        return (not (self == other))


def sort_categories(categories):
    sorted_categories = list(categories)
    sorted_categories.sort(cmp, lambda x: x.name.lower())
    return sorted_categories


def clone_categories_list(categories):
    cloned_list = []
    clones = {}
    for category in categories:
        clone = category.clone()
        clone.id = category.id
        cloned_list.append(clone)
        clones[category] = clone
    for category in cloned_list:
        if category.parent is not None:
            category.parent = clones[category.parent]
    return (cloned_list, clones)
