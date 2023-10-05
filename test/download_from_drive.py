#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

__author__  = ['Nico Curti']
__email__   = ['nico.curti2@unibo.it']
__all__ = ['download_file_from_google_drive']

def download_file_from_google_drive (Id : int, destination : str):

  '''
  Download file from google drive page.

  Parameters
  ----------
    Id : int
      File Id in Google Drive page

    destination : str
      Destination path of the download

  Returns
  -------
    None

  Notes
  -----
  The file Id can be extracted from the google drive page when the file is shared.
  '''

  url = f'https://docs.google.com/uc?export=download&id={Id}'

  def get_confirm_token (response):
    '''
    Check token validity.
    '''
    for key, value in response.cookies.items():
      if key.startswith('download_warning'):
        return value

    return None

  def save_response_content (response, destination : str):
    '''
    Download the file chunk by chunk and plot the progress
    '''

    chunk_size = 64 * 1024

    with open(destination, 'wb') as fp:
      dl = 0

      for chunk in response.iter_content(chunk_size):

        dl += len(chunk)

        if chunk:
          fp.write(chunk)

    print('', end='\n')

  session  = requests.Session()
  response = session.get(
    url,
    stream=True
  )
  token = get_confirm_token(response)

  if token:
    params = {
      'id' : Id,
      'confirm' : token
    }
    response = session.get(
      url,
      params=params,
      stream=True
    )

  save_response_content(response, destination)
  

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

  args = parser.parse_args()
  
  download_file_from_google_drive(
    Id=args.Id,
    destination=args.destination
  )
