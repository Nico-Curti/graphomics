import os
import pytest
from graphomics import GraphThicknessImageFilter
from graphomics import LoadImageFileInAnyFormat
from graphomics import SkeletonizeImageFilter
import SimpleITK as sitk
import numpy as np

__author__  = ['Nico Curti',
               'Gianluca Carlini',
               'Riccardo Biondi'
              ]
__email__ = ['nico.curti2@unibo.it',
             'gianluca.carlini3@unibo.it',
             'riccardo.biondi7@unibo.it'
            ]

img_sample = os.path.join(
  os.path.abspath(
    os.path.dirname(__file__)
  ),
  '../samples/brain_seg.nii'
)


class TestGraphFilter:
  """
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
  """
  
  def test_skeletonezer_img_required (self):

    # construct the object
    skeleton_filter = SkeletonizeImageFilter()
    
    # execute the filter without a img
    with pytest.raises(TypeError):
      skeleton_filter.Execute()

  def test_graph_filter_img_required (self):

    # construct the object
    graph_filter = GraphThicknessImageFilter()

    # execute the filter without a img
    with pytest.raises(TypeError):
      graph_filter.Execute()
  
  def test_ndim_2D_3D (self):
    
    # create a 4D image
    src = np.ones(shape=(10, 10, 10, 10), dtype=np.uint8)
    src = sitk.GetImageFromArray(src)

    # construct the object
    skeleton_filter = SkeletonizeImageFilter()

    # execute the filter with a 4D image
    with pytest.raises(ValueError):
      skeleton_filter.Execute(src=src)

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

