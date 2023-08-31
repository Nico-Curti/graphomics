#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import argparse

from .__version__ import __version__
from .featureextractor import GraphomicsFeatureExtractor

__author__  = ['Nico Curti',
               'Gianluca Carlini',
               'Riccardo Biondi'
              ]
__email__ = ['nico.curti2@unibo.it',
             'gianluca.carlini2@unibo.it',
             'riccardo.biondi2@unibo.it'
            ]

def parse_args ():

  description = ('Graphomics library - '
    'Open-source python package for the extraction of '
    'Graphomics features from 2D and 3D binary masks'
  )

  # global sofware information
  parser = argparse.ArgumentParser(
    prog='graphomics',
    argument_default=None,
    add_help=True,
    prefix_chars='-',
    allow_abbrev=True,
    exit_on_error=True,
    description=description,
    epilog=f'pyGraphomics Python package v{__version__}'
  )

  # pygraphomics --version
  parser.add_argument(
    '--version', '-v',
    dest='version',
    required=False,
    action='store_true',
    default=False,
    help='Get the current version installed',
  )

  # number of threads
  parser.add_argument(
    '--nth', '-j',
    dest='nth',
    required=False,
    action='store',
    default=1,
    type=int,
    help='Number of threads to use during the filter execution (when possible)'
  )

  # configuration file
  parser.add_argument(
    '--config', '-c',
    dest='config',
    required=False,
    action='store',
    default=None,
    type=str,
    help='Configuration file in Yaml format for the pipeline execution',
  )

  # input mask filename
  parser.add_argument(
    '--input', '-i',
    dest='mask_filepath',
    required=False,
    action='store',
    default=None,
    type=str,
    help=(
      'Input filename or path on which load the binary mask of the shape.'
      'Ref https://simpleitk.readthedocs.io/en/master/IO.html for the list of '
      'supported format. '
    )
  )

  # input skeleton filename
  parser.add_argument(
    '--skeleton', '-k',
    dest='skeleton_filepath',
    required=False,
    action='store',
    default=None,
    type=str,
    help=(
      'Input filename or path on which load the binary skeleton of the shape.'
      'Ref https://simpleitk.readthedocs.io/en/master/IO.html for the list of '
      'supported format. '
    )
  )

  # input labelmap filename
  parser.add_argument(
    '--label', '-l',
    dest='label_filepath',
    required=False,
    action='store',
    default=None,
    type=str,
    help=(
      'Input filename or path on which load the labelmap to use for the network weighting.'
      'Ref https://simpleitk.readthedocs.io/en/master/IO.html for the list of '
      'supported format. '
    )
  )

  # enable network weighting
  parser.add_argument(
    '--weight', '-w',
    dest='enable_weighted_features',
    required=False,
    action='store_true',
    default=False,
    help='Enable network weights during the features extraction'
  )

  # network weight extractor model
  parser.add_argument(
    '--wextractor', '-e',
    dest='graph_weights',
    required=False,
    action='store',
    default='EdgeLengthPathsFilter',
    choices=[
      'NodePairwiseDistanceFilter',
      'EdgeLengthPathsFilter',
      'EdgeLabelWeightFilter',
    ],
    help='Network weight extractor model to use during the features extraction'
  )

  # enable topological graphomic features
  parser.add_argument(
    '--topology', '-T',
    dest='enable_topology',
    required=False,
    action='store_true',
    default=False,
    help='Enable Topological Graphomic features extraction'
  )

  # enable spatial graphomic features
  parser.add_argument(
    '--spatial', '-S',
    dest='enable_spatial',
    required=False,
    action='store_true',
    default=False,
    help='Enable Spatial Graphomic features extraction'
  )

  # enable centrality graphomic features
  parser.add_argument(
    '--centrality', '-C',
    dest='enable_centrality',
    required=False,
    action='store_true',
    default=False,
    help='Enable Centrality Graphomic features extraction'
  )

  # set output filename in which save the graphomic features
  parser.add_argument(
    '--output', '-o',
    dest='output_filename',
    required=True,
    action='store',
    default='',
    type=str,
    help=(
      'Output filename in which save the graphomic features as JSON. '
      'If a file with the same name already exists it will be overwritten by '
      'a new one'
    )
  )

  args = parser.parse_args()

  return args


def main ():

  # get the cmd parameters
  args = parse_args()

  # results if version is required
  if args.version:
    # print it to stdout
    print(f'Graphomics package v{__version__}',
      end='\n', file=sys.stdout, flush=True
    )
    # exit success
    exit(0)

  # check that at least one of the required inputs is provided
  if args.config is None and args.input is None:
    raise ValueError((
      'Invalid command line. '
      'Neither configuration nor input file was provided. '
      'At least one of these parameters must be give for the correct '
      'run of the graphomics pipeline'
    ))

  # declare the feature extractor filter
  extractor = GraphomicsFeatureExtractor()

  # if the configuration file is provided than we get all
  # the information from it, overriding only the information
  # passed via command line
  if args.config:
    # load the config file
    extractor.LoadConfig(
      filename=args.config
    )

  # override the provided information if necessary

  if args.mask_filepath:
    # set the mask file if provided via command line
    extractor.SetMaskFilepath(
      maskfile=args.mask_filepath
    )

  if args.skeleton_filepath:
    # set the skeleton file if provided via command line
    extractor.SetSkeletonFilepath(
      skeletonfile=args.skeleton_filepath
    )

  if args.label_filepath:
    # set the skeleton file if provided via command line
    extractor.SetLabelFilepath(
      labelfile=args.label_filepath
    )

  if args.enable_weighted_features:
    # override the weight evaluation in the config file
    extractor.EnableWeightedFeatures()

  if args.graph_weights:
    # override the weight extractor
    extractor.SetWeightExtractorByName(
      wtype=args.graph_weights
    )

  if args.nth:
    # override the number of threads to use
    extractor.SetGlobalDefaultNumberOfThreads(
      nth=args.nth
    )

  if args.enable_topology:
    # override the extraction of all the topological features
    extractor.EnableFeatureClassByName(
      name='topology'
    )

  if args.enable_spatial:
    # override the extraction of all the spatial features
    extractor.EnableFeatureClassByName(
      name='spatial'
    )

  if args.enable_centrality:
    # override the extraction of all the centrality features
    extractor.EnableFeatureClassByName(
      name='centrality'
    )

  # run the feature extraction task
  extractor.Execute()

  # get the resulting graphomics features
  graphomic_features = extractor.GetFeatures()

  # dump the extracted features to file
  with open(args.output_filename, 'w', encoding='utf-8') as fp:
    json.dumps(
      obj=graphomic_features,
      fp=fp,
      ensure_ascii=True,
      indent=2
    )

  # exit success
  exit(0)

if __name__ == '__main__':

  main ()
