#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import numpy as np
import SimpleITK as sitk

from .__version__ import __version__

# import filter for skeletonize image/volume
from ._skeletonizer import SkeletonizeImageFilter
# import filter for graph extraction
from ._graphfilter import GraphThicknessImageFilter
# import filters for graph weighting
from ._graph import (
  NodePairwiseDistanceFilter,
  EdgeLengthPathsFilter,
  EdgeLabelWeightFilter,
  GraphFilter
)
# import filters for topological graphomics features
from ._topology import GraphomicsTopology
# import filters for centrality graphomics features
from ._centrality import GraphomicsCentrality
# import filters for spatial graphomics features
from ._spatial import GraphomicsSpatial

__author__  = ['Nico Curti',
               'Gianluca Carlini',
               'Riccardo Biondi'
              ]
__email__ = ['nico.curti2@unibo.it',
             'gianluca.carlini2@unibo.it',
             'riccardo.biondi2@unibo.it'
            ]

__all__ = ['GraphomicsFeatureExtractor']


class GraphomicsFeatureExtractor (object):
  '''
  Core function for the graphomics feature extraction.

  '''

  _feature_classes = [
    'topology',
    'spatial',
    'centrality',
  ]

  def __init__ (self):

    self._features = {}

  def LoadConfig (self, filename : str):
    '''
    Load the graphomics features from a configuration
    file used for the customization of the workflow.
    The configuration file must be in Yaml format, following
    a strict nomenclature of the keys and values.
    The general template for the configuration file is
    provided in `cfg/template.yml`

    Parameters
    ----------
      filename : str
        Filename or path to the configuration file.
    '''

    with open(filename, 'r', encoding='utf-8') as fp:
      cfg = yaml.safe_load(fp)

    # TODO: add check about the values of the feature class
    self._features = cfg

    return self

  def DisableAllFeatures (self):
    '''
    Disable all the possible graphomics features.
    '''
    for name in self._feature_classes:
      self._features = None

    return self

  def EnableAllFeatures (self):
    '''
    Enable all the possible graphomics features.
    '''
    for name in self._feature_classes:
      self._features[name] = {}

    return self

  def EnableFeatureClassByName (self, name : str):
    '''
    Enable the features belonging to the provided
    class name.

    Possible classes of features are:

    * topology
    * spatial
    * centrality

    Parameters
    ----------
      name : str
        Name of graphomics features class to enable
    '''

    if name not in self._feature_classes:
      available_classes = ', '.join(self._feature_classes)
      raise ValueError(('Invalid feature class name. '
        f'Available classes are {available_classes}. '
        f'Given {name}.'
      ))

    self._features[name] = {}

    return self

  def EnableFeaturesByName (self, features : dict):
    '''
    Enable the list of features provided in input

    Parameters
    ----------
      features : dict
        Dictionary of required graphomics features divided
        by classes. The dictionary must be formatted as
        {'feature_class' : 'feature_name'}, following the
        same syntax of the configuration file.
        See at `cfg/template.yml` for a complete example
        of configuration file.
    '''

    for key, val in features:
      if key not in self._feature_classes:
        available_classes = ', '.join(self._feature_classes)
        raise ValueError(('Invalid feature class name. '
          f'Available classes are {available_classes}. '
          f'Given {key}.'
        ))

      # TODO: add check about the values of the feature class

    self._features = features

    return self

  def Execute (self, mask : sitk.Image,
                     labelmap : sitk.Image
              ) -> dict :
    '''
    '''
    pass