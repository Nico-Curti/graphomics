#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest

import numpy as np
import SimpleITK as sitk

# import filter for the medical image loading
from graphomics import LoadImageFileInAnyFormat
# import filter for the image skeletonization
from graphomics import SkeletonizeImageFilter
# import filter for the skeleton graph extraction
from graphomics import GraphThicknessImageFilter
# import the test sample downloader
from .download_from_drive import download_file_from_google_drive

__author__  = ['Nico Curti',
               'Gianluca Carlini',
               'Riccardo Biondi'
              ]
__email__ = ['nico.curti2@unibo.it',
             'gianluca.carlini3@unibo.it',
             'riccardo.biondi7@unibo.it'
            ]

# get the path of the sample image directory
sample_dir = os.path.join(
  os.path.abspath(
    os.path.dirname(__file__)
  ),
  '../samples'
)

# define the path of the sample image
img_sample = os.path.join(sample_dir, 'brain_seg_anon.nii')

if not os.path.exists(img_sample):
  # create the folder to store the files
  os.makedirs(sample_dir, exist_ok=True)

  # download the sample image
  download_file_from_google_drive(
    Id='1UBPKRkadArzZBbBn3GeCDRDIOy199NeB',
    destination=img_sample
  )


class TestGraphFilter:
  '''
  Tests:
    - if the skeletonizer raises an error without a image
    - if the graph filter raises an error without a image
    - if the skeletonizer raises an error with an image which is not 2D or 3D
    - if the number of nodes is equal to the number of negative connected components
    - if the number of edges is equal to the number of positive connected components
    - if the number of lut keys is equal to the number of positive connected components
    - if all the lut keys are in the edge map and all the labels in the edge map are in the lut keys
    - if the edge map is equal to the skeleton
    - if there are no pixels equal to -1 in the edge map
  '''

  def test_graph_filter_img_required (self):

    # construct the object
    graph_filter = GraphThicknessImageFilter()

    # execute the filter without a img
    with pytest.raises(TypeError):
      graph_filter.Execute()

  def test_graph_filter_get_without_execute (self):

    # construct the object
    graph_filter = GraphThicknessImageFilter()

    # get the nodes without the execute
    with pytest.raises(RuntimeError):
      graph_filter.GetNodeIndexes()
    with pytest.raises(RuntimeError):
      graph_filter.GetNodePhysicalPoints()

    # get the edges without the execute
    with pytest.raises(RuntimeError):
      graph_filter.GetEdgeIndexes()
    with pytest.raises(RuntimeError):
      graph_filter.GetEdgePhysicalPoints()

    # get the lut without the execute
    with pytest.raises(RuntimeError):
      graph_filter.GetEdgeLUTIndexes()
    with pytest.raises(RuntimeError):
      graph_filter.GetEdgeLUTPhysicalPoints()

    # get the edge map without the execute
    with pytest.raises(RuntimeError):
      graph_filter.GetEdgeMap()
  
  def test_n_nodes_negative_components (self):
    
    # load the image
    mask = LoadImageFileInAnyFormat(
      filepath=img_sample,
      binarize=True,
      equal_spacing=True
    )

    # skeletonize the image
    skeleton_filter = SkeletonizeImageFilter()
    skeleton_filter.Execute(src=mask)
    skeleton = skeleton_filter.GetSkeletonImage()

    # get the number of dimensions
    ndim = len(skeleton.GetSize())

    # compute the graph
    graph_filter = GraphThicknessImageFilter()
    graph_filter.SetInputDimensionality(ndim=ndim)
    graph_filter.Execute(src=skeleton)

    # get the nodes and the edge map
    nodelist = graph_filter.GetNodeIndexes()
    edgemap = graph_filter.GetEdgeMap()

    # get the number of negative connected components in the edge map
    _stats = sitk.LabelShapeStatisticsImageFilter()
    _stats.SetBackgroundValue(0)
    _stats.SetGlobalDefaultNumberOfThreads(1)
    _stats.Execute(edgemap)
    n_cc_nodes = len([x for x in _stats.GetLabels() if x < 0])

    # check if the number of nodes is equal to the number of 
    # negative connected components
    assert len(nodelist) == n_cc_nodes

    # check if nodes are sequential
    cc_nodes = [x for x in _stats.GetLabels() if x < 0]
    assert all([x in range(-2, -len(nodelist) - 2, -1) for x in cc_nodes])

  def test_n_edges_positive_components (self):
      
    # load the image
    mask = LoadImageFileInAnyFormat(
      filepath=img_sample,
      binarize=True,
      equal_spacing=True
    )

    # skeletonize the image
    skeleton_filter = SkeletonizeImageFilter()
    skeleton_filter.Execute(src=mask)
    skeleton = skeleton_filter.GetSkeletonImage()
    
    # get the number of dimensions
    ndim = len(skeleton.GetSize())

    # compute the graph
    graph_filter = GraphThicknessImageFilter()
    graph_filter.SetInputDimensionality(ndim=ndim)
    graph_filter.Execute(src=skeleton)

    # get the edges and the edge map
    edgelist = graph_filter.GetEdgeIndexes()
    edgemap = graph_filter.GetEdgeMap()

    # get the number of positive connected components in the edge map    
    _stats = sitk.LabelShapeStatisticsImageFilter()
    _stats.SetBackgroundValue(0)
    _stats.SetGlobalDefaultNumberOfThreads(1)
    _stats.Execute(edgemap)
    n_cc_edges = len([x for x in _stats.GetLabels() if x > 0])

    # check if the number of edges is equal to the number of
    # positive connected components
    assert len(edgelist) == n_cc_edges

    # check if edges are sequential
    cc_edges = [x for x in _stats.GetLabels() if x > 0]
    assert all([x in range(1, len(edgelist) + 1) for x in cc_edges])

  def test_n_edges_lut_keys (self):
      
    # load the image
    mask = LoadImageFileInAnyFormat(
      filepath=img_sample,
      binarize=True,
      equal_spacing=True
    )

    # skeletonize the image
    skeleton_filter = SkeletonizeImageFilter()
    skeleton_filter.Execute(src=mask)
    skeleton = skeleton_filter.GetSkeletonImage()

    # get the number of dimensions
    ndim = len(skeleton.GetSize())

    # compute the graph
    graph_filter = GraphThicknessImageFilter()
    graph_filter.SetInputDimensionality(ndim=ndim)
    graph_filter.Execute(src=skeleton)

    # get the lut and the edge map
    lut = graph_filter.GetEdgeLUTIndexes()
    edgemap = graph_filter.GetEdgeMap()
  
    # get the number of positive connected components in the edge map
    _stats = sitk.LabelShapeStatisticsImageFilter()
    _stats.SetBackgroundValue(0)
    _stats.SetGlobalDefaultNumberOfThreads(1)
    _stats.Execute(edgemap)
    n_cc_edges = len([x for x in _stats.GetLabels() if x > 0])

    # check if the number of lut keys is equal to the number of
    # positive connected components
    assert len(lut) == n_cc_edges

    # check if lut keys are sequential
    lut_keys = list(lut.keys())
    assert all([x in range(1, len(lut) + 1) for x in lut_keys])

  def test_lut_keys_in_edge_map (self):
      
    # load the image
    mask = LoadImageFileInAnyFormat(
      filepath=img_sample,
      binarize=True,
      equal_spacing=True
    )
    
    # skeletonize the image
    skeleton_filter = SkeletonizeImageFilter()
    skeleton_filter.Execute(src=mask)
    skeleton = skeleton_filter.GetSkeletonImage()

    # get the number of dimensions
    ndim = len(skeleton.GetSize())

    # compute the graph
    graph_filter = GraphThicknessImageFilter()
    graph_filter.SetInputDimensionality(ndim=ndim)
    graph_filter.Execute(src=skeleton)

    # get the lut and the edge map
    lut = graph_filter.GetEdgeLUTIndexes()
    edgemap = graph_filter.GetEdgeMap()

    # get the labels of positive connected components in the edge map    
    _stats = sitk.LabelShapeStatisticsImageFilter()
    _stats.SetBackgroundValue(0)
    _stats.SetGlobalDefaultNumberOfThreads(1)
    _stats.Execute(edgemap)
    cc_edges = [x for x in _stats.GetLabels() if x > 0]

    # check if all the lut keys are in the edge map
    # and all the labels in the edge map are in the lut keys
    assert all([x in lut.keys() for x in cc_edges])
    assert all([x in cc_edges for x in lut.keys()])

  def test_edgemap_equals_skeleton (self):
      
    # load the image
    mask = LoadImageFileInAnyFormat(
      filepath=img_sample,
      binarize=True,
      equal_spacing=True
    )
  
    # skeletonize the image
    skeleton_filter = SkeletonizeImageFilter()
    skeleton_filter.Execute(src=mask)
    skeleton = skeleton_filter.GetSkeletonImage()

    # get the number of dimensions
    ndim = len(skeleton.GetSize())

    # compute the graph
    graph_filter = GraphThicknessImageFilter()
    graph_filter.SetInputDimensionality(ndim=ndim)
    graph_filter.Execute(src=skeleton)

    # get the edge map and binarize it
    edgemap = graph_filter.GetEdgeMap()
    edgemap = edgemap != 0

    # binarize the skeleton (just to be sure)
    skeleton = skeleton != 0

    # check if skeleton and edge map have the same physical properties
    assert skeleton.GetSize() == edgemap.GetSize()
    assert skeleton.GetSpacing() == edgemap.GetSpacing()
    assert skeleton.GetOrigin() == edgemap.GetOrigin()
    assert skeleton.GetDirection() == edgemap.GetDirection()

    # subtract the edge map from the skeleton
    diff = sitk.Subtract(skeleton, edgemap)

    # assert that the diff is 0
    assert sitk.GetArrayViewFromImage(diff).sum() == 0

  def test_no_neighbour_pixels (self):

    # load the image
    mask = LoadImageFileInAnyFormat(
      filepath=img_sample,
      binarize=True,
      equal_spacing=True
    )

    # skeletonize the image
    skeleton_filter = SkeletonizeImageFilter()
    skeleton_filter.Execute(src=mask)
    skeleton = skeleton_filter.GetSkeletonImage()

    # get the number of dimensions
    ndim = len(skeleton.GetSize())

    # compute the graph
    graph_filter = GraphThicknessImageFilter()
    graph_filter.SetInputDimensionality(ndim=ndim)
    graph_filter.Execute(src=skeleton)

    # get the edge map
    edgemap = graph_filter.GetEdgeMap()

    # get the edge map pixels equal to -1
    edgemap = edgemap == -1

    # assert that there are no pixels equal to -1
    assert sitk.GetArrayViewFromImage(edgemap).sum() == 0
