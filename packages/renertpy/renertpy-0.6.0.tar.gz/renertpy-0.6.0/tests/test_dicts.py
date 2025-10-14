"""
RenertPy Python Package
Copyright (C) 2022 Assaf Gordon (assafgordon@gmail.com)
License: BSD (See LICENSE file)
"""
import unittest
import renertpy
from renertpy.all import *

class DictsFunctionsTest(unittest.TestCase):

    def test_capital_cities(self):
        x = get_capital_cities()
        self.assertIsInstance(x,dict)
    
    def test_pokemon_abilities(self):
        x = get_pokemon_abilities()
        self.assertIsInstance(x,dict)

    def test_l_words(self):
        x = get_l_words()
        self.assertIsInstance(x,dict)

if __name__ == '__main__':
    unittest.main()
