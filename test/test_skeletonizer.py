#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest

import numpy as np
import SimpleITK as sitk

# import filter for the image skeletonization
from graphomics import SkeletonizeImageFilter

__author__  = ['Nico Curti',
               'Gianluca Carlini',
               'Riccardo Biondi'
              ]
__email__ = ['nico.curti2@unibo.it',
             'gianluca.carlini3@unibo.it',
             'riccardo.biondi7@unibo.it'
            ]

class TestGraphFilter:
  '''
  Tests:
    - if the skeletonizer raises an error without a image
    - if the skeletonizer raises an error without the execute
    - if the skeletonizer raises an error with an image which is not 2D or 3D
    - if the skeletonizer works with 2D input
    - if the skeletonizer works with 3D input
  '''

  def test_skeletonezer_img_required (self):

    # construct the object
    skeleton_filter = SkeletonizeImageFilter()

    # execute the filter without a img
    with pytest.raises(TypeError):
      skeleton_filter.Execute()

  def test_skeletonezer_get_without_execute (self):

    # construct the object
    skeleton_filter = SkeletonizeImageFilter()

    # get the image without the execute
    with pytest.raises(RuntimeError):
      skeleton_filter.GetSkeletonImage()

  def test_ndim_2D_3D (self):

    # create a 4D image
    src = np.ones(shape=(10, 10, 10, 10), dtype=np.uint8)
    src = sitk.GetImageFromArray(src)

    # construct the object
    skeleton_filter = SkeletonizeImageFilter()

    # execute the filter with a 4D image
    # This error is raised by skimage function!
    with pytest.raises(ValueError):
      skeleton_filter.Execute(src=src)

  def test_ndim_2D (self):
    # test with 2D input
    src = np.ones(shape=(10, 10), dtype=np.uint8)
    src = sitk.GetImageFromArray(src)

    # construct the object
    skeleton_filter = SkeletonizeImageFilter()
    skeleton_filter.Execute(src=src)

    # get the skeleton image
    skeleton = skeleton_filter.GetSkeletonImage()

    assert isinstance(skeleton, sitk.Image)
    assert len(skeleton.GetSize()) == 2
    assert skeleton.GetSize() == src.GetSize()
    assert skeleton.GetDirection() == src.GetDirection()
    assert skeleton.GetSpacing() == src.GetSpacing()

  def test_ndim_3D (self):
    # test with 3D input
    src = np.ones(shape=(10, 10, 10), dtype=np.uint8)
    src = sitk.GetImageFromArray(src)

    # construct the object
    skeleton_filter = SkeletonizeImageFilter()
    skeleton_filter.Execute(src=src)

    # get the skeleton image
    skeleton = skeleton_filter.GetSkeletonImage()

    assert isinstance(skeleton, sitk.Image)
    assert len(skeleton.GetSize()) == 3
    assert skeleton.GetSize() == src.GetSize()
    assert skeleton.GetDirection() == src.GetDirection()
    assert skeleton.GetSpacing() == src.GetSpacing()
