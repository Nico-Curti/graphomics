# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1] - 2025-03-05

First version of the library.
This is the starting point of the development of the *pyGraphomics* package.
Further improvements will occur in the next versions.

### Added

- :globe_with_meridians: [Global] Instruction for the pull-requests and issues with related templates
- :globe_with_meridians: [Global] Firt version of the configuration template for the graphomics workflow
- :globe_with_meridians: [Global] List of requirements for the Python package
- :globe_with_meridians: [Global] Manifest and pyproject files for the Python package
- :globe_with_meridians: [Global] Add first version of Appveyor build CI for Windows
- :globe_with_meridians: [Global] Add first version of Github Actions CI for Python and Docs
- :globe_with_meridians: [Global] Add download of medical image sample via Google Drive for testing
- :globe_with_meridians: [Global] Include Codecov tracking of the package
- :globe_with_meridians: [Global] Add snakemake workflow manager for multi-patients applications

- :computer: [Python] Installation file for the Python package
- :computer: [Python] Entry point of the library for its usage with command line interface (ref. `graphomics/__main__.py`)
- :computer: [Python] Automated versioning of the library via setup installation
- :computer: [Python] Definition of Graphomics Feature classes and Statistics
- :computer: [Python] Generalization of the `GraphThicknessImageFilter` to support also 2D inputs
- :computer: [Python] Computational improvement of the `GraphThicknessImageFilter` playing with sitk filters
- :computer: [Python] Wrap of the skeletonization algorithm for an easier interface of the package
- :computer: [Python] Image loader for DCM and Nifti file formats
- :computer: [Python] New technique of semantic segmentation via Watershed algorithm, based on graphomics extraction
- :computer: [Python] First version of the entire feature extraction module
- :computer: [Python] Loader of medical images supporting all the SimpleITK fmt + FreeSurfer .mgz
- :computer: [Python] Image resampling to equal spacing for the correct weighing of the network according to the path length
- :computer: [Python] Input mask binarization according to 1 or multiple values
- :computer: [Python] Test for feature extractor management
- :computer: [Python] Test for feature extractor configuration file
- :computer: [Python] Test for image data loader
- :computer: [Python] Test for image skeletonizer (aka `SkeletonizeImageFilter`)
- :computer: [Python] Test for `GraphThicknessImageFilter` on medical images and random 2D/3D blobs
- :computer: [Python] Test for graphomic topological features (aka `GraphomicsTopology`)
- :computer: [Python] Test for graphomic centrality features (aka `GraphomicsCentrality`)
- :computer: [Python] Test for graphomic spatial features (aka `GraphomicsSpatial`)
- :computer: [Python] Test for graphomic weight extractor (aka `GraphWeightsExtractorFilter`)
- :computer: [Python] Test for graphomic base features (aka `_BaseGraphomicsFeatures`)
- :computer: [Python] Test for graphomic features extractor (aka `GraphomicsFeatureExtractor`)

- :construction: [Features] First list of `Centrality` Graphomics features:
  * **Node degree centrality statistics**:
    The node degree is the number of edges adjacent to the node.
    The weighted node degree is the sum of the edge weights for
    edges incident to that node.
    The node degree centrality quantifies the importance of a
    node in the graph in terms of the number of links connected
    to it.
    This metric could be informative about the presence of hubs
    and ramifications in the skeleton structure.
  * **Node betweenness centrality statistics**:
    Betweenness centrality of a node `v` is the sum of the fraction
    of all-pairs shortest paths that pass through `v`.
    The betweenness centrality quantifies the importance of a
    node in the graph in terms of the number of paths that must pass
    through it.
    This metric could be informative about the presence of hubs
    and ramifications in the skeleton structure.
  * **Node clustering coefficients statistics**:
    The local clustering coefficient of a node in a graph
    quantifies how close its neighbours are to being a clique
    (complete graph).
  * **Node closeness centrality statistics**:
    Closeness centrality of a node `u` is the reciprocal of the
    average shortest path distance to `u` over all `n-1` reachable
    nodes.
  * **Node page-rank centrality statistics**:
    PageRank computes a ranking of the nodes in the graph `G` based
    on the structure of the incoming links.
    It was originally designed as an algorithm to rank web pages.
  * **Node harmonic centrality statistics**:
    Harmonic centrality of a node `u` is the sum of the reciprocal
    of the shortest path distances from all other nodes to `u`.
    The harmonic centrality quantifies the importance of a node
    in the graph in terms of its distance to the other nodes.
    This metric could be informative about the presence of hubs
    and ramifications in the skeleton structure.
  * **Degree distribution power law fit:**
    Fit of the degree distribution values as power law function.
    The characterization of the degree distribution provides hints
    about the nature of the underlying graph.
    A power law degree distribution is typical of scale-free graph.
    The value of the power law exponent and the associated score
    of Kolmogorov-Smirnov fit allow the description of the graph
    in these terms.
  * **Degree distribution exponential fit:**
    Fit of the degree distribution values as exponential function.
    The characterization of the degree distribution provides hints
    about the nature of the underlying graph.
    An exponential degree distribution is typical of Barabasi graph.
    The value of the fit exponent and the associated score
    of Kolmogorov-Smirnov fit allow the description of the graph
    in these terms.

