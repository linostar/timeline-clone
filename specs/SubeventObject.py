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


import unittest

from specs.utils import a_subevent_with
from specs.utils import a_container_with


class describe_subevent(unittest.TestCase):

    def test_can_change_container(self):
        subevent = a_subevent_with(start="1 Jan 200 10:01", end="3 Mar 200 10:01")
        container = a_container_with(text="container", cid=99)
        subevent.register_container(container)
        self.assertEqual(99, subevent.cid())
        self.assertEqual(container, subevent.container)

    def test_properties_defaults(self):
        subevent = a_subevent_with(start="1 Jan 200 10:01", end="3 Mar 200 10:01")
        self.assertEqual(-1, subevent.cid())
        self.assertEqual(False, subevent.get_fuzzy())
        self.assertEqual(False, subevent.get_locked())
        self.assertEqual(False, subevent.get_ends_today())
        self.assertEqual(False, subevent.is_container())
        self.assertEqual(True, subevent.is_subevent())

    def test_cid_can_be_set_a_construction(self):
        subevent = a_subevent_with(start="1 Jan 200 10:01", end="3 Mar 200 10:01", cid=99)
        self.assertEqual(99, subevent.cid())


class describe_subevent_cloning(unittest.TestCase):

    def test_cloning_returns_new_object(self):
        subevent = a_subevent_with(start="1 Jan 200 10:01", end="3 Mar 200 10:01")
        cloned_subevent = subevent.clone()
        self.assertTrue(subevent is not cloned_subevent)
        self.assertEqual(cloned_subevent.get_time_type(), subevent.get_time_type())
        self.assertEqual(cloned_subevent.get_time_period(), subevent.get_time_period())
        self.assertEqual(cloned_subevent.get_text(), subevent.get_text())
        self.assertEqual(cloned_subevent.get_category(), subevent.get_category())
        self.assertEqual(cloned_subevent.get_fuzzy(), subevent.get_fuzzy())
        self.assertEqual(cloned_subevent.get_locked(), subevent.get_locked())
        self.assertEqual(cloned_subevent.get_ends_today(), subevent.get_ends_today())
