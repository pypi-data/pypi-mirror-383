"""
RenertPY Python Package
Copyright (C) 2022 Assaf Gordon (assafgordon@gmail.com)
License: BSD (See LICENSE file)
"""

from setuptools import setup
from detect_version import detect_version

setup(
    name = "renertpy",
    version = detect_version("renertpy"),
    author = "Assaf Gordon",
    author_email = "AssafGordon@gmail.com",

    description = "Collection of functions used to teach Python at Renert School",
    long_description="Collection of functions used to teach Python at Renert School",

    license = "BSD",
    keywords = "jupyter",
    url = "https://github.com/agordon/renertpy",
    packages=['renertpy'],
    install_requires=[
              'numpy',
              'ipycanvas',
              'pillow'
              ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
    ],
    test_suite = 'tests',
    include_package_data=True,
    package_data={'renertpy': ['data/*.jpg']},

)
