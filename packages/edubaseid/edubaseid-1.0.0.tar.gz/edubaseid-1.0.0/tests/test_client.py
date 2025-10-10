# tests/test_client.py
import pytest
from requests_mock import Mocker

from edubaseid.client import EduBaseIDClient
from edubaseid.exceptions import EduBaseIDError

@pytest.fixture
def client():
    return EduBaseIDClient({
        'SERVER_URL': 'http://test.com',
        'CLIENT_ID': 'id',
        'CLIENT_SECRET': 'secret',
        'REDIRECT_URI': 'http://callback',
    })

def test_get_authorize_url(client):
    url = client.get_authorize_url()
    assert 'client_id=id' in url
    assert 'redirect_uri=http%3A%2F%2Fcallback' in url

def test_exchange_code_for_token(client, requests_mock: Mocker):
    requests_mock.post('http://test.com/oauth/token/', json={'access_token': 'tok'})
    token = client.exchange_code_for_token('code')
    assert token['access_token'] == 'tok'

def test_exchange_failure(client, requests_mock: Mocker):
    requests_mock.post('http://test.com/oauth/token/', status_code=400, text='error')
    with pytest.raises(EduBaseIDError):
        client.exchange_code_for_token('code')

# Add more tests for other methods