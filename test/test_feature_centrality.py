#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

import numpy as np
import networkx as nx
import SimpleITK as sitk

# import filters for centrality graphomics features
from graphomics import GraphomicsCentrality

__author__  = ['Nico Curti',
               'Gianluca Carlini',
               'Riccardo Biondi'
              ]
__email__ = ['nico.curti2@unibo.it',
             'gianluca.carlini3@unibo.it',
             'riccardo.biondi7@unibo.it'
            ]


class TestFeatureCentrality:
  '''
  Tests all the possible outcomes of each feature
  belonging to the class Centrality.
  '''

  def test_feature_NodeDegreeCentrality (self):
    # define the feature extractor class
    feat = GraphomicsCentrality()

    # generate a random number of nodes
    n = np.random.randint(
      low=3,
      high=30
    )
    # generate a probability from a uniform distribution
    p = np.random.uniform(
      low=0.5,
      high=1.
    )

    # create a random graph according to Erdos-Renyi definition
    G = nx.erdos_renyi_graph(
      n=n,
      p=p,
      seed=42,
      directed=False
    )

    # evaluate the feature
    res = feat._GetNodeDegreeCentrality(G=G)

    # check the feature properties
    assert isinstance(res, dict)
    for k, v in res.items():
      assert k.startswith('node_degree')
      assert isinstance(k, str)
      assert v >= 0.
      assert np.isfinite(v)

    # add random weights to nodes
    for (e1, e2) in G.edges():
      G[e1][e2]['weight'] = 3.14

    # evaluate the feature
    res = feat._GetNodeDegreeCentrality(G=G, weight='weight')

    # check the feature properties
    assert isinstance(res, dict)
    for k, v in res.items():
      assert k.startswith('node_weighted_degree')
      assert isinstance(k, str)
      assert v >= 0.
      assert np.isfinite(v)

  def test_feature_NodeBetweennessCentrality (self):
    # define the feature extractor class
    feat = GraphomicsCentrality()

    # generate a random number of nodes
    n = np.random.randint(
      low=3,
      high=30
    )
    # generate a probability from a uniform distribution
    p = np.random.uniform(
      low=0.5,
      high=1.
    )

    # create a random graph according to Erdos-Renyi definition
    G = nx.erdos_renyi_graph(
      n=n,
      p=p,
      seed=42,
      directed=False
    )

    # evaluate the feature
    res = feat._GetNodeBetweennessCentrality(G=G)

    # check the feature properties
    assert isinstance(res, dict)
    for k, v in res.items():
      assert k.startswith('node_betweenness')
      assert isinstance(k, str)
      assert v >= 0.
      assert isinstance(v, float) or isinstance(v, int)
      assert np.isfinite(v)

    # add random weights to nodes
    for (e1, e2) in G.edges():
      G[e1][e2]['weight'] = 3.14

    # evaluate the feature
    res = feat._GetNodeBetweennessCentrality(G=G, weight='weight')

    # check the feature properties
    assert isinstance(res, dict)
    for k, v in res.items():
      assert k.startswith('node_weighted_betweenness')
      assert isinstance(k, str)
      assert v >= 0.
      assert np.isfinite(v)

  def test_feature_NodeClusteringCoefficient (self):
    # define the feature extractor class
    feat = GraphomicsCentrality()

    # generate a random number of nodes
    n = np.random.randint(
      low=3,
      high=30
    )
    # generate a probability from a uniform distribution
    p = np.random.uniform(
      low=0.5,
      high=1.
    )

    # create a random graph according to Erdos-Renyi definition
    G = nx.erdos_renyi_graph(
      n=n,
      p=p,
      seed=42,
      directed=False
    )

    # evaluate the feature
    res = feat._GetNodeClusteringCoefficient(G=G)

    # check the feature properties
    assert isinstance(res, dict)
    for k, v in res.items():
      assert k.startswith('node_clustering')
      assert isinstance(k, str)
      assert v >= 0.
      assert np.isfinite(v)

    # add random weights to nodes
    for (e1, e2) in G.edges():
      G[e1][e2]['weight'] = 3.14

    # evaluate the feature
    res = feat._GetNodeClusteringCoefficient(G=G, weight='weight')

    # check the feature properties
    assert isinstance(res, dict)
    for k, v in res.items():
      assert k.startswith('node_weighted_clustering')
      assert isinstance(k, str)
      assert v >= 0.
      assert np.isfinite(v)

  def test_feature_NodeClosenessCentrality (self):
    # define the feature extractor class
    feat = GraphomicsCentrality()

    # generate a random number of nodes
    n = np.random.randint(
      low=3,
      high=30
    )
    # generate a probability from a uniform distribution
    p = np.random.uniform(
      low=0.5,
      high=1.
    )

    # create a random graph according to Erdos-Renyi definition
    G = nx.erdos_renyi_graph(
      n=n,
      p=p,
      seed=42,
      directed=False
    )

    # evaluate the feature
    res = feat._GetNodeClosenessCentrality(G=G)

    # check the feature properties
    assert isinstance(res, dict)
    for k, v in res.items():
      assert k.startswith('node_closeness')
      assert isinstance(k, str)
      assert v >= 0.
      assert isinstance(v, float) or isinstance(v, int)
      assert np.isfinite(v)

    # add random weights to nodes
    for (e1, e2) in G.edges():
      G[e1][e2]['weight'] = 3.14

    # evaluate the feature
    res = feat._GetNodeClosenessCentrality(G=G, weight='weight')

    # check the feature properties
    assert isinstance(res, dict)
    for k, v in res.items():
      assert k.startswith('node_weighted_closeness')
      assert isinstance(k, str)
      assert v >= 0.
      assert np.isfinite(v)

  def test_feature_NodePageRankCentrality (self):
    # define the feature extractor class
    feat = GraphomicsCentrality()

    # generate a random number of nodes
    n = np.random.randint(
      low=3,
      high=30
    )
    # generate a probability from a uniform distribution
    p = np.random.uniform(
      low=0.5,
      high=1.
    )

    # create a random graph according to Erdos-Renyi definition
    G = nx.erdos_renyi_graph(
      n=n,
      p=p,
      seed=42,
      directed=False
    )

    # evaluate the feature
    res = feat._GetNodePageRankCentrality(G=G)

    # check the feature properties
    assert isinstance(res, dict)
    for k, v in res.items():
      assert k.startswith('node_pagerank')
      assert isinstance(k, str)
      assert v >= 0.
      assert isinstance(v, float) or isinstance(v, int)
      assert np.isfinite(v)

    # add random weights to nodes
    for (e1, e2) in G.edges():
      G[e1][e2]['weight'] = 3.14

    # evaluate the feature
    res = feat._GetNodePageRankCentrality(G=G, weight='weight')

    # check the feature properties
    assert isinstance(res, dict)
    for k, v in res.items():
      assert k.startswith('node_weighted_pagerank')
      assert isinstance(k, str)
      assert v >= 0.
      assert np.isfinite(v)

  def test_feature_NodeHarmonicCentrality (self):
    # define the feature extractor class
    feat = GraphomicsCentrality()

    # generate a random number of nodes
    n = np.random.randint(
      low=3,
      high=30
    )
    # generate a probability from a uniform distribution
    p = np.random.uniform(
      low=0.5,
      high=1.
    )

    # create a random graph according to Erdos-Renyi definition
    G = nx.erdos_renyi_graph(
      n=n,
      p=p,
      seed=42,
      directed=False
    )

    # evaluate the feature
    res = feat._GetNodeHarmonicCentrality(G=G)

    # check the feature properties
    assert isinstance(res, dict)
    for k, v in res.items():
      assert k.startswith('node_harmonic')
      assert isinstance(k, str)
      assert v >= 0.
      assert np.isfinite(v)

    # add random weights to nodes
    for (e1, e2) in G.edges():
      G[e1][e2]['weight'] = 3.14

    # evaluate the feature
    res = feat._GetNodeHarmonicCentrality(G=G, weight='weight')

    # check the feature properties
    assert isinstance(res, dict)
    for k, v in res.items():
      assert k.startswith('node_weighted_harmonic')
      assert isinstance(k, str)
      assert v >= 0.
      assert np.isfinite(v)
