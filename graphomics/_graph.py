#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import networkx as nx
import SimpleITK as sitk
from scipy.spatial.distance import cdist

__author__  = ['Nico Curti',
               'Gianluca Carlini',
               'Riccardo Biondi'
              ]
__email__ = ['nico.curti2@unibo.it',
             'gianluca.carlini3@unibo.it',
             'riccardo.biondi7@unibo.it'
            ]

__all__ = ['GraphWeightsExtractorFilter',
           'NodePairwiseDistanceFilter',
           'EdgeLengthPathsFilter',
           'EdgeLabelWeightFilter',
           'GraphFilter'
          ]


ROI_METRICS = {
  'average' : np.mean,
  'median' : np.median,
  'std' : np.std,
  'variance' : np.var,
  'max' : np.max,
  'min' : np.min,
}


class GraphWeightsExtractorFilter (object):
  '''
  Abstract class for the computation of edge weights.

  All the provided weight evaluator must inherit from
  this class. In this way we can ensure a consistency
  of the entire package with also other custom implementations.
  The object architecture follows the same syntax of
  any other SimpleITK filter to facilitate the readability of
  the final pipeline.
  '''

  def __init__ (self):
    pass

  def _check_input (self, nodelist : list,
                          edgelist : list,
                          lut : dict,
                          mapper : sitk.Image
                    ) :
    '''
    Validate the input parameters
    '''
    # TODO: implement it
    pass

  def Execute (self, nodelist : list,
                     edgelist : list,
                     lut : dict,
                     mapper : sitk.Image
              ) -> dict :
    '''
    Compute the graph weights according to a
    custom evaluation metric.
    The input represents the entire set of knowledge
    about the graph identified by the GraphThicknessImageFilter.

    Parameters
    ----------
      nodelist : list
        List of node coordinates

      edgelist : list
        List of pairs as (src, tgt) with the items belonging
        to the nodelist

      lut : dict
        Lookup table of the edge labels for the mapper.

      mapper : sitk.Image
        The edge map stores the edge paths as disjoint lines in the
        original volume. The connected components of the edge-map are
        the edges of the graph found by the filter.

    Returns
    -------
      weights : dict
        Lookup table of weights to associate at each edge in the graph
    '''
    # TODO: add here all the pre-processing steps required
    # by all the inherit filters
    self._check_input(
      nodelist=nodelist,
      edgelist=edgelist,
      lut=lut,
      mapper=mapper,
    )

    return self

  def GetWeightsList (self) -> dict :
    '''
    Get the graph weights computed according to the defined
    evaluation criteria.

    Returns
    -------
      weights : dict
        Lookup table of floating point weights to associate at each edge pair
        in the graph. The keys of the weights' lut are associated to the
        list of keys of the original edge lut.
    '''
    if not hasattr(self, '_weights'):
      class_name = self.__class__.__name__
      raise RuntimeError(('Runtime Exception. '
        f'The {class_name} object is not executed yet. '
        'To get the weigts list you need to call the Execute function'
      ))

    return self._weights


