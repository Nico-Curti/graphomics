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
  r'''
  Estimate graphomics node-centrality statistic features.

  This class implements the estimation of the centrality
  features of the nodes in the skeleton graph.
  The centrality features provides information about the
  importance of the nodes in the skeleton graph and their
  informative power in terms of robustness of the network
  architecture.
  The list of implemented node-centrality statistic features is:

  * **Node degree centrality statistics:**

    The node degree is the number of edges adjacent to the node.
    The weighted node degree is the sum of the edge weights for
    edges incident to that node.
    The node degree centrality quantifies the importance of a
    node in the graph in terms of the number of links connected
    to it.
    This metric could be informative about the presence of hubs
    and ramifications in the skeleton structure.

  * **Node betweenness centrality statistics:**

    Betweenness centrality of a node `v` is the sum of the fraction
    of all-pairs shortest paths that pass through `v`:

    .. math::
      c_B(v) = \sum_{s,t \in V}\frac{\sigma(s,t|v)}{\sigma(s,t)}

    where :math:`V` is the set of nodes, :math:`\sigma(s,t)` is the
    number of shortest :math:`(s,t)` -paths, and :math:`\sigma(s,t|v)`
    is the number of those paths passing through some node :math:`v`
    other than :math:`s,t`.
    The betweenness centrality quantifies the importance of a
    node in the graph in terms of the number of paths that must pass
    through it.
    This metric could be informative about the presence of hubs
    and ramifications in the skeleton structure.

  * **Node clustering coefficients statistics:**

    The local clustering coefficient of a node in a graph
    quantifies how close its neighbours are to being a clique
    (complete graph).

  * **Node closeness centrality statistics:**

    Closeness centrality of a node `u` is the reciprocal of the
    average shortest path distance to `u` over all `n-1` reachable
    nodes.

    .. math::
      C(u) = \frac{n-1}{\sum_{v=1}^{n-1}d(v,u)}

    where :math:`d(v, u)` is the shortest-path distance between
    `v` and `u`, and `n-1` is the number of nodes reachable from
    `u`.

  * **Node page-rank centrality statistics:**

    PageRank computes a ranking of the nodes in the graph `G` based
    on the structure of the incoming links.
    It was originally designed as an algorithm to rank web pages.

  * **Node harmonic centrality statistics:**

    Harmonic centrality of a node `u` is the sum of the reciprocal
    of the shortest path distances from all other nodes to `u`

    .. math::
      C(u) = \sum_{v\neq u}\frac{1}{d(v, u)}

    where :math:`d(v, u)` is the shortest-path distance between `v`
    and `u`.
    The harmonic centrality quantifies the importance of a node
    in the graph in terms of its distance to the other nodes.
    This metric could be informative about the presence of hubs
    and ramifications in the skeleton structure.
  '''

  def __init__ (self, *args, **kwargs):
    super(GraphomicsCentrality, self).__init__(*args, **kwargs)

  def _GetNodeDegreeCentrality (self, G : nx.Graph,
                                      weight : str = None
                               ) -> dict :
    '''
    Compute the main statistics of the node degree centrality
    distribution (ref. [networkx-degree_]).

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

    .. _networkx-degree: https://networkx.org/documentation/stable/reference/classes/generated/networkx.Graph.degree.html
    '''
    # check if weights are available
    weight_prefix = '' if weight is None else 'weighted_'
    # compute the distribution of values
    degree = G.degree(
      weight=weight
    )
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
    distribution (ref. [networkx-betweenness_]).

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

    .. _networkx-betweenness: https://networkx.org/documentation/networkx-1.10/reference/generated/networkx.algorithms.centrality.betweenness_centrality.html
    '''
    # check if weights are available
    weight_prefix = '' if weight is None else 'weighted_'
    # compute the distribution of values
    bc = nx.betweenness_centrality(
      G=G,
      weight=weight
    )
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
    distribution (ref. [networkx-clustering_]).

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

    .. _networkx-clustering: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.cluster.clustering.html#networkx.algorithms.cluster.clustering
    '''
    # check if weights are available
    weight_prefix = '' if weight is None else 'weighted_'
    # compute the distribution of values
    cc = nx.clustering(
      G=G,
      weight=weight
    )
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
    distribution (ref. [networkx-closeness_]).

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

    .. _networkx-closeness: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.closeness_centrality.html
    '''
    # check if weights are available
    weight_prefix = '' if weight is None else 'weighted_'
    # compute the distribution of values
    clo = nx.closeness_centrality(
      G=G,
      distance=weight
    )
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
    distribution (ref. [networkx-pagerank_]).

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

    .. _networkx-pagerank: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.link_analysis.pagerank_alg.pagerank.html
    '''
    # check if weights are available
    weight_prefix = '' if weight is None else 'weighted_'
    # compute the distribution of values
    pagerank = nx.pagerank(
      G=G,
      weight=weight
    )
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
    distribution (ref. [networkx-harmonic_]).

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

    .. _networkx-harmonic: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.harmonic_centrality.html
    '''
    # check if weights are available
    weight_prefix = '' if weight is None else 'weighted_'
    # compute the distribution of values
    harmonic = nx.harmonic_centrality(
      G=G,
      distance=weight
    )
    # compute the statistics of the values distribution
    stats = _get_distribution_main_stats(
      x=harmonic,
      prefix=f'node_{weight_prefix}harmonic_'
    )

    return stats


if __name__ == '__main__':

  pass
