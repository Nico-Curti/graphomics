#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from graphomics import __version__
# import filter for the graphomic feature extraction
from graphomics import GraphomicsFeatureExtractor

__author__  = ['Nico Curti',
               'Gianluca Carlini',
               'Riccardo Biondi'
              ]
__email__ = ['nico.curti2@unibo.it',
             'gianluca.carlini2@unibo.it',
             'riccardo.biondi2@unibo.it'
            ]


if __name__ == '__main__':

  # In this example we will see how we can deeply manage
  # the graphomic filter, describing all the available
  # parameters and member functions.
  # This is just an 'HelloWorld' example and further
  # documentations and real-case applications could be found
  # in the notebooks folder
  # (ref. https://github.com/Nico-Curti/graphomics/blob/main/docs/source/notebooks)

  # ####################################################### #
  # NOTE: this code is not a ready-to-use code since it     #
  # depends on the definition of the `cfg` variable         #
  # defined below!                                          #
  # ####################################################### #

  # check the version of the installed pyGraphomics library
  print(f'Working with pyGraphomics v{__version__}',
    end='\n\n',
    flush=True
  )

  # define the graphomic features extraction filter
  extractor = GraphomicsFeatureExtractor()

  # using the member function of the object you can disable/enable
  # all the possible graphomic features with a single
  # function call
  extractor.DisableAllFeatures()
  extractor.EnableAllFeatures()
  # In this case the each graphomic feature will acquire
  # the default parameters.

  # To check the current enabled features you can inspect
  # the SelectedFeatures list, which returns a dictionary
  # including all the currently enabled features in the
  # filter
  selected_features = extractor.GetSelectedFeatures()
  print(f'Currently enabled graphomic features: {json.dumps(selected_features, indent=2)}',
    end='\n\n',
    flush=True
  )

  # Let's start from a complete set of turned-off features
  extractor.DisableAllFeatures()

  # A more accurate selection could be obtained by enabling
  # a single class of features.
  # First of all, you can check the list of available feature
  # classes, inspecting the filter
  feature_classes = extractor.GetAvailableFeatureClasses()
  print(f'Available graphomic feature classes: {json.dumps(feature_classes, indent=2)}',
    end='\n\n',
    flush=True
  )
  # and then you can enable a single class of features
  # by calling the member function
  first_class = feature_classes[-1]
  print(f'Enabling only {first_class} graphomic feature class',
    end='\n\n',
    flush=True
  )
  extractor.EnableFeatureClassByName(name=first_class)
  # and check the change
  selected_features = extractor.GetSelectedFeatures()
  print(f'Currently enabled graphomic features: {json.dumps(selected_features, indent=2)}')

  # OR you can also enable a single feature using its name,
  # associated to the belonging class name as in the following
  feature_to_enable = {'topology' : ['NumberOfEdges']}
  extractor.EnableFeaturesByName(features=feature_to_enable)
  # and check the change
  selected_features = extractor.GetSelectedFeatures()
  print(f'Currently enabled graphomic features: {json.dumps(selected_features, indent=2)}',
    end='\n\n',
    flush=True
  )

  # A complete management of the available features and their
  # internal parameters could be obtained using a configuration
  # file in which specify all our needs.
  # In this case we can manage our graphomic pipeline in a
  # more easy way and ensure monitor the reproducibility/changing
  # of the results on different datasets.
  # A full 'template' example of the configuration file can
  # be found in the cfg folder
  # (ref. https://github.com/Nico-Curti/graphomics/blob/main/cfg/template.yml)
  # with a detailed documentation of all its sections and components
  cfg = 'path/to/the/configuration/file.yml'
  cfg = '../cfg/template.yml'
  extractor.LoadConfig(filename=cfg)
  selected_features = extractor.GetSelectedFeatures()
  print(f'Currently enabled graphomic features: {json.dumps(selected_features, indent=2)}',
    end='\n\n',
    flush=True
  )
