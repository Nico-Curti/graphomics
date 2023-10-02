#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest

import numpy as np
import skimage as sk
import SimpleITK as sitk
from functools import partial
# generation of random binary blobs
from skimage.data import binary_blobs

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

img = LoadImageFileInAnyFormat(img_sample, binarize=True, equal_spacing=True)

skeleton_filter = SkeletonizeImageFilter()
skeleton_filter.Execute(src=img)
skeleton_3d = skeleton_filter.GetSkeletonImage()

_slice = img[:, :, img.GetSize()[2] // 2]
skeleton_filter.Execute(src=_slice)
skeleton_2d = skeleton_filter.GetSkeletonImage()

# get the skimage version for retro-compatibility
binary_blobs_3d = partial(binary_blobs,
  length=128,
  blob_size_fraction=.25,
  volume_fraction=.5,
  n_dim=3
)
binary_blobs_2d = partial(binary_blobs,
  length=128,
  blob_size_fraction=.25,
  volume_fraction=.5,
  n_dim=2
)
sk_major, sk_minor, *_ = sk.__version__.split('.')

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

    # get the edges lut without the execute
    with pytest.raises(RuntimeError):
      graph_filter.GetEdgeLUTIndexes()
    with pytest.raises(RuntimeError):
      graph_filter.GetEdgeLUTPhysicalPoints()
    
    # get the nodes lut without the execute
    with pytest.raises(RuntimeError):
      graph_filter.GetNodeLUTIndexes()
    with pytest.raises(RuntimeError):
      graph_filter.GetNodeLUTPhysicalPoints()

    # get the edge map without the execute
    with pytest.raises(RuntimeError):
      graph_filter.GetEdgeMap()
  
  def test_ndim_not_2D_3D (self):
    
    # create a random dimension between 4 and 10
    ndim = np.random.randint(4, 10)
    
    # construct the object
    graph_filter = GraphThicknessImageFilter()

    with pytest.raises(ValueError):
      # set the dimensionality
      graph_filter.SetInputDimensionality(ndim)

  def set_number_of_threads (self):
    
    # create a random number of threads between 1 and 100
    n_threads = np.random.randint(1, 100)
    
    # construct the object
    graph_filter = GraphThicknessImageFilter()
    
    # set the number of threads
    graph_filter.SetGlobalDefaultNumberOfThreads(n_threads)

  @pytest.mark.parametrize('inpt, volume',
                           [(skeleton_3d, True), (skeleton_2d, False),
                            *[(np.random.randint(0, 1e5), True) for _ in range(2)],
                            *[(np.random.randint(0, 1e5), False) for _ in range(2)],])
  def test_n_nodes_negative_components (self, inpt, volume):
    
    # load or create the image
    if isinstance(inpt, sitk.Image):
      skeleton = inpt
    else:
      # create a random mask, either 2D or 3D
      if volume:
        mask = binary_blobs_3d(seed=inpt) if sk_major == '0' and int(sk_minor) < 21 else binary_blobs_3d(rng=inpt)
      else:
        mask = binary_blobs_2d(seed=inpt) if sk_major == '0' and int(sk_minor) < 21 else binary_blobs_2d(rng=inpt)

      mask = sitk.GetImageFromArray(mask.astype(np.uint8))

      # skeletonize the image
      skeleton_filter = SkeletonizeImageFilter()
      skeleton_filter.Execute(src=mask)
      skeleton = skeleton_filter.GetSkeletonImage()

    # compute the graph
    graph_filter = GraphThicknessImageFilter()
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

  @pytest.mark.parametrize('inpt, volume',
                           [(skeleton_3d, True), (skeleton_2d, False),
                            *[(np.random.randint(0, 1e5), True) for _ in range(2)],
                            *[(np.random.randint(0, 1e5), False) for _ in range(2)],])
  def test_n_edges_positive_components (self, inpt, volume):
      
    # load or create the image
    if isinstance(inpt, sitk.Image):
      skeleton = inpt
    else:
      # create a random mask, either 2D or 3D
      if volume:
        mask = binary_blobs_3d(seed=inpt) if sk_major == '0' and int(sk_minor) < 21 else binary_blobs_3d(rng=inpt)
      else:
        mask = binary_blobs_2d(seed=inpt) if sk_major == '0' and int(sk_minor) < 21 else binary_blobs_2d(rng=inpt)

      mask = sitk.GetImageFromArray(mask.astype(np.uint8))

      # skeletonize the image
      skeleton_filter = SkeletonizeImageFilter()
      skeleton_filter.Execute(src=mask)
      skeleton = skeleton_filter.GetSkeletonImage()
    
    # compute the graph
    graph_filter = GraphThicknessImageFilter()
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

  @pytest.mark.parametrize('inpt, volume',
                           [(skeleton_3d, True), (skeleton_2d, False),
                            *[(np.random.randint(0, 1e5), True) for _ in range(2)],
                            *[(np.random.randint(0, 1e5), False) for _ in range(2)],])
  def test_n_edges_lut_keys (self, inpt, volume):
      
    # load or create the image
    if isinstance(inpt, sitk.Image):
      skeleton = inpt
    else:
      # create a random mask, either 2D or 3D
      if volume:
        mask = binary_blobs_3d(seed=inpt) if sk_major == '0' and int(sk_minor) < 21 else binary_blobs_3d(rng=inpt)
      else:
        mask = binary_blobs_2d(seed=inpt) if sk_major == '0' and int(sk_minor) < 21 else binary_blobs_2d(rng=inpt)

      mask = sitk.GetImageFromArray(mask.astype(np.uint8))

      # skeletonize the image
      skeleton_filter = SkeletonizeImageFilter()
      skeleton_filter.Execute(src=mask)
      skeleton = skeleton_filter.GetSkeletonImage()

    # compute the graph
    graph_filter = GraphThicknessImageFilter()
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
    assert all([x in list(range(1, len(lut) + 1)) for x in lut_keys])

  @pytest.mark.parametrize('inpt, volume',
                           [(skeleton_3d, True), (skeleton_2d, False),
                            *[(np.random.randint(0, 1e5), True) for _ in range(2)],
                            *[(np.random.randint(0, 1e5), False) for _ in range(2)],])
  def n_nodes_lut_keys(self, inpt, volume):
    
    # load or create the image
    if isinstance(inpt, sitk.Image):
      skeleton = inpt
    else:
      # create a random mask, either 2D or 3D
      if volume:
        mask = binary_blobs_3d(seed=inpt) if sk_major == '0' and int(sk_minor) < 21 else binary_blobs_3d(rng=inpt)
      else:
        mask = binary_blobs_2d(seed=inpt) if sk_major == '0' and int(sk_minor) < 21 else binary_blobs_2d(rng=inpt)

      mask = sitk.GetImageFromArray(mask.astype(np.uint8))

      # skeletonize the image
      skeleton_filter = SkeletonizeImageFilter()
      skeleton_filter.Execute(src=mask)
      skeleton = skeleton_filter.GetSkeletonImage()

    # compute the graph
    graph_filter = GraphThicknessImageFilter()
    graph_filter.Execute(src=skeleton)

    # get the lut and the edge map
    lut = graph_filter.GetNodeLUTIndexes()
    edgemap = graph_filter.GetEdgeMap()
  
    # get the number of positive connected components in the edge map
    _stats = sitk.LabelShapeStatisticsImageFilter()
    _stats.SetBackgroundValue(0)
    _stats.SetGlobalDefaultNumberOfThreads(1)
    _stats.Execute(edgemap)
    n_cc_nodes = len([x for x in _stats.GetLabels() if x < 0])

    # check if the number of lut keys is equal to the number of
    # positive connected components
    assert len(lut) == n_cc_nodes

    # check if lut keys are sequential
    lut_keys = list(lut.keys())
    assert all([x in list(range(1, len(lut) + 1)) for x in lut_keys])

  @pytest.mark.parametrize('inpt, volume',
                           [(skeleton_3d, True), (skeleton_2d, False),
                            *[(np.random.randint(0, 1e5), True) for _ in range(2)],
                            *[(np.random.randint(0, 1e5), False) for _ in range(2)],])
  def test_edge_lut_keys_in_edge_map (self, inpt, volume):
      
    # load or create the image
    if isinstance(inpt, sitk.Image):
      skeleton = inpt
    else:
      # create a random mask, either 2D or 3D
      if volume:
        mask = binary_blobs_3d(seed=inpt) if sk_major == '0' and int(sk_minor) < 21 else binary_blobs_3d(rng=inpt)
      else:
        mask = binary_blobs_2d(seed=inpt) if sk_major == '0' and int(sk_minor) < 21 else binary_blobs_2d(rng=inpt)

      mask = sitk.GetImageFromArray(mask.astype(np.uint8))
    
      # skeletonize the image
      skeleton_filter = SkeletonizeImageFilter()
      skeleton_filter.Execute(src=mask)
      skeleton = skeleton_filter.GetSkeletonImage()

    # compute the graph
    graph_filter = GraphThicknessImageFilter()
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

  @pytest.mark.parametrize('inpt, volume',
                           [(skeleton_3d, True), (skeleton_2d, False),
                            *[(np.random.randint(0, 1e5), True) for _ in range(2)],
                            *[(np.random.randint(0, 1e5), False) for _ in range(2)],])
  def test_node_lut_keys_in_edge_map(self, inpt, volume):

    # load or create the image
    if isinstance(inpt, sitk.Image):
      skeleton = inpt
    else:
      # create a random mask, either 2D or 3D
      if volume:
        mask = binary_blobs_3d(seed=inpt) if sk_major == '0' and int(sk_minor) < 21 else binary_blobs_3d(rng=inpt)
      else:
        mask = binary_blobs_2d(seed=inpt) if sk_major == '0' and int(sk_minor) < 21 else binary_blobs_2d(rng=inpt)

      mask = sitk.GetImageFromArray(mask.astype(np.uint8))
    
      # skeletonize the image
      skeleton_filter = SkeletonizeImageFilter()
      skeleton_filter.Execute(src=mask)
      skeleton = skeleton_filter.GetSkeletonImage()

    # compute the graph
    graph_filter = GraphThicknessImageFilter()
    graph_filter.Execute(src=skeleton)

    # get the lut and the edge map
    # here we take the physical points and not the indexes
    # just to cover more test cases
    lut = graph_filter.GetNodeLUTPhysicalPoints()
    edgemap = graph_filter.GetEdgeMap()

    # get the labels of positive connected components in the edge map    
    _stats = sitk.LabelShapeStatisticsImageFilter()
    _stats.SetBackgroundValue(0)
    _stats.SetGlobalDefaultNumberOfThreads(1)
    _stats.Execute(edgemap)
    cc_nodes = [x for x in _stats.GetLabels() if x < 0]

    # check if all the lut keys are in the edge map
    # and all the labels in the edge map are in the lut keys
    assert all([abs(x + 1) in lut.keys() for x in cc_nodes])
    assert all([- x - 1 in cc_nodes for x in lut.keys()])

  @pytest.mark.parametrize('inpt, volume',
                           [(skeleton_3d, True), (skeleton_2d, False),
                            *[(np.random.randint(0, 1e5), True) for _ in range(2)],
                            *[(np.random.randint(0, 1e5), False) for _ in range(2)],])
  def test_edgemap_equals_skeleton (self, inpt, volume):
      
    # load or create the image
    if isinstance(inpt, sitk.Image):
      skeleton = inpt
    else:
      # create a random mask, either 2D or 3D
      if volume:
        mask = binary_blobs_3d(seed=inpt) if sk_major == '0' and int(sk_minor) < 21 else binary_blobs_3d(rng=inpt)
      else:
        mask = binary_blobs_2d(seed=inpt) if sk_major == '0' and int(sk_minor) < 21 else binary_blobs_2d(rng=inpt)

      mask = sitk.GetImageFromArray(mask.astype(np.uint8))
  
      # skeletonize the image
      skeleton_filter = SkeletonizeImageFilter()
      skeleton_filter.Execute(src=mask)
      skeleton = skeleton_filter.GetSkeletonImage()

    # compute the graph
    graph_filter = GraphThicknessImageFilter()
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

  @pytest.mark.parametrize('inpt, volume',
                           [(skeleton_3d, True), (skeleton_2d, False),
                            *[(np.random.randint(0, 1e5), True) for _ in range(2)],
                            *[(np.random.randint(0, 1e5), False) for _ in range(2)],])
  def test_no_neighbour_pixels (self, inpt, volume):

    # load or create the image
    if isinstance(inpt, sitk.Image):
      skeleton = inpt
    else:
      # create a random mask, either 2D or 3D
      if volume:
        mask = binary_blobs_3d(seed=inpt) if sk_major == '0' and int(sk_minor) < 21 else binary_blobs_3d(rng=inpt)
      else:
        mask = binary_blobs_2d(seed=inpt) if sk_major == '0' and int(sk_minor) < 21 else binary_blobs_2d(rng=inpt)

      mask = sitk.GetImageFromArray(mask.astype(np.uint8))

      # skeletonize the image
      skeleton_filter = SkeletonizeImageFilter()
      skeleton_filter.Execute(src=mask)
      skeleton = skeleton_filter.GetSkeletonImage()

    # compute the graph
    graph_filter = GraphThicknessImageFilter()
    graph_filter.Execute(src=skeleton)

    # get the edge map
    edgemap = graph_filter.GetEdgeMap()

    # get the edge map pixels equal to -1
    edgemap = edgemap == -1

    # assert that there are no pixels equal to -1
    assert sitk.GetArrayViewFromImage(edgemap).sum() == 0
