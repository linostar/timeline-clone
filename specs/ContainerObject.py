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


from specs.utils import a_category_with
from specs.utils import a_container_with
from specs.utils import a_subevent_with
from specs.utils import CONTAINER_MODIFIERS
from specs.utils import TestCase


class describe_container(TestCase):

    def test_can_have_subevents(self):
        subevent = a_subevent_with(start="1 Jan 200 10:01", end="3 Mar 200 10:01")
        container = a_container_with(text="container")
        container.register_subevent(subevent)
        self.assertEqual(1, len(container.events))
        self.assertEqual(subevent, container.events[0])

    def test_subevents_can_be_unregistered(self):
        subevent = a_subevent_with(start="1 Jan 200 10:01", end="3 Mar 200 10:01")
        container = a_container_with(text="container")
        container.register_subevent(subevent)
        container.unregister_subevent(subevent)
        self.assertEqual(0, len(container.events))

    def test_name_can_be_updated(self):
        container = a_container_with(text="container")
        new_name = "new text"
        container.update_properties(new_name)
        self.assertEqual(new_name, container.get_text())

    def test_category_can_be_updated(self):
        container = a_container_with(text="container")
        new_name = "new text"
        new_category = a_category_with(name="cat")
        container.update_properties(new_name, category=new_category)
        self.assertEqual(new_category, container.get_category())

    def test_default_cid(self):
        container = a_container_with(text="container")
        self.assertEqual(-1, container.cid())

    def test_cid_can_be_changed(self):
        container = a_container_with(text="container")
        container.set_cid(99)
        self.assertEqual(99, container.cid())

    def test_can_be_compared(self):
        self.assertEqNeImplementationIsCorrect(a_container_with, CONTAINER_MODIFIERS)



class describe_container_construction(TestCase):

    def test_properties_defaults(self):
        container = a_container_with(text="container")
        self.assertEqual(-1, container.cid())
        self.assertEqual(False, container.get_fuzzy())
        self.assertEqual(False, container.get_locked())
        self.assertEqual(False, container.get_ends_today())
        self.assertEqual(True, container.is_container())
        self.assertEqual(False, container.is_subevent())
        self.assertEqual(None, container.get_category())

    def test_cid_can_be_set_at_construction(self):
        container = a_container_with(text="container", cid=99)
        self.assertEqual(99, container.cid())


class describe_container_cloning(TestCase):

    def test_cloning_returns_new_object(self):
        container = a_container_with(text="container", cid=99)
        cloned_container = container.clone()
        self.assertTrue(container is not cloned_container)
        self.assertEqual(cloned_container,  container)
