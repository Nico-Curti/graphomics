#!/usr/bin/env python
# -*- coding: utf-8 -*-

import networkx as nx
import SimpleITK as sitk
from skimage.measure import euler_number

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

__all__ = ['GraphomicsTopology']


class GraphomicsTopology (_BaseGraphomicsFeatures):
  r'''
  Estimate graphomics topological features.

  This class implements the estimation of the most
  general graphomics features.
  The topological features estimates the main parameters
  of the input graph, providing a global overview of the
  structure and its architecture.
  The list of implemented topological features is:

  * **Number of nodes:**

    The number of nodes of the skeleton
    graph could provides a fast information about the complexity
    of the network architecture and its fractality.

  * **Number of edges:**

    The number of edges of the skeleton
    graph could provides a fast information about the ramification
    of the network and the presence of holes in the original shape.

  * **Edge weight statistics:**

    The edges could be weighted according to a predefined
    score metrics, highlighting the significance of that link
    in the skeleton graph.
    The distribution of the weight scores could be used as feature
    for the quantification of that metric.

  * **Euler number:**

    The Euler number is a topological invariant
    which resume in a unique number the topological space's shape
    or structure regardless of the way it is bent. Mathematically
    it is defined as

    .. math::
      \textit{Euler} = V - E + F

    where `V`, `E`, and `F` are the number of vertices, edges,
    and faces, respectively.

  * **Number of pendant nodes:**

    A pendant node is defined as a node of the graph connected with
    only 1 link, i.e. a node with degree equal to 1 in an undirect graph.
    The number of pendant nodes could be informative about the
    presence of shape's holes and invaginations.

  * **Number of connected components:**

    The number of connected components of the skeleton graph
    could provides a fast information about the number of distinct
    objects included in the mask.

  * **Modularity:**

    Modularity is a measure of the structure of networks or graphs which
    measures the strength of division of a network into modules
    (also called groups, clusters or communities).
    Networks with high modularity have dense connections between the nodes
    within modules but sparse connections between nodes in different modules.
    This feature could provide a fast information about the complexity
    of the skeleton graph.

  * **Number of maximal cliques:**

    A clique is a subset of vertices of an undirected graph such that every
    two distinct vertices in the clique are adjacent.
    The number of maximal cliques as feature could provide information
    about the complexity of the skeleton graph.
  '''

  def __init__ (self, *args, **kwargs):
    super(GraphomicsTopology, self).__init__(*args, **kwargs)

  def _GetNumberOfNodes (self, G : nx.Graph) -> int :
    '''
    Return the number of nodes of the input graph
    (ref. [networkx-nodes_]).

    Parameters
    ----------
      G : nx.Graph
        Input graph to analyze

    Returns
    -------
      nnodes : int
        Number of nodes in the graph.

    .. _networkx-nodes: https://networkx.org/documentation/stable/reference/classes/generated/networkx.Graph.number_of_nodes.html
    '''
    return G.number_of_nodes()

  def _GetNumberOfEdges (self, G : nx.Graph) -> int :
    '''
    Return the number of edges of the input graph
    (ref. [networkx-edges_]).

    Parameters
    ----------
      G : nx.Graph
        Input graph to analyze

    Returns
    -------
      nedges : int
        Number of edges in the graph.

    .. _networkx-edges: https://networkx.org/documentation/stable/reference/classes/generated/networkx.Graph.number_of_edges.html
    '''
    return G.number_of_edges()

  def _GetEdgeWeights (self, G : nx.Graph) -> dict :
    '''
    Compute the main statistics of the edge weights
    distribution (ref. [networkx-weights_]).

    Parameters
    ----------
      G : nx.Graph
        Input graph to analyze.

    Returns
    -------
      stats : dict
        Dictionary with the computed statistics.

    .. _networkx-weights: https://networkx.org/documentation/stable/reference/classes/generated/networkx.Graph.get_edge_data.html
    '''

    # get the weight attribute from the graph
    weights = nx.get_edge_attributes(
      G=G,
      name='weight'
    )
    # if it is an empty dict there are no weights
    if weights == {}:
      # set the weights to a uniform list of ones
      weights = [1] * G.number_of_edges()

    # convert it to a list for safety evaluation
    weight = list(weights)
    # compute the statistics of the values distribution
    stats = _get_distribution_main_stats(
      x=weights,
      prefix=f'edge_weights_'
    )

    return stats

  def _GetEulerNumber (self, mask : sitk.Image,
                             connectivity : int = None
                      ) -> int :
    '''
    Compute the Euler number of the input image/volume
    (ref. [skimage-euler_]).

    Parameters
    ----------
      mask : sitk.Image
        Input binary image/volume to analyze.

      connectivity : int (default := None)
        Maximum number of orthogonal hops to consider a
        pixel/voxel as a neighbor.
        Accepted values are ranging from 1 to input.ndim.
        If None, a full connectivity of input.ndim is used.
        4 or 8 neighborhoods are defined for 2D images
        (connectivity 1 and 2, respectively).
        6 or 26 neighborhoods are defined for 3D images,
        (connectivity 1 and 3, respectively).
        Connectivity 2 is not defined.

    Returns
    -------
      euler_number : int
        Euler characteristic of the set of all objects in
        the image.

    .. _skimage-euler: https://scikit-image.org/docs/stable/api/skimage.measure.html#skimage.measure.euler_number
    '''
    # convert the input sitk.Image to numpy
    np_mask = sitk.GetArrayViewFromImage(mask)

    # compute the Euler number
    E = euler_number(
      image=np_mask,
      connectivity=connectivity
    )

    return E

  def _GetNumberOfPendantNodes (self, G : nx.Graph) -> int :
    '''
    Return the number of pendant nodes of the input graph
    (ref. [networkx-degree_]).

    Parameters
    ----------
      G : nx.Graph
        Input graph to analyze

    Returns
    -------
      npendant : int
        Number of pendant nodes in the graph.

    .. _networkx-degree: https://networkx.org/documentation/stable/reference/classes/generated/networkx.Graph.degree.html
    '''

    return len((n for n, d in G.degree() if d == 1))

  def _GetNumberOfConnectedComponents (self, G : nx.Graph) -> int :
    '''
    Return the number of connected components of the input graph
    (ref. [networkx-components_]).

    Parameters
    ----------
      G : nx.Graph
        Input graph to analyze

    Returns
    -------
      ncomponent : int
        Number of connected components in the graph.

    .. _networkx-components: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.components.connected_components.html
    '''

    return nx.number_connected_components(G=G)

  def _GetModularityScore (self, G : nx.Graph,
                                 weight : str = None
                          ) -> float :
    '''
    Return the modularity score of the input graph
    (ref. [networkx-modularity_]).

    Parameters
    ----------
      G : nx.Graph
        Input graph to analyze

      weight : str (default := None)
        Use weights information during the evaluation.

    Returns
    -------
      modularity : float
        Modularity score of the partion of the graph
        obtained by the label propagation algorithm.

    .. _networkx-modularity: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.quality.modularity.html
    '''

    # evaluate the graph communities for the partition
    communities = nx.community.label_propagation_communities(G=G)
    # compute the modularity score
    modularity = nx.community.modularity(
      G=G,
      weight=weight,
      communities=communities,
      resolution=1.
    )

    return modularity

  def _GetNumberOfMaximalCliques (self, G : nx.Graph) -> int :
    '''
    Get the number of maximal cliques in the graph
    (ref. [networkx-cliques_]).

    Parameters
    ----------
      G : nx.Graph
        Input graph to analyze

    Returns
    -------
      ncliques : int
        The number of maximal cliques in the graph.

    .. _networkx-cliques: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.clique.find_cliques.html
    '''

    return sum(1 for _ in nx.find_cliques(G=G, nodes=None))


if __name__ == '__main__':

  pass