class NodePairwiseDistanceFilter (GraphWeightsExtractorFilter):
  '''
  Evaluate the weights of the graph as the pairwise distance
  between the node positions according to the given metric.
  The object wraps the scipy implementation of the function
  (ref. [scipy_])

  Parameters
  ----------
    metric: str or function (optional, default 'euclidean')
      The metric to use to compute distances in high dimensional space.
      If a string is passed it must match a valid predefined metric. If
      a general metric is required a function that takes two 1d arrays and
      returns a float can be provided. For performance purposes it is
      required that this be a numba jit'd function. Valid string metrics
      include:

      * euclidean (or l2)
      * manhattan (or l1)
      * cityblock
      * braycurtis
      * canberra
      * chebyshev
      * correlation
      * cosine
      * dice
      * hamming
      * jaccard
      * kulsinski
      * ll_dirichlet
      * mahalanobis
      * matching
      * minkowski
      * rogerstanimoto
      * russellrao
      * seuclidean
      * sokalmichener
      * sokalsneath
      * sqeuclidean
      * yule
      * wminkowski

      Metrics that take arguments (such as minkowski, mahalanobis etc.)
      can have arguments passed via the metric_kwds dictionary. At this
      time care must be taken and dictionary elements must be ordered
      appropriately; this will hopefully be fixed in the future.

    metric_kwds: dict (default := {})
      Arguments to pass on to the metric, such as the ``p`` value for
      Minkowski distance.

  .. _scipy: https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.cdist.html
  '''

  def __init__ (self, metric : str = 'euclidean',
                      metric_kwds : dict = {}
               ):

    super(NodePairwiseDistanceFilter, self).__init__()
    self._metric = metric
    self._metric_kwds = metric_kwds

  def Execute (self, nodelist : list,
                     edgelist : list,
                     lut : dict,
                     mapper : sitk.Image
              ) -> dict :
    '''
    Compute the graph weights according to a
    custom evaluation metric.
    The input represents the entire set of knowledge
    about the graph identified by the GraphThicknessImageFilter.

    Parameters
    ----------
      nodelist : list
        List of node coordinates

      edgelist : list
        List of pairs as (src, tgt) with the items belonging
        to the nodelist

      lut : dict
        Lookup table of the edge labels for the mapper.

      mapper : sitk.Image
        The edge map stores the edge paths as disjoint lines in the
        original volume. The connected components of the edge-map are
        the edges of the graph found by the filter.

    Returns
    -------
      weights : dict
        Lookup table of weights to associate at each edge in the graph
    '''
    # call the base class executor for safety checks
    super(NodePairwiseDistanceFilter, self).Execute(
      nodelist=nodelist,
      edgelist=edgelist,
      lut=lut,
      mapper=mapper
    )

    # unpack the source and target coordinates
    src, dst = zip(*edgelist)

    # compute the distance between each pair of points
    weights = cdist(src, dst, metric=self._metric, **self._metric_kwds)

    # ravel the weight buffer and convert it to a list
    # for consistency with the other filters
    weights = weights.ravel().tolist()

    # create the lut of weights
    self._weights = {k : w for k, w in zip(lut.keys(), weights)}

    return self


class EdgeLengthPathsFilter (GraphWeightsExtractorFilter):
  '''
  Evaluate the weights of the graph as the lenght of the original
  path between two node positions as the number of items in the
  mapper.
  '''

  def __init__ (self):
    super(EdgeLengthPathsFilter, self).__init__()

    self._stats = sitk.LabelShapeStatisticsImageFilter()
    self._stats.SetBackgroundValue(0)
    self._stats.SetGlobalDefaultNumberOfThreads(1)

  def SetGlobalDefaultNumberOfThreads (self, nth : int):
    '''
    Set the number of threads to used by the parallel
    filters used by the object.

    Parameters
    ----------
      nth : int
        Number of threads
    '''
    self._stats.SetGlobalDefaultNumberOfThreads(max(nth, 1))

  def Execute (self, nodelist : list,
                     edgelist : list,
                     lut : dict,
                     mapper : sitk.Image
              ) -> dict :
    '''
    Compute the graph weights according to a
    custom evaluation metric.
    The input represents the entire set of knowledge
    about the graph identified by the GraphThicknessImageFilter.

    Parameters
    ----------
      nodelist : list
        List of node coordinates

      edgelist : list
        List of pairs as (src, tgt) with the items belonging
        to the nodelist

      lut : dict
        Lookup table of the edge labels for the mapper.

      mapper : sitk.Image
        The edge map stores the edge paths as disjoint lines in the
        original volume. The connected components of the edge-map are
        the edges of the graph found by the filter.

    Returns
    -------
      weights : dict
        Lookup table of weights to associate at each edge in the graph
    '''
    # call the base class executor for safety checks
    super(EdgeLengthPathsFilter, self).Execute(
      nodelist=nodelist,
      edgelist=edgelist,
      lut=lut,
      mapper=mapper
    )

    # get the dimension of the input (aka 3D or 2D)
    ndim = len(mapper.GetSize())

    # compute the statistics of the connected components found
    # in the mapper input
    self._stats.Execute(mapper)

    # initialize an empty buffer for the weights
    weights = {}

    # loop along the edge lut keys
    # NOTE: the edgelist is ordered as the lut
    # dictionary so the correspondance between
    # edgelist and weights is correct
    for l in lut.keys():
      # get the indices of the voxels belonging to the CC
      idx = self._stats.GetIndexes(int(l))
      # the length of the path is given by the number of items
      # found in the index list (corrected by the dimensionality
      # of the mapper, aka 2D or 3D)
      w = len(idx) // ndim
      # we are assuming an equal spacing of the volume along
      # all direction

      # associate the weight to the corresponding edge
      weights[l] = w

    self._weights = weights

    return self


