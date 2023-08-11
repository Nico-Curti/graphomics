#!/usr/bin/env python
# -*- coding: utf-8 -*-

import networkx as nx

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

__all__ = ['GraphomicsCentrality']


class GraphomicsCentrality (_BaseGraphomicsFeatures):
  '''
  Estimate graphomics node-centrality statistic features.

  This class implements the estimation of the centrality
  features of the nodes in the skeleton graph.
  The centrality features provides information about the
  importance of the nodes in the skeleton graph and their
  informative power in terms of robustness of the network
  architecture.
  The list of implemented node-centrality statistic features is:

  * **Node degree centrality statistics:**
  * **Node betweenness centrality statistics:**
  * **Node clustering coefficients statistics:**
  * **Node closeness centrality statistics:**
  * **Node page-rank centrality statistics:**
  * **Node harming centrality statistics:**
  '''

  def __init__ (self, *args, **kwargs):
    super(GraphomicsCentrality, self).__init__(*args, **kwargs)

  def _GetNodeDegreeCentrality (self, G : nx.Graph,
                                      weight : str = None
                               ) -> dict :
    '''
    Compute the main statistics of the node degree centrality
    distribution.

    Parameters
    ----------
      G : nx.Graph
        Input graph to analyze.

      weight : str (default := None)
        Evaluate the metric considering the graph weights.

    Returns
    -------
      stats : dict
        Dictionary with the computed statistics.
    '''
    # check if weights are available
    weight_prefix = '' if weight is None else 'weighted_'
    # compute the distribution of values
    degree = G.degree(weight=weight)
    # compute the statistics of the values distribution
    stats = _get_distribution_main_stats(
      x=degree,
      prefix=f'node_{weight_prefix}degree_'
    )

    return stats

  def _GetNodeBetweennessCentrality (self, G : nx.Graph,
                                           weight : str = None
                                    ) -> dict :
    '''
    Compute the main statistics of the node betweenness centrality
    distribution.

    Parameters
    ----------
      G : nx.Graph
        Input graph to analyze.

      weight : str (default := None)
        Evaluate the metric considering the graph weights.

    Returns
    -------
      stats : dict
        Dictionary with the computed statistics.
    '''
    # check if weights are available
    weight_prefix = '' if weight is None else 'weighted_'
    # compute the distribution of values
    bc = nx.betweenness_centrality(G=G, weight=weight)
    # compute the statistics of the values distribution
    stats = _get_distribution_main_stats(
      x=bc,
      prefix=f'node_{weight_prefix}betweenness_'
    )

    return stats

  def _GetNodeClusteringCoefficient (self, G : nx.Graph,
                                           weight : str = None
                                    ) -> dict :
    '''
    Compute the main statistics of the node clustering coefficient
    distribution.

    Parameters
    ----------
      G : nx.Graph
        Input graph to analyze.

      weight : str (default := None)
        Evaluate the metric considering the graph weights.

    Returns
    -------
      stats : dict
        Dictionary with the computed statistics.
    '''
    # check if weights are available
    weight_prefix = '' if weight is None else 'weighted_'
    # compute the distribution of values
    cc = nx.clustering(G=G, weight=weight)
    # compute the statistics of the values distribution
    stats = _get_distribution_main_stats(
      x=cc,
      prefix=f'node_{weight_prefix}clustering_'
    )

    return stats

  def _GetNodeClosenessCentrality (self, G : nx.Graph,
                                         weight : str = None
                                  ) -> dict :
    '''
    Compute the main statistics of the node closeness centrality
    distribution.

    Parameters
    ----------
      G : nx.Graph
        Input graph to analyze.

      weight : str (default := None)
        Evaluate the metric considering the graph weights.

    Returns
    -------
      stats : dict
        Dictionary with the computed statistics.
    '''
    # check if weights are available
    weight_prefix = '' if weight is None else 'weighted_'
    # compute the distribution of values
    clo = nx.closeness_centrality(G=G, distance=weight)
    # compute the statistics of the values distribution
    stats = _get_distribution_main_stats(
      x=clo,
      prefix=f'node_{weight_prefix}closeness_'
    )

    return stats

  def _GetNodePageRankCentrality (self, G : nx.Graph,
                                        weight : str = None
                                 ) -> dict :
    '''
    Compute the main statistics of the node page-rank centrality
    distribution.

    Parameters
    ----------
      G : nx.Graph
        Input graph to analyze.

      weight : str (default := None)
        Evaluate the metric considering the graph weights.

    Returns
    -------
      stats : dict
        Dictionary with the computed statistics.
    '''
    # check if weights are available
    weight_prefix = '' if weight is None else 'weighted_'
    # compute the distribution of values
    pagerank = nx.pagerank(G=G, weight=weight)
    # compute the statistics of the values distribution
    stats = _get_distribution_main_stats(
      x=pagerank,
      prefix=f'node_{weight_prefix}pagerank_'
    )

    return stats

  def _GetNodeHarmonicCentrality (self, G : nx.Graph,
                                        weight : str = None
                                 ) -> dict :
    '''
    Compute the main statistics of the node harmonic centrality
    distribution.

    Parameters
    ----------
      G : nx.Graph
        Input graph to analyze.

      weight : str (default := None)
        Evaluate the metric considering the graph weights.

    Returns
    -------
      stats : dict
        Dictionary with the computed statistics.
    '''
    # check if weights are available
    weight_prefix = '' if weight is None else 'weighted_'
    # compute the distribution of values
    harmonic = nx.harmonic_centrality(G=G, distance=weight)
    # compute the statistics of the values distribution
    stats = _get_distribution_main_stats(
      x=harmonic,
      prefix=f'node_{weight_prefix}harmonic_'
    )

    return stats
