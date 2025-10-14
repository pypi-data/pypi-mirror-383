"""
RenertPy Python Package
Copyright (C) 2022 Assaf Gordon (assafgordon@gmail.com)
License: BSD (See LICENSE file)
"""
import unittest
from renertpy.all import *
from IPython.display import Audio

class AudioFunctionsTest(unittest.TestCase):

    def test_play_freq(self):
        data = [ 400, 500, 600, 700, 800 ]
        x = play_frequencies(data)
        self.assertIsInstance(x,Audio)

    def test_play_freq_dur(self):
        data = [ [400, 0.4],
                 [500, 0.3],
                 [600, 0.5],
                  ]
        x = play_frequencies_durations(data)
        self.assertIsInstance(x,Audio)


if __name__ == '__main__':
    unittest.main()
