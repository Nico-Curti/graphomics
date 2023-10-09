#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest

import numpy as np
import SimpleITK as sitk

# import filter for the graphomic feature extraction
from graphomics import GraphomicsFeatureExtractor
# import filters for graph weighing
from graphomics import (
  GraphWeightsExtractorFilter,
  NodePairwiseDistanceFilter,
  EdgeLengthPathsFilter,
  EdgeLabelWeightFilter,
)
from graphomics import LoadImageFileInAnyFormat
from graphomics import SkeletonizeImageFilter
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

# define the path of the sample skeleton
skeleton_sample = os.path.join(sample_dir, 'skeleton.nii.gz')

if not os.path.exists(skeleton_sample):
  # create the folder to store the files
  os.makedirs(sample_dir, exist_ok=True)

  # download the sample image
  download_file_from_google_drive(
    Id='1szzofLxu9lVqjOwMubVIXfvkdCJs5dJJ',
    destination=skeleton_sample
  )

# load the sample image
mask = LoadImageFileInAnyFormat(nifti_sample)

# define the skeleton filter
skeleton_filter = SkeletonizeImageFilter()
skeleton_filter.Execute(src=mask)
skeleton = skeleton_filter.GetSkeletonImage()

template_file = os.path.join(
  os.path.abspath(
    os.path.dirname(__file__)
  ),
  '../cfg/template.yml'
)

