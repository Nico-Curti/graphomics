.. _usage:

Usage
=====

You can use the `graphomics` library into your Python scripts or directly via command line.

Command Line Interface
----------------------

The `graphomics` package could be easily used via command line by simply calling the `graphomics` program.

The full list of available flags for the customization of the command line could be obtained by calling:

.. code-block:: bash

  $ graphomics --help

  usage: pyGraphomics [-h] [--version] [--nth NTH] [--config CONFIG] [--input MASK_FILEPATH]
                      [--skeleton SKELETON_FILEPATH] [--label LABEL_FILEPATH] [--weight]
                      [--wextractor {NodePairwiseDistanceFilter,EdgeLengthPathsFilter,EdgeLabelWeightFilter}]
                      [--topology] [--spatial] [--centrality] --output OUTPUT_FILENAME

  Graphomics library - Open-source python package for the extraction of Graphomics features from 2D and 3D binary masks

  optional arguments:
    -h, --help            show this help message and exit
    --version, -v         Get the current version installed
    --nth NTH, -j NTH     Number of threads to use during the filter execution (when possible)
    --config CONFIG, -c CONFIG
                          Configuration file in Yaml format for the pipeline execution
    --input MASK_FILEPATH, -i MASK_FILEPATH
                          Input filename or path on which load the binary mask of the shape. Ref
                          https://simpleitk.readthedocs.io/en/master/IO.html for the list of supported format.
    --skeleton SKELETON_FILEPATH, -k SKELETON_FILEPATH
                          Input filename or path on which load the binary skeleton of the shape. Ref
                          https://simpleitk.readthedocs.io/en/master/IO.html for the list of supported format.
    --label LABEL_FILEPATH, -l LABEL_FILEPATH
                          Input filename or path on which load the labelmap to use for the network weighing. Ref
                          https://simpleitk.readthedocs.io/en/master/IO.html for the list of supported format.
    --weight, -w          Enable network weights during the features extraction
    --wextractor {NodePairwiseDistanceFilter,EdgeLengthPathsFilter,EdgeLabelWeightFilter}, -e {NodePairwiseDistanceFilter,EdgeLengthPathsFilter,EdgeLabelWeightFilter}
                          Network weight extractor model to use during the features extraction
    --topology, -T        Enable Topological Graphomic features extraction
    --spatial, -S         Enable Spatial Graphomic features extraction
    --centrality, -C      Enable Centrality Graphomic features extraction
    --output OUTPUT_FILENAME, -o OUTPUT_FILENAME
                          Output filename in which save the graphomic features as JSON. If a file with the same name
                          already exists it will be overwritten by a new one

  pyGraphomics Python package v0.0.1

Python script
-------------

A complete list of beginner-examples for the build of a custom `graphomic` pipeline could be found here_.

For more advanced users, we suggest to take a look at the example notebooks_, in which are reported more sophisticated applications and real-world examples.

For sake of completeness, a simple `graphomic` pipeline could be obtained by the following snippet:

.. code-block:: python

  from graphomics import LoadImageFileInAnyFormat
  from graphomics import GraphomicsFeatureExtractor

  # load the medical image in any SimpleITK supported fmt
  img = LoadImageFileInAnyFormat(
    filename='/path/to/medical/image.nii.gz',
    binarize=True
  )
  # define the graphomic filter
  extractor = GraphomicsFeatureExtractor()
  # enable all the available graphomic features
  extractor.EnableAllFeatures()
  # set the input image-mask
  extractor.SetMaskImage(mask=img)
  # execute the filter
  extractor.Execute()
  # get the resulting graphomic features computed
  graphomic_features = extractor.GetFeatures()

  # display the results
  print(graphomic_features)

.. _here: https://github.com/Nico-Curti/graphomics/blob/main/examples
.. _notebooks: https://github.com/Nico-Curti/graphomics/blob/main/notebooks
