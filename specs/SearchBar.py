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

from mock import Mock

from timelinelib.wxgui.components.search import SearchBar
from timelinelib.wxgui.components.search import SearchBarController


class SearchBarTestCase(unittest.TestCase):

    def test_no_events_found_displays_nomatch_label(self):
        self.view.get_value.return_value = ""
        self.controller.search()
        self.view.update_nomatch_labels.assert_called_with(True)
        self.view.update_singlematch_label.assert_called_with(False)

    def test_no_events_found_no_navigation_call(self):
        self.view.get_value.return_value = ""
        self.controller.search()
        self.assertFalse(self.drawing_area_panel.navigate)

    def test_on_event_found_displays_singlematch_label(self):
        self.view.get_value.return_value = "one"
        self.controller.search()
        self.view.update_nomatch_labels.assert_called_with(False)
        self.view.update_singlematch_label.assert_called_with(True)

    def test_on_event_found_navigation_called(self):
        self.view.get_value.return_value = "one"
        self.controller.search()
        self.assertTrue(self.drawing_area_panel.navigate)

    def test_two_events_found_displays_no_label(self):
        self.view.get_value.return_value = "two"
        self.controller.search()
        self.view.update_nomatch_labels.assert_called_with(False)
        self.view.update_singlematch_label.assert_called_with(False)

    def test_three_events_makes_it_possible_to_move_to_next(self):
        self.view.get_value.return_value = "three"
        self.controller.search()
        self.assertTrue(self.controller.result_index == 0)
        self.controller.next()
        self.assertTrue(self.controller.result_index == 1)
        self.controller.next()
        self.assertTrue(self.controller.result_index == 2)
        self.controller.next()
        self.assertTrue(self.controller.result_index == 2)

    def test_three_events_makes_it_possible_to_move_to_prev(self):
        self.view.get_value.return_value = "three"
        self.controller.search()
        self.controller.next()
        self.controller.next()
        self.assertTrue(self.controller.result_index == 2)
        self.controller.prev()
        self.assertTrue(self.controller.result_index == 1)
        self.controller.prev()
        self.assertTrue(self.controller.result_index == 0)
        self.controller.prev()
        self.assertTrue(self.controller.result_index == 0)

    def test_searching_for_same_term_twice_goes_to_next_match(self):
        self.view.get_value.return_value = "three"
        self.controller.search()
        self.controller.search()
        self.assertEqual(self.controller.result_index, 1)

    def test_no_drawing_area_panel_hides_search_bar(self):
        self.controller.set_drawing_area_panel(None)
        self.view.Enable.assert_called_with(False)

    def setUp(self):
        self.view = Mock(SearchBar)
        self.drawing_area_panel = DrawingAreaPanel()
        self.controller = SearchBarController(self.view)
        self.controller.set_drawing_area_panel(self.drawing_area_panel)


class DrawingAreaPanel():

    def __init__(self):
        self.navigate = False

    def get_filtered_events(self, search):
        if search == "":
            return []
        elif search == "one":
            return [1]
        elif search == "two":
            return [1, 2]
        elif search == "three":
            return [1, 2, 3]

    def navigate_timeline(self, fn):
        self.navigate = True
