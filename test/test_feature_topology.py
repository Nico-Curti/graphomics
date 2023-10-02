#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

import numpy as np
import networkx as nx
import SimpleITK as sitk

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


class TestFeatureTopology:
  '''
  Tests all the possible outcomes of each feature
  belonging to the class Topology.
  '''

  def test_feature_NumberOfNodes (self):
    # define the feature extractor class
    feat = GraphomicsTopology()

    # generate a random number of nodes
    n = np.random.randint(
      low=1,
      high=20
    )
    # generate a probability from a uniform distribution
    p = np.random.uniform(
      low=0.,
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
    res = feat._GetNumberOfNodes(G=G)

    # check the feature properties
    assert isinstance(res, int)
    assert res == n
    assert res > 0
    assert np.isfinite(res)

  def test_feature_NumberOfEdges (self):
    # define the feature extractor class
    feat = GraphomicsTopology()

    # generate a random number of nodes
    n = np.random.randint(
      low=3,
      high=20
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
    res = feat._GetNumberOfEdges(G=G)

    # check the feature properties
    assert isinstance(res, int)
    assert res == G.number_of_edges()
    assert res > 0
    assert np.isfinite(res)

  def test_feature_EdgeWeights (self):
    # define the feature extractor class
    feat = GraphomicsTopology()

    # generate a random number of nodes
    n = np.random.randint(
      low=3,
      high=20
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
    res = feat._GetEdgeWeights(G=G)

    # check the feature properties
    assert isinstance(res, dict)
    for k, v in res.items():
      assert k.startswith('edge_weights_')
      assert isinstance(k, str)
      assert v >= 0
      assert np.isfinite(v)

    assert isinstance(res['edge_weights_average'], float)
    assert res['edge_weights_average'] == 1.
    assert isinstance(res['edge_weights_median'], float)
    assert res['edge_weights_median'] == 1.
    assert isinstance(res['edge_weights_std'], float)
    assert res['edge_weights_std'] == 0.

    # add random weights to nodes
    for (e1, e2) in G.edges():
      G[e1][e2]['weight'] = 3.14

    # evaluate the feature
    res = feat._GetEdgeWeights(G=G)

    # check the feature properties
    assert isinstance(res, dict)
    for k, v in res.items():
      assert k.startswith('edge_weights_')
      assert isinstance(k, str)
      assert v >= 0
      assert np.isfinite(v)

  def test_feature_SelfLinks (self):
    # define the feature extractor class
    feat = GraphomicsTopology()

    # generate a random number of nodes
    n = np.random.randint(
      low=3,
      high=20
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
    # generate the lut
    lut = {i : v for i, v in enumerate(G.edges())}

    # evaluate the feature
    res = feat._GetSelfLinks(lut=lut)

    # check the feature properties
    assert isinstance(res, int)
    assert res == 0
    assert np.isfinite(res)

    # manually add a self link
    G.add_edge(1, 1)
    # generate the lut
    lut = {i : v for i, v in enumerate(G.edges())}

    # evaluate the feature
    res = feat._GetSelfLinks(lut=lut)

    # check the feature properties
    assert isinstance(res, int)
    assert np.isfinite(res)
    assert res == 1

  def test_feature_EulerNumber (self):
    # define the feature extractor class
    feat = GraphomicsTopology()

    def sphere (shape: tuple, radius: int, position: tuple):
      '''
      Generate an n-dimensional spherical mask.
      '''
      # assume shape and position have the same length and contain ints
      # the units are pixels / voxels (px for short)
      # radius is a int or float in px
      assert len(position) == len(shape)
      n = len(shape)
      semisizes = (radius,) * len(shape)

      # genereate the grid for the support points
      # centered at the position indicated by position
      grid = [slice(-x0, dim - x0) for x0, dim in zip(position, shape)]
      position = np.ogrid[grid]
      # calculate the distance of all points from `position` center
      # scaled by the radius
      arr = np.zeros(shape, dtype=float)
      for x_i, semisize in zip(position, semisizes):
          # this can be generalized for exponent != 2
          # in which case `(x_i / semisize)`
          # would become `np.abs(x_i / semisize)`
          arr += (x_i / semisize) ** 2

      # the inner part of the sphere will have distance below or equal to 1
      return arr <= 1.0

    # generate a sphere
    volume = sphere(
      shape=(64, 64, 64),
      radius=16,
      position=(32, 32, 32)
    )
    # convert it to sitk format
    mask = sitk.GetImageFromArray(np.uint8(volume))

    # evaluate the feature
    res = feat._GetEulerNumber(mask=mask)

    # check the feature properties
    assert isinstance(res, int)
    assert np.isfinite(res)
    assert res == 1

    # generate an hollow sphere
    # create a 3D hollow sphere as volume mask
    external = sphere(
      shape=(64, 64, 64),
      radius=16,
      position=(32, 32, 32)
    )
    hollow = sphere(
      shape=(64, 64, 64),
      radius=8,
      position=(32, 32, 32)
    )
    volume = external ^ hollow

    # convert it to sitk format
    mask = sitk.GetImageFromArray(np.uint8(volume))

    # evaluate the feature
    res = feat._GetEulerNumber(mask=mask)

    # check the feature properties
    assert isinstance(res, int)
    assert np.isfinite(res)
    assert res == 2

  def test_feature_NumberOfPendantNodes (self):
    # define the feature extractor class
    feat = GraphomicsTopology()

    # generate a random number of nodes
    n = np.random.randint(
      low=3,
      high=20
    )

    # create a complete graph
    G = nx.complete_graph(n=n)

    # evaluate the feature
    res = feat._GetNumberOfPendantNodes(G=G)

    # check the feature properties
    assert isinstance(res, int)
    assert np.isfinite(res)
    assert res == 0

    # create a star graph
    G = nx.star_graph(n=n)

    # evaluate the feature
    res = feat._GetNumberOfPendantNodes(G=G)

    # check the feature properties
    assert isinstance(res, int)
    assert np.isfinite(res)
    assert res == n

  def test_feature_NumberOfIsolatedNodes (self):
    # define the feature extractor class
    feat = GraphomicsTopology()

    # generate a random number of nodes
    n = np.random.randint(
      low=3,
      high=20
    )

    # create a complete graph
    G = nx.complete_graph(n=n)

    # evaluate the feature
    res = feat._GetNumberOfIsolatedNodes(G=G)

    # check the feature properties
    assert isinstance(res, int)
    assert np.isfinite(res)
    assert res == 0

    # create a star graph
    G = nx.star_graph(n=n)

    # evaluate the feature
    res = feat._GetNumberOfIsolatedNodes(G=G)

    # check the feature properties
    assert isinstance(res, int)
    assert np.isfinite(res)
    assert res == 0

  def test_feature_NumberOfConnectedComponents (self):
    # define the feature extractor class
    feat = GraphomicsTopology()

    # generate a random number of nodes
    n = np.random.randint(
      low=1,
      high=20
    )

    # create a first graph
    G1 = nx.complete_graph(range(0, 20, n))

    # evaluate the feature
    res = feat._GetNumberOfConnectedComponents(G=G1)

    # check the feature properties
    assert isinstance(res, int)
    assert np.isfinite(res)
    assert res == 1

    # create a second graph
    G2 = nx.complete_graph(range(20, 100, n))

    # merge the two graphs
    G = nx.compose(G1, G2)

    # evaluate the feature
    res = feat._GetNumberOfConnectedComponents(G=G)

    # check the feature properties
    assert isinstance(res, int)
    assert np.isfinite(res)
    assert res == 2

  def test_feature_ModularityScore (self):
    # define the feature extractor class
    feat = GraphomicsTopology()

    # generate a random number of nodes
    n = np.random.randint(
      low=3,
      high=20
    )

    # create a complete graph
    G = nx.complete_graph(n=n)

    # evaluate the feature
    res = feat._GetModularityScore(G=G)

    # check the feature properties
    assert isinstance(res, float)
    assert np.isfinite(res)
    assert res >= 0.

  def test_feature_NumberOfMaximalCliques (self):
    # define the feature extractor class
    feat = GraphomicsTopology()

    # generate a random number of nodes
    n = np.random.randint(
      low=10,
      high=20
    )

    # create a complete graph
    G = nx.complete_graph(n=n)

    # evaluate the feature
    res = feat._GetNumberOfMaximalCliques(G=G)

    # check the feature properties
    assert isinstance(res, int)
    assert np.isfinite(res)
    assert res >= 0.
