#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

# import filter for the graphomic feature extraction
from graphomics import GraphomicsFeatureExtractor

__author__  = ['Nico Curti',
               'Gianluca Carlini',
               'Riccardo Biondi'
              ]
__email__ = ['nico.curti2@unibo.it',
             'gianluca.carlini3@unibo.it',
             'riccardo.biondi7@unibo.it'
            ]


class TestExtractorClasses:
  '''
  Tests:
    - if disabling all features the selected ones are an empty dict
    - if enabling all features the selected ones cover all the classes
    - if enabling all features the returning dict has the format (name, list)
    - if enabling all features the returning dict has at least 1 element in each list
    - if enabling and then disabling the selection is an empty dict
    - if in any moment (enable/disable) the feature class names are available
    - if enabling feature class by name works with valid inputs
    - if enabling feature class by incorrect name raise an error
    - if enabling feature by name works with valid inputs
    - if enabling feature by incorrect name raise an error
    - if it is not executed raise an error
    - if the number of threads is correctly set when valid
    - if the number of threads raise an error when invalid
  '''

  def test_disable_all_features (self):

    # construct the object
    extractor = GraphomicsFeatureExtractor()
    # disable all features
    _ = extractor.DisableAllFeatures()
    # the returning value must be self
    assert isinstance(_, GraphomicsFeatureExtractor)

    # get the selected features
    selected_features = extractor.GetSelectedFeatures()

    # it must be a dictionary type
    assert isinstance(selected_features, dict)
    # it must be empty
    assert selected_features == {}

  def test_enable_all_feature_classes (self):

    # construct the object
    extractor = GraphomicsFeatureExtractor()
    # enable all features
    _ = extractor.EnableAllFeatures()
    # the returning value must be self
    assert isinstance(_, GraphomicsFeatureExtractor)

    # get the selected features
    selected_features = extractor.GetSelectedFeatures()

    # it must be a dictionary type
    assert isinstance(selected_features, dict)
    # it must have all the graphomic classes of features
    # as keys
    assert 'topology' in selected_features
    assert 'centrality' in selected_features
    assert 'spatial' in selected_features

  def test_enable_all_feature_classes_types (self):

    # construct the object
    extractor = GraphomicsFeatureExtractor()
    # enable all features
    _ = extractor.EnableAllFeatures()
    # the returning value must be self
    assert isinstance(_, GraphomicsFeatureExtractor)

    # get the selected features
    selected_features = extractor.GetSelectedFeatures()

    # the elements of the dictionary must be lists
    assert isinstance(selected_features['topology'], list)
    assert isinstance(selected_features['spatial'], list)
    assert isinstance(selected_features['centrality'], list)

  def test_enable_all_feature_classes_element_num (self):

    # construct the object
    extractor = GraphomicsFeatureExtractor()
    # enable all features
    _ = extractor.EnableAllFeatures()
    # the returning value must be self
    assert isinstance(_, GraphomicsFeatureExtractor)

    # get the selected features
    selected_features = extractor.GetSelectedFeatures()

    # they must contain at least 1 element
    assert len(selected_features['topology']) >= 1
    assert len(selected_features['spatial']) >= 1
    assert len(selected_features['centrality']) >= 1

  def test_enable_then_disable (self):

    # construct the object
    extractor = GraphomicsFeatureExtractor()
    # enable all features
    extractor.EnableAllFeatures()
    # disable all features
    extractor.DisableAllFeatures()

    # get the selected features
    selected_features = extractor.GetSelectedFeatures()

    # it must be a dictionary type
    assert isinstance(selected_features, dict)
    # it must be empty
    assert selected_features == {}

  def test_get_feature_classes_when_enable (self):

    # construct the object
    extractor = GraphomicsFeatureExtractor()
    # enable all features
    extractor.EnableAllFeatures()

    # get the feature classes
    feature_classes = extractor.GetAvailableFeatureClasses()

    # it must contain all the feature class names
    assert 'topology' in feature_classes
    assert 'centrality' in feature_classes
    assert 'spatial' in feature_classes

  def test_get_feature_classes_when_disable (self):

    # construct the object
    extractor = GraphomicsFeatureExtractor()
    # disable all features
    extractor.DisableAllFeatures()

    # get the feature classes
    feature_classes = extractor.GetAvailableFeatureClasses()

    # it must contain all the feature class names
    assert 'topology' in feature_classes
    assert 'centrality' in feature_classes
    assert 'spatial' in feature_classes

  def test_enable_feature_class_by_name (self):

    # construct the object
    extractor = GraphomicsFeatureExtractor()
    # disable all features
    extractor.DisableAllFeatures()

    # enable only 1 class
    _ = extractor.EnableFeatureClassByName('topology')
    # the returning value must be self
    assert isinstance(_, GraphomicsFeatureExtractor)

    # get the selected features
    selected_features = extractor.GetSelectedFeatures()
    # it must contain the correct feature class
    assert 'topology' in selected_features
    # it must contain only 1 feature class
    assert len(selected_features) == 1
    # it must contain the full list of member features
    assert isinstance(selected_features['topology'], list)
    assert len(selected_features['topology']) >= 1

    # re-adding does not alter the results
    extractor.EnableFeatureClassByName('topology')
    # get the selected features
    selected_features = extractor.GetSelectedFeatures()
    # it must contain the correct feature class
    assert 'topology' in selected_features
    # it must contain only 1 feature class
    assert len(selected_features) == 1
    # it must contain the full list of member features
    assert isinstance(selected_features['topology'], list)
    assert len(selected_features['topology']) >= 1

    # adding a new one increase the size of the dict to 2
    # re-adding does not alter the results
    extractor.EnableFeatureClassByName('spatial')
    # get the selected features
    selected_features = extractor.GetSelectedFeatures()
    # it must contain the correct feature class
    assert 'spatial' in selected_features
    # it must contain only 1 feature class
    assert len(selected_features) == 2

  def test_enable_feature_class_by_name_invalid (self):

    # construct the object
    extractor = GraphomicsFeatureExtractor()
    # disable all features
    extractor.DisableAllFeatures()

    # enable only 1 invalid class
    with pytest.raises(ValueError):
      _ = extractor.EnableFeatureClassByName('dummy')

  def test_enable_feature_by_name (self):

    # construct the object
    extractor = GraphomicsFeatureExtractor()
    # disable all features
    extractor.DisableAllFeatures()

    # enable only 1 feature
    _ = extractor.EnableFeaturesByName({'topology': ['NumberOfNodes']})
    # the returning value must be self
    assert isinstance(_, GraphomicsFeatureExtractor)

    # get the selected features
    selected_features = extractor.GetSelectedFeatures()
    # it must contain the correct feature class
    assert 'topology' in selected_features
    # it must contain only 1 feature class
    assert len(selected_features) == 1
    # it must contain only that member feature
    assert isinstance(selected_features['topology'], list)
    assert len(selected_features['topology']) == 1
    assert selected_features['topology'] == ['NumberOfNodes']

  def test_enable_feature_by_name_invalid (self):

    # construct the object
    extractor = GraphomicsFeatureExtractor()
    # disable all features
    extractor.DisableAllFeatures()

    # enable only 1 incorrect feature name
    with pytest.raises(ValueError):
      extractor.EnableFeaturesByName({'topology': ['dummy']})

    # enable only 1 incorrect feature class
    with pytest.raises(ValueError):
      extractor.EnableFeaturesByName({'dummy': ['NumberOfNodes']})

  def test_get_without_execute (self):

    # construct the object
    extractor = GraphomicsFeatureExtractor()
    # disable all features
    extractor.DisableAllFeatures()

    with pytest.raises(RuntimeError):
      extractor.GetFeatures()

  def test_num_threads (self):

    # construct the object
    extractor = GraphomicsFeatureExtractor()

    # set the number of threads to use
    extractor.SetGlobalDefaultNumberOfThreads(nth=1)
    assert extractor._features['nth'] == 1

    # change it
    extractor.SetGlobalDefaultNumberOfThreads(nth=3)
    assert extractor._features['nth'] == 3

    # invalid int
    with pytest.raises(ValueError):
      extractor.SetGlobalDefaultNumberOfThreads(nth=-42)

    # invalid num
    with pytest.raises(ValueError):
      extractor.SetGlobalDefaultNumberOfThreads(nth=3.14)
