#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import partial
from inspect import signature
from inspect import getmembers

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
  feature extraction pipeline.
  In this class the desired set of features for each
  type is determined and fixed.
  '''

  def __init__ (self, *args, **kwargs):
    pass

  def _GetAvailableMembers (self) -> list:
    '''
    Inspect the class members and get the
    available ones, considering as valid features
    all the member functions identified by the
    private prefix '_Get'.

    Returns
    -------
      (name, func) : iterable
        Iterable of pairs member func (without prefix)
        and callable member function.
    '''
    # get the list of available members/features
    # Start with the full list of members
    features = getmembers(self)
    # filter the private getter ones
    features = filter(
      lambda x : '_Get' in x[0],
      features
    )
    # set the name as properties removing the
    # tag '_Get'
    features = map(
      lambda x : (x[0][4:], x[1]),
      features
    )
    return features

  def Execute (self, todo : list,
                     params : dict
              ):
    '''
    '''
    feature_names, feature_funcs = zip(*self._GetAvailableMembers())
    # filter the full list of features keeping only
    # the "todo-ones"
    feature_todo = {}
    # loop along the available members
    for name, func in zip(feature_names, feature_funcs):
      # if it is not a required features skip it
      if name not in todo:
        continue

      # get the position of the element in the todo-list
      idx = todo.index(name)
      # bind the member function with the provided parameters
      try:
        # check the validity of the provided parameters
        caller = partial(func, **params[idx])
      except TypeError:
        # something goes wrong with the given inputs...
        # get the list of available parameters
        sign = signature(func)
        # raise the error with a complete message of help
        raise ValueError(
          'Message'
        )
      # set the partial function in the feature-list
      feature_todo[name] = caller
      # remove the item from the todo-list to be
      # sure that no input-error will occur
      todo.remove(name)

    # check if the list of todo is empty
    # otherwise there must be something wrong in the
    # information read by the configuration file or
    # by the user
    if todo:
      raise ValueError(
        'Message'
      )

    # now we can run the evaluation
    # TODO: think about the possibility to run it in parallel
