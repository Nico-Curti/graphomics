#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .__version__ import __version__
# import the function required for the input loading
from ._loader import (
  LoadImageFileInAnyFormat,
  ResampleSpacing,
  ResampleSize,
  BoundingBox,
  CropMinimumBoundingBox,
  IsInImageFilter,
)
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
# import filter for the graphomic feature extraction
from .featureextractor import GraphomicsFeatureExtractor

__author__  = ['Nico Curti',
               'Gianluca Carlini',
               'Riccardo Biondi'
              ]
__email__ = ['nico.curti2@unibo.it',
             'gianluca.carlini3@unibo.it',
             'riccardo.biondi7@unibo.it'
            ]
