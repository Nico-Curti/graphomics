#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse

from .__version__ import __version__

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

  parser = argparse.ArgumentParser(
    description=description
  )

  parser.add_argument(
    '--version', '-v',
    dest='version',
    required=False,
    action='store_true',
    help='Get the current version installed',
  )


def main ():

  args = parse_args()

  if args.version:
    print(f'Graphomics package v{__version__}',
      end='\n', file=sys.stdout, flush=True
    )




if __name__ == '__main__':

  main ()
