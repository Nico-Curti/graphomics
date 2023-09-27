#!/usr/bin/env python
import os
import time
import argparse
import requests
import platform
from zipfile import ZipFile

_author_  = ['Nico Curti']
_email_   = ['nico.curti2@unibo.it']


CRLF = '\r\x1B[K' if platform.system() != 'Windows' else '\r'


def download_file_from_google_drive (Id, destination):

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
  The total length is useful only for graphics.
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

  def save_response_content (response, destination):
    '''
    Download the file chunk by chunk and plot the progress
    '''
    chunk_size = 32768
    with open(destination, 'wb') as fp:
      dl = 0

      for chunk in response.iter_content(chunk_size):

        dl += len(chunk)

        if chunk:
          fp.write(chunk)

    print('', end='\n')

  session  = requests.Session()
  response = session.get(url, stream=True)
  token    = get_confirm_token(response)

  if token:
    params = { 'id' : Id, 'confirm' : token}
    response = session.get(url, params=params, stream=True)

  save_response_content(response, destination)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Download file from google drive page.')
  parser.add_argument('--Id', dest='Id', type=str, required=True, help='File Id in Google Drive page')
  parser.add_argument('--destination', dest='destination', type=str, required=True, help='Destination path of the download')
  parser.add_argument('--total_length', dest='total_length', type=int, default=230636758, help='File dimension in byte')
  args = parser.parse_args()
  
  download_file_from_google_drive(args.Id, args.destination, args.total_length)