#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

__author__  = ['Nico Curti',
               'Gianluca Carlini',
               'Riccardo Biondi'
              ]
__email__ = ['nico.curti2@unibo.it',
             'gianluca.carlini2@unibo.it',
             'riccardo.biondi2@unibo.it'
            ]

__all__ = ['_get_distribution_main_stats']


def _get_distribution_main_stats (x : list, prefix : str = '') -> dict :
  '''
  Get the main statistics of the input set of values.

  Parameters
  ----------
    x : list
      Input array of values to evaluate.

    prefix : str (default := '')
      Prefix string to prepend to the dictionary keys

  Returns
  -------
    stats : dict
      Dictionary in which are stored the main
      statistics of the provided input, aka
      average, median, std, min, and max values
  '''

  stats = {
    f'{prefix}average' : np.nanmean(x),
    f'{prefix}median' : np.nanmedian(x),
    f'{prefix}std' : np.nanstd(x),
    f'{prefix}min' : np.nanmin(x),
    f'{prefix}max' : np.nanmax(x)
  }

  return stats


if __name__ == '__main__':

  pass
