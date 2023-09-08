#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import SimpleITK as sitk
from collections import defaultdict

__author__  = ['Nico Curti',
               'Gianluca Carlini',
               'Riccardo Biondi'
              ]
__email__ = ['nico.curti2@unibo.it',
             'gianluca.carlini2@unibo.it',
             'riccardo.biondi2@unibo.it'
            ]

__all__ = ['GraphThicknessImageFilter']


class GraphThicknessImageFilter (object):
  '''
  Extraction of graph attributes from skeletonized images.

  This filter computes the graph of a 2D/3D skeletonized image/volume.
  The official implementation of the algorithm is provided
  as ITK image filter class.
  This implementation provides the same interface using
  python codes and algorithms. The resulting graph could
  be obtained merging the list of nodes provided by the
  `GetNodes` and `GetEdges` member functions. The list
  of nodes stored the points as pixel coordinates of the
  volumes, while the edge list (bi-directional) stores the
  association map between node coordinates.

  The code implements the 2D/3D translation of the original
  2D algorithm provided in the online gist_.

  Parameters
  ----------
    surface_min_points : int (default := 8)
      Minimum number of points for the identification of a surface in
      the binary skeleton. The presence of surface areas could be due
      to the skeleton algorithm used (ref. sitk.BinaryThinningImageFilter3D).
      The value 8 is estimated as the number of voxels belonging to a
      plane in a 3x3x3 VOI of the skeleton. The resulting graph can
      change according to this parameter!

    remove_surface : bool (default := False)
      In case of "surface edges" found in the 3D skeleton, turning on this
      parameter, the related connected component can be discarded by the
      skeleton and by the graph extraction procedure. The remotion of these
      components can lead to broken graphs (i.e. multiple connected components)
      and therefore it should be used with caution, according to your needs.

  .. _gist: https://gist.github.com/Nico-Curti/a586e6f58d4a2c758b77a3f4492e6d3f
  '''

  def __init__ (self, surface_min_points : int = 8,
                      remove_surface : bool = False
                ):
    self._ndim = None
    self.surface_min_points = surface_min_points
    self.remove_surface = remove_surface

    self._stats_shape = sitk.LabelShapeStatisticsImageFilter()
    self._stats_shape.SetBackgroundValue(0)
    self._stats_shape.SetGlobalDefaultNumberOfThreads(1)

  def SetInputDimensionality (self, ndim : int = 3):
    '''
    Set the dimensionality of the skeleton input and
    compute the internal parameters accordingly.

    Parameters
    ----------
      ndim : int (default := 3)
        Number of dimension of the input image (ndim:=2)
        or volume (ndim:=3)
    '''
    # work-around to reduce code redundancy
    self._SetInternalKernels(shape=(1, 1, 1))
    return self


  def _SetInternalKernels (self, shape : tuple):
    '''
    Set the internal parameters of the filter according
    to the provided shape.

    Parameters
    ----------
      shape : tuple
        Dimension of the input image to analyze.
    '''
    # get the input dimensionality
    self._ndim = len(shape)

    # check if it is a valid shape
    if self._ndim not in [2, 3]:
      raise ValueError(('Invalid number of dimension for the filter. '
        f'Given {self._ndim} but possible values are only [2, 3]'
      ))

    if self._ndim == 3:
      kernel = np.array([[[-1, -1, -1],
                          [-1, -1, -1],
                          [-1, -1, -1]],
                         [[-1, -1, -1],
                          [-1, 26, -1],
                          [-1, -1, -1]],
                         [[-1, -1, -1],
                          [-1, -1, -1],
                          [-1, -1, -1]]], dtype=np.int32)
      self._get_neighborhood = self._get_3x3x3_voi

    else: # it must be 2 in this case
      kernel = np.array([[-1, -1, -1],
                         [-1,  8, -1],
                         [-1, -1, -1]], dtype=np.int32)
      self._get_neighborhood = self._get_3x3_roi
      # in 2D there are no possible surfaces in the skeleton
      self.surface_min_points = float('inf')
      self.remove_surface = False

    # convolutional kernel
    # (ref. `_ComputeNodes` for a deeper explanation of the coefficients)
    self._kernel = sitk.GetImageFromArray(kernel)

    return self

  def SetGlobalDefaultNumberOfThreads (self, nth : int):
    '''
    Set the number of threads to used by the parallel
    filters used by the object.

    Parameters
    ----------
      nth : int
        Number of threads
    '''
    self._stats_shape.SetGlobalDefaultNumberOfThreads(max(nth, 1))

    return self

  def _get_3x3_roi (self, img : sitk.Image, coords : tuple) -> sitk.Image:
    '''
    Extract a 3x3 ROI from the image around the coordinates
    given in input.

    Parameters
    ----------
      img : sitk.Image
        Input image

      coords : tuple
        2D tuple of integer values

    Returns
    -------
      roi : sitk.Image
        Extracted 3x3 ROI around the coordinates

    .. note::
      If the coordinates do not allow the extraction of a 3x3 ROI,
      i.e. the coordinates are <= 1 or >= D, the extracted ROI is
      the maximum possible ROI.
    '''
    h, w = img.GetSize()
    x, y = coords

    return img[max(x - 1, 0) : min(x + 2, h),
               max(y - 1, 0) : min(y + 2, w),
              ]

  def _get_3x3x3_voi (self, vol : sitk.Image, coords : tuple) -> sitk.Image:
    '''
    Extract a 3x3x3 VOI from the volume around the coordinates
    given in input.

    Parameters
    ----------
      vol : sitk.Image
        Input volume

      coords : tuple
        3D tuple of integer values

    Returns
    -------
      voi : sitk.Image
        Extracted 3x3x3 VOI around the coordinates

    .. note::
      If the coordinates do not allow the extraction of a 3x3x3 VOI,
      i.e. the coordinates are <= 1 or >= D, the extracted VOI is
      the maximum possible VOI.
    '''
    h, w, c = vol.GetSize()
    x, y, z = coords

    return vol[max(x - 1, 0) : min(x + 2, h),
               max(y - 1, 0) : min(y + 2, w),
               max(z - 1, 0) : min(z + 2, c),
              ]

  def _check_input(self, src : sitk.Image):
    '''
    Check required properties for the correct
    application of the filter on the input.

    Parameters
    ----------
      src : sitk.Image
        Input to check.
    '''

    # the input must contains only positive values
    # since the skeleton should be binary
    return self

  def Execute (self, src : sitk.Image):
    '''
    Execute the filter on the given input.
    The input must be a sitk.Image with the skeleton
    structure of the input. Internal checks are performed
    to evaluate the correctness of the input.

    Parameters
    ----------
      src : sitk.Image
        Skeletonized input volume/image.
    '''
    # set the internal kernels of the filters if not already set
    if self._ndim is None:
      self._SetInternalKernels(shape=src.GetSize())
    # define the transformer for the coordinate systems
    self._cooordinate_converter = src.TransformIndexToPhysicalPoint
    # check the input validity
    self._check_input(src=src)
    # compute the node coordinates
    hypernodes, src, true_vertex, cc_vertices = self._ComputeNodes(src=src)
    # compute the edgelist of the graph
    edge_map, lut_edges = self._ComputeEdges(
      src=src,
      true_vertex=true_vertex,
      cc_vertices=cc_vertices,
      hypernodes=hypernodes
    )

    self.lut = lut_edges

    # get the nodelist from the lut for a faster output
    self.nodes = list(set(sum(list(map(list, self.lut.values())), [])))

    # get the edgelist from the lut for a faster output
    self.edges = list(map(tuple, self.lut.values()))

    # get the edge map of the volume
    self.edge_map = edge_map

    return self

  def _ComputeNodes (self, src : sitk.Image):
    '''
    Compute the node coordinates using convolutional filter.
    The algorithm explanation is provided step-by-step in the
    comments below.

    Parameters
    ----------
      src : sitk.Image
        Input volume of the 3D skeletonized image.

    Returns
    -------
      hypernodes : dict
        Dictionary of hyper-nodes coordinates related to each node
        component found in the volume. The hypernode is represented
        by the minimum value of the connected component or by its
        median coordinates along first axis.

      tmp : sitk.Image
        Binary skeleton volume to use for the edge processing.

      true_vertex : sitk.Image
        Binary volume of the vertices VOI found by the convolutional
        filter.

      cc_vertices : sitk.Image
        Volume of vertices labeled according to each connected component.
        The volume has the same dimension of the true_vertex one and it
        represents the labeling of each vertex.
    '''
    # binarize the input image to avoid possible issues with
    # the provided input
    tmp = src != 0
    # cast the binarized image to a minimal dtype
    tmp = sitk.Cast(
      image=tmp,
      pixelID=sitk.sitkInt32
    )

    # pad the input image pre-convolution
    padded = sitk.ConstantPad(
      image1=src,
      padLowerBound=(1, 1, 1),
      padUpperBound=(1, 1, 1),
      constant=0
    )

    # apply the convolutional operator
    # Note: the central value is set to 26 since it is the 3D
    # translation of the original kernel used for the estimation
    # of the nodes in 2D images
    # An implementation of the 2D algorithm could be found at:
    # https://gist.github.com/Nico-Curti/a586e6f58d4a2c758b77a3f4492e6d3f

    # apply the kernel via convolution
    conv = sitk.Convolution(
      image=padded,
      kernelImage=self._kernel,
      normalize=False,
      boundaryCondition=0,
      outputRegionMode=1
    )

    # threshold only the valid values

    # 1. a ramification node is given by a value of the
    # resulting convolution < 24 in 3D and convolution < 6 in 2D

    # 2. a ramification node could be given also by any
    # positive value > 0 in both 3D and 2D

    # 3. a pendant node is given by a value
    # of the resulting convolution == 25 in 3D and convolution == 7 in 2D
    ramification_score = (3 ** self._ndim) - 3
    pendant_score = (3 ** self._ndim) - 2

    true_vertex = ((conv < ramification_score) & (conv > 0)) | (conv == pendant_score)
    # cast to integer for next computation
    true_vertex = sitk.Cast(
      image=true_vertex,
      pixelID=sitk.sitkInt32
    )

    # detect the connected components of the vertices image, i.e. each
    # connected component provides a vertex.
    cc_vertices = sitk.ConnectedComponent(
      true_vertex, # image
      True # fullyConnected
    )
    # cast to integer for next computation
    cc_vertices = sitk.Cast(
      image=cc_vertices,
      pixelID=sitk.sitkInt32
    )

    # monitor the shape of the cc_vertices
    self._stats_shape.Execute(cc_vertices)

    # extract the hyper-node coordinates.
    # An hyper-node identifies a connected component made by multiple
    # node-like positions. Since in output we are interested in nodes
    # described by a single point in the 3D space, the most connected
    # voxel in each connected component will be used as centroid of
    # the hyper-nodes. If all the coordinates belonging to the same
    # connected component store the same value, the median index
    # is used as hyper-node centroid.
    hypernodes = {}

    # loop along the hyper-node components found
    for l in self._stats_shape.GetLabels():
      # get the indices of the voxels belonging to the CC
      idx = self._stats_shape.GetIndexes(l)

      # if the CC represents a surface skip it
      # or remove it, according the input parameter
      # NOTE: we will take care of them after...
      if len(idx) > self.surface_min_points * self._ndim and self.remove_surface:

        # turn off this component from both the
        # binary map of vertices, on the vertices label
        # and on the processed skeleton
        for i in range(0, len(idx), self._ndim):
          coord = idx[i : i + self._ndim]
          true_vertex[coord] = 0
          cc_vertices[coord] = 0
          tmp[coord] = 0
        # skip
        continue

      # reshape to numpy coords
      idx = [idx[i : i + self._ndim]
             for i in range(0, len(idx), self._ndim)
            ]
      # get the value in the convolution volume
      conv_val = [conv[i] for i in idx]

      # extract the hyper-node position in the idx list
      # NOTE: the hyper-node coordinate will be named root
      if len(set(conv_val)) == 1:
        root_val = len(idx) // 2
      else:
        root_val = np.argmin(conv_val)

      # conver the idx coordinates to the correct physical space
      # NOTE: this is mandatory due to the boundary condition set
      # in the convolution
      #idx = [padded.TransformPhysicalPointToIndex(i) for i in idx]

      # get the root position
      root = idx[root_val]

      # update the nodes information
      # 1. For each node coordinate the root position will be the same
      hypernodes[l] = root

    return hypernodes, tmp, true_vertex, cc_vertices

    raise NotImplementedError

  def _ComputeEdges (self, src : sitk.Image,
                           true_vertex : sitk.Image,
                           cc_vertices : sitk.Image,
                           hypernodes : dict) -> tuple:
    '''
    Compute the edges coordinates as connected components of
    the original input with the node coordinates removed.
    The algorithm explanation is provided step-by-step in the
    comments below.

    Parameters
    ----------
      src : sitk.Image
        Input skeletonized image.

      true_vertex : sitk.Image
        Binary input of the vertices VOI found by the convolutional
        filter.

      cc_vertices : sitk.Image
        Input of vertices labeled according to each connected component.
        The input has the same dimension of the true_vertex one and it
        represents the labeling of each vertex.

      hypernodes : dict
        Dictionary of hyper-nodes coordinates related to each node
        component found in the input. The hypernode is represented
        by the minimum value of the connected component or by its
        median coordinates along first axis.

    Returns
    -------
      edge_map : sitk.Image
        Output with the same size of the original one, in which
        each edge component is labelled with a different index:
        0    values identify the background
        > 0  values identify the labeled edges found
        < -1 values identify the labeled hyper-nodes found

      lut_edges : defaultdict(set)
        LookUp table of the edge labels associated to the correspoding
        nodes. This object is mandatory for the correct association
        between the value in the edge_map, the nodes, and the possible
        weighted graph.
    '''

    # perform a 3x3[x3] dilation of the vertices map
    dilated_vertex = sitk.BinaryDilate(
      image1=true_vertex,
      kernelRadius=(1, ) * self._ndim,
      kernelType=sitk.sitkBox,
      backgroundValue=0,
      foregroundValue=1,
      boundaryToForeground=False
    )
    # 1. set all 3x3[x3] squares/cubes around the nodes to null in the edge_map
    # 2. set all vertices to null in the len2_map
    # NOTE: in this way we can compute the edge-paths as
    # connected components
    # NOTE2: turning off the 3x3[x3] squares/cubes we are implicitly discarding
    # all the edges with length == 2; for this reason we have created
    # the len2_map volume!
    edge_map = src * sitk.Not(dilated_vertex)

    # compute the connected components that in this case are
    # represented by only the edges
    cc_edges = sitk.ConnectedComponent(
      edge_map, # image
      True # fullyConnected
    )
    # cast it to integer for next computation
    cc_edges = sitk.Cast(
      image=cc_edges,
      pixelID=sitk.sitkInt32
    )

    # get the number of edge components found
    _ = self._stats_shape.Execute(cc_edges)
    # the current number of edges is equal to the number
    # of labels found +1 since it starts from 1
    ne = len(self._stats_shape.GetLabels()) + 1

    # set all 3x3[x3] squares/cubes around the nodes to -1
    # NOTE: in this way all the starting and ending point
    # of each edge will be marked as -1
    # NOTE2: since we want to preserve the background values
    # we use the corresponding source VOI as mask

    # enumerate the vertex-coords with negative numbers
    # to better discriminate these points from the edges
    # NOTE: in this way we can get the edges near to a vertex
    # NOTE2: This is the magic trick proposed by Gianluca Carlini ;)
    edge_map = (cc_edges - cc_vertices - dilated_vertex) * src

    # create the look-up table for the graph
    lut_edges = defaultdict(set)

    # get the coordinates of -1 voxels as points in which
    # monitor the vertex connection
    # NOTE: we transform the sitk.Image to a Numpy volume for a
    # faster execution time
    # NOTE2: the Numpy indexing is inverse!
    pxyz = np.where(sitk.GetArrayViewFromImage(edge_map) == -1)

    # Now we can loop along the -1 voxels looking at their
    # 3x3[x3] neighborhood. In this case each -1 voxel could
    # have only value equal to 0 -> background;
    # > 0 -> links; < -1 -> associated node

    for coords in zip(*pxyz):
      # revert order for the compatibility between Numpy and Sitk
      coords = coords[::-1]
      coords = tuple(map(int, coords))

      # get the 3x3[x3] ROI of the -1 voxel
      voi = self._get_neighborhood(edge_map, coords=coords)

      # get the unique set of labels found in the voi
      edge_lbl = np.unique(voi, axis=None)

      # the nodes are negative values < -1
      # NOTE: abs to get it positive; -1 is the starting
      # point for node labeling
      nodes_id = abs(edge_lbl[edge_lbl < -1]) - 1
      # get the associated hyper-node position
      nodes_id = [hypernodes[x] for x in nodes_id]
      # the links are positive values > 0
      edges_id = edge_lbl[edge_lbl > 0]

      # reduce the node list to a unique set of values
      nodes_id = set(nodes_id)

      # if there is just 1 node without edges, can be treated
      # in a separated way since it is an artifact related to
      # our algorithm
      if len(nodes_id) > 1 and not len(edges_id):
        # store in the lut this new component with a new label
        lut_edges[ne] = nodes_id
        # set the value of the edge_map with the new edge label
        edge_map[coords] = ne
        # increment the number of edge labels
        ne += 1
      # otherwise it is a spurious neighborhood of the vertex
      # so we need to turn off the edge_map element
      else:
        edge_map[coords] = 0

      # else condition is redundant

      # for each edge found
      for e in edges_id:
        # add all the nodes to this edge
        lut_edges[e].update(nodes_id)
        # update the edge_map with this value
        # NOTE: the int cast is mandatory due to a sitk issue with
        # np.int32 values for the volume indexing
        edge_map[coords] = int(e)

    # Now we have the LookUP table between edge components
    # and associated nodes. In this way we can preserve the
    # correct association between the values stored in the edge_map
    # and the connection between the vertices found.
    # This is a mandatory step if we want to use a weighted graph!

    # NOTE: a 2D graph could accept nodes with a maximum degree equal to 4,
    # since a 2D skeleton does not admit any component with more than 4
    # connectivity.
    # NOTE2: in contrary, a 3D skeleton could admit also surface
    # components, i.e. planary edges belonging to a 2D space. In these
    # situations, a "surface edge" is a more complex structure to manage
    # in terms of connection between nodes and the 26 (3x3x3 - 1)
    # maximum connectivity accepted in a 3D graph could drastically increase!
    # A "surface edge", indeed, is able to connect multiple nodes together,
    # incrementing the limit of the vertices' degree to high values.
    # A drastically way to avoid the presence of "surface edges" is given by
    # the parameter "remove_surface" of the constructor.

    # Now it is time to manage the edges with length == 2.
    # This step is obtained considering the subtraction between
    # the skeleton without nodes and the edge_map.
    # This is the magic trick proposed by Riccardo Biondi ;)
    # NOTE: we have already prepared the len2_map removing the node
    # coordinates; the list of edges already processed by our
    # algorithm could be obtained filtering the positive components
    # of the edge_map volume.

    # remove the true links from the len2 map
    len2_map = src - true_vertex - sitk.Cast(image=edge_map > 0, pixelID=sitk.sitkInt32)

    # get the connected components of the len2 edges
    # NOTE: after the subtraction of the already processed edges,
    # the remaining voxels are all related to these components
    cc_len2 = sitk.ConnectedComponent(
      len2_map, # image
      True # fullyConnected
    )

    # evalute it to get the positions of these objects
    self._stats_shape.Execute(cc_len2)

    # Now we can iterate over the len2 components and manage
    # these links with more caution

    for l in self._stats_shape.GetLabels():

      # if the CC is just an isolated voxel skip it
      if self._stats_shape.GetNumberOfPixels(l) == 1:
        continue

      # get the indices of the voxels belonging to the CC
      idx = self._stats_shape.GetIndexes(l)
      # reshape to list of 2D-3D tuples
      idx = [idx[i : i + self._ndim]
             for i in range(0, len(idx), self._ndim)
            ]

      # it must be a pair of 2 values given by
      # the source and target nodes
      assert len(idx) == 2

      # Since it is just a list of 2 values is more convenient
      # to process it one by one, starting from the source node

      ## Source node

      # extract the source node coords
      coords = idx[0]
      coords = tuple(map(int, coords))

      # get the 3x3[x3] voi of the -1 voxel
      src_voi = self._get_neighborhood(edge_map, coords=coords)

      # get the unique set of labels found in the voi
      edge_lbl = np.unique(src_voi, axis=None)

      # the nodes are negative values < -1
      # NOTE: abs to get it positive; -2 is the starting
      # point for node labeling
      nodes_id = abs(edge_lbl[edge_lbl < -1]) - 1
      # there must be only one node
      assert len(nodes_id) == 1
      # get the associated hyper-node position
      src_coords = hypernodes[nodes_id[0]]

      # replace the value of the edge_map with the correct ne value
      edge_map[coords] = ne

      ## Target node

      # extract the destination node coords
      coords = idx[1]
      coords = tuple(map(int, coords))

      # get the 3x3[x3] voi of the -1 voxel
      dst_voi = self._get_neighborhood(edge_map, coords=coords)

      # get the unique set of labels found in the voi
      edge_lbl = np.unique(dst_voi, axis=None)

      # the nodes are negative values < -1
      # NOTE: abs to get it positive; -2 is the starting
      # point for node labeling
      nodes_id = abs(edge_lbl[edge_lbl < -1]) - 1
      # there must be only one node
      assert len(nodes_id) == 1
      # get the associated hyper-node position
      dst_coords = hypernodes[nodes_id[0]]

      # NOTE: in some particular cases the skeleton structure
      # could preserve node components which could lead to edges
      # with length equal to 2.
      # To avoid the creation of misleading edges and/or self
      # loops in the graph, we can easily skip these cases
      # checking if the source node is different to the target
      # one or not. If they are equal we can just skip that
      # fake-edge
      if src_coords == dst_coords:
        continue

      # replace the value of the edge_map with the correct ne value
      edge_map[coords] = ne

      # now we need to take care of the LookUp table of the edges
      # and update it with the new edge label
      lut_edges[ne] = {src_coords, dst_coords}
      # at the end we can increment the value of the edge labels
      # to be ready for the next component
      ne += 1

    # NOTE: the processed src image was padded with ones
    # and to keep the edge_map with the same dimensions of the
    # original skeleton we need to remove the padding
    # TODO!!!

    return edge_map, lut_edges

  def GetNodeIndexes (self) -> list:
    '''
    Get the list of nodes as point-coordinates of the
    provided volume.
    '''
    if not hasattr(self, 'nodes'):
      class_name = self.__class__.__name__
      raise RuntimeError(('Runtime Exception. '
        f'The {class_name} object is not executed yet. '
        'To get the node list you need to call the Execute function'
      ))

    return self.nodes

  def GetNodePhysicalPoints(self) -> list:
    '''
    Get the list of nodes as physical point-coordinates of the
    provided volume.
    '''
    if not hasattr(self, 'nodes'):
      class_name = self.__class__.__name__
      raise RuntimeError(('Runtime Exception. '
        f'The {class_name} object is not executed yet. '
        'To get the node list you need to call the Execute function'
      ))

    # convert the node indexes into image physical space
    # (usually in millimeters)
    return [self._cooordinate_converter(coord) for coord in self.nodes]

  def GetEdgeIndexes (self) -> list:
    '''
    Get the list of edges as list of paired of node coordinates.
    '''
    if not hasattr(self, 'edges'):
      class_name = self.__class__.__name__
      raise RuntimeError(('Runtime Exception. '
        f'The {class_name} object is not executed yet. '
        'To get the node list you need to call the Execute function'
      ))

    return self.edges

  def GetEdgePhysicalPoints (self) -> list:
    '''
    Get the list of edges as list of paired of node physical
    point-coordinates.
    '''
    if not hasattr(self, 'edges'):
      class_name = self.__class__.__name__
      raise RuntimeError(('Runtime Exception. '
        f'The {class_name} object is not executed yet. '
        'To get the node list you need to call the Execute function'
      ))

    return [(self._cooordinate_converter(src),
             self._cooordinate_converter(dst)
            )
            for (src, dst) in self.edges
           ]

  def GetEdgeLUTIndexes (self) -> defaultdict:
    '''
    Get the lookup table of the edge labels for the edge map.
    '''
    if not hasattr(self, 'lut'):
      class_name = self.__class__.__name__
      raise RuntimeError(('Runtime Exception. '
        f'The {class_name} object is not executed yet. '
        'To get the node list you need to call the Execute function'
      ))

    return self.lut

  def GetEdgeLUTPhysicalPoints (self) -> defaultdict:
    '''
    Get the lookup table of the edge labels for the edge map.
    '''
    if not hasattr(self, 'lut'):
      class_name = self.__class__.__name__
      raise RuntimeError(('Runtime Exception. '
        f'The {class_name} object is not executed yet. '
        'To get the node list you need to call the Execute function'
      ))

    return {k: (self._cooordinate_converter(src),
                self._cooordinate_converter(dst)
               )
            for k, (src, dst) in self.lut.items()
           }

  def GetEdgeMap (self) -> sitk.Image:
    '''
    Get the edge-map of the volumes.
    The edge map stores the edge paths as disjoint lines in the
    original volume. The connected components of the edge-map are
    the edges of the graph found by the filter.
    '''
    if not hasattr(self, 'edge_map'):
      class_name = self.__class__.__name__
      raise RuntimeError(('Runtime Exception. '
        f'The {class_name} object is not executed yet. '
        'To get the node list you need to call the Execute function'
      ))

    return self.edge_map


