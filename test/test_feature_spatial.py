#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

import numpy as np
import networkx as nx
import SimpleITK as sitk
# generation of random binary blobs
from skimage.data import binary_blobs

# import filter for the image skeletonization
from graphomics import SkeletonizeImageFilter
# import filters for spatial graphomics features
from graphomics import GraphomicsSpatial

__author__  = ['Nico Curti',
               'Gianluca Carlini',
               'Riccardo Biondi'
              ]
__email__ = ['nico.curti2@unibo.it',
             'gianluca.carlini3@unibo.it',
             'riccardo.biondi7@unibo.it'
            ]


class TestFeatureSpatial:
  '''
  Tests all the possible outcomes of each feature
  belonging to the class Spatial.
  '''

  def test_feature_NodeDensityStatistics (self):
    # define the feature extractor class
    feat = GraphomicsSpatial()

    # generate a random number of nodes
    n = np.random.randint(
      low=3,
      high=30
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

    #evaluate the feature
    res = feat._GetNodeDensityStatistics(G=G)

    # check the feature properties
    assert isinstance(res, dict)
    for k, v in res.items():
      assert k.startswith('node_density')
      assert isinstance(k, str)
      assert v >= 0.
      assert isinstance(v, float)
      assert np.isfinite(v)

  def test_feature_FractalDimension (self):
    # define the feature extractor class
    feat = GraphomicsSpatial()

    # create a random binary volume
    volume = binary_blobs(
      length=64,
      blob_size_fraction=.5,
      volume_fraction=.1,
      seed=42,
      n_dim=3
    )
    # convert it to a sitk format
    mask = sitk.GetImageFromArray(np.uint8(volume))

    # skeletonize the image
    skeleton_filter = SkeletonizeImageFilter()
    skeleton_filter.Execute(src=mask)
    skeleton = skeleton_filter.GetSkeletonImage()

    #evaluate the feature
    res = feat._GetFractalDimension(skeleton=skeleton)

    # check the feature properties
    assert isinstance(res, float)
    assert res >= 0.
    assert np.isfinite(res)

    #evaluate the feature
    res = feat._GetFractalDimension(
      skeleton=skeleton,
      max_box_size=4
    )

    # check the feature properties
    assert isinstance(res, float)
    assert res >= 0.
    assert np.isfinite(res)

    #evaluate the feature
    res = feat._GetFractalDimension(
      skeleton=skeleton,
      n_offsets=1
    )

    # check the feature properties
    assert isinstance(res, float)
    assert res >= 0.
    assert np.isfinite(res)

  def test_feature_AverageShortestPathLength (self):
    # define the feature extractor class
    feat = GraphomicsSpatial()

    # generate a random number of nodes
    n = np.random.randint(
      low=3,
      high=30
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

    #evaluate the feature
    res = feat._GetAverageShortestPathLength(G=G)

    # check the feature properties
    assert res >= 0.
    assert np.isfinite(res)

    # create a second graph
    G2 = nx.complete_graph(range(40, 100, n))

    # merge the two graphs
    G = nx.compose(G, G2)

    #evaluate the feature
    res = feat._GetAverageShortestPathLength(G=G)

    # check the feature properties
    assert res >= 0.
    assert np.isfinite(res)

  def test_feature_Eccentricity (self):
    # define the feature extractor class
    feat = GraphomicsSpatial()

    # generate a random number of nodes
    n = np.random.randint(
      low=3,
      high=30
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

    #evaluate the feature
    res = feat._GetEccentricity(G=G)

    # check the feature properties
    assert isinstance(res, dict)
    for k, v in res.items():
      assert k.startswith('node_eccentricity')
      assert isinstance(k, str)
      assert v >= 0.
      assert np.isfinite(v)

    # create a second graph
    G2 = nx.complete_graph(range(40, 100, n))

    # merge the two graphs
    G = nx.compose(G, G2)

    #evaluate the feature
    res = feat._GetEccentricity(G=G)

    # check the feature properties
    assert isinstance(res, dict)
    for k, v in res.items():
      assert k.startswith('node_eccentricity')
      assert isinstance(k, str)
      assert v >= 0.
      assert np.isfinite(v)

  def test_feature_CenterOfMass (self):
    # define the feature extractor class
    feat = GraphomicsSpatial()

    # generate a random number of nodes
    n = np.random.randint(
      low=3,
      high=30
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

    #evaluate the feature
    res = feat._GetCenterOfMass(G=G)

    # check the feature properties
    assert isinstance(res, float)
    assert res >= 0
    assert np.isfinite(res)

  def test_feature_DistanceMostCentralNodes (self):
    # define the feature extractor class
    feat = GraphomicsSpatial()

    # generate a random number of nodes
    n = np.random.randint(
      low=3,
      high=30
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
    # re-label the nodes to create 3D tuples of coords
    nx.relabel_nodes(
      G=G,
      mapping={
        k : tuple(np.random.uniform(low=0., high=1., size=(3, )))
        for k in G.nodes()
      },
      copy=False
    )

    #evaluate the feature
    res = feat._GetDistanceMostCentralNodes(G=G)
    topk = min(G.number_of_nodes() - 1, 10)

    # check the feature properties
    assert isinstance(res, dict)
    for k, v in res.items():
      assert k.startswith(f'node_top{topk}_distance')
      assert isinstance(k, str)
      assert v >= 0.
      assert isinstance(v, float)
      assert np.isfinite(v)

  def test_feature_DistanceNoPendantNodes (self):
    # define the feature extractor class
    feat = GraphomicsSpatial()

    # generate a random number of nodes
    n = np.random.randint(
      low=3,
      high=30
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
    # re-label the nodes to create 3D tuples of coords
    nx.relabel_nodes(
      G=G,
      mapping={
        k : tuple(np.random.uniform(low=0., high=1., size=(3, )))
        for k in G.nodes()
      },
      copy=False
    )

    #evaluate the feature
    res = feat._GetDistanceNoPendantNodes(G=G)

    # check the feature properties
    assert isinstance(res, dict)
    for k, v in res.items():
      assert k.startswith('node_no_pendant_distance')
      assert isinstance(k, str)
      assert v >= 0.
      assert isinstance(v, float)
      assert np.isfinite(v)

  def test_feature_DistancePendantNodes (self):
    # define the feature extractor class
    feat = GraphomicsSpatial()

    # generate a random number of nodes
    n = np.random.randint(
      low=3,
      high=30
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
    # re-label the nodes to create 3D tuples of coords
    mapping = {
      k : tuple(np.random.uniform(low=0., high=1., size=(3, )))
      for k in G.nodes()
    }
    nx.relabel_nodes(
      G=G,
      mapping=mapping,
      copy=False
    )

    #evaluate the feature
    res = feat._GetDistancePendantNodes(G=G)

    # check the feature properties
    assert isinstance(res, dict)
    for k, v in res.items():
      assert k.startswith('node_pendant_distance')
      assert isinstance(k, str)
      assert v >= 0.
      assert isinstance(v, float)
      assert np.isfinite(v)

    # create a complete graph
    G = nx.complete_graph(n=n)
    # re-label the nodes to create 3D tuples of coords
    nx.relabel_nodes(
      G=G,
      mapping=mapping,
      copy=False
    )

    #evaluate the feature
    res2 = feat._GetDistancePendantNodes(G=G)

    # check the feature properties
    assert isinstance(res2, dict)
    for k, v in res2.items():
      assert k.startswith('node_pendant_distance')
      assert isinstance(k, str)
      assert v >= 0.
      assert isinstance(v, float)
      assert np.isfinite(v)
