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
# import filter for the skeleton graph extraction
from graphomics import GraphThicknessImageFilter
# import filters for graph weighing
from graphomics import (
  NodePairwiseDistanceFilter,
  EdgeLengthPathsFilter,
  EdgeLabelWeightFilter,
  GraphFilter
)

__author__  = ['Nico Curti',
               'Gianluca Carlini',
               'Riccardo Biondi'
              ]
__email__ = ['nico.curti2@unibo.it',
             'gianluca.carlini3@unibo.it',
             'riccardo.biondi7@unibo.it'
            ]


class TestGraphWeightsExtractor:
  '''
  Tests all the available graph weight extractor
  and their properties.
  '''

  def test_NodePairwiseDistance_weights (self):
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

    # compute the graph
    graph_filter = GraphThicknessImageFilter()
    graph_filter.SetInputDimensionality(ndim=len(volume.shape))
    graph_filter.Execute(src=skeleton)

    # get the resulting graph properties
    nodelist = graph_filter.GetNodePhysicalPoints()
    edgelist = graph_filter.GetEdgePhysicalPoints()
    lut = graph_filter.GetEdgeLUTPhysicalPoints()
    mapper = graph_filter.GetEdgeMap()

    # create the weight extractor filter
    wtype = NodePairwiseDistanceFilter()

    # raise an error if we get the edges without execute
    with pytest.raises(RuntimeError):
      wtype.GetWeightsList()

    # apply the weight extractor to the graph
    wtype.Execute(
      nodelist=nodelist,
      edgelist=edgelist,
      lut=lut,
      mapper=mapper,
    )

    # get the computed weights from the filter
    weights = wtype.GetWeightsList()

    # check the correctness of the weights
    assert len(weights) == len(edgelist)
    assert weights.keys() == lut.keys()
    assert isinstance(weights, dict)
    assert all(isinstance(x, float) for x in weights.values())

  def test_EdgeLengthPaths_weights (self):
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

    # compute the graph
    graph_filter = GraphThicknessImageFilter()
    graph_filter.SetInputDimensionality(ndim=len(volume.shape))
    graph_filter.Execute(src=skeleton)

    # get the resulting graph properties
    nodelist = graph_filter.GetNodePhysicalPoints()
    edgelist = graph_filter.GetEdgePhysicalPoints()
    lut = graph_filter.GetEdgeLUTPhysicalPoints()
    mapper = graph_filter.GetEdgeMap()

    # create the weight extractor filter
    wtype = EdgeLengthPathsFilter()
    wtype.SetGlobalDefaultNumberOfThreads(1)

    # raise an error if we get the edges without execute
    with pytest.raises(RuntimeError):
      wtype.GetWeightsList()

    # apply the weight extractor to the graph
    wtype.Execute(
      nodelist=nodelist,
      edgelist=edgelist,
      lut=lut,
      mapper=mapper,
    )

    # get the computed weights from the filter
    weights = wtype.GetWeightsList()

    # check the correctness of the weights
    assert len(weights) == len(edgelist)
    assert weights.keys() == lut.keys()
    assert isinstance(weights, dict)
    assert all(isinstance(x, int) for x in weights.values())

  def test_EdgeLabelWeight_weights (self):
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

    # compute the graph
    graph_filter = GraphThicknessImageFilter()
    graph_filter.SetInputDimensionality(ndim=len(volume.shape))
    graph_filter.Execute(src=skeleton)

    # get the resulting graph properties
    nodelist = graph_filter.GetNodePhysicalPoints()
    edgelist = graph_filter.GetEdgePhysicalPoints()
    lut = graph_filter.GetEdgeLUTPhysicalPoints()
    mapper = graph_filter.GetEdgeMap()

    # create the weight extractor filter
    wtype = EdgeLabelWeightFilter()
    wtype.SetGlobalDefaultNumberOfThreads(1)

    # raise an error if we get the edges without execute
    with pytest.raises(RuntimeError):
      wtype.GetWeightsList()

    # raise an error if the metric is incorrect
    with pytest.raises(ValueError):
      wtype.Execute(
      nodelist=nodelist,
      edgelist=edgelist,
      lut=lut,
      mapper=mapper,
      labelmap=mapper,
      metric='dummy'
    )

    # apply the weight extractor to the graph
    wtype.Execute(
      nodelist=nodelist,
      edgelist=edgelist,
      lut=lut,
      mapper=mapper,
      labelmap=mapper,
    )

    # get the computed weights from the filter
    weights = wtype.GetWeightsList()

    # check the correctness of the weights
    assert len(weights) == len(edgelist)
    assert weights.keys() == lut.keys()
    assert isinstance(weights, dict)
    assert all(isinstance(x, float) for x in weights.values())

    # create the weight extractor filter with a custom metric
    wtype.Execute(
      nodelist=nodelist,
      edgelist=edgelist,
      lut=lut,
      mapper=mapper,
      labelmap=mapper,
      metric=np.nanmean,
    )

    # get the computed weights from the filter
    weights = wtype.GetWeightsList()

    # check the correctness of the weights
    assert len(weights) == len(edgelist)
    assert weights.keys() == lut.keys()
    assert isinstance(weights, dict)
    assert all(isinstance(x, float) for x in weights.values())

  def test_GraphFilter (self):
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

    # compute the graph
    graph_filter = GraphThicknessImageFilter()
    graph_filter.SetInputDimensionality(ndim=len(volume.shape))
    graph_filter.Execute(src=skeleton)

    # get the resulting graph properties
    nodelist = graph_filter.GetNodePhysicalPoints()
    edgelist = graph_filter.GetEdgePhysicalPoints()
    lut = graph_filter.GetEdgeLUTPhysicalPoints()
    mapper = graph_filter.GetEdgeMap()

    # check the graph filter
    graph_proxy = GraphFilter()

    # raise an error if we get the edges without execute
    with pytest.raises(RuntimeError):
      graph_proxy.GetGraph()

    # execute the filter on the inputs
    graph_proxy.Execute(
      lut=lut,
      weights=None
    )

    # get the graph and store it in the common inputs
    G = graph_proxy.GetGraph()

    # check the correctness of the output
    assert isinstance(G, nx.Graph)
    assert len(G.nodes()) > 0
    assert len(G.edges()) > 0
    assert nx.get_edge_attributes(G, name='weight') == {}

    # raise an error if we use an incorrect number of weights
    with pytest.raises(ValueError):
      w = {k : 1 for k in lut.keys()}
      # add an extra key
      w[-1] = 1.
      graph_proxy.Execute(
        lut=lut,
        weights=w
      )
    # raise an error if we use an incorrect set of keys
    with pytest.raises(ValueError):
      graph_proxy.Execute(
        lut=lut,
        weights={k + 1 : 1 for k in lut.keys()}
      )

    # execute the filter on the inputs
    graph_proxy.Execute(
      lut=lut,
      weights={k : 1 for k in lut.keys()}
    )

    # get the graph and store it in the common inputs
    G = graph_proxy.GetGraph()

    # check the correctness of the output
    assert isinstance(G, nx.Graph)
    assert len(G.nodes()) > 0
    assert len(G.edges()) > 0
    assert nx.get_edge_attributes(G, name='weight') == {e : 1. for e in G.edges()}
