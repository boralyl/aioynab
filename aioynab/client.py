import asyncio
import logging

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
                       params: dict = None, body: dict = None) -> dict:
        """Performs a http request and returns the json response.

        :param endpoint: The API endpoint.
        :param method: The HTTP method to use (GET, POST, PUT).
        :param params: Any parameters to send with the request.
        :param body: A json body to send with the request.
        :returns: The json data as a dict.
        """
        url = '{}{}'.format(BASE_URL, endpoint)
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

    async def user(self) -> dict:
        """Returns authenticated user information.

        Corresponds to the /user endpoint.

        :returns:
        """
        return await self._request('/user', 'GET')

    async def budgets(self) -> dict:
        """Returns budgets list with summary information.

        Corresponds to the /budgets endpoint.

        :reutrns:
        """
        return await self._request('/budgets', 'GET')

    async def budget(self, budget_id: str,
                     last_knowledge_of_server: int = None) -> dict:
        """Returns a single budget with all related entities.

        This resource is effectively a full budget export.  Corresponds to the
        /budget/{budget_id} endpoint.

        :param budget_id: The ID of the budget to look up.
        :param last_knowledge_of_server: The starting server knowledge. If
            provided, only entities that have changed since
            last_knowledge_of_server will be included.
        :returns:
        """
        params = {}
        if last_knowledge_of_server:
            params['last_knowledge_of_server'] = last_knowledge_of_server
        return await self._request(
            '/budgets/{}'.format(budget_id), 'GET', params)

    async def budget_settings(self, budget_id: str) -> dict:
        """Returns settings for a budget.

        Corresponds to the /budget/{budget_id/settings endpont.

        :param budget_id: The ID of the budget.
        :returns: The budget settings data as a dict.
        """
        return await self._request(
            '/budgets/{}/settings'.format(budget_id), 'GET')

    async def accounts(self, budget_id: str,
                       last_knowledge_of_server: int = None) -> dict:
        """Returns all accounts associated with the budget.

        Corresponds to the /budget/{budget_id}/accounts endpoint.

        :param budget_id: The ID of the budget to look up.
        :param last_knowledge_of_server: The starting server knowledge. If
            provided, only entities that have changed since
            last_knowledge_of_server will be included.
        :returns:
        """
        params = {}
        if last_knowledge_of_server:
            params['last_knowledge_of_server'] = last_knowledge_of_server
        return await self._request(
            '/budgets/{}/accounts'.format(budget_id), 'GET', params)

    async def account(self, budget_id: str, account_id: str) -> dict:
        """Returns a single account associated with a budget.

        Corresponds to the /budget/{budget_id}/accounts/{account_id} endpoint.

        :param budget_id: The ID of the budget to look up.
        :param account_id: The ID of the account.
        :returns:
        """
        return await self._request(
            '/budgets/{}/accounts/{}'.format(budget_id, account_id), 'GET')

    async def categories(self, budget_id: str,
                         last_knowledge_of_server: int = None) -> dict:
        """Returns all categories grouped by category group.

        Corresponds to the /budgets/{budget_id}/categories endpoint.

        :param budget_id: The ID of the budget to look up.
        :param last_knowledge_of_server: The starting server knowledge. If
            provided, only entities that have changed since
            last_knowledge_of_server will be included.
        :returns:
        """
        params = {}
        if last_knowledge_of_server:
            params['last_knowledge_of_server'] = last_knowledge_of_server
        return await self._request(
            '/budgets/{}/categories'.format(budget_id), 'GET', params)

    async def category(self, budget_id: str, category_id: str) -> dict:
        """Returns a single category.

        Amounts (budgeted, activity, balance, etc.) are specific to the current
        budget month (UTC). Corresponds to the
        /budgets/{budget_id}/categories/{category_id} endpoint.

        :param budget_id: The ID of the budget.
        :param category_id: The ID of the category.
        :returns:
        """
        return await self._request(
            '/budgets/{}/categories/{}'.format(budget_id, category_id), 'GET')

    async def category_month(
            self, budget_id: str, category_id: str, month: str) -> dict:
        """Returns a single category for a specific budget month.

        Amounts (budgeted, activity, balance, etc.) are specific to the current
        budget month (UTC).  Corresponds to the
        /budgets/{budget_id}/months/{month}/categories/{category_id} endpoint.

        :param budget_id: The ID of the budget.
        :param category_id: The ID of the category.
        :param month: The budget month in ISO format (e.g. 2016-12-01)
            ('current' can also be used to specify the current calendar month
            (UTC)).
        :returns:
        """
        url = '/budgets/{}/months/{}/categories/{}'.format(
            budget_id, month, category_id)
        return await self._request(url, 'GET')

    async def update_category_month(
            self, budget_id: str, category_id: str, month: str,
            data: dict) -> dict:
        """Updates a category for a specific month.

        Corresponds to the
        /budgets/{budget_id}/months/{month}/categories/{category_id} endpoint.

        :param budget_id: The ID of the budget.
        :param category_id: The ID of the category.
        :param month: The budget month in ISO format (e.g. 2016-12-01)
            ('current' can also be used to specify the current calendar month
            (UTC)).
        :param data: A dict containing the fields/values to update.
        :returns:
        """
        url = '/budgets/{}/months/{}/categories/{}'.format(
            budget_id, month, category_id)
        return await self._request(url, 'PATCH', body=data)

    async def payees(self, budget_id: str,
                     last_knowledge_of_server: int = None) -> dict:
        """Returns all payees.

        Corresponds to the /budgets/{budget_id}/payees endpoint.

        :param budget_id: The ID of the budget.
        :param last_knowledge_of_server: The starting server knowledge. If
            provided, only entities that have changed since
            last_knowledge_of_server will be included.
        :returns:
        """
        params = {}
        if last_knowledge_of_server:
            params['last_knowledge_of_server'] = last_knowledge_of_server
        return await self._request(
            '/budgets/{}/payees'.format(budget_id), 'GET', params)

    async def payee(self, budget_id: str, payee_id: str) -> dict:
        """Returns single payee.

        :param budget_id: The ID of the budget.
        :param payee_id: The ID of the payee.
        :returns:
        """
        return await self._request(
            '/budgets/{}/payees/{}'.format(budget_id, payee_id), 'GET')
