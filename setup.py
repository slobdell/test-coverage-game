#!/usr/bin/env python

from setuptools import find_packages
from setuptools import setup


setup(
    name='test-coverage-game',
    version="1.0.10",
    url='https://github.com/slobdell/test-coverage-game',
    author="Scott Lobdell",
    author_email="scott.lobdell@gmail.com",
    description=("Works in conjunction with a web application to gamify test coverage"),
    long_description=("Works in conjunction with a web application to gamify test coverage"),
    keywords="",
    license="",
    platforms=['linux'],
    packages=find_packages(exclude=[]),
    include_package_data=True,
    install_requires=[
        "requests==2.6.2",
        "coverage==3.7.1"
    ],
    extras_require={},
    entry_points = {
        "console_scripts": [
            "test-coverage-game = test_coverage_game.main:run",
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Topic :: Other/Nonlisted Topic'],
)
