#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import networkx as nx
import SimpleITK as sitk
from scipy.stats import gaussian_kde

from ._statistics import _get_distribution_main_stats
from ._basefeature import _BaseGraphomicsFeatures

__author__  = ['Nico Curti',
               'Gianluca Carlini',
               'Riccardo Biondi'
              ]
__email__ = ['nico.curti2@unibo.it',
             'gianluca.carlini2@unibo.it',
             'riccardo.biondi2@unibo.it'
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
    using a gaussian kernel density estimator. This
    metric could provide information about the sparsity
    of the nodes in the graph and the presence of possible
    clusters of points.
    As resulting features the filter provides the main
    statistics of the density distribution of values.

  * **Fractal dimension:**

    The fractal dimension is a term invoked in the science of geometry to
    provide a rational statistical index of complexity detail in a pattern.
    The fractal dimension is a feature strictly related to the complexity
    of the skeleton graph and it can be evaluated directly from the binarized
    mapper of the skeleton.
  '''

  def __init__ (self, *args, **kwargs):
    super(GraphomicsSpatial, self).__init__(*args, **kwargs)

  def _GetNodeDensityStatistics (self, G : nx.Graph) -> dict :
    '''
    Get the main statistics of the node density distribution
    of values.

    Parameters
    ----------
      G : nx.Graph
        Input graph to analyze

    Returns
    -------
      stats : dict
        Dictionary with the computed statistics
    '''
    # extract the list of node coordinates from the graph
    nodes = G.nodes(data=False, default=None)
    # convert the nodes to numpy coordinates
    pts = np.asarray(nodes)
    pts = np.transpose(pts) # KDE requires input (dim, N)
    # apply the gaussian KDE for the density estimation
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
      dim(S) = \lim_{\epsil\rightarrow0}\frac{\log{N(\epsil)}}{\log{\frac{1}{\epsil}}}

    Parameters
    ----------
      skeleton : sitk.Image

      max_box_size : int (default := None)
        The largest box size, given as the power of 2 so that
        2**max_box_size gives the sidelength of the largest box.

      min_box_size : int (default := 1)
        The smallest box size, given as the power of 2 so that
        2**min_box_size gives the sidelength of the smallest box.

      n_samples : int (default := 0)
        Number of scales to measure over.

      n_offsets : int (default := 0)
        Number of offsets to search over to find the smallest set N(s)
        to cover all voxels>0.

    Returns
    -------
      fractal_dim : float
        Fractal dimension score

    References
    ----------
    [1] https://github.com/ChatzigeorgiouGroup/FractalDimension
    '''

    # convert the input skeleton to a binary mask
    mask = sitk.GetArrayViewFromImage(skeleton)
    mask = np.where(mask != 0, 1, 0)

    # determine the scales to measure on
    if max_box_size == None:
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
    voxels = np.squeeze(
      np.dstack(
        np.where(skeleton != 0)
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
          voxels,
          bins=bin_edges
        )
        touched.append(np.sum(H1 > 0))

      Ns.append(touched)

    Ns = np.asarray(Ns)

    # From all sets N found, keep the smallest one at each scale
    Ns = Ns.min(axis=1)
    Ns = np.unique(Ns)

    # Only keep scales at which Ns changed
    scales = [1. / np.min(scales[Ns == x])
              for x in Ns
             ]

    Ns = Ns[Ns > 0]
    scales = scales[:len(Ns)]
    # perform fit
    coeffs = np.polyfit(np.log(scales), np.log(Ns), 1)

    return -coeffs[0]
