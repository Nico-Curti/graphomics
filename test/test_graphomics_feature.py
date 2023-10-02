#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest
import networkx as nx

# import filters for topological graphomics features
from graphomics import GraphomicsTopology

__author__  = ['Nico Curti',
               'Gianluca Carlini',
               'Riccardo Biondi'
              ]
__email__ = ['nico.curti2@unibo.it',
             'gianluca.carlini3@unibo.it',
             'riccardo.biondi7@unibo.it'
            ]

class TestGraphomicsFeature:
  '''
  Tests:
    - if it get the correct number of members in inheritance
    - if it raise error with incorrect execute function
    - if it provide a valid dict of features as result
  '''

  def test_get_members (self):
    # define the feature extractor
    feat = GraphomicsTopology()
    # get the available members
    members = feat.GetAvailableMembers()

    # check the output
    assert hasattr(members, '__iter__')
    members = list(members)
    assert len(members) > 0
    assert isinstance(members[0], tuple)
    # check member types
    assert all(isinstance(x, str) for x, _ in members)
    assert all(callable(x) for _, x in members)
    # check feature names
    assert all(x.__name__.startswith('_Get') for _, x in members)

  def test_execute (self):
    # define the feature extractor
    feat = GraphomicsTopology()

    # run just one feature as check
    feat.Execute(
      todo=['NumberOfNodes'],
      params={},
      inputs={'G': nx.complete_graph(n=5)}
    )

    # run an invalid feature
    with pytest.raises(ValueError):
      feat.Execute(
        todo=['nodes'],
        params={},
        inputs={'G': nx.complete_graph(n=5)}
      )

    # run with invalid parameters
    with pytest.raises(ValueError):
      feat.Execute(
        todo=['NumberOfNodes'],
        params={'NumberOfNodes': {'n': 5}},
        inputs={'G': nx.complete_graph(n=5)}
      )

    # run with invalid input
    with pytest.raises(ValueError):
      feat.Execute(
        todo=['NumberOfNodes'],
        params={},
        inputs={'graph': nx.complete_graph(n=5)}
      )

  def test_get_features (self):
    # define the feature extractor
    feat = GraphomicsTopology()

    # raise error if it was not executed
    with pytest.raises(RuntimeError):
      feat.GetFeatures()

    # run just one feature as check
    feat.Execute(
      todo=['NumberOfNodes'],
      params={},
      inputs={'G': nx.complete_graph(n=5)}
    )

    # get the features
    res = feat.GetFeatures()

    # check result properties
    assert isinstance(res, dict)
    assert 'NumberOfNodes' in res
    assert res['NumberOfNodes'] == 5
    assert len(res) == 1
