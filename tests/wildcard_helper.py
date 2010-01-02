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


import unittest

from timelinelib.gui.utils import WildcardHelper


class FileDialogMock(object):
    """Mock object for a wx.FileDialog."""

    def __init__(self, path):
        self.path = path

    def GetPath(self):
        return self.path


class TestWildcardHelper(unittest.TestCase):

    def setUp(self):
        self.images_wildcard_helper = WildcardHelper(
            "image files", [("png", 1), ("bmp", 2)])
        self.dummies_wildcard_helper = WildcardHelper(
            "dummy files", ["foo", "bar"])

    def testWildcardString(self):
        simple_wildcard_helper = WildcardHelper("foo files", ["foo"])
        self.assertEquals(
            simple_wildcard_helper.wildcard_string(),
            "foo files (*.foo)|*.foo")
        self.assertEquals(
            self.dummies_wildcard_helper.wildcard_string(),
            "dummy files (*.foo, *.bar)|*.foo;*.bar")

    def testWildcardStringWithTupleExtensions(self):
        self.assertEquals(
            self.images_wildcard_helper.wildcard_string(),
            "image files (*.png, *.bmp)|*.png;*.bmp")

    def testGetExtensionData(self):
        self.assertEquals(
            self.images_wildcard_helper.get_extension_data("bar.png"),
            1)
        self.assertEquals(
            self.images_wildcard_helper.get_extension_data("bar"),
            None)
        self.assertEquals(
            self.dummies_wildcard_helper.get_extension_data("foo.bar"),
            None)

    def testGetPath(self):
        self.assertEquals(
            self.images_wildcard_helper.get_path(FileDialogMock("bar.bmp")),
            "bar.bmp")
        # First given extension used as default
        self.assertEquals(
            self.images_wildcard_helper.get_path(FileDialogMock("bar")),
            "bar.png")
