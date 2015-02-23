# Copyright (C) 2015  Linostar
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
from random import random

from timelinelib.drawing.utils import darken_color, lighten_color


class drawing_utils(unittest.TestCase):

    def test_darken_color_good_factor(self):
        randColor = self.random_color()
        randFactor = random()
        newColor = darken_color(randColor, randFactor)
        for x in newColor:
            self.assertTrue(x >= 0 and x <= 255)

    def test_darken_color_bad_factor(self):
        lowFactor = random() * 256 - 256 # -256 < factor < 0
        highFactor = 1 + random() * 255 # 1 < factor < 256
        randColor = self.random_color()
        self.assertEqual(randColor, darken_color(randColor, lowFactor))
        self.assertEqual(randColor, darken_color(randColor, highFactor))

    def test_lighten_color_good_factor(self):
        randColor = self.random_color()
        randFactor = 1 + random() * 254 # 1 < factor < 255
        newColor = lighten_color(randColor, randFactor)
        for x in newColor:
            self.assertTrue(x >= 0 and x <= 255)

    def test_lighten_color_bad_factor(self):
        lowFactor = random() * 257 - 256 # -256 < factor < 1
        highFactor = 255 + random() # 255 < factor < 256
        randColor = self.random_color()
        self.assertEqual(randColor, lighten_color(randColor, lowFactor))
        self.assertEqual(randColor, lighten_color(randColor, highFactor))

    def random_color(self):
        return tuple([int(random() * 256) for _ in (1, 2, 3)])
