"""
RenertPy Python Package
Copyright (C) 2022 Assaf Gordon (assafgordon@gmail.com)
License: BSD (See LICENSE file)
"""
import unittest
import renertpy
from renertpy.all import *


class MinimalImportTest(unittest.TestCase):

    def test_import(self):
        pass

    def test_version(self):
        print("RenertPy Reported Version: ", renertpy.__version__)

if __name__ == '__main__':
    unittest.main()
