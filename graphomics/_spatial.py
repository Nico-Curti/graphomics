#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import networkx as nx
import SimpleITK as sitk
from operator import itemgetter
from functools import lru_cache
from scipy.stats import gaussian_kde

from ._statistics import _get_distribution_main_stats
from ._basefeature import _BaseGraphomicsFeatures

__author__  = ['Nico Curti',
               'Gianluca Carlini',
               'Riccardo Biondi'
              ]
__email__ = ['nico.curti2@unibo.it',
             'gianluca.carlini3@unibo.it',
             'riccardo.biondi7@unibo.it'
            ]

__all__ = ['GraphomicsSpatial']


class GraphomicsSpatial (_BaseGraphomicsFeatures):
  '''
  Estimate graphomics spatial statistic features.

  This class implements the estimation of the spatial
  statistic graphomics features, considering the node
  coordinates as a set of disjointed data points.
  The spatial statistics features estimates a series of
  metric for the quantification of the fractality, density,
  and randomness of the vertices of the input graph.
  The list of implemented spatial statistic features is:

  * **Node density statistics:**

    The local spatial density of the nodes is evaluated
    using a Gaussian kernel density estimator. This
    metric could provide information about the sparsity
    of the nodes in the graph and the presence of possible
    clusters of points.
    As resulting features the filter provides the main
    statistics of the density distribution of values.

  * **Fractal dimension:**

    The fractal dimension is a term invoked in the science of
    geometry to provide a rational statistical index of
    complexity detail in a pattern.
    The fractal dimension is a feature strictly related to the
    complexity of the skeleton graph and it can be evaluated
    directly from the binarized mapper of the skeleton.

  * **Average shortest path:**

    The average shortest path length is the sum of path lengths `d(u,v)`
    between all pairs of nodes.
    This metric could be useful for the quantification of the complexity
    of the skeleton graph, especially when we consider a weighted graph.

  * **Eccentricity:**

    The eccentricity of a node v is the maximum distance from v to all
    other nodes in G.
    In diffusion processes, this is an indicator of the effort to
    reach the periphery of a network from a source node.
    The reciprocal of the eccentricity is called the eccentricity
    centrality.
    This is used to make sure that more central nodes have a higher
    value because such central nodes are the ones with the smallest
    eccentricity score.
    Like other centralities, the node with the highest score is now
    the most central node and these values are comparable.

  * **Center of Mass:**

    The center of mass of the skeleton graph is defined as the
    point equally distanced by all the other
    points.
    The center of mass of the skeleton graph could not belong to
    the skeleton and it could be different by the center of
    mass of the 2D/3D shape.
    The value could be significant of asymmetries in the shape
    and it could be used for the evaluation of relative
    distances of the other nodes (ref. Distance features
    of the Spatial class).

  * **Distance of most central nodes:**

    The distance of the nodes with higher degree centrality in
    relation to the center of mass of the 2D/3D shape could be
    informative about the distribution of the "bridges" in
    the shape.

  * **Distance of no-pendant nodes:**

    The distance of the no-pendant nodes, i.e. the nodes a degree
    centrality != 1, in relation to the center of mass of the
    2D/3D shape could be informative about the distribution of
    the ramification points in the shape.

  * **Distance of pendant nodes:**

    The distance of the pendant nodes, i.e. the nodes with lowest
    degree centrality, in relation to the center of mass of the
    2D/3D shape could be informative about the distribution of
    the tails in the shape.
  '''

  def __init__ (self, *args, **kwargs):
    super(GraphomicsSpatial, self).__init__(*args, **kwargs)

  def _GetNodeDensityStatistics (self, G : nx.Graph) -> dict :
    '''
    Get the main statistics of the node density distribution
    of values (ref. [scipy-kde_]).

    Parameters
    ----------
      G : nx.Graph
        Input graph to analyze

    Returns
    -------
      stats : dict
        Dictionary with the computed statistics

    .. _scipy-kde: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.gaussian_kde.html
    '''
    # extract the list of node coordinates from the graph
    nodes = G.nodes(data=False, default=None)
    # convert the nodes to numpy coordinates
    pts = np.asarray(nodes)
    pts = np.transpose(pts) # KDE requires input (dim, N)
    # apply the Gaussian KDE for the density estimation
    kde = gaussian_kde(pts)
    # evaluate the density on the original points
    density = kde(pts)

    # compute the statistics of the density distribution
    stats = _get_distribution_main_stats(
      x=density,
      prefix='node_density_'
    )

    return stats

  def _GetFractalDimension (self, skeleton : sitk.Image,
                                  max_box_size : int = None,
                                  min_box_size : int = 1,
                                  n_samples : int = 10,
                                  n_offsets : int = 0
                           ) -> float :
    r'''
    Evaluate the fractal dimension of the skeleton graph.

    The computation follows the box-counting algorithm
    performing the polynomial fit according to the equation:

    .. math::
      dim(S) = \lim_{\varepsilon\rightarrow0}\frac{\log{N(\varepsilon)}}{\log{\frac{1}{\varepsilon}}}

    This is a wrap of the original function proposed by
    [ChatzigeorgiouGroup_]

    Parameters
    ----------
      skeleton : sitk.Image
        Input image to analyze.

      max_box_size : int (default := None)
        The largest box size, given as the power of 2 so that
        2**max_box_size gives the side-length of the largest box.

      min_box_size : int (default := 1)
        The smallest box size, given as the power of 2 so that
        2**min_box_size gives the side-length of the smallest box.

      n_samples : int (default := 0)
        Number of scales to measure over.

      n_offsets : int (default := 0)
        Number of offsets to search over to find the smallest set N(s)
        to cover all voxels>0.

    Returns
    -------
      fractal_dim : float
        Fractal dimension score

    .. _ChatzigeorgiouGroup: https://github.com/ChatzigeorgiouGroup/FractalDimension
    '''

    # convert the input skeleton to a binary mask
    mask = sitk.GetArrayViewFromImage(skeleton)
    mask = np.where(mask != 0, 1, 0)

    # determine the scales to measure on
    if max_box_size is None:
      # default max size is the largest power of 2 that
      # fits in the smallest dimension of the array:
      max_box_size = int(
        np.floor(
          np.log2(
            np.min(mask.shape)
          )
        )
      )

    scales = np.floor(
      np.logspace(
        max_box_size,
        min_box_size,
        num=n_samples,
        base=2
      )
    )
    # remove duplicates that could occur as a result of the floor
    scales = np.unique(scales)

    # get the locations of all non-zero pixels
    voxels = np.asarray(
      list(
        zip(*np.where(mask != 0))
      )
    )

    # count the minimum amount of boxes touched
    Ns = []
    # loop over all scales
    for scale in scales:
      touched = []
      if n_offsets == 0:
        offsets = [0]
      else:
        offsets = np.linspace(0, scale, n_offsets)

      # search over all offsets
      for offset in offsets:
        bin_edges = [np.arange(0, i, scale)
                      for i in mask.shape
                    ]
        bin_edges = [np.hstack([0 - offset, x + offset])
                      for x in bin_edges
                    ]
        H1, e = np.histogramdd(
          sample=voxels,
          bins=bin_edges
        )
        touched.append(np.sum(H1 > 0))

      Ns.append(touched)

    Ns = np.asarray(Ns)

    # From all sets N found, keep the smallest one at each scale
    Ns = Ns.min(axis=1)

    # Only keep scales at which Ns changed
    scales = [1. / np.min(scales[Ns == x])
              for x in Ns
             ]

    Ns = np.unique(Ns)
    Ns = Ns[Ns > 0]
    scales = scales[:len(Ns)]
    # perform fit
    coeffs = np.polyfit(np.log(scales), np.log(Ns), 1)

    return -coeffs[0]

  def _GetAverageShortestPathLength (self, G : nx.Graph,
                                           weight : str = None
                                    ) -> float :
    '''
    Get the average shortest path length in the graph.
    If the graph is made by a single connected component, the
    metric is evaluated on the entire graph (ref [networkx-shortestpath_]).
    If the graph is made by multiple connected components, the
    metric is evaluated considering only the largest connected
    component sub-graph.
    If the weight key is passed the metric takes care of the
    edge weights during the evaluation.

    Parameters
    ----------
      G : nx.Graph
        Input graph to analyze.

      weight : str (default := None)
        Evaluate the metric considering the graph weights.

    Returns
    -------
      shortest : float
        The average shortest path length in the graph.

    .. _networkx-shortestpath: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.generic.average_shortest_path_length.html
    '''

    # if the network is a single connected component
    if nx.is_connected(G):
      shortest = nx.average_shortest_path_length(
        G=G,
        weight=weight
      )
    # otherwise evaluate the metric on the largest connected
    # component
    else:
      # get the largest connected component indices
      cc = max(nx.connected_components(G),
        key=len
      )
      # extract the related sub-graph
      G0 = G.subgraph(cc)
      # evaluate the shortest path on it
      shortest = nx.average_shortest_path_length(
        G=G0,
        weight=weight
      )

    return shortest

  def _GetEccentricity (self, G : nx.Graph,
                              weight : str = None
                       ) -> dict :
    '''
    Get the main statistics of the node eccentricity
    distribution of values (ref. [networkx-eccentricity_]).

    Parameters
    ----------
      G : nx.Graph
        Input graph to analyze

    Returns
    -------
      stats : dict
        Dictionary with the computed statistics

    .. _networkx-eccentricity: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.distance_measures.eccentricity.html
    '''
    # check if weights are available
    weight_prefix = '' if weight is None else 'weighted_'

    # if the network is a single connected component
    if nx.is_connected(G):
      # compute the distribution of values
      if int(nx.__version__.split('.')[0]) >= 3:
        ecc = nx.eccentricity(
          G=G,
          v=None,
          sp=None,
          weight=weight
        )
      else:
        # for the older version of networkx there is no
        # the possibility to insert weights
        weight_prefix = ''
        ecc = nx.eccentricity(
          G=G,
          v=None,
          sp=None
        )
      # compute the statistics of the values distribution
      stats = _get_distribution_main_stats(
        x=list(ecc.values()),
        prefix=f'node_{weight_prefix}eccentricity_'
      )
    # otherwise evaluate the metric on the largest connected
    # component
    else:
      # get the largest connected component indices
      cc = max(nx.connected_components(G),
        key=len
      )
      # extract the related sub-graph
      G0 = G.subgraph(cc)
      # compute the distribution of values
      if int(nx.__version__.split('.')[0]) >= 3:
        ecc = nx.eccentricity(
          G=G0,
          v=None,
          sp=None,
          weight=weight
        )
      else:
        weight_prefix = ''
        ecc = nx.eccentricity(
          G=G0,
          v=None,
          sp=None
        )
      # compute the statistics of the values distribution
      stats = _get_distribution_main_stats(
        x=list(ecc.values()),
        prefix=f'node_{weight_prefix}eccentricity_'
      )

    return stats

  @lru_cache(maxsize=1)
  def _GetCenterOfMass (self, G : nx.Graph) -> np.ndarray :
    '''
    Get the center of mass of the input graph nodes
    (ref. [wiki_]).

    Parameters
    ----------
      G : nx.Graph
        Input graph to analyze.

    Returns
    -------
      cdm : np.ndarray
        2D or 3D array of the coordinates of the center
        of mass of the input graph nodes.

    .. _wiki: https://en.wikipedia.org/wiki/Center_of_mass
    '''
    # get the node coordinates from the graph
    nodes = np.asarray(G.nodes())
    # evaluate the barycenter of the coordinates
    cdm = nodes.mean(axis=0)

    return cdm

  def _GetDistanceMostCentralNodes (self, G : nx.Graph,
                                          weight : str = None,
                                          topk : int = 10,
                                   ) -> dict:
    '''
    Get the distance of the top-k most central nodes in the graph
    in relation to the center of mass.

    Parameters
    ----------
      G : nx.Graph
        Input graph to analyze.

      weight : str (default := None)
        Evaluate the metric considering the graph weights.

      topk : int (default := 10)
        Top K nodes to consider in the evaluation.

    Returns
    -------
      stats : dict
        Dictionary with the computed statistics.
    '''
    # ensure that at least the top K exists
    topk = min(G.number_of_nodes() - 1, topk)
    # check if weights are available
    weight_prefix = '' if weight is None else 'weighted_'
    # add parameter of topk in the label
    weight_prefix += f'top{topk}_'
    # compute the distribution of values
    degree = G.degree(weight=weight)
    # get the top K node coordinates
    topk_degree = list(map(itemgetter(0),
      sorted(
        dict(degree).items(),
        key=lambda x : x[1]
        )[-topk:]
      )
    )
    # convert it to numpy array
    topk_degree = np.asarray(topk_degree)
    # evaluate the center of mass of the graph
    cdm = self._GetCenterOfMass(G=G)
    # standardize the coordinates translating the center
    topk_degree_standardized = (topk_degree - cdm)
    # evaluate the Euclidean distance from the center
    distance = np.sqrt(
      np.sum(
        np.square(topk_degree_standardized),
        axis=1
      )
    )
    # compute the statistics of the values distribution
    stats = _get_distribution_main_stats(
      x=distance,
      prefix=f'node_{weight_prefix}distance_'
    )

    return stats

  def _GetDistanceNoPendantNodes (self, G : nx.Graph) -> dict:
    '''
    Get the main statistics of the distribution of distances
    of pendant nodes of the graph in relation to the center
    of mass.

    Parameters
    ----------
      G : nx.Graph
        Input graph to analyze.

    Returns
    -------
      stats : dict
        Dictionary with the computed statistics.
    '''
    # get the list of no-pendant nodes
    no_pendant = [n for n, d in G.degree() if d > 1]
    # check if the graph is not a set of disjointed nodes
    if not no_pendant:
      # the no-pendant nodes are the same of pendant ones
      # and therefore the statistics must be the same
      no_pendant = list(G.nodes())
    # convert it to a numpy array
    no_pendant = np.asarray(no_pendant)
    # evaluate the center of mass of the graph
    cdm = self._GetCenterOfMass(G=G)
    # standardize the coordinates translating the center
    no_pendant_standardized = (no_pendant - cdm)
    # evaluate the Euclidean distance from the center
    distance = np.sqrt(
      np.sum(
        np.square(no_pendant_standardized),
        axis=1
      )
    )
    # compute the statistics of the values distribution
    stats = _get_distribution_main_stats(
      x=distance,
      prefix=f'node_no_pendant_distance_'
    )

    return stats

  def _GetDistancePendantNodes (self, G : nx.Graph) -> dict:
    '''
    Get the main statistics of the distribution of distances
    of pendant nodes of the graph in relation to the center
    of mass.

    Parameters
    ----------
      G : nx.Graph
        Input graph to analyze.

    Returns
    -------
      stats : dict
        Dictionary with the computed statistics.
    '''
    # get the list of pendant nodes
    pendant = [n for n, d in G.degree() if d == 1]
    # check if the graph has no pendant nodes
    if not pendant:
      # the pendant nodes are the same of no-pendant ones
      # and therefore the statistics must be the same
      pendant = list(G.nodes())
    # convert it to a numpy array
    pendant = np.asarray(pendant)
    # evaluate the center of mass of the graph
    cdm = self._GetCenterOfMass(G=G)
    # standardize the coordinates translating the center
    pendant_standardized = (pendant - cdm)
    # evaluate the Euclidean distance from the center
    distance = np.sqrt(
      np.sum(
        np.square(pendant_standardized),
        axis=1
      )
    )
    # compute the statistics of the values distribution
    stats = _get_distribution_main_stats(
      x=distance,
      prefix=f'node_pendant_distance_'
    )

    return stats


if __name__ == '__main__':

  pass