class EdgeLabelWeightFilter (GraphWeightsExtractorFilter):
  '''
  Evaluate the weights of the graph keeping information from
  a label image/volume.

  An example of application of this filter is given by the
  possibility to weigh the topological network determined
  by a CT/MRI scan according to the signal of the corresponding
  and co-registered PET scan.

  The filter apply a Watershed segmentation algorithm on the
  provided label map, considering as marker for the segmentation
  the topological edge curves contained in the mapper.
  Considering each region identified by the Watershed algorithm,
  the required metric signal is computed masking the segmentation
  with the original mask and the score is associated as weight
  of the corresponding edge.

  A step-by-step procedure for this filter is detailed in the
  notebooks_.

  .. _notebooks: https://github.com/Nico-Curti/graphomics/blob/main/docs/source/notebooks/graphomics_semantic_segmentation.ipynb
  '''

  def __init__ (self):
    super(EdgeLabelWeightFilter, self).__init__()

    self._stats = sitk.LabelShapeStatisticsImageFilter()
    self._stats.SetBackgroundValue(0)
    self._stats.SetGlobalDefaultNumberOfThreads(1)

  def SetGlobalDefaultNumberOfThreads (self, nth : int):
    '''
    Set the number of threads to used by the parallel
    filters used by the object.

    Parameters
    ----------
      nth : int
        Number of threads
    '''
    self._stats.SetGlobalDefaultNumberOfThreads(max(nth, 1))

  def Execute (self, nodelist : list,
                     edgelist : list,
                     lut : dict,
                     mapper : sitk.Image,
                     mask : sitk.Image,
                     labelmap : sitk.Image,
                     metric : str = 'average'
              ) -> dict :
    '''
    Compute the graph weights according to the information stored
    in the corresponding labelmap, according to the provided metric.
    The input represents the entire set of knowledge
    about the graph identified by the GraphThicknessImageFilter.

    Parameters
    ----------
      nodelist : list
        List of node coordinates

      edgelist : list
        List of pairs as (src, tgt) with the items belonging
        to the nodelist

      lut : dict
        Lookup table of the edge labels for the mapper.

      mapper : sitk.Image
        The edge map stores the edge paths as disjoint lines in the
        original volume. The connected components of the edge-map are
        the edges of the graph found by the filter.

      mask : sitk.Image
        Original image volume to use as mask on the resulting
        semantic segmentation.

      labelmap : sitk.Image
        Input image/volume with the same dimensions and metadata
        of the mapper input. The labelmap is used to evaluate
        the network weights considering the tasselation obtained
        by the Watershed algorithm applied marking the edgelist
        as seed points.

        .. note::
          The labelmap must contains the signal on the only region
          of interest of the image/volume, i.e. it must be masked
          according to the original image/volume from which the
          skeleton was extracted.
          We considered the background set as 0 and non null values
          in the region to be considered.

      metric : str or collable (default := 'average')
        Function to apply for the estimation of the weight in the
        identified label ROI.
        Pre-built functions are:

        * average
        * median
        * std
        * variance
        * max
        * min

    Returns
    -------
      weights : dict
        Lookup table of weights to associate at each edge in the graph
    '''
    # call the base class executor for safety checks
    super(EdgeLabelWeightFilter, self).Execute(
      nodelist=nodelist,
      edgelist=edgelist,
      lut=lut,
      mapper=mapper
    )

    # check the validity of the provided metric

    # it belongs to the list of pre-built functions
    if metric in ROI_METRICS:
      reducer = ROI_METRICS[metric]
    # it could be a custom callable function...
    elif callable(metric):
      reducer = metric
    # otherwise it should be an error...
    else:
      raise ValueError((
        'Invalid reduction metric for ROI weight estimation. '
        'The metric must be one of the pre-built function or a custom '
        'callable object which accept as input only the list of variables. '
        f'Given {metric}'
      ))

    # determine the dimensionality of the provided input (2D/3D)
    ndim = len(mapper.GetSize())

    # extract the marker mask filtering the mapper and
    # selecting only the positive values, i.e. the edge markers
    markers = sitk.Threshold(
      image1=mapper,
      lower=0.0,
      upper=float(max(lut.keys())),
      outsideValue=0.0
    )

    # apply the watershed algorithm using the marker image
    # for the initialization of the seed points
    ws = sitk.MorphologicalWatershedFromMarkers(
      image=mapper,
      markerImage=markers,
      markWatershedLine=True,
      fullyConnected=False
    )

    # mask the resulting watershed segmentation according
    # to the original volume
    ws = sitk.Mask(
      image=ws,
      maskImage=mask,
      outsideValue=0,
      maskingValue=0,
    )

    # evaluate the connected components statistics of the
    # identified regions
    self._stats.Execute(ws)

    # initialize an empty buffer for the weights
    weights = {}

    # loop along the edge lut keys
    # NOTE: the edgelist is ordered as the lut
    # dictionary so the correspondance between
    # edgelist and weights is correct
    for l in lut.keys():
      # get the indices of the voxels belonging to the CC
      idx = self._stats.GetIndexes(int(l))

      # reshape to numpy coords
      idx = [idx[i : i + ndim]
             for i in range(0, len(idx), ndim)
            ]
      # get the value in the convolution volume
      label_val = [labelmap[i] for i in idx]

      # estimate the weight considering the required statistic
      w = reducer(label_val)

      # associate the weight to the corresponding edge
      weights[l] = w

    self._weights = weights

    return self


