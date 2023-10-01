#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest

# import filter for the graphomic feature extraction
from graphomics import GraphomicsFeatureExtractor
# import filters for graph weighing
from graphomics import (
  GraphWeightsExtractorFilter,
  NodePairwiseDistanceFilter,
  EdgeLengthPathsFilter,
  EdgeLabelWeightFilter,
)
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

class TestGraphomicsFeatureExtractor:
  '''
  Tests:
    - the correct/incorrect behavior in setting the mask image
    - the correct/incorrect behavior in setting the skeleton image
    - the correct/incorrect behavior in setting the label image
    - the correct/incorrect behavior in setting the weighted features
    - the correct/incorrect behavior in setting the weights extractor
  '''

  def test_set_mask_file (self):
    # define the graphomic features extraction filter
    extractor = GraphomicsFeatureExtractor()
    # if not present raise error
    with pytest.raises(ValueError):
      extractor.Execute()

    # check it is not set as default
    assert 'mask_filepath' not in extractor._features

    # manual set a path
    extractor.SetMaskFilepath(maskfile='dummy.nii')
    # check if it was set
    assert extractor._features['mask_filepath'] == 'dummy.nii'

    # an analogous behavior could be obtained also
    # by the incorrect setting of the image as filepath...
    extractor.SetMaskImage(mask='dummy.nii')
    # check if it was set
    assert extractor._features['mask_filepath'] == 'dummy.nii'

  def test_set_skeleton_file (self):
    # define the graphomic features extraction filter
    extractor = GraphomicsFeatureExtractor()
    # if not present raise error
    with pytest.raises(ValueError):
      extractor.Execute()

    # check it is not set as default
    assert 'skeleton_filepath' not in extractor._features

    # manual set a path
    extractor.SetSkeletonFilepath(skeletonfile='dummy.nii')
    # check if it was set
    assert extractor._features['skeleton_filepath'] == 'dummy.nii'

    # an analogous behavior could be obtained also
    # by the incorrect setting of the image as filepath...
    extractor.SetSkeletonImage(skeleton='dummy.nii')
    # check if it was set
    assert extractor._features['skeleton_filepath'] == 'dummy.nii'

  def test_set_labelmap_file (self):
    # define the graphomic features extraction filter
    extractor = GraphomicsFeatureExtractor()
    # if not present raise error
    with pytest.raises(ValueError):
      extractor.Execute()

    # check it is not set as default
    assert 'label_filepath' not in extractor._features

    # manual set a path
    extractor.SetLabelFilepath(labelfile='dummy.nii')
    # check if it was set
    assert extractor._features['label_filepath'] == 'dummy.nii'

    # an analogous behavior could be obtained also
    # by the incorrect setting of the image as filepath...
    extractor.SetLabelImage(label='dummy.nii')
    # check if it was set
    assert extractor._features['label_filepath'] == 'dummy.nii'

  def test_enable_weight (self):
    # define the graphomic features extraction filter
    extractor = GraphomicsFeatureExtractor()

    # check it is not set as default
    assert 'enable_weighted_features' not in extractor._features

    # set it
    extractor.EnableWeightedFeatures()
    # check if it was set
    assert extractor._features['enable_weighted_features']

    # unset it
    extractor.DisableWeightedFeatures()
    # check if it was set
    assert not extractor._features['enable_weighted_features']

  def test_weight_extractor (self):
    # define the graphomic features extraction filter
    extractor = GraphomicsFeatureExtractor()

    # check it is not set as default
    assert 'graph_weights' not in extractor._features

    # set it by name
    extractor.SetWeightExtractorByName(wtype='EdgeLengthPathsFilter')
    # check if it was set
    assert extractor._features['graph_weights'] == 'EdgeLengthPathsFilter'
    assert not hasattr(extractor, '_wtype')

    # check invalid name
    with pytest.raises(ValueError):
      extractor.SetWeightExtractorByName(wtype='dummy')

    # set it by object
    wtype = EdgeLengthPathsFilter()
    extractor.SetWeightExtractor(wtype=wtype)
    # check if it was set
    assert extractor._features['graph_weights'] == 'EdgeLengthPathsFilter'
    assert isinstance(extractor._wtype, GraphWeightsExtractorFilter)

    # check invalid obj
    with pytest.raises(ValueError):
      extractor.SetWeightExtractor(wtype=TestGraphomicsFeatureExtractor())
