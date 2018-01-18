from __future__ import absolute_import
from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

# Define required packages.
import py2gcode as meta

setup(name='py2gcode', url=meta.__homepage__, license=meta.__license__,
      version='.'.join(map(str, meta.__version__)),
      author=meta.__author__, author_email=meta.__contact__,
      description='py2gcode is a library for use "gcode" in python easily',
      requires=['six', 'numpy'],
      install_requires=['six', 'numpy'],
      classifiers=[
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.7",
          "License :: OSI Approved :: Apache Software License",
      ],
      packages=find_packages())
