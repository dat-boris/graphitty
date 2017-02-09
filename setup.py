# -*- coding: utf-8 -*-
import sys

from setuptools import setup

requires = []

setup(
    name="graphitty",
    version='0.0.1',
    description="A Python library that convert time series to direction " +
    "Graph to discover the story within data.",
    long_description="\n\n".join([open("README.md").read()]),
    author="Boris Lau",
    author_email="boris@techie.im",
    url="https://github.com/sketchytechky/graphitty",
    packages=['graphitty'],
    install_requires=requires)
