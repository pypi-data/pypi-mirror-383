"""
RenertPy Python Package
Copyright (C) 2022 Assaf Gordon (assafgordon@gmail.com)
License: BSD (See LICENSE file)
"""
import unittest
import renertpy
from renertpy.all import *

class ColorFunctionsTest(unittest.TestCase):

    def test_rgb_to_hsv(self):
        h,s,v = rgb_to_hsv(255,128,80)
    
    def test_hsv_to_rgb(self):
        r,g,b = hsv_to_rgb(345, 0.4, 1.0)

if __name__ == '__main__':
    unittest.main()