class TestGraphomicsFeatureExtractor:
  '''
  Tests:
    - the correct/incorrect behavior in setting the mask image
    - the correct/incorrect behavior in setting the skeleton image
    - the correct/incorrect behavior in setting the label image
    - the correct/incorrect behavior in setting the weighted features
    - the correct/incorrect behavior in setting the weights extractor
    - the correct/incorrect execution of the filter
    - the correct/incorrect behavior in checking the consistency of the input type
    - the correct/incorrect behavior in checking the consistency of the input shape
    - the correct/incorrect behavior in checking the consistency of the input spacing
    - the correct/incorrect behavior in checking the consistency of the input direction
    - the correct/incorrect execution with skeleton not provided
    - the correct/incorrect behavior in getting an invalid feature
    - the correct/incorrect behavior in getting a non-enabled feature
    - the correct/incorrect behavior in getting the features and parameters
    - the correct/incorrect behavior in executing the filter with skeleton from file
    - the correct/incorrect behavior in executing the filter with labelmap from file
    - the correct/incorrect behavior in executing the filter with invalid weight extractor
    - the correct/incorrect behavior in executing the filter with no weight extractor
    - the correct/incorrect behavior in executing the filter with EdgeLabelWeightFilter
    - the correct/incorrect behavior in executing the filter with EdgeLengthPathsFilter
    - the correct/incorrect behavior in executing the filter with wrong parameters for weight extractor
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

  def test_execute (self):

    # define the graphomic features extraction filter
    extractor = GraphomicsFeatureExtractor()

    # set check consistency to true
    extractor._features['check_consistency'] = True

    # enable all the available graphomic features
    extractor.EnableAllFeatures()

    # set the required arguments
    extractor.SetMaskImage(mask=mask)
    extractor.SetSkeletonImage(skeleton=skeleton)

    # manually disable some features
    topology_disabled = ['ModularityScore', 'NumberOfMaximalCliques']
    spatial_disabled = ['DistanceMostCentralNodes', 'Eccentricity']
    centrality_disabled = ['NodeDegreeCentrality', 'NodeBetweennessCentrality']
    for name in topology_disabled:
      extractor._features['topology'][name] = False
    for name in spatial_disabled:
      extractor._features['spatial'][name] = False
    for name in centrality_disabled:
      extractor._features['centrality'][name] = False

    # execute the filter on the set inputs
    extractor.Execute()
    
    # get the resulting graphomic features computed
    graphomic_features = extractor.GetFeatures()

    # check the output is not empty
    assert graphomic_features

    # check if all the topology features are present and are not empty
    # check if the disabled features are not present
    members = extractor._feature_classes['topology'].GetAvailableMembers()
    for member, _ in members:
      if member not in topology_disabled:
        assert member in graphomic_features
        assert graphomic_features.get(member, None) is not None
      else:
        assert member not in graphomic_features
    
    # check if all the spatial features are present and are not empty
    members = extractor._feature_classes['spatial'].GetAvailableMembers()
    for member, _ in members:
      if member not in spatial_disabled:
        assert member in graphomic_features
        assert graphomic_features.get(member, None) is not None
      else:
        assert member not in graphomic_features
    
    # check if all the centrality features are present and are not empty
    members = extractor._feature_classes['centrality'].GetAvailableMembers()
    for member, _ in members:
      if member not in centrality_disabled:
        assert member in graphomic_features
        assert graphomic_features.get(member, None) is not None
      else:
        assert member not in graphomic_features

  def test_check_consistency_input_type (self):
    
    # define the graphomic features extraction filter
    extractor = GraphomicsFeatureExtractor()

    # set check consistency to true
    extractor._features['check_consistency'] = True

    skl = np.random.rand(100, 100, 100)
    skl = sitk.GetImageFromArray(skl)

    label = np.random.rand(100, 100, 100)
    label = sitk.GetImageFromArray(label)

    # set input mask, skeleton, and label map as random numpy arrays
    extractor.SetMaskImage(mask=np.random.rand(100, 100, 100))
    extractor.SetSkeletonImage(skeleton=skl)
    extractor.SetLabelImage(label=label)

    with pytest.raises(ValueError):
      extractor.Execute()

    # set valid input mask and skeleton to verify that the error is raised
    # only for the label map
    extractor.SetMaskImage(mask=mask)
    extractor.SetSkeletonImage(skeleton=skeleton)

    with pytest.raises(ValueError):
      extractor.Execute()
    

  def test_check_consistency_input_shape (self):

    # define the graphomic features extraction filter
    extractor = GraphomicsFeatureExtractor()

    # set check consistency to true
    extractor._features['check_consistency'] = True

    msk = np.random.rand(100, 100, 100)
    msk = sitk.GetImageFromArray(msk)

    skl = np.random.rand(100, 100)
    skl = sitk.GetImageFromArray(skl)

    label = np.random.rand(100, 100)
    label = sitk.GetImageFromArray(label)

    # set input mask and skeleton as random numpy arrays
    extractor.SetMaskImage(msk)
    extractor.SetSkeletonImage(skl)
    extractor.SetLabelImage(label)

    with pytest.raises(ValueError):
      extractor.Execute()

    # set valid input mask and skeleton to verify that the error is raised
    # only for the label map
    extractor.SetMaskImage(mask=mask)
    extractor.SetSkeletonImage(skeleton=skeleton)

    with pytest.raises(ValueError):
      extractor.Execute()

  def test_check_consistency_input_spacing (self):
      
    # define the graphomic features extraction filter
    extractor = GraphomicsFeatureExtractor()

    # set check consistency to true
    extractor._features['check_consistency'] = True

    msk = np.random.rand(100, 100, 100)
    msk = sitk.GetImageFromArray(msk)
    msk.SetSpacing((1, 1, 1))

    skl = np.random.rand(100, 100, 100)
    skl = sitk.GetImageFromArray(skl)
    skl.SetSpacing((1, 1, 2))

    label = np.random.rand(100, 100, 100)
    label = sitk.GetImageFromArray(label)
    label.SetSpacing((1, 1, 2))

    # set input mask and skeleton as random numpy arrays
    extractor.SetMaskImage(msk)
    extractor.SetSkeletonImage(skl)
    extractor.SetLabelImage(label)

    with pytest.raises(ValueError):
      extractor.Execute()

    # set valid input mask and skeleton to verify that the error is raised
    # only for the label map
    extractor.SetMaskImage(mask=mask)
    extractor.SetSkeletonImage(skeleton=skeleton)

    with pytest.raises(ValueError):
      extractor.Execute()

  def test_check_consistency_input_direction (self):

    # define the graphomic features extraction filter
    extractor = GraphomicsFeatureExtractor()

    # set check consistency to true
    extractor._features['check_consistency'] = True

    msk = np.random.rand(100, 100, 100)
    msk = sitk.GetImageFromArray(msk)
    msk.SetDirection((1, 0, 0, 0, -1, 0, 0, 0, 1))

    skl = np.random.rand(100, 100, 100)
    skl = sitk.GetImageFromArray(skl)
    skl.SetDirection((1, 0, 0, 0, 1, 0, 0, 0, 1))

    label = np.random.rand(100, 100, 100)
    label = sitk.GetImageFromArray(label)
    label.SetDirection((1, 0, 0, 0, 1, 0, 0, 0, 1))

    # set input mask and skeleton as random numpy arrays
    extractor.SetMaskImage(msk)
    extractor.SetSkeletonImage(skl)
    extractor.SetLabelImage(label)

    with pytest.raises(ValueError):
      extractor.Execute()

    # set valid input mask and skeleton to verify that the error is raised
    # only for the label map
    extractor.SetMaskImage(mask=mask)
    extractor.SetSkeletonImage(skeleton=skeleton)

    with pytest.raises(ValueError):
      extractor.Execute()
  
  def test_skeleton_not_provided (self):

    # define the graphomic features extraction filter
    extractor = GraphomicsFeatureExtractor()

    # set check consistency to true
    extractor._features['check_consistency'] = True

    # set the required arguments
    extractor.SetMaskImage(mask=mask)

    # execute the filter on the set inputs
    extractor.Execute()

  def test_get_invalid_feature_class (self):

    # define the graphomic features extraction filter
    extractor = GraphomicsFeatureExtractor()

    # enable all the available graphomic features
    extractor.EnableAllFeatures()

    # set required arguments
    extractor.SetMaskImage(mask=mask)

    # get an invalid feature class
    with pytest.raises(ValueError):
      extractor._GetEnabledFeaturesByClassName('dummy')
    
  def test_get_empty_feature_class (self):

    # define the graphomic features extraction filter
    extractor = GraphomicsFeatureExtractor()

    # set required arguments
    extractor.SetMaskImage(mask=mask)

    # get an empty feature class
    with pytest.raises(ValueError):
      extractor._GetEnabledFeaturesByClassName('topology')

  def get_features_and_parameters (self):

    # define the graphomic features extraction filter
    extractor = GraphomicsFeatureExtractor()

    # set required arguments
    extractor.SetMaskImage(mask=mask)

    # enable all the available graphomic features
    extractor.EnableFeatureClassByName('topology')
    extractor.EnableFeatureClassByName('spatial')

    # manually disable a spatial feature
    extractor._features['spatial']['NodeDensityStatistics'] = False

    # set some feature parameters
    extractor._features['EulerNumberParameters'] = {'connectivity': 1}

    # get the features and parameters for the topology class
    features, parameters = extractor._GetEnabledFeaturesByClassName('topology')

    # assert features is not empty and parameters is not empty
    assert features
    assert parameters

    # get the features and parameters for the spatial class
    features, parameters = extractor._GetEnabledFeaturesByClassName('spatial')

    # assert features is not empty and parameters is empty
    assert features
    assert not parameters

    # assert NodeDensityStatistics not in features
    assert 'NodeDensityStatistics' not in features

    # get the features and parameters for the centrality class
    features, parameters = extractor._GetEnabledFeaturesByClassName('centrality')

    # assert features is empty and parameters is empty
    assert not features
    assert not parameters

  def test_execute_skeleton_from_file (self):

    # define the graphomic features extraction filter
    extractor = GraphomicsFeatureExtractor()

    # set required arguments
    extractor.SetMaskImage(mask=mask)

    # set the skeleton image from file
    extractor.SetSkeletonImage(skeleton_sample)

    # execute the filter on the set inputs
    extractor.Execute()

    assert extractor._features['skeleton_filepath'] == skeleton_sample

    # the same should be obtained with SetSkeletonFilepath
    extractor.SetSkeletonFilepath(skeleton_sample)

    # execute the filter on the set inputs
    extractor.Execute()

    assert extractor._features['skeleton_filepath'] == skeleton_sample

  def test_execute_labelmap_from_file (self):
      
    # define the graphomic features extraction filter
    extractor = GraphomicsFeatureExtractor()

    # set required arguments
    extractor.SetMaskImage(mask=mask)

    # set the label image from file
    extractor.SetLabelImage(skeleton_sample)

    # execute the filter on the set inputs
    extractor.Execute()

    assert extractor._features['label_filepath'] == skeleton_sample

    # the same should be obtained with SetLabelFilepath
    extractor.SetLabelFilepath(skeleton_sample)

    # execute the filter on the set inputs
    extractor.Execute()

    assert extractor._features['label_filepath'] == skeleton_sample

  def test_execute_invalid_weight_wextractor (self):

    # define the graphomic features extraction filter
    extractor = GraphomicsFeatureExtractor()

    # set required arguments
    extractor.SetMaskImage(mask=mask)

    # enable the weighted features
    extractor.EnableWeightedFeatures()

    # set an invalid weight extractor
    extractor._features['graph_weights'] = 'dummy'

    # execute the filter and check it raises an error
    with pytest.raises(ValueError):
      extractor.Execute()

  def test_weighted_execute_with_no_wextractor (self):
    
    # define the graphomic features extraction filter
    extractor = GraphomicsFeatureExtractor()

    # set required arguments
    extractor.SetMaskImage(mask=mask)

    # enable the weighted features
    extractor.EnableWeightedFeatures()

    # execute the filter
    extractor.Execute()

    # check the weight is the default one
    assert isinstance(extractor._wtype, EdgeLengthPathsFilter)

  def test_weight_extractor_weighted_disabled (self):
      
    # define the graphomic features extraction filter
    extractor = GraphomicsFeatureExtractor()

    # set required arguments
    extractor.SetMaskImage(mask=mask)

    # set an invalid weight extractor
    extractor.SetWeightExtractor(EdgeLengthPathsFilter())

    # execute the filter and check it raises an error
    extractor.Execute()

    with pytest.raises(AttributeError):
      extractor._wtype

  def test_EdgeLabelWeightFilter_no_labelmap (self):

    # define the graphomic features extraction filter
    extractor = GraphomicsFeatureExtractor()

    # set required arguments
    extractor.SetMaskImage(mask=mask)

    # enable the weighted features
    extractor.EnableWeightedFeatures()

    # set the weight extractor
    extractor.SetWeightExtractorByName('EdgeLabelWeightFilter')

    # execute the filter and check it raises an error
    with pytest.raises(ValueError):
      extractor.Execute()

  def test_EdgeLabelWeightFilter_with_labelmap (self):

    # define the graphomic features extraction filter
    extractor = GraphomicsFeatureExtractor()

    # set required arguments
    extractor.SetMaskImage(mask=mask)
    extractor.SetLabelImage(label=skeleton)

    # enable the weighted features
    extractor.EnableWeightedFeatures()

    # set the weight extractor
    extractor.SetWeightExtractorByName('EdgeLabelWeightFilter')

    # execute the filter
    extractor.Execute()

  def test_EdgeLabelWeightFilter_with_extra_params (self):

    # define de graphomic features extraction filter
    extractor = GraphomicsFeatureExtractor()

    # set required arguments
    extractor.SetMaskImage(mask=mask)
    extractor.SetLabelImage(label=skeleton)

    # enable the weighted features
    extractor.EnableWeightedFeatures()

    # set the weight extractor
    extractor.SetWeightExtractorByName('EdgeLabelWeightFilter')

    # set extra parameters
    extractor._features['EdgeLabelWeightFilterParameters'] = {'metric': 'median'}

    # execute the filter and check it raises an error
    extractor.Execute()

  def test_EdgeLengthPathsFilter_with_unequal_spacing (self):

    # define the graphomic features extraction filter
    extractor = GraphomicsFeatureExtractor()

    # change the spacing of the input mask
    msk = np.random.rand(100, 100, 100)
    msk = sitk.GetImageFromArray(msk)
    msk.SetSpacing((1, 1, 2))

    # set required arguments
    extractor.SetMaskImage(mask=msk)

    # enable the weighted features
    extractor.EnableWeightedFeatures()

    # set the weight extractor
    extractor.SetWeightExtractorByName('EdgeLengthPathsFilter')

    # execute the filter and check it raises an error
    with pytest.raises(ValueError):
      extractor.Execute()

  def test_WeightFilter_with_invalid_parameters (self):

    # define the graphomic features extraction filter
    extractor = GraphomicsFeatureExtractor()

    # set required arguments
    extractor.SetMaskImage(mask=mask)

    # enable the weighted features
    extractor.EnableWeightedFeatures()

    # set the weight extractor
    extractor.SetWeightExtractorByName('EdgeLengthPathsFilter')

    # set invalid parameters
    extractor._features['EdgeLengthPathsFilterParameters'] = {'metric': 'dummy'}

    # execute the filter and check it raises an error
    with pytest.raises(TypeError):
      extractor.Execute()
 