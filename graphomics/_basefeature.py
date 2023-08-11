#!/usr/bin/env python
# -*- coding: utf-8 -*-


__author__  = ['Nico Curti',
               'Gianluca Carlini',
               'Riccardo Biondi'
              ]
__email__ = ['nico.curti2@unibo.it',
             'gianluca.carlini2@unibo.it',
             'riccardo.biondi2@unibo.it'
            ]

__all__ = ['_BaseGraphomicsFeatures']

class _BaseGraphomicsFeatures (object):
  '''
  Base class for the feature extraction types.

  This class is the main orchestra for the graphomic
  feature extraction pipeline. In this class the desired
  set of features for each type is determined and fixed.
  '''

  def __init__ (self, *args, **kwargs):
    pass