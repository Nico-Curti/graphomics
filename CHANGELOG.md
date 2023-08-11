# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1] - 2023-08-09

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

- :computer: [Python] Installation file for the Python package
- :computer: [Python] Entry point of the library for its usage with command line interface (ref. `graphomics/__main__.py`)
- :computer: [Python] Automated versioning of the library via setup installation
- :computer: [Python] Definition of Graphomics Feature classes and Statistics
- :computer: [Python] Generalization of the `GraphThicknessImageFilter` to support also 2D inputs
- :computer: [Python] Wrap of the skeletonization algorithm for an easier interface of the package
- :computer: [Python] New technique of semantic segmnetation via Watershed algorithm, based on graphomics extraction

- :construction: [Features] Add first list of Centrality Graphomics features: *Node degree centrality statistics*, *Node betweenness centrality statistics*, *Node clustering coefficients statistics*, *Node closeness centrality statistics*, *Node page-rank centrality statistics*
- :construction: [Features] Add first list of Topological Graphomics features: *Number of nodes*, *Number of edges*, *Euler number*, *Number of pendant nodes*, *Number of connected components*, *Modularity*, *Number of maximal cliques*
- :construction: [Features] Adding first list of Spatial Graphomics features: *Node density statistics*, *Fractal dimension*
- :construction: [Features] Add first list of Network weighting techniques: *NodePairwiseDistanceFilter*, *EdgeLengthPathsFilter*, *EdgeLabelWeightFilter*

- :closed_book: [Docs] Add first version of the README instructions
- :closed_book: [Docs] Add first version of the Sphinx documentation
- :closed_book: [Docs] Add first version of the Read-the-Docs documentation
- :closed_book: [Docs] Add notebook example for geometrical meaning of the Graphomics analysis
- :closed_book: [Docs] Add notebook example for the graph extraction processing in 3D
- :closed_book: [Docs] Add notebook example for the medical imaging application in 3D
- :closed_book: [Docs] Add notebook example for the graphomics semantic segmentation in 2D
