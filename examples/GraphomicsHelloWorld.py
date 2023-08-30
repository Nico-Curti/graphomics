#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .__version__ import __version__
from .featureextractor import GraphomicsFeatureExtractor

__author__  = ['Nico Curti',
               'Gianluca Carlini',
               'Riccardo Biondi'
              ]
__email__ = ['nico.curti2@unibo.it',
             'gianluca.carlini2@unibo.it',
             'riccardo.biondi2@unibo.it'
            ]


if __name__ == '__main__':

	# check the version of the installed pyGraphomics library
  print(f'Working with pyGraphomics v{__version__}')
	