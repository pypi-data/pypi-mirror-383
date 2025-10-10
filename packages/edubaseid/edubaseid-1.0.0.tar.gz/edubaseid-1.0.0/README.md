# EduBaseID SDK

EduBaseID OAuth2 client for Python.

## Installation
pip install edubaseid

## Usage
from edubaseid import EduBaseIDClient
client = EduBaseIDClient()
url = client.get_authorize_url()