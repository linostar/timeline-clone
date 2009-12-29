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
Implementation of the observer design pattern.

To make an object observable, inherit from the Observable class.
"""


class Observable(object):
    """
    Base class for objects that would like to be observable.

    The function registered should take one argument which represent the state
    change. It can be any object.
    """

    def __init__(self):
        self.observers = []

    def register(self, fn):
        self.observers.append(fn)

    def unregister(self, fn):
        if fn in self.observers:
            self.observers.remove(fn)

    def _notify(self, state_change):
        for fn in self.observers:
            fn(state_change)
