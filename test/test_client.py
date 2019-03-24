import asyncio

import aiohttp
import pytest
from aioresponses import aioresponses

from aioynab.client import BASE_URL, Client, YNABAPIError


@pytest.fixture(scope='module')
def client():
    loop = asyncio.get_event_loop()
    client = Client('access-token', loop=loop)
    yield client
    loop.run_until_complete(client.close())


def test_init(client):
    assert 'access-token' == client.personal_access_token
    assert {'Authorization': 'Bearer access-token'} == client.headers


def test_request_clienterror(client):
    with aioresponses() as mock_req:
        mock_req.get(
            BASE_URL + '/foo', exception=aiohttp.ClientError('timeout'))
        with pytest.raises(aiohttp.ClientError, match='timeout'):
            client.loop.run_until_complete(client._request('/foo', 'GET'))


def test_request_success(client):
    mock_res = {'data': 'foo'}
    with aioresponses() as mock_req:
        mock_req.get(BASE_URL + '/foo', payload=mock_res)
        actual = client.loop.run_until_complete(client._request('/foo', 'GET'))
        assert 'foo' == actual


def test_request_api_error(client):
    mock_res = {
        'error': {
            'id': '404.1',
            'name': 'not_found',
            'detail': 'Invalid URI',
        },
    }
    with aioresponses() as mock_req:
        mock_req.get(BASE_URL + '/foo', payload=mock_res, status=404)
        with pytest.raises(YNABAPIError) as err:
            client.loop.run_until_complete(client._request('/foo', 'GET'))
        assert 404 == err.value.status
        assert '404 - Invalid URI' == str(err.value)
        assert mock_res['error'] == err.value.error_data


def test_user(client):
    mock_res = {
        'data': {
            'user': {'id': 'abcd'},
        },
    }
    with aioresponses() as mock_req:
        mock_req.get(BASE_URL + '/user', payload=mock_res)
        actual = client.loop.run_until_complete(client.user())
        assert mock_res['data'] == actual


def test_budgets(client):
    mock_res = {
        'data': {
            'budgets': [{
                'currency_format': {
                    'currency_symbol': '$',
                    'decimal_digits': 2,
                    'decimal_separator': '.',
                    'display_symbol': True,
                    'example_format': '123,456.78',
                    'group_separator': ',',
                    'iso_code': 'USD',
                    'symbol_first': True,
                },
                'date_format': {'format': 'MM/DD/YYYY'},
                'first_month': '2018-09-01',
                'id': '01234567-012a-3fe0-abc1-9e123456789c',
                'last_modified_on': '2019-03-21T00:03:57+00:00',
                'last_month': '2019-04-01',
                'name': 'Our Budget',
            }],
        },
    }
    with aioresponses() as mock_req:
        mock_req.get(BASE_URL + '/budgets', payload=mock_res)
        actual = client.loop.run_until_complete(client.budgets())
        assert mock_res['data'] == actual


def test_budget(client):
    mock_res = {
        'data': {
            'budget': {}
        },
    }
    with aioresponses() as mock_req:
        budget_id = '01234567-012a-3fe0-abc1-9e123456789c'
        mock_req.get(BASE_URL + '/budgets/{}'.format(budget_id),
                     payload=mock_res)
        actual = client.loop.run_until_complete(client.budget(budget_id))
        assert mock_res['data'] == actual


def test_budget_settings(client):
    mock_res = {
        'data': {
            'settings': {}
        },
    }
    with aioresponses() as mock_req:
        budget_id = '01234567-012a-3fe0-abc1-9e123456789c'
        mock_req.get(BASE_URL + '/budgets/{}/settings'.format(budget_id),
                     payload=mock_res)
        actual = client.loop.run_until_complete(
            client.budget_settings(budget_id))
        assert mock_res['data'] == actual


def test_accounts(client):
    mock_res = {
        'data': {
            'accounts': []
        },
    }
    with aioresponses() as mock_req:
        budget_id = '01234567-012a-3fe0-abc1-9e123456789c'
        mock_req.get(BASE_URL + '/budgets/{}/accounts'.format(budget_id),
                     payload=mock_res)
        actual = client.loop.run_until_complete(client.accounts(budget_id))
        assert mock_res['data'] == actual


def test_account(client):
    mock_res = {
        'data': {
            'account': {}
        },
    }
    with aioresponses() as mock_req:
        budget_id = account_id = '01234567-012a-3fe0-abc1-9e123456789c'
        mock_req.get(BASE_URL + '/budgets/{}/accounts/{}'.format(
            budget_id, account_id), payload=mock_res)
        actual = client.loop.run_until_complete(
            client.account(budget_id, account_id))
        assert mock_res['data'] == actual