if __name__ == '__main__':

  import argparse
  import pylab as plt
  from skimage.morphology import skeletonize

  parser = argparse.ArgumentParser(description='Graph Extraction from binary volumes')
  parser.add_argument('--filename', type=str, required=True, action='store',
    help='Path or Filename of the binary CT volume to analyze'
  )
  args = parser.parse_args()

  # load the input CT volume
  ct = sitk.ReadImage(args.filename)
  # convert it to numpy
  ct_np = sitk.GetArrayViewFromImage(ct)
  # get the related skeleton
  # Note: if you are using ITK volume a possible alternative
  # is given by the BinaryThinningImageFilter3D filter
  np_skeleton = skeletonize(ct_np, method='lee')
  # convert it to sitk.Image
  skeleton = sitk.GetImageFromArray(np_skeleton)

  # create the graph filter
  graph_filter = GraphThicknessImageFilter()
  # set the number of threads to use
  graph_filter.SetGlobalDefaultNumberOfThreads(4)
  # execute the filter
  graph_filter.Execute(skeleton)

  # get the returning values
  nodes = graph_filter.GetNodeIndexes()
  edges = graph_filter.GetEdgeIndexes()
  edgeLUT = graph_filter.GetEdgeLUTIndexes()
  edges_lbl = graph_filter.GetEdgeMap()

  # create the 3D plot
  fig = plt.figure(figsize=(15, 15))
  ax = fig.add_subplot(projection='3d')

  # plot the skeleton paths as series of points
  pz, py, px = np.where(np_skeleton != 0)
  ax.scatter(px, py, pz, marker='o', color='lightgray', alpha=.5)

  # plot the nodes as single dots
  ax.scatter(*zip(*nodes), marker='.', color='blue', s=200, alpha=.1)

  # plot the edges as lines between vertices
  for ex, ey in edges:
    ax.plot(*zip(*(ex, ey)), color='blue', linewidth=2, alpha=.5)

  # multiply by 2 the z axis since it is commonly lower than x, y
  ax.set_box_aspect((np.ptp(px), np.ptp(py), np.ptp(pz)*2))
  ax.view_init(elev=0., azim=270)
