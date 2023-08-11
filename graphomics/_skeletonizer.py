#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import SimpleITK as sitk
from skimage.morphology import skeletonize

__author__  = ['Nico Curti',
               'Gianluca Carlini',
               'Riccardo Biondi'
              ]
__email__ = ['nico.curti2@unibo.it',
             'gianluca.carlini2@unibo.it',
             'riccardo.biondi2@unibo.it'
            ]

__all__ = ['SkeletonizeImageFilter']


class SkeletonizeImageFilter (object):
  '''
  Skeletonizer binary filter in 2D and 3d

  This filter apply the skeletonization algorithm
  to extract a binary output containing only the
  backbone of the input shape.
  This object is just an utility class to wrap the
  skimage functions for 2D and 3D inputs.
  The filter returns an output in sitk.Image format,
  preserving all the metadata related to spacing and
  size of the pixels/voxels.
  '''

  def __init__ (self):
    pass

  def Execute (self, src : sitk.Image) :
    '''
    Perform the skeletonization algorithm.

    Skeletonization reduces binary objects to 1 pixel
    wide representations.

    Skeletonization 2D: Zhang's method [1].
    Zhang's method works by making successive passes of
    the image, removing pixels on object borders.
    This continues until no more pixels can be removed.
    The image is correlated with a mask that assigns each
    pixel a number in the range [0…255] corresponding to
    each possible pattern of its 8 neighboring pixels.
    A look up table is then used to assign the pixels a
    value of 0, 1, 2 or 3, which are selectively removed
    during the iterations.

    Skeletonization 3D: Lee's method [2].
    Lee's method uses an octree data structure to examine a
    3x3x3 neighborhood of a pixel. The algorithm proceeds by
    iteratively sweeping over the image, and removing pixels
    at each iteration until the image stops changing.
    Each iteration consists of two steps: first, a list of
    candidates for removal is assembled; then pixels from this
    list are rechecked sequentially, to better preserve
    connectivity of the image.

    Parameters
    ----------
      src : sitk.Image
        Input binary mask on which extract the skeleton backbone.

    References
    ----------
    [1] A fast parallel algorithm for thinning digital patterns,
        T. Y. Zhang and C. Y. Suen, Communications of the ACM,
        March 1984, Volume 27, Number 3.

    [2] T.-C. Lee, R.L. Kashyap and C.-N. Chu, Building skeleton
        models via 3-D medial surface/axis thinning algorithms.
        Computer Vision, Graphics, and Image Processing,
        56(6):462-478, 1994.
    '''

    # get the dimensionality of the input
    ndim = len(src.GetSize())

    if ndim not in [2, 3]:
      raise ValueError(('Input mismatch shape. '
        f'Valid input shape must be 2 or 3. Given {ndim}.'
        )
      )

    # convert the input to a numpy buffer
    src_np = sitk.GetArrayViewFromImage(src)

    # perform the skeletonization
    if ndim == 2:
      np_skeleton = skeletonize(src_np)
    else: # it must be a 3D input
      np_skeleton = skeletonize(src_np, method='lee')

    # cast the resulting segmentation to int32 dtype
    np_skeleton = np.int32(np_skeleton)

    # associate the metadata to the skeleton output
    # and re-convert it to a sitk.Image data type
    skeleton = sitk.GetImageFromArray(np_skeleton)
    skeleton.CopyInformation(src)

    self._skeleton = skeleton

    return self

  def GetSkeletonImage (self) -> sitk.Image :
    '''
    Get the skeleton image/volume evaluated by the filter.

    Returns
    -------
      skeleton : sitk.Image
        Skeleton image/volume with the same dimensionality and
        metadata of the provided input.
    '''
    if not hasattr(self, '_skeleton'):
      class_name = self.__class__.__name__
      raise RuntimeError('Runtime Exception. ',
        f'The {class_name} object is not executed yet. ',
        'To get the skeleton image you need to call the Execute function'
        )

    return self._skeleton
