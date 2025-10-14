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
from renertpy.data import files

class DataFunctionsTest(unittest.TestCase):

    def test_parrot_rgb_data(self):
        x = get_data_parrot_rgb()
        self.assertIsInstance(x,list)
    
    def test_parrot_bw_data(self):
        x = get_data_parrot_bw()
        self.assertIsInstance(x,list)
    
    def test_butterfly_rgb_data(self):
        x = get_data_butterfly_rgb()
        self.assertIsInstance(x,list)

    def test_butterfly_bw_data(self):
        x = get_data_butterfly_bw()
        self.assertIsInstance(x,list)

    def test_data_bw(self):
        x = get_data_bw("tulips")
        self.assertIsInstance(x,list)

    def test_data_rgb(self):
        x = get_data_rgb("tulips")
        self.assertIsInstance(x,list)

    def test_files_rgb(self):
        for k,v in files.items():
            x = get_data_rgb(k)

    def test_files_bw(self):
        for k,v in files.items():
            x = get_data_bw(k)

if __name__ == '__main__':
    unittest.main()
