"""
RenertPy Python Package
Copyright (C) 2022-2024 Assaf Gordon (assafgordon@gmail.com)
License: BSD (See LICENSE file)
"""
import unittest
from renertpy.moby import nouns,verbs,adverbs,adjectives

class MobyWordsTest(unittest.TestCase):

    def helper_test_moby_collection(self,data):
        self.assertIsInstance(data,tuple)
        self.assertIsInstance(data[0],str)

    def test_nouns(self):
        self.helper_test_moby_collection(nouns)

    def test_verbs(self):
        self.helper_test_moby_collection(verbs)

    def test_adverbs(self):
        self.helper_test_moby_collection(adverbs)

    def test_adjectives(self):
        self.helper_test_moby_collection(adjectives)


if __name__ == '__main__':
    unittest.main()
