"""
RenertPy Python Package
Copyright (C) 2022 Assaf Gordon (assafgordon@gmail.com)
License: BSD (See LICENSE file)
"""

from .list_plots import (bar_plot,
                         line_plot,
                         greyscale_plot,
                         greyscale_2d_plot,
                         colorname_plot,
                         rgb_plot,
                         rgb_2d_plot)

from .list_audio import (play_frequencies,
        play_frequencies_durations)

from .data import (load_picture_data,
                    get_data_rgb,
                    get_data_bw,
                  get_data_parrot_rgb,
                  get_data_parrot_bw,
                  get_data_butterfly_rgb,
                  get_data_butterfly_bw)

from .colors import rgb_to_hsv, hsv_to_rgb

from .display import clear_output

from .dicts import get_capital_cities, get_pokemon_abilities, get_l_words

from .moby import nouns, verbs, adverbs, adjectives

load_picture_data()
