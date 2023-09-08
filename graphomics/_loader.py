#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import SimpleITK as sitk
from nibabel import aff2axcodes
import nibabel.freesurfer.mghformat as mghf # read mgz images

__author__  = ['Nico Curti',
               'Gianluca Carlini',
               'Riccardo Biondi'
              ]
__email__ = ['nico.curti2@unibo.it',
             'gianluca.carlini2@unibo.it',
             'riccardo.biondi2@unibo.it'
            ]

__all__ = ['LoadImageFileInAnyFormat']


def LoadImageFileInAnyFormat (filepath : str,
                              binarize : bool = True,
                              equal_spacing : bool = False
                             ) -> sitk.Image :
  '''
  Medical Image data loader.
  The function supports the loading of both 2D and 3D images,
  involving all the data formats already supported by SimpleITK_
  package and adding the .mgz (freeSurfer) format.

  Parameters
  ----------
    filepath : str
      Input filename or path in which load the images.

    binarize : bool (default := True)
      Force the binarization of the loaded image into [0, 1] range,
      considering all the no-null values as signal.

    equal_spacing : bool (default := False)
      Force the image resampling to an equal spacing in all direction.
      The new spacing will acquired the most common size in the
      volume shape.

  Returns
  -------
    img : sitk.Image
      Loaded 2D/3D image as SimpleITK format.

  .. _SimpleITK: https://simpleitk.readthedocs.io/en/master/IO.html
  '''

  # check if the filepath exists
  if not os.path.exists(filepath):
    raise ValueError((
      'Invalid input filepath. '
      f'The provided filepath {filepath} does not exists or '
      'it is incorrect.'
    ))

  # if the filepath is a directory we need to move to a DCM dir fmt
  if os.path.isdir(filepath):

    # load the image as dicom dir
    # set the reader
    reader = sitk.ImageSeriesReader()
    # set filepath in which read the filenames
    dicom_names = reader.GetGDCMSeriesFileNames(
      directory=filepath,
      seriesID='',
      useSeriesDetails=False,
      recursive=False,
      loadSequences=False
    )
    reader.SetFileNames(fileNames=dicom_names)
    # execute the filter to get the loaded image
    image = reader.Execute()

  # otherwise it should be a simple image format
  else:

    # check if it is a freesurfer file
    if '.mgz' in filepath:
      # load the image as mgz file
      mgz = mghf.load(filepath)
      # convert the image to a SimpleITK format
      image = sitk.GetImageFromArray(mgz.get_fdata())
      # extract the useful metadata
      # Ref. https://discourse.itk.org/t/read-ct-volume-compatible-to-nibabel-orientation-using-simpleitk/5254
      affine = mgz.affine
      orientation = ''.join(aff2axcodes(affine))
      origin = tuple(affine[:3, 3])
      spacing = tuple(filter(lambda x : x != 0, affine[:3, :3].ravel()))
      # assign the metadata
      image = sitk.DICOMOrient(image, orientation)
      image.SetOrigin(origin)
      image.SetSpacing(spacing)

    # otherwise try to load it with the SimpleITK support
    else:
      # omit the imageIO parameter to leave the task to SimpleITK
      try:
        image = sitk.ReadImage(
          fileName=filepath,
          outputPixelType=sitk.sitkUnknown,
          imageIO=''
        )
      except RuntimeError:
        raise ValueError((
          f'Unable to open {filepath} for reading. '
          'The provided file format is not supported by SimpleITK '
          'See https://simpleitk.readthedocs.io/en/master/IO.html '
          'for the complete list of supported formats'
        ))

  # if the binarization is required
  if binarize:
    # performed a thresholding in [0, 1] of all the values
    image = (image != 0)

  # if the resampling is required
  if equal_spacing:
    # get the current image spacing
    space = image.GetSpacing()
    # count the occurrences of each dimension
    _, counts = np.unique(space, return_counts=True)
    # evaluate the most common dimension in the image spacing
    index = np.argmax(counts)
    # get the new spacing as a tuple of unique
    new_spacing = (space[index], ) * len(space)
    # resample the image
    image = ResampleSpacing(
      mask=image,
      new_spacing=new_spacing,
      interpolator=sitk.sitkNearestNeighbor
    )

  return image

def ResampleSpacing (mask : sitk.Image,
                     new_spacing : tuple,
                     interpolator : int = sitk.sitkNearestNeighbor,
                    ) -> sitk.Image :
  '''
  Resample input binary mask to equal spacing

  Parameters
  ----------
    mask : sitk.Image
      Input binary image mask to process.

    new_spacing : tuple
      Spacing required for the new image.

    interpolator : int (default := sitk.sitkNearestNeighbor)
      Interpolator type to use.
      Default is the NearestNeighbor interpolator which is the most
      appropriated to preserve binary format of the masks.
  '''

  # get the original spacing
  orig_spacing = mask.GetSpacing()
  # get the original size
  orig_size = mask.GetSize()
  # compute the new size of the image according
  # to the required new spacing
  new_size = []
  # loop along the available variables
  for osi, osp, nsp in zip(orig_size, orig_spacing, new_spacing):
    # the new size is given by (old_size / old_spacing) / new_spacing
    s = np.round((osi * osp) / nsp)
    s = int(s)
    new_size.append(s)

  # evaluate the resampling
  resampled_mask = sitk.Resample(
    image1=mask,
    size=new_size,
    transform=sitk.Transform(),
    interpolator=interpolator,
    outputOrigin=mask.GetOrigin(),
    outputSpacing=new_spacing,
    outputDirection=mask.GetDirection(),
    defaultPixelValue=0,
    outputPixelType=mask.GetPixelID(),
    useNearestNeighborExtrapolator=False
  )

  return resampled_mask