- :construction: [Features] First list of `Topological` Graphomics features:
  * **Number of nodes**:
    The number of nodes of the skeleton
    graph could provides a fast information about the complexity
    of the network architecture and its fractality.
  * **Number of edges**:
    The number of edges of the skeleton
    graph could provides a fast information about the ramification
    of the network and the presence of holes in the original shape.
  * **Edge weight statistics**:
    The edges could be weighted according to a predefined
    score metrics, highlighting the significance of that link
    in the skeleton graph.
    The distribution of the weight scores could be used as feature
    for the quantification of that metric.
  * **Number of self links:**
    A self link is defined as a link between a node and itself.
    The number of self links could be informative about the
    presence of shape's holes and invaginations.
  * **Euler number**:
    The Euler number is a topological invariant
    which resume in a unique number the topological space's shape
    or structure regardless of the way it is bent.
  * **Number of pendant nodes**:
    A pendant node is defined as a node of the graph connected with
    only 1 link, i.e. a node with degree equal to 1 in an undirect graph.
    The number of pendant nodes could be informative about the
    presence of shape's holes and invaginations.
  * **Number of isolated nodes:**
    An isolated node is defined as a node with a degree equal to
    zero.
    The number of isolated nodes could be informative about the
    presence of spurious parts on the volume mask or they describe
    sphere-like structures on the volume (note: the skeleton of
    a sphere is just its center point).
  * **Number of connected components**:
    The number of connected components of the skeleton graph
    could provides a fast information about the number of distinct
    objects included in the mask.
  * **Modularity**:
    Modularity is a measure of the structure of networks or graphs which
    measures the strength of division of a network into modules
    (also called groups, clusters or communities).
    Networks with high modularity have dense connections between the nodes
    within modules but sparse connections between nodes in different modules.
    This feature could provide a fast information about the complexity
    of the skeleton graph.
  * **Number of maximal cliques**:
    A clique is a subset of vertices of an undirected graph such that every
    two distinct vertices in the clique are adjacent.
    The number of maximal cliques as feature could provide information
    about the complexity of the skeleton graph.

- :construction: [Features] First list of `Spatial` Graphomics features:
  * **Node density statistics**:
    The local spatial density of the nodes is evaluated
    using a Gaussian kernel density estimator. This
    metric could provide information about the sparsity
    of the nodes in the graph and the presence of possible
    clusters of points.
    As resulting features the filter provides the main
    statistics of the density distribution of values.
  * **Fractal dimension**:
    The fractal dimension is a term invoked in the science of
    geometry to provide a rational statistical index of
    complexity detail in a pattern.
    The fractal dimension is a feature strictly related to the
    complexity of the skeleton graph and it can be evaluated
    directly from the binarized mapper of the skeleton.
  * **Average shortest path**:
    The average shortest path length is the sum of path lengths `d(u,v)`
    between all pairs of nodes.
    This metric could be useful for the quantification of the complexity
    of the skeleton graph, especially when we consider a weighted graph.
  * **Statistics of Eccentricity distribution**:
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
  * **Center of Mass**:
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
  * **Statistics of Distances of the most central nodes**
    The distance of the nodes with higher degree centrality in
    relation to the center of mass of the 2D/3D shape could be
    informative about the distribution of the "bridges" in
    the shape.
  * **Statistics of Distances of No-pendant nodes**:
    The distance of the no-pendant nodes, i.e. the nodes a degree
    centrality != 1, in relation to the center of mass of the
    2D/3D shape could be informative about the distribution of
    the ramification points in the shape.
  * **Statistics of pendant nodes**:
    The distance of the pendant nodes, i.e. the nodes with lowest
    degree centrality, in relation to the center of mass of the
    2D/3D shape could be informative about the distribution of
    the tails in the shape.

- :construction: [Features] First list of `Network weighing` techniques:
  * **NodePairwiseDistanceFilter**:
    Evaluate the weights of the graph as the pairwise distance
    between the node positions according to the given metric.
  * **EdgeLengthPathsFilter**:
    Evaluate the weights of the graph as the lenght of the original
    path between two node positions as the number of items in the
    mapper.
  * **EdgeLabelWeightFilter**:
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

- :closed_book: [Docs] First version of the README instructions
- :closed_book: [Docs] First version of the Sphinx documentation
- :closed_book: [Docs] First version of the Read-the-Docs documentation
- :closed_book: [Docs] "HelloWorld" example of a graphomic pipeline
  (ref. [here](https://github.com/Nico-Curti/graphomics/blob/main/examples/GraphomicsHelloWorld.py))
- :closed_book: [Docs] Example of graphomic filter management in terms of features and classes
  (ref. [here](https://github.com/Nico-Curti/graphomics/blob/main/examples/GraphomicsFeatureClass.py))
- :closed_book: [Docs] Notebook example for geometrical meaning of the Graphomics analysis
- :closed_book: [Docs] Notebook example for the graph extraction processing in 3D
- :closed_book: [Docs] Notebook example for the medical imaging application in 3D
- :closed_book: [Docs] Notebook example for the graphomics semantic segmentation in 2D
  with real-case application to femour, brain, and liver volumes
- :closed_book: [Docs] Notebook example for the graphomics semantic segmentation in 3D
  with real-case application to femour, brain, and liver volumes
- :closed_book: [Docs] Notebook example for multi-modal image analysis
  with real-case application to multiple myeloma
- :closed_book: [Docs] List of notebook examples in the sphinx documentation
- :closed_book: [Docs] Snakefile example for workflow management
- :closed_book: [Docs] README documentation of the snakemake script
- :closed_book: [Docs] README documentation of the example scripts
- :closed_book: [Docs] Add FAQ section in main README
