"""
RenertPy Python Package
Copyright (C) 2022 Assaf Gordon (assafgordon@gmail.com)
License: BSD (See LICENSE file)
"""
import unittest
import renertpy
from renertpy.all import *
from ipycanvas import Canvas
import PIL

data = [1,2,3,4]

class PlotFunctionsTest(unittest.TestCase):

    def test_bar_plot(self):
        x = bar_plot(data)
        self.assertIsInstance(x,Canvas)

    def test_line_plot(self):
        x = line_plot(data)
        self.assertIsInstance(x,Canvas)

    def test_greyscale_plot(self):
        x = greyscale_plot(data)
        self.assertIsInstance(x,PIL.Image.Image)

    def test_greyscale_2d_plot(self):
        x = greyscale_2d_plot(data,2)
        self.assertIsInstance(x,PIL.Image.Image)

    def test_colorname_plot(self):
        x = colorname_plot(["black","white","red"])
        self.assertIsInstance(x,PIL.Image.Image)

    def test_rgb_plot(self):
        data = [ [255,0,0], [0,0,255], [255,255,0] ]
        x = rgb_plot(data)
        self.assertIsInstance(x,PIL.Image.Image)

    def test_rgb_2d_plot(self):
        data = [ [255,0,0], [0,0,255], [255,255,0],
                 [255,0,0], [0,0,255], [255,255,0] ]

        x = rgb_2d_plot(data, 2)
        self.assertIsInstance(x,PIL.Image.Image)

if __name__ == '__main__':
    unittest.main()
