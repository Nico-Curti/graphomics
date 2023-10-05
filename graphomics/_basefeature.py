#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import partial
from inspect import Parameter
from inspect import signature
from inspect import getmembers
import inspect

__author__  = ['Nico Curti',
               'Gianluca Carlini',
               'Riccardo Biondi'
              ]
__email__ = ['nico.curti2@unibo.it',
             'gianluca.carlini3@unibo.it',
             'riccardo.biondi7@unibo.it'
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

  def GetAvailableMembers (self) -> list:
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
                     params : dict,
                     inputs : dict
              ) :
    '''
    Execute the filter running only the features
    stored in the todo-list.

    Parameters
    ----------
      todo : list
        List of graphomic feature names to compute.

      params : dict
        Dictionary of extra-parameters to pass to the
        corresponding graphomic feature evaluation.

      inputs : dict
        Dictionary of inputs required for the function
        call.
    '''
    feature_names, feature_funcs = zip(*self.GetAvailableMembers())
    # filter the full list of features keeping only
    # the "todo-ones"
    feature_todo = {}
    # loop along the available members
    for name, func in zip(feature_names, feature_funcs):
      # if it is not a required features skip it
      if name not in todo:
        continue

      # bind the member function with the provided parameters
      try:
        # check the validity of the provided parameters
        caller = partial(func, **params.get(name, {}))
      except TypeError:
        # something goes wrong with the given inputs...
        # get the list of available parameters
        sign = signature(func)
        # raise the error with a complete message of help
        raise ValueError((
          'Invalid function parameters. '
          f'The expected signature for {name} is {sign} '
          f'Given {params[name]}'
        ))
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
      raise ValueError((
        'Invalid list of required graphomic features. '
        f'The following features were not found in the package: {todo}'
      ))

    # now we can run the evaluation
    # TODO: think about the possibility to run it in parallel
    features = {}
    for name, func in feature_todo.items():
      # get the list of the required parameters
      sign = signature(func)
      # filter the list of parameters according to
      # the only required ones, aka the parameters
      # without a default value already set
      req_params = [name
        for name, param in sign.parameters.items()
          if param.default == Parameter.empty
      ]
      # select the appropriated inputs to feed
      inpts = {}
      # loop along the required parameters
      for k in req_params:
        # if it is not a parameter already set
        if k not in params.get(name, {}):
          # add it to the dictionary if it exists
          try:
            inpts[k] = inputs[k]
          except KeyError:
            raise ValueError((
              'Missing required input. '
              f'Function {name} requires {k} as input. '
              f'Given {inputs}'
            ))
      # call the function and get the results
      features[name] = func(**inpts)

    self._features = features

    return self

  def GetFeatures (self) -> dict :
    '''
    Get the graphomic features computed.

    Returns
    -------
      features : dict
        Dictionary of graphomic features evaluated by the filter.
        The features are indexed according to their name.
    '''
    if not hasattr(self, '_features'):
      class_name = self.__class__.__name__
      raise RuntimeError(('Runtime Exception. '
        f'The {class_name} object is not executed yet. '
        'To get the weigts list you need to call the Execute function'
      ))

    return self._features


if __name__ == '__main__':

  pass
