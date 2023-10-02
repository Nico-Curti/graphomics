#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest

import numpy as np
import SimpleITK as sitk

# import filter for the medical image loading
from graphomics import LoadImageFileInAnyFormat
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
nifti_sample = os.path.join(sample_dir, 'brain_seg_anon.nii')

if not os.path.exists(nifti_sample):
  # create the folder to store the files
  os.makedirs(sample_dir, exist_ok=True)

  # download the sample image
  download_file_from_google_drive(
    Id='1UBPKRkadArzZBbBn3GeCDRDIOy199NeB',
    destination=nifti_sample
  )


class TestLoader:
  '''
  Tests:
    - if the data loader raise error if the file does not exist
    - if the data loader works with DCM dir
    - if the data loader works with mgz file
    - if the data loader raise error with invalid extension
    - if the data loader works with nifti brain
    - if the data loader binarize the input on demand
    - if the data loader resample the input to equal spacing on demand
    - if the data loader crop the input on demand
  '''

  def test_file_not_found (self):

    # file not found
    with pytest.raises(ValueError):
      LoadImageFileInAnyFormat(filepath='dummy.txt')

  def test_dcm_directory (self):
    # TODO: add a dcm sample to check
    pass

  def test_mgz_directory (self):
    # TODO: add a mgz sample to check
    pass

  def test_invalid_extension (self):

    file_dir = os.path.join(
      os.path.abspath(
        os.path.dirname(__file__)
      ),
      '../graphomics'
    )
    filepath = os.path.join(file_dir, '__init__.py')

    # invalid extension
    with pytest.raises(ValueError):
      LoadImageFileInAnyFormat(filepath=filepath)

  def test_valid_brain_sample (self):

    # load the image
    mask = LoadImageFileInAnyFormat(
      filepath=nifti_sample,
      binarize=False,
      equal_spacing=False,
      crop=False
    )

    # check input properties
    assert isinstance(mask, sitk.Image)
    assert len(mask.GetSize()) == 3

  def test_binarize_brain_sample (self):

    # load the image
    mask = LoadImageFileInAnyFormat(
      filepath=nifti_sample,
      binarize=True,
      equal_spacing=False,
      crop=False
    )

    # get the numpy volume for faster checks
    np_mask = sitk.GetArrayFromImage(mask)

    # check input properties
    assert isinstance(mask, sitk.Image)
    assert len(np_mask.shape) == 3
    assert np.unique(np_mask).size == 2
    assert np.max(np_mask) == 1
    assert np.min(np_mask) == 0

  def test_resample_brain_sample (self):

    # load the image
    mask = LoadImageFileInAnyFormat(
      filepath=nifti_sample,
      binarize=False,
      equal_spacing=True,
      crop=False
    )

    # check input properties
    assert isinstance(mask, sitk.Image)
    assert len(set(mask.GetSpacing())) == 1

  def test_crop_brain_sample (self):

    # load the image without crop
    orig = LoadImageFileInAnyFormat(
      filepath=nifti_sample,
      binarize=False,
      equal_spacing=False,
      crop=False
    )
    # load the image with crop
    mask = LoadImageFileInAnyFormat(
      filepath=nifti_sample,
      binarize=False,
      equal_spacing=False,
      crop=True
    )

    # check input properties
    assert isinstance(mask, sitk.Image)
    assert mask.GetSize() < orig.GetSize()

