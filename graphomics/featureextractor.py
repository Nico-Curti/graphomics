#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import yaml
import powerlaw
import numpy as np
import scipy as sp
import skimage as ski
import networkx as nx
import SimpleITK as sitk
from datetime import datetime

from .__version__ import __version__

# import the functions required for the input loading
from ._loader import LoadImageFileInAnyFormat
# import the functions required for the pre-processing
# of the loaded inputs
from ._loader import BoundingBox
# import the functions required for the pre-processing
# of the loaded inputs
from ._loader import CropMinimumBoundingBox
# import filter for skeletonize image/volume
from ._skeletonizer import SkeletonizeImageFilter
# import filter for graph extraction
from ._graphfilter import GraphThicknessImageFilter
# import filters for graph weighing
from ._graph import (
  GraphWeightsExtractorFilter,
  NodePairwiseDistanceFilter,
  EdgeLengthPathsFilter,
  EdgeLabelWeightFilter,
  GraphFilter
)
# import filters for topological graphomics features
from ._topology import GraphomicsTopology
# import filters for centrality graphomics features
from ._centrality import GraphomicsCentrality
# import filters for spatial graphomics features
from ._spatial import GraphomicsSpatial

__author__  = ['Nico Curti',
               'Gianluca Carlini',
               'Riccardo Biondi'
              ]
__email__ = ['nico.curti2@unibo.it',
             'gianluca.carlini3@unibo.it',
             'riccardo.biondi7@unibo.it'
            ]

__all__ = ['GraphomicsFeatureExtractor']