class GraphFilter (object):
  '''
  Create a graph object from attributes (ref. [networkx_]).

  This is an utility class to wrap the outputs of
  the GraphThicknessImageFilter, providing a ready-to-use
  graph object (networkx-like) for the next features
  extraction step.
  The object architecture follows the same syntax of
  any other SimpleITK filter to facilitate the readability of
  the final pipeline.

  .. _networkx: https://networkx.org/documentation/stable/tutorial.html
  '''

  def __init__ (self):
    pass

  def Execute (self, lut : dict,
                     weights : dict = None
              ) :
    '''
    Execute the filter on the network attributes and
    create a weighted graph object.

    Parameters
    ----------
      lut : dict
        LookUp table of the edge labels associated to the correspoding
        nodes. This object is mandatory for the correct association
        between the value in the edge_map, the nodes, and the possible
        weighted graph.

      weights : list (default := None)
        List of weights associated to each edge pair
    '''

    # define the graph
    graph = nx.Graph()
    # get the list of nodes from the lut
    nodelist = list(set(sum(list(map(list, lut.values())), [])))
    # add the list of nodes to the empty graph
    graph.add_nodes_from(nodelist)

    if weights is not None:

      # check the consistency of the edgelist and weights
      if len(lut) != len(weights):
        raise ValueError((
          'Lenght mismatch between edgelist and weights'
        ))

      # check the two lut has the same set of keys
      if lut.keys() != weights.keys():
        raise ValueError((
          'Key mismatch between edge lut and weights'
        ))

      # associate the correct weight to each edge pair
      wedges = [(*lut[k], weights[k])
        for k, (src, tgt) in lut.items()
        if src != tgt
      ]

      # add the list of edges to the graph
      graph.add_weighted_edges_from(wedges, weight='weight')

    else:
      # add the list of edges to the graph
      graph.add_edges_from([(src, tgt)
        for src, tgt in lut.values()
        if src != tgt
      ])

    self._graph = graph

    return self

  def GetGraph (self) -> nx.Graph :
    '''
    Get the graph built using the provided parameters.

    Returns
    -------
      graph : nx.Graph
        Graph object with the correct setting of all the parameters.
    '''
    if not hasattr(self, '_graph'):
      class_name = self.__class__.__name__
      raise RuntimeError(('Runtime Exception. '
        f'The {class_name} object is not executed yet. '
        'To get the graph object you need to call the Execute function'
      ))

    return self._graph


if __name__ == '__main__':

  pass
