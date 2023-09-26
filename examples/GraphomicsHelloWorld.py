#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import numpy as np
import pylab as plt
import SimpleITK as sitk

from graphomics import __version__
# import the function required for the input loading
from graphomics import LoadImageFileInAnyFormat
# import filter for skeletonize image/volume
from graphomics import SkeletonizeImageFilter
# import filter for graph extraction
from graphomics import GraphThicknessImageFilter
# import filter for the graphomic feature extraction
from graphomics import GraphomicsFeatureExtractor

__author__  = ['Nico Curti',
               'Gianluca Carlini',
               'Riccardo Biondi'
              ]
__email__ = ['nico.curti2@unibo.it',
             'gianluca.carlini3@unibo.it',
             'riccardo.biondi7@unibo.it'
            ]


if __name__ == '__main__':

  # In this example we will see how we can define and manage
  # a graphomic pipeline, starting from the loading of the
  # input medical image/volume, passing throw the extraction
  # of the skeleton graph and its visualization, reaching the
  # extraction of the graphomic features using the filters
  # provided by the package.
  # This is just an 'HelloWorld' example and further
  # documentations and real-case applications could be found
  # in the notebooks folder
  # (ref. https://github.com/Nico-Curti/graphomics/blob/main/docs/source/notebooks)

  # ####################################################### #
  # NOTE: this code is not a ready-to-use code since it     #
  # depends on the definition of the `filename` variable    #
  # defined below!                                          #
  # ####################################################### #

	# check the version of the installed pyGraphomics library
  print(f'Working with pyGraphomics v{__version__}')

  # The initial point of any image analysis application
  # involves the loading of the image file.
  # It can be easily done using the SimpleITK APIs which
  # supports a wide range of data formats.
  # However, the pyGraphomics package provides a ready-to-use
  # function which wraps and extends the SimpleITK functions.

  # NOTE: the most important thing to take in mind when you
  # work with the pyGraphomics package is that the format of
  # the input data **must** be a sitk.Image. This is a mandatory
  # requirement, so also if you decide to move to other import
  # tools, please ensure to cast the input to this format before
  # the feeding to the package filters, taking care about preserving
  # all the metadata of the image!

  # declare a filename of the image that you want to load
  filename = 'path/to/data/image.nii.gz'
  # load the image volume
  # NOTE: to ensure the correct behavior of the graphomic features
  # extraction, the input image **must** be a binary mask with values
  # equal to 0 (background) and 1 (foreground).
  # You can easily force the binarization of the loaded volume, setting
  # the `binarize` argument to True: the loaded image will be thresholded
  # in the correct binary format keeping all the values != 0 as
  # foreground.
  # If the `equal_spacing` is True, we force a resampling of the input
  # volume to an equal spacing along all directions: assuming an image
  # with spacing (N, N, M), the equal spacing force it to become
  # uniform according to the most frequent value, i.e. (N, N, N)
  mask = LoadImageFileInAnyFormat(
    filepath=filename,
    binarize=False,
    equal_spacing=False
  )
  assert isinstance(mask, sitk.Image)

  # The next step will involve the evaluation of skeleton of the input
  # shape image.
  # Also in this case there can be used different skeletonization
  # algorithms to achieve this purpose, but the pyGraphomics package
  # provides a ready-to-use wrap of the most common implementation
  # that can be directly applied on the mask image

  # declare the skeletonization filter to use
  skeleton_filter = SkeletonizeImageFilter()
  # execute the skeleton filter on the input image mask
  skeleton_filter.Execute(src=mask)
  # extract the resulting skeleton image
  skeleton = skeleton_filter.GetSkeletonImage()

  # The skeleton image has the same dimensionality and metadata of the
  # original mask: this is another requirement of the pyGraphomics
  # package that aims to ensure the correct behavior of the feature
  # extraction steps.
  assert isinstance(skeleton, sitk.Image)
  assert mask.GetSize() == skeleton.GetSize()
  assert mask.GetSpacing() == skeleton.GetSpacing()
  assert mask.GetDirection() == skeleton.GetDirection()

  # After the skeleton extraction, the processing involves the estimation
  # of the network from the skeleton, identifying the nodes and edges
  # which define the graph of the ramification found.
  # This step could be achieved using the filter defined in the
  # pyGraphomics library which works on both 2D and 3D images.
  # To be sure to use the correct version of the graph-extraction algorithm
  # we need to provide to the filter the dimensionality of the input
  # that we want to process.
  ndim = len(skeleton.GetSize())
  graph_filter = GraphThicknessImageFilter()
  graph_filter.SetInputDimensionality(ndim=ndim)
  # execute the filter on the evaluated skeleton image
  graph_filter.Execute(src=skeleton)
  # get the evaluated graph properties
  nodelist = graph_filter.GetNodePhysicalPoints()
  edgelist = graph_filter.GetEdgePhysicalPoints()
  edgeLUT  = graph_filter.GetEdgeLUTPhysicalPoints()
  mapper   = graph_filter.GetEdgeMap()
  # NOTE: in the above filter we are using an image directly loaded
  # by the package, so we can be reasonably sure that the metadata
  # stored in the file were preserved correctly.
  # In this case the filter allows us to extract the node/edge
  # coordinates in terms of `PhysicalPoints`, i.e. related to the
  # real-world system of coordinates.
  # If you are not interested on this kind of information, the
  # graph_filter allow to get also the related indexes of the
  # coordinates, i.e. the coordinates in the system of the image
  # space.
  # In this case, it is sufficient to change the suffix `PhysicalPoint`
  # with the `Indexes` one.

  # Now you can visualize the obtained graph information in a 3D plot
  # to ensure the correctness of the extracted results.

  # define a 3D figure
  fig = plt.figure(figsize=(15, 15))
  ax = fig.add_subplot(projection='3d')

  # plot the skeleton paths as a series of scatter points
  pz, py, px = np.where(sitk.GetArrayViewFromImage(skeleton))
  ax.scatter(px, py, pz,
    color='lightgray',
    marker='o',
    s=10,
    alpha=0.25
  )

  # plot the node coordinates as dots with a different color and size
  # NOTE: since the `np.where` function works on the indexes
  # of the image, the nodelist to plot **must** be the correct one!
  ax.scatter(*zip(*graph_filter.GetNodeIndexes()),
    color='blue',
    marker='o',
    s=20,
    alpha=0.5
  )

  # plot the graph links as lines between vertices
  # NOTE: also in this case you need to use the correct transformation
  # of the edge coordinates!
  for src, dst in graph_filter.GetEdgeIndexes():
    ax.plot(*zip(*(src, dst)), '-',
      color='lime',
      linewidth=2,
      alpha=0.5
    )

  # Now we can run our graphomics pipeline, extracting the whole set
  # of available features in the package.
  # To this purpose, you can use the `GraphomicsFeatureExtractor`
  # provided by the pyGraphomics package

  # define the filter
  extractor = GraphomicsFeatureExtractor()
  # enable all the available graphomic features
  # NOTE: a customization of the list of features to process and their
  # internal parameters could be achieved by loading a pre-defined configuration
  # file (ref. https://github.com/Nico-Curti/graphomics/blob/main/cfg/template.yml)
  # or by manually setting the feature-classes and feature-names using
  # the filter member functions
  extractor.EnableAllFeatures()
  # set the required arguments
  extractor.SetMaskImage(mask=mask)
  # NOTE: if the skeleton was not pre-computed you can avoid this
  # input setting and the skeleton image will be internally pre-computed
  # by the extractor filter itself!
  extractor.SetSkeletonImage(skeleton=skeleton)
  # execute the filter on the set inputs
  extractor.Execute()
  # get the resulting graphomic features computed
  graphomic_features = extractor.GetFeatures()

  # display the results
  print(graphomic_features)
  # or/and save it to file
  with open('results.json', 'w', encoding='utf-8') as fp:
    json.dumps(
      obj=graphomic_features,
      fp=fp,
      ensure_ascii=True,
      indent=2
    )
