"""
RenertPy Python Package
Copyright (C) 2022 Assaf Gordon (assafgordon@gmail.com)
License: BSD (See LICENSE file)
"""

import warnings
import numpy

# https://musicinformationretrieval.com/ipython_audio.html
import IPython.display as ipd
from .utils import (check_iterable,
                    check_numeric_iterable,
                    check_numeric_iterable_2d,
                    truncate_list,
                    check_color_name,
                    validate_color_name,
                    check_colorname_iterable)

default_sample_rate = 22050 # sample rate

def gen_sound_wave(freq, seconds, amplitude = 0.5, sample_rate=default_sample_rate):
    x = numpy.sin(freq * 2. * numpy.pi * numpy.linspace(0., seconds, int(sample_rate * seconds)))
    return x


def play_frequencies(data, duration=0.4):
    check_iterable(data)
    check_numeric_iterable(data)
    
    x = numpy.empty([0])
    
    for i,freq in enumerate(data):
        if freq < 200 or freq > 11000:
            warnings.warn("ignoring invalid frequency %d in element %d (must be between 300 and 11000)" % (freq, i))
            continue
            
        y = gen_sound_wave(freq, duration)
        x = numpy.concatenate( (x,y) )
        
    a = ipd.Audio(x, rate=default_sample_rate,  autoplay=False) # load a NumPy array
    return a


def play_frequencies_durations(data):
    check_iterable(data)
    check_numeric_iterable_2d(data)
    
    x = numpy.empty([0])
    
    for i,pair in enumerate(data):
        if len(pair) != 2:
            raise ValueError("error in element %d: expecting a list of 2 values [freq,duration], got '%s'" % ( i, str(pair) ) )

        freq, dur = pair        
        if freq < 200 or freq > 11000:
            warnings.warn("ignoring invalid frequency '%d' in element %d (must be between 300 and 11000)" % (freq, i))
            continue

        if dur <= 0 or dur > 1:
            warnings.warn("ignoring invalid duration '%s' in element %d (must be between 0.1 and 1.0 seconds)" % (str(dur), i))
            continue

        y = gen_sound_wave(freq, dur)
        x = numpy.concatenate( (x,y) )
        
    a = ipd.Audio(x, rate=default_sample_rate,  autoplay=False) # load a NumPy array
    return a
