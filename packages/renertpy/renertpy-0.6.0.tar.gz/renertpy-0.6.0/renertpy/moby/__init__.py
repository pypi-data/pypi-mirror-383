"""
RenertPy Python Package
Copyright (C) 2024 Assaf Gordon (assafgordon@gmail.com)
License: BSD (See LICENSE file)
"""
from .nouns_b64 import nouns_b64
from .verbs_b64 import verbs_b64
from .adverbs_b64 import adverbs_b64
from .adjectives_b64 import adjectives_b64
import pickle,base64

"""
Words from the Moby Lexicon Collection:
======================
June 1, 1996

The Moby lexicon project is complete and has
been place into the public domain. Use, sell,
rework, excerpt and use in any way on any platform.

Placing this material on internal or public servers is
also encouraged. The compiler is not aware of any
export restrictions so freely distribute world-wide.

You can verify the public domain status by contacting

Grady Ward
3449 Martha Ct.
Arcata, CA  95521-4884

grady@netcom.com
grady@northcoast.com
======================

NOTES:
1. Some words have been removed for brevity.
2. Each of 'nouns','verbs','adverbs','adjectives' is a TUPLE of STRINGS (each string = a word).
3. Base64 and Pickling is done for fast-ish loading with minimal external dependances.
"""

nouns = pickle.loads(base64.b64decode(nouns_b64))
verbs = pickle.loads(base64.b64decode(verbs_b64))
adverbs = pickle.loads(base64.b64decode(adverbs_b64))
adjectives = pickle.loads(base64.b64decode(adjectives_b64))
