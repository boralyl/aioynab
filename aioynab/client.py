import asyncio
import logging
from typing import Any, Dict, List

import aiohttp
import uvloop


uvloop.install()

#: The base API URL for YNAB.
BASE_URL = 'https://api.youneedabudget.com/v1'


class YNABAPIError(Exception):
    """An error class for YNAB API errors.

    :param status: The http status code.
    :param error_data: The error data returned in the response.
    """

    def __init__(self, status: int, error_data: dict):
        self.status = status
        self.error_data = error_data
        super().__init__('{} - {}'.format(status, error_data['detail']))


class Client(object):
    """A client for the YNAB API.

    :param personal_access_token: The YNAB personal access token.  Create one
        at `https://app.youneedabudget.com/settings/developer`.
    :param loop: Optional event loop, one will be created if not passed.
    :param session: Optional aiohttp client session, one will be created if
        not passed.
    """

    def __init__(self, personal_access_token: str,
                 loop: asyncio.AbstractEventLoop = None,
                 session: aiohttp.ClientSession = None):
        self.personal_access_token = personal_access_token
        self.loop = loop if loop else asyncio.get_event_loop()
        self.session = (
            session if session else aiohttp.ClientSession(loop=self.loop))

        self.headers = {
            'Authorization': 'Bearer {}'.format(personal_access_token),
        }

    async def close(self):
        """Closes the session."""
        await self.session.close()

    async def _request(self, endpoint: str, method: str = 'GET',
                       params: dict = None) -> dict:
        """Performs a http request and returns the json response.

        :param endpoint: The API endpoint.
        :param method: The HTTP method to use (GET, POST, PUT).
        :param params: Any parameters to send with the request.
        :returns: The json data as a dict.
        """
        url = '{}/{}'.format(BASE_URL, endpoint)
        try:
            response = await self.session.request(
                method, url, params=params, headers=self.headers)
        except aiohttp.ClientError:
            logging.exception('Error requesting %s %s', method, url)
            raise

        json = await response.json()
        if response.status >= 400 or 'error' in json:
            error = json['error']
            logging.error(
                '%s Error requesting %s %s: %s', response.status, method, url,
                error['detail'])
            raise YNABAPIError(response.status, error)

        return json['data']

    async def user(self) -> Dict[str, str]:
        """Returns authenticated user information.

        Corresponds to the /user endpoint.

        :returns:
        """
        return await self._request('/user', 'GET')

    async def budgets(self) -> List[Dict[str, Any]]:
        """Returns budgets list with summary information.

        Corresponds to the /budgets endpoint.

        :reutrns:
        """
        return await self._request('/budgets', 'GET')

    async def budget(self, budget_id: str,
                     last_knowledge_of_server: int = None) -> Dict[str, Any]:
        """Returns a single budget with all related entities.

        This resource is effectively a full budget export.  Corresponds to the
        /budget/{budget_id} endpoint.

        :param budget_id: The ID of the budget to look up.
        :returns:
        """
        params = {}
        if last_knowledge_of_server:
            params['last_knowledge_of_server'] = last_knowledge_of_server
        return await self._request(
            '/budgets/{}'.format(budget_id), 'GET', params)
