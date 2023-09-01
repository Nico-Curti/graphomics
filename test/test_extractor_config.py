#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest

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

template_file = os.path.join(
  os.path.abspath(
    os.path.dirname(__file__)
  ),
  '../cfg/template.yml'
)

class TestExtractorConfig:
  '''
  Tests:
    - if loading the template config the features are stored
    - if common properties are included in the template config
    - if the mask_filepath is a mandatory input for the execution
  '''

  def test_load_config_type (self):

    # construct the object
    extractor = GraphomicsFeatureExtractor()
    # load the template file
    extractor.LoadConfig(filename=template_file)

    # it must store all the features

    # get the selected features
    selected_features = extractor.GetSelectedFeatures()
    # it must be a dictionary type
    assert isinstance(selected_features, dict)
    # it must have all the graphomic classes of features
    # as keys
    assert 'topology' in selected_features
    assert 'centrality' in selected_features
    assert 'spatial' in selected_features

    # the elements of the dictionary must be lists
    assert isinstance(selected_features['topology'], list)
    assert isinstance(selected_features['spatial'], list)
    assert isinstance(selected_features['centrality'], list)

    # they must contain at least 1 element
    assert len(selected_features['topology']) >= 1
    assert len(selected_features['spatial']) >= 1
    assert len(selected_features['centrality']) >= 1

  def test_single_properties (self):

    # construct the object
    extractor = GraphomicsFeatureExtractor()
    # load the template file
    extractor.LoadConfig(filename=template_file)

    assert 'name' in extractor._features
    assert 'desc' in extractor._features
    assert 'pipeline_version' in extractor._features
    assert 'mask_filepath' in extractor._features
    assert 'skeleton_filepath' in extractor._features
    assert 'label_filepath' in extractor._features
    assert 'check_consistency' in extractor._features
    assert 'nth' in extractor._features
    assert 'binarize_input' in extractor._features
    assert 'surface_min_points' in extractor._features
    assert 'remove_surface' in extractor._features
    assert 'graph_weights' in extractor._features
    assert 'enable_weighted_features' in extractor._features
    assert 'enable_topology_features' in extractor._features
    assert 'enable_centrality_features' in extractor._features
    assert 'enable_spatial_features' in extractor._features

  def test_mask_filepath_requirement (self):

    # construct the object
    extractor = GraphomicsFeatureExtractor()
    # load the template file
    extractor.LoadConfig(filename=template_file)

    with pytest.raises(ValueError):
      extractor.Execute()