class GraphomicsFeatureExtractor (object):
  '''
  Core function for the graphomics feature extraction.

  '''

  _feature_classes = {
    'topology' : GraphomicsTopology(),
    'spatial' : GraphomicsSpatial(),
    'centrality' : GraphomicsCentrality(),
  }

  _weight_extractor = {
    'NodePairwiseDistanceFilter' : NodePairwiseDistanceFilter(
      metric='euclidean',
    ),
    'EdgeLengthPathsFilter' : EdgeLengthPathsFilter(),
    'EdgeLabelWeightFilter' : EdgeLabelWeightFilter(),
  }

  def __init__ (self):

    self._features = {}

  def LoadConfig (self, filename : str):
    '''
    Load the graphomics features from a configuration
    file used for the customization of the workflow.
    The configuration file must be in Yaml format, following
    a strict nomenclature of the keys and values.
    The general template for the configuration file is
    provided in `cfg/template.yml`

    Parameters
    ----------
      filename : str
        Filename or path to the configuration file.
    '''
    # open the configuration file in YAML format
    with open(filename, 'r', encoding='utf-8') as fp:
      cfg = yaml.safe_load(fp)

    # TODO: add check about the values of the feature class
    # and inner-class names
    self._features = cfg

    return self

  def SetConfig (self, config : dict):
    '''
    Set the configuration dictionary to use for the
    feature extraction.
    Pay attention to the name of the keys in the
    dictionary, since only valid names will be used
    during the extraction step.
    No internal checks are performed on the validity
    of the names, to leave the user to set further
    parameters/metadata useful for its pipeline.

    Parameters
    ----------
      config : dict
        Configuration dictionary to use.
    '''

    # set the configuration dictionary as internal
    # features config
    self._features = config

    return self

  def DisableAllFeatures (self):
    '''
    Disable all the possible graphomics features.
    '''
    # loop along all the feature classes
    for name in self._feature_classes.keys():
      # remove the key and related values
      self._features.pop(name, None)

    return self

  def EnableAllFeatures (self):
    '''
    Enable all the possible graphomics features.
    '''
    for name in self._feature_classes.keys():
      
      # enable the feature class
      self._features[f'enable_{name}_features'] = True

      # add the feature class to the list of features
      self._features[name] = {}
      # get all the possible inner-features related
      # to that class
      members = self._feature_classes[name].GetAvailableMembers()
      # enable all
      for mem, _ in members:
        self._features[name][mem] = True

    return self

  def EnableFeatureClassByName (self, name : str):
    '''
    Enable the features belonging to the provided
    class name.

    Possible classes of features are:

    * topology
    * spatial
    * centrality

    Parameters
    ----------
      name : str
        Name of graphomics features class to enable
    '''

    if name not in self._feature_classes.keys():
      available_classes = ', '.join(self._feature_classes.keys())
      raise ValueError(('Invalid feature class name. '
        f'Available classes are {available_classes}. '
        f'Given {name}.'
      ))
    # add the feature class to the keys
    self._features[name] = {}
    # get all the possible inner-features related
    # to that class
    members = self._feature_classes[name].GetAvailableMembers()
    # enable all
    for mem, _ in members:
      # set the feature name to True
      self._features[name][mem] = True

    return self

  def EnableFeaturesByName (self, features : dict):
    '''
    Enable the list of features provided in input

    Parameters
    ----------
      features : dict
        Dictionary of required graphomics features divided
        by classes. The dictionary must be formatted as
        {'feature_class' : ['feature_name1', 'feature_name2', etc.]},
        following the same syntax of the configuration file.
        See at `cfg/template.yml` for a complete example
        of configuration file.
    '''
    # temporary dictionary for the variable casting
    new_features = {}

    for key, val in features.items():
      if key not in self._feature_classes.keys():
        available_classes = ', '.join(self._feature_classes.keys())
        raise ValueError(('Invalid feature class name. '
          f'Available classes are {available_classes}. '
          f'Given {key}.'
        ))
      # otherwise proceed to analyze the inner-class names
      else:
        # add the key as a valid name
        new_features[key] = {}
        # get all the possible inner-features related
        # to that class
        members = self._feature_classes[key].GetAvailableMembers()
        # get only the member name without the caller
        members = [x[0] for x in members]
        # loop along the provided feature names and check them one-by-one
        for v in val:
          # if it is an invalid member
          if v not in members:
            raise ValueError(('Invalid graphomic feature name. '
              f'In class {key} the available features are {members}. '
              f'Given {v}.'
            ))

          # add the new feature as value turned on
          new_features[key][v] = True

    # update the feature list
    self._features.update(new_features)

    return self

  def GetSelectedFeatures (self) -> dict :
    '''
    Get the list of graphomic features currently enabled
    in the filter.

    Returns
    -------
      features : dict
        Dictionary of features enabled
    '''
    enabled = {}
    # loop along the stored configuration
    for name in self._feature_classes.keys():
      # if the name is enabled in the global dict
      if name in self._features:
        # filter the turned on feature names
        features = [f for f, v in self._features[name].items() if v]
        # add it to the new dictionary
        enabled[name] = features

    return enabled

  def GetAvailableFeatureClasses (self) -> list :
    '''
    Get the list of names of the available
    graphomic features in the filter.

    Returns
    -------
      classes : list
        List of feature class names
    '''
    return list(self._feature_classes)

  def _CheckInputs (self, image1 : sitk.Image,
                          image2 : sitk.Image
                    ) -> bool :
    '''
    Check the consistency of the two images taking care
    about the metadata and the input types.
    If the two image are compatible, the result of this
    function is a positive check.

    Parameters
    ----------
      image1 : sitk.Image
        First input image.

      image2 : sitk.Image
        Second input image.

    Returns
    -------
      checked : bool
        True if the two inputs are compatible, False otherwise.
    '''
    # firstly check the input types
    if not (isinstance(image1, sitk.Image) and isinstance(image2, sitk.Image)):
      return False

    # then check the input sizes
    if image1.GetSize() != image2.GetSize():
      return False

    # then check the input spacings
    if image1.GetSpacing() != image2.GetSpacing():
      return False

    # then check the input directions
    if image1.GetDirection() != image2.GetDirection():
      return False

    # TODO: implements check between inputs
    return True

  def SetMaskFilepath (self, maskfile : str) :
    '''
    Set the input mask filename or path in which
    load the image/volume.
    The allowed file types include DCM, Nifti, mgz formats,
    related to the .dcm, .nii, .nii.gz, .mgz extensions.
    For the DCM format the filepath must be related to the
    directory in which the dcm is stored.

    Parameters
    ----------
      maskfile : str
        Input filename to set.
    '''
    # override the key
    self._features['mask_filepath'] = maskfile

    return self

  def SetMaskImage (self, mask : sitk.Image) :
    '''
    Set the input mask image.
    The correctness of the input image will be check
    (if required) during the graphomic features extraction.

    Parameters
    ----------
      mask : sitk.Image
    '''
    # override the key
    self._features['mask_filepath'] = mask

    return self

  def SetSkeletonFilepath (self, skeletonfile : str) :
    '''
    Set the input skeleton filename or path in which
    load the image/volume.
    The allowed file types include DCM, Nifti, mgz formats,
    related to the .dcm, .nii, .nii.gz, .mgz extensions.
    For the DCM format the filepath must be related to the
    directory in which the dcm is stored.

    Parameters
    ----------
      skeletonfile : str
        Input filename to set.
    '''
    # override the key
    self._features['skeleton_filepath'] = skeletonfile

    return self

  def SetSkeletonImage (self, skeleton : sitk.Image) :
    '''
    Set the input skeleton image.
    The correctness of the input image will be check
    (if required) during the graphomic features extraction.

    Parameters
    ----------
      skeleton : sitk.Image
    '''
    # override the key
    self._features['skeleton_filepath'] = skeleton

    return self

  def SetLabelFilepath (self, labelfile : str) :
    '''
    Set the input label filename or path in which
    load the image/volume.
    The allowed file types include DCM, Nifti, mgz formats,
    related to the .dcm, .nii, .nii.gz, .mgz extensions.
    For the DCM format the filepath must be related to the
    directory in which the dcm is stored.

    Parameters
    ----------
      labelfile : str
        Input filename to set.
    '''
    # override the key
    self._features['label_filepath'] = labelfile

    return self

  def SetLabelImage (self, label : sitk.Image) :
    '''
    Set the input label image.
    The correctness of the input image will be check
    (if required) during the graphomic features extraction.

    Parameters
    ----------
      label : sitk.Image
    '''
    # override the key
    self._features['label_filepath'] = label

    return self

  def EnableWeightedFeatures (self) :
    '''
    Enable the evaluation of the graphomic features using
    the weighted network.
    '''
    # override the key
    self._features['enable_weighted_features'] = True

    return self

  def DisableWeightedFeatures (self) :
    '''
    Disable the evaluation of the graphomic features using
    the weighted network.
    '''
    # override the key
    self._features['enable_weighted_features'] = False

    return self

  def SetWeightExtractorByName (self, wtype : str) :
    '''
    Set the graph weight extractor filter to use during the graphomic
    features extraction.

    Parameters
    ----------
      wtype : str
        Name of the weight extractor type to use.
    '''

    if wtype not in self._weight_extractor.keys():
      # get the list of available methods
      available_wtype = ', '.join(self._weight_extractor.keys())
      raise ValueError((
        'Invalid weight extractor name. '
        f'Available classes are {available_wtype}. '
        f'Given {wtype}.'
      ))

    # override the key
    self._features['graph_weights'] = wtype

    return self

  def SetWeightExtractor (self, wtype : GraphWeightsExtractorFilter) :
    '''
    Set the graph weight extractor filter to use during the graphomic
    features extraction.
    The object type must inherit from the base GraphWeightsExtractorFilter
    type.
    This function could be used to set the specif parameters
    of the weight extractor that cannot be set in the configuration
    file OR to use custom versions of the objects.

    Parameters
    ----------
      wtype : GraphWeightsExtractorFilter
        Weight extractor filter to use.
    '''

    if not isinstance(wtype, GraphWeightsExtractorFilter):
      raise ValueError((
        'Invalid weight extractor object. '
        'To ensure the correctness of the graphomic pipeline, the '
        'weight extractor must inherit from the GraphWeightsExtractorFilter '
        'class type. '
        'See graphomics/_graph.py for the details about the requirements'
      ))

    # assign the weight extractor
    self._wtype = wtype
    # set also the config key for sake of
    # completeness
    self._features['graph_weights'] = wtype.__class__.__name__

    return self

  def SetGlobalDefaultNumberOfThreads (self, nth : int) :
    '''
    Set the number of threads to used by the parallel
    filters used by the object.

    Parameters
    ----------
      nth : int
        Number of threads
    '''
    # check input validity
    if nth < 1 or not isinstance(nth, int):
      raise ValueError((
        'Invalid number of threads. '
        'It must be a positive integer number >= 1 '
        'and <= maximum number of available threads. '
        f'Given {nth}'
      ))

    self._features['nth'] = nth

    return self

  def _GetEnabledFeaturesByClassName (self, feature_class : str) -> tuple :
    '''
    Extract the list of enabled features related to a provided
    feature class.

    Parameters
    ----------
      feature_class : str
        Name of the graphomic feature class to inspect.
        Possible values are stored in the `_feature_classes` private
        variable.

    Returns
    -------
      todo : list
        List of feature names enabled during the current evaluation.

      params : dict
        Dictionary of the private parameters related to each filter.
        The dictionary is organized as (FeatureName, dictionary of parameters).
    '''
    # get the available feature classes
    available_classes = list(self._feature_classes.keys())

    # check the validity of the provided feature class
    if feature_class not in available_classes:
      # get the list of available feature class
      available_classes = ', '.join(available_classes)
      raise ValueError((
        'Invalid feature class name. '
        f'Available classes are {available_classes}. '
        f'Given {feature_class}.'
      ))

    # extract the list of required features for that class
    whole_dict = self._features.get(feature_class, None)
    if whole_dict is None:
      # raise an error if the feature class was not enabled
      raise ValueError(f'No features enabled for the given class ({feature_class}).')

    # declare the list of todo and related parameters
    todo = []
    params = {}

    # loop along it selecting only the turned on ones
    for name, enable in whole_dict.items():
      # if the value is set to true
      if enable:
        # append the feature to the list of todo
        todo.append(name)
        # check if there are some related parameters
        if self._features.get(f'{name}Parameters', False):
          params[f'{name}'] = self._features.get(f'{name}Parameters')

    return (todo, params)

  def Execute (self) :
    '''
    Execute the graphomics feature extraction calling the required
    list of feature-classes and feature-names.
    The results will be collected in a dict with the features indexed
    by their name.
    '''

    # the mask_filepath is mandatory for the correct usage of this
    # filter object
    if not self._features.get('mask_filepath', False):
      raise ValueError((
        'Invalid input mask. '
        'Before the execution of the filter a valid input mask image must be provided.'
      ))
    # otherwise we need to load it from file
    else:
      # get the provided filename
      mask_file = self._features.get('mask_filepath')
      # check if it is a file or a ready-to-use image
      if isinstance(mask_file, sitk.Image):
        # set it directly
        mask = mask_file
      # otherwise load it from file
      else:
        # load it
        mask = LoadImageFileInAnyFormat(
          filepath=mask_file,
          masklabel=self._features.get('masklabel', None),
          equal_spacing=self._features.get('equal_spacing', False),
        )

    # perform the image cropping
    if self._features.get('crop_input', False):
      # evaluate the minimum bounding box around the
      # masked volume
      bbox = BoundingBox(mask=mask)
      # call the crop function according to the
      # minimum bounding box around the object
      mask = CropMinimumBoundingBox(
        mask=mask,
        bbox=bbox
      )
    else:
      bbox = None

    # if the skeleton file was not provided, we can compute using
    # the package filter
    if not self._features.get('skeleton_filepath', False):
      # initialize the skeleton filter
      sk_filter = SkeletonizeImageFilter()
      # execute it on the give input mask
      sk_filter.Execute(src=mask)
      # extract the resulting image/volume
      skeleton = sk_filter.GetSkeletonImage()
    # otherwise we need to load it from file
    else:
      # get the provided filename
      sk_file = self._features.get('skeleton_filepath')
      # check if it is a file or a ready-to-use image
      if isinstance(sk_file, sitk.Image):
        # set it directly
        skeleton = sk_file
      # otherwise load it from file
      else:
        # load it
        skeleton = LoadImageFileInAnyFormat(
          filepath=sk_file,
          masklabel=self._features.get('masklabel', None),
          equal_spacing=self._features.get('equal_spacing', False),
        )

        # if required use the mask bbox to crop also
        # the skeleton
        if self._features.get('crop_input', False):
          # call the crop function according to the
          # minimum bounding box around the object
          skeleton = CropMinimumBoundingBox(
            mask=skeleton,
            bbox=bbox
          )

    # if the label file was not provided, we can set the
    # value to None
    if not self._features.get('label_filepath', False):
      labelmap = None
    # otherwise we need to load it from file
    else:
      # get the provided filename
      lbl_file = self._features.get('label_filepath')
      # check if it is a file or a ready-to-use image
      if isinstance(lbl_file, sitk.Image):
        labelmap = lbl_file
      # otherwise load it from file
      else:
        # load it
        labelmap = LoadImageFileInAnyFormat(
          filepath=lbl_file,
          # masklabel=self._features.get('masklabel', False)
          masklabel=None, # in this case the label map could contain
                          # also floating point values that must be preserved
          equal_spacing=self._features.get('equal_spacing', False),
        )
        # if required use the mask bbox to crop also
        # the labelmap
        if self._features.get('crop_input', False):
          # call the crop function according to the
          # minimum bounding box around the object
          labelmap = CropMinimumBoundingBox(
            mask=labelmap,
            bbox=bbox
          )

    self._graphomic_features = self._Execute(
      mask=mask,
      skeleton=skeleton,
      labelmap=labelmap
    )

    return self

  def _Execute (self, mask : sitk.Image,
                      skeleton : sitk.Image = None,
                      labelmap : sitk.Image = None
               ) -> dict :
    '''
    Core function for the extraction of the graphomic features.

    Parameters
    ----------
      mask : sitk.Image
        Input 2D/3D binary image with the shape to analyze

      skeleton : sitk.Image (default := None)
        Input 2D/3D skeleton image with the same shape of the
        mask one.
        The default value is set to None: in this case the skeleton
        extraction will be performed by the package filter before
        the graphomics feature extraction.

      labelmap : sitk.Image (default := None)
        Input 2D/3D image with the same shape of the mask one.
        If provided, the labelmap is used internally for the weighing
        of the skeleton graph and the correction of the graphomic
        features.

    Returns
    -------
      features : dict
        Dictionary containing the required graphomics features
        indexed by their names.
    '''
    # if the check consistency is required perfom it
    if self._features.get('check_consistency', False):
      # run the tests if the inputs are provided

      # check consistency between mask and skeleton
      res = self._CheckInputs(
        image1=mask,
        image2=skeleton
      )
      # arise errors if necessary
      if not res:
        raise ValueError((
          'Check consistency between mask and skeleton: FAILED '
          'There is a mismatch in the volume metadata that could alter '
          'the correctness of the results. '
          'Pipeline aborted'
        ))

      if labelmap:
        # check consistency between mask and labelmap
        res = self._CheckInputs(
          image1=mask,
          image2=labelmap
        )
        # arise errors if necessary
        if not res:
          raise ValueError((
            'Check consistency between mask and labelmap: FAILED '
            'There is a mismatch in the volume metadata that could alter '
            'the correctness of the results. '
            'Pipeline aborted'
          ))

    # set a dictionary with the common parameters
    # to share along the feature functors
    common = {
      'mask' : mask,
      'skeleton' : skeleton,
      'labelmap' : labelmap,
    }

    # store the weight extra parameters
    wextra_params = {}

    # if the weight are required set the key in the common
    # dictionary of parameters
    if self._features.get('enable_weighted_features', False):
      # set the weight common variable
      common['weight'] = 'weight'

      # check if the graphomics weight estimation algorithm
      # was set by the member functions or by the configuration file
      if not hasattr(self, '_wtype') and self._features.get('graph_weights'):
        # get the selected weight type
        wtype = self._features.get('graph_weights')
        # check the correctness of the name

      # If not, the default EdgeLengthPathsFilter will
      # be used
      else:
        wtype = 'EdgeLengthPathsFilter'

      if wtype not in self._weight_extractor.keys():
        # get the list of available methods
        available_wtype = ', '.join(self._weight_extractor.keys())
        raise ValueError((
          'Invalid weight extractor name. '
          f'Available classes are {available_wtype}. '
          f'Given {wtype}.'
        ))
      # extract the object from the available ones
      wtype = self._weight_extractor[wtype]
      # set the extra parameters that could be need by the filter
      wextra_params = {}

      # check if the required weight extractor has all the
      # inputs necessary
      # TODO: find a better way to check the wtype requirements
      if isinstance(wtype, EdgeLabelWeightFilter):
        # if it is a EdgeLabelWeightFilter the labelmap must
        # be provided by the user
        if labelmap is None:
          raise ValueError((
            'Invalid weight extractor. '
            'For the correct usage of the EdgeLabelWeightFilter as weight extractor '
            'a valid labelmap must be provided. '
            'See the SetLabelImage or SetLabelFilepath for the details.'
          ))
        # set the extra parameters required
        wextra_params['labelmap'] = labelmap
        wextra_params['mask'] = mask

      elif isinstance(wtype, EdgeLengthPathsFilter):
        # if it is a EdgeLengthPathsFilter the input volume
        # must have an equal spacing along all directions to
        # preserve the correctness evaluation of the lengths

        # get the image spacing
        spacing = mask.GetSpacing()
        # check the equality of the values
        if not all(spacing[0] == x for x in spacing):
          raise ValueError((
            'Invalid image spacing. '
            'For the correct usage of the EdgeLengthPathsFilter as weight extractor '
            'the input mask must have an equal spacing along all direction. '
            f'Given {spacing}'
          ))

      # set all the extra parameters
      w_name = wtype.__class__.__name__
      # if there are parameters to store
      if self._features.get(f'{w_name}Parameters', False):
        # set all the extra parameters
        for k, v in self._features.get(f'{w_name}Parameters').items():
          wextra_params[k] = v

      self._wtype = wtype

    # if the enable_weighted_features is not required
    # we can nullify the wtype object also if it was set
    else:
      # if it was set
      if hasattr(self, '_wtype'):
        # remove the attribute
        del self._wtype

    # check the number of threads to use
    nth = self._features.get('nth', 1)

    # Now we can perform the skeleton network extraction
    # on the input skeleton image/volume, getting all the
    # informations about nodes and edges

    # determine the input dimensionality
    ndim = len(skeleton.GetSize())

    # create the graph filter
    graph_filter = GraphThicknessImageFilter()
    # set the dimensionality of the input in the filter
    # for the evaluation of the internal kernels
    graph_filter.SetInputDimensionality(ndim=ndim)
    # set the number of threads to use
    graph_filter.SetGlobalDefaultNumberOfThreads(nth=nth)
    # execute the filter
    graph_filter.Execute(src=skeleton)

    # get the returning values
    nodes = graph_filter.GetNodePhysicalPoints()
    edges = graph_filter.GetEdgePhysicalPoints()
    lut = graph_filter.GetEdgeLUTPhysicalPoints()
    mapper = graph_filter.GetEdgeMap()
    weights = None # set to None as default

    # if necessary evaluate the graph weights according to the
    # required settings
    if hasattr(self, '_wtype'):
      # run the weight extractor filter
      self._wtype.Execute(
        nodelist=nodes,
        edgelist=edges,
        lut=lut,
        mapper=mapper,
        **wextra_params
      )
      # get the resulting weights
      weights = self._wtype.GetWeightsList()

    # using all the extracted information we can build the skeleton
    # graph using the filter
    graph_proxy = GraphFilter()
    # execute the filter on the inputs
    graph_proxy.Execute(
      lut=lut,
      weights=weights
    )
    # get the graph and store it in the common inputs
    common['G'] = graph_proxy.GetGraph()

    # store also the edge lut of the graph for further feature extraction
    common['lut'] = lut

    # run the graphomic features extraction for each class

    # define the storage of the final feature dict
    graphomic_features = {}

    # if the topological feature are required
    if self._features.get('enable_topology_features', False):
      # extract the list of required features
      todo, params = self._GetEnabledFeaturesByClassName(
        feature_class='topology'
      )
      # define the filter
      topology = GraphomicsTopology()
      # execute the filter considering the todo list
      topology.Execute(
        todo=todo,
        params=params,
        inputs=common
      )
      # get the computed features
      topological_features = topology.GetFeatures()
      # update the dictionary of graphomic features
      graphomic_features.update(topological_features)

    # if the spatial feature are required
    if self._features.get('enable_spatial_features', False):
      # extract the list of required features
      todo, params = self._GetEnabledFeaturesByClassName(
        feature_class='spatial'
      )
      # define the filter
      spatial = GraphomicsSpatial()
      # execute the filter considering the todo list
      spatial.Execute(
        todo=todo,
        params=params,
        inputs=common
      )
      # get the computed features
      spatial_features = spatial.GetFeatures()
      # update the dictionary of graphomic features
      graphomic_features.update(spatial_features)

    # if the centrality feature are required
    if self._features.get('enable_centrality_features', False):
      # extract the list of required features
      todo, params = self._GetEnabledFeaturesByClassName(
        feature_class='centrality'
      )
      # define the filter
      centrality = GraphomicsCentrality()
      # execute the filter considering the todo list
      centrality.Execute(
        todo=todo,
        params=params,
        inputs=common
      )
      # get the computed features
      centrality_features = centrality.GetFeatures()
      # update the dictionary of graphomic features
      graphomic_features.update(centrality_features)

    # return the graphomic features
    return graphomic_features

  def GetFeatures (self) -> dict :
    '''
    Get the graphomic features computed.

    Returns
    -------
      features : dict
        Dictionary of graphomic features evaluated by the filter.
        The features are indexed according to their name.
    '''
    if not hasattr(self, '_graphomic_features'):
      class_name = self.__class__.__name__
      raise RuntimeError(('Runtime Exception. '
        f'The {class_name} object is not executed yet. '
        'To get the weigts list you need to call the Execute function'
      ))

    # get the today date in YYYY-mm-dd hh:mm:sec fmt
    today = datetime.now()

    # Add to the dictionary the metadata of the package
    # required for the correct reproducibility of the results
    metadata = {
      'pyGraphomics_version' : __version__,
      'SimpleITK_version': sitk.__version__,
      'Numpy_version': np.__version__,
      'Scipy_version': sp.__version__,
      'Networkx_version': nx.__version__,
      'Skimage_version': ski.__version__,
      'Powerlaw_version': powerlaw.__version__,
      'Python_version': sys.version,
      'PipelineName': self._features.get('name', f'pygraphomics_{today}'),
      'PipelineDescription': self._features.get('desc', None),
      'PipelineVersion': self._features.get('pipeline_version', '0.0.1'),
      # TODO: check if other global metadata could be helpful
    }

    # save information about the weights usage
    metadata['WeightedGraph'] = self._features.get('enable_weighted_features', False)
    # if the weight extractor was used, save its information
    if hasattr(self, '_wtype'):
      metadata['GraphWeightsExtractor'] = self._wtype.__class__.__name__

    # add to the results the graphomic features
    metadata.update(self._graphomic_features)

    return metadata


if __name__ == '__main__':

  pass
