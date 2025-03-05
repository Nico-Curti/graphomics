#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gdown

__author__  = ['Nico Curti']
__email__   = ['nico.curti2@unibo.it']
__all__ = ['download_file_from_google_drive']

def download_file_from_google_drive (Id : str, destination : str, quiet : bool = True):
  '''
  Download the files from google-drive repository
  and move the files in the 'data' directory.

  Parameters
  ----------
  Id : str
    Google Drive Id of the weights file to download

  destination : str
    Output filepath of the downloaded file

  quiet : bool
    Verbose download
  '''

  gdown.download(
    id=Id,
    output=destination,
    quiet=quiet
  )
  # if something goes wrong the file does not exist
  if not os.path.exists(destination):
    # raise an exception
    raise ValueError(f'Download file failed for {destination}')
  return
  

if __name__ == '__main__':

  import argparse

  parser = argparse.ArgumentParser(
    description='Download file from google drive page.'
  )

  # id of the google drive file
  parser.add_argument(
    '--Id', '-i',
    dest='Id',
    type=str,
    required=True,
    help='File Id in Google Drive page'
  )

  # destination path of the downloaded file
  parser.add_argument(
    '--destination', '-d',
    dest='destination',
    type=str,
    required=True,
    help='Destination path of the download'
  )

  parser.add_argument(
    '--quite', '-q',
    dest='quiet',
    required=False,
    action='store_true',
    default=False,
    help='Verbosity in download'
  )

  args = parser.parse_args()
  
  download_file_from_google_drive(
    Id=args.Id,
    destination=args.destination,
    quiet=args.quiet
  )
