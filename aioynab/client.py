import asyncio
import json
import logging
from typing import List

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
        :raises YNABAPIError: If there is an api error.
        """
        url = '{}{}'.format(BASE_URL, endpoint)
        try:
            response = await self.session.request(
                method, url, params=params, json=body, headers=self.headers)
        except aiohttp.ClientError:
            logging.exception('Error requesting %s %s', method, url)
            raise

        try:
            data = await response.json()
        except aiohttp.ContentTypeError:
            # 429 responses are not returned as json responses, but can be
            # parsed as such.
            text = await response.text()
            try:
                data = json.loads(text)
            except ValueError:
                logging.exception('Error parsing response as json: %s', text)
                raise
        if response.status >= 400 or 'error' in data:
            # @TODO: X-Rate-Limit header does not appear to be returned in
            # the response headers when a 429 error occurs.  Open a ticket and
            # come back to that later.
            error = data['error']
            logging.error(
                '%s Error requesting %s %s: %s', response.status, method, url,
                error['detail'])
            raise YNABAPIError(response.status, error)

        return data['data']

    async def user(self) -> dict:
        """Returns authenticated user information.

        Corresponds to the `/user` endpoint.

        :returns: A dict with user data.
        """
        return await self._request('/user', 'GET')

    async def budgets(self) -> dict:
        """Returns budgets list with summary information.

        Corresponds to the `/budgets` endpoint.

        :reutrns: A dict containing all budgets.
        """
        return await self._request('/budgets', 'GET')

    async def budget(self, budget_id: str,
                     last_knowledge_of_server: int = None) -> dict:
        """Returns a single budget with all related entities.

        This resource is effectively a full budget export.  Corresponds to the
        `/budget/{budget_id}` endpoint.

        :param budget_id: The ID of the budget to look up.
        :param last_knowledge_of_server: The starting server knowledge. If
            provided, only entities that have changed since
            last_knowledge_of_server will be included.
        :returns: A dict containing the requested budget.
        """
        params = {}
        if last_knowledge_of_server is not None:
            params['last_knowledge_of_server'] = last_knowledge_of_server
        return await self._request(
            '/budgets/{}'.format(budget_id), 'GET', params)

    async def budget_settings(self, budget_id: str) -> dict:
        """Returns settings for a budget.

        Corresponds to the `/budget/{budget_id/settings` endpont.

        :param budget_id: The ID of the budget.
        :returns: The budget settings data as a dict.
        """
        return await self._request(
            '/budgets/{}/settings'.format(budget_id), 'GET')

    async def accounts(self, budget_id: str,
                       last_knowledge_of_server: int = None) -> dict:
        """Returns all accounts associated with the budget.

        Corresponds to the `/budget/{budget_id}/accounts` endpoint.

        :param budget_id: The ID of the budget to look up.
        :param last_knowledge_of_server: The starting server knowledge. If
            provided, only entities that have changed since
            last_knowledge_of_server will be included.
        :returns: A dict containing all accounts.
        """
        params = {}
        if last_knowledge_of_server is not None:
            params['last_knowledge_of_server'] = last_knowledge_of_server
        return await self._request(
            '/budgets/{}/accounts'.format(budget_id), 'GET', params)

    async def account(self, budget_id: str, account_id: str) -> dict:
        """Returns a single account associated with a budget.

        Corresponds to the `/budget/{budget_id}/accounts/{account_id}` endpoint.

        :param budget_id: The ID of the budget to look up.
        :param account_id: The ID of the account.
        :returns: A dict of the account.
        """
        return await self._request(
            '/budgets/{}/accounts/{}'.format(budget_id, account_id), 'GET')

    async def categories(self, budget_id: str,
                         last_knowledge_of_server: int = None) -> dict:
        """Returns all categories grouped by category group.

        Corresponds to the `/budgets/{budget_id}/categories` endpoint.

        :param budget_id: The ID of the budget to look up.
        :param last_knowledge_of_server: The starting server knowledge. If
            provided, only entities that have changed since
            last_knowledge_of_server will be included.
        :returns: A dict of all categories.
        """
        params = {}
        if last_knowledge_of_server is not None:
            params['last_knowledge_of_server'] = last_knowledge_of_server
        return await self._request(
            '/budgets/{}/categories'.format(budget_id), 'GET', params)

    async def category(self, budget_id: str, category_id: str) -> dict:
        """Returns a single category.

        Amounts (budgeted, activity, balance, etc.) are specific to the current
        budget month (UTC). Corresponds to the
        `/budgets/{budget_id}/categories/{category_id}` endpoint.

        :param budget_id: The ID of the budget.
        :param category_id: The ID of the category.
        :returns: A dict of the requested category.
        """
        return await self._request(
            '/budgets/{}/categories/{}'.format(budget_id, category_id), 'GET')

    async def category_month(
            self, budget_id: str, category_id: str, month: str) -> dict:
        """Returns a single category for a specific budget month.

        Amounts (budgeted, activity, balance, etc.) are specific to the current
        budget month (UTC).  Corresponds to the
        `/budgets/{budget_id}/months/{month}/categories/{category_id}` endpoint.

        :param budget_id: The ID of the budget.
        :param category_id: The ID of the category.
        :param month: The budget month in ISO format (e.g. 2016-12-01)
            ('current' can also be used to specify the current calendar month
            (UTC)).
        :returns: A dict for the specified category and month.
        """
        url = '/budgets/{}/months/{}/categories/{}'.format(
            budget_id, month, category_id)
        return await self._request(url, 'GET')

    async def update_category_month(
            self, budget_id: str, category_id: str, month: str,
            data: dict) -> dict:
        """Updates a category for a specific month.

        Corresponds to the
        `/budgets/{budget_id}/months/{month}/categories/{category_id}` endpoint.

        :param budget_id: The ID of the budget.
        :param category_id: The ID of the category.
        :param month: The budget month in ISO format (e.g. 2016-12-01)
            ('current' can also be used to specify the current calendar month
            (UTC)).
        :param data: A dict containing the fields/values to update.
        :returns: A dict of the category for the month.
        """
        data = {'category': data}
        url = '/budgets/{}/months/{}/categories/{}'.format(
            budget_id, month, category_id)
        return await self._request(url, 'PATCH', body=data)

    async def payees(self, budget_id: str,
                     last_knowledge_of_server: int = None) -> dict:
        """Returns all payees.

        Corresponds to the `/budgets/{budget_id}/payees` endpoint.

        :param budget_id: The ID of the budget.
        :param last_knowledge_of_server: The starting server knowledge. If
            provided, only entities that have changed since
            last_knowledge_of_server will be included.
        :returns: A dict of all payees.
        """
        params = {}
        if last_knowledge_of_server:
            params['last_knowledge_of_server'] = last_knowledge_of_server
        return await self._request(
            '/budgets/{}/payees'.format(budget_id), 'GET', params)

    async def payee(self, budget_id: str, payee_id: str) -> dict:
        """Returns single payee.

        Corresponds to the `/budgets/{budget_id}/payees/{payee_id}` endpoint.

        :param budget_id: The ID of the budget.
        :param payee_id: The ID of the payee.
        :returns: A dict of the requested payee.
        """
        return await self._request(
            '/budgets/{}/payees/{}'.format(budget_id, payee_id), 'GET')

    async def payee_locations(self, budget_id: str) -> dict:
        """Returns all payee locations.

        Corresponds to the `/budgets/{budget_id}/payee_locations` endpoint.

        :param budget_id: The ID of the budget.
        :returns: A dict of all payee locations.
        """
        return await self._request(
            '/budgets/{}/payee_locations'.format(budget_id), 'GET')

    async def payee_location(
            self, budget_id: str, payee_location_id: str) -> dict:
        """Returns all payee locations.

        Corresponds to the
        `/budgets/{budget_id}/payee_locations/{payee_location_id}` endpoint.

        :param budget_id: The ID of the budget.
        :param payee_location_id: The ID of the payee location.
        :returns: A dict of the requested payee location.
        """
        return await self._request(
            '/budgets/{}/payee_locations/{}'.format(
                budget_id, payee_location_id), 'GET')

    async def locations_payee(self, budget_id: str, payee_id: str) -> dict:
        """Returns all payee locations for the specified payee.

        Corresponds to the
        `/budgets/{budget_id}/payees/{payee_id}/payee_locations` endpoint.

        :param budget_id: The ID of the budget.
        :param payee_id: The ID of the payee.
        :returns: A dict of locations for the requested payee.
        """
        return await self._request(
            '/budgets/{}/payees/{}/payee_locations'.format(budget_id, payee_id),
            'GET')

    async def budget_months(
            self, budget_id: str, last_knowledge_of_server: int = None) -> dict:
        """Returns all budget months.

        Corresponds to the `/budgets/{budget_id}/months` endpoint.

        :param budget_id: The ID of the budget.
        :param last_knowledge_of_server: The starting server knowledge. If
            provided, only entities that have changed since
            last_knowledge_of_server will be included.
        :returns: A dict of all budget months.
        """
        params = {}
        if last_knowledge_of_server is not None:
            params['last_knowledge_of_server'] = last_knowledge_of_server
        return await self._request(
            '/budgets/{}/months'.format(budget_id), 'GET', params)

    async def budget_month(self, budget_id: str, month: str) -> dict:
        """Returns a single budget month.

        Corresponds to the `/budgets/{budget_id}/months/{month}` endpoint.

        :param budget_id: The ID of the budget.
        :param month: The budget month in ISO format (e.g. 2016-12-01)
            ('current' can also be used to specify the current calendar month
            (UTC)).
        :returns: A dict for the requested budget month.
        """
        return await self._request(
            '/budgets/{}/months/{}'.format(budget_id, month), 'GET')

    async def transactions(
            self, budget_id: str, since_date: str = None, type: str = None,
            last_knowledge_of_server: int = None) -> dict:
        """Returns budget transactions.

        Corresponds to the `/budgets/{budget_id}/transactions` endpoint.

        :param budget_id: The ID of the budget.
        :param since_date: If specified, only transactions on or after this
            date will be included. The date should be ISO formatted
            (e.g. 2016-12-30).
        :param type: If specified, only transactions of the specified type will
            be included. 'uncategorized'and 'unapproved' are currently
            supported.
        :param last_knowledge_of_server: The starting server knowledge. If
            provided, only entities that have changed since
            last_knowledge_of_server will be included.
        :returns: A dict of all transactions for the budget.
        """
        params = {}
        if last_knowledge_of_server is not None:
            params['last_knowledge_of_server'] = last_knowledge_of_server
        if since_date is not None:
            params['since_date'] = since_date
        if type is not None:
            params['type'] = type
        return await self._request(
            '/budgets/{}/transactions'.format(budget_id), 'GET', params)

    async def create_transactions(
            self, budget_id: str, transaction: dict = None,
            transactions: List[dict] = None) -> dict:
        """Creates a single transaction or multiple transactions.

        One of transaction or transactions must be specified, but not both.
        Corresponds to the `/budgets/{budget_id}/transactions` endpoint.

        :param budget_id: The ID of the budget.
        :param transaction: The transaction to create.
        :param transactions: The list of transactions to create.
        :returns: A dict of the created transaction(s).
        :raises ValueError: If both transaction and transactions are provided or
            neither are provided.
        """
        if not transaction and not transactions:
            raise ValueError('Must specify one of transaction or transactions.')
        if transaction and transactions:
            raise ValueError('Only one of transaction or transactions can be '
                             'specified, not both.')

        if transaction is not None:
            data = {'transaction': transaction}
        elif transactions is not None:
            data = {'transactions': transactions}
        return await self._request(
            '/budgets/{}/transactions'.format(budget_id), 'POST', body=data)

    async def update_transactions(
            self, budget_id: str, transaction: dict = None,
            transactions: List[dict] = None) -> dict:
        """Updates multiple transactions, by 'id' or 'import_id'.

        One of transaction or transactions must be specified, but not both.
        Corresponds to the `/budgets/{budget_id}/transactions` endpoint.

        :param budget_id: The ID of the budget.
        :param transaction: The transaction to update.
        :param transactions: The list of transactions to updates.
        :returns: A dict of the updated transaction(s).
        :raises ValueError: If both transaction and transactions are provided or
            neither are provided.
        """
        if not transaction and not transactions:
            raise ValueError('Must specify one of transaction or transactions.')
        if transaction and transactions:
            raise ValueError('Only one of transaction or transactions can be '
                             'specified, not both.')

        if transaction is not None:
            data = {'transaction': transaction}
        elif transactions is not None:
            data = {'transactions': transactions}
        return await self._request(
            '/budgets/{}/transactions'.format(budget_id), 'PATCH', body=data)

    async def transaction(self, budget_id: str, transaction_id: str) -> dict:
        """Returns a single transaction.

        Corresponds to the `/budgets/{budget_id}/transactions/{transaction_id}`
        endpoint.

        :param budget_id: The ID of the budget.
        :param transaction_id: The ID of the transaction.
        :returns: A dict of the requested transaction.
        """
        return await self._request(
            '/budgets/{}/transactions/{}'.format(budget_id, transaction_id),
            'GET')

    async def update_transaction(
            self, budget_id: str, transaction_id: str, data: dict) -> dict:
        """Updates a single transaction.

        Corresponds to the `/budgets/{budget_id}/transactions/{transaction_id}`
        endpoint.

        :param budget_id: The ID of the budget.
        :param transaction_id: The ID of the transaction.
        :param data: A dict containing the fields/values to update.
        :returns: A dict of the updated transaction.
        """
        data = {'transaction': data}
        return await self._request(
            '/budgets/{}/transactions/{}'.format(budget_id, transaction_id),
            'PUT', body=data)

    async def account_transactions(
            self, budget_id: str, account_id: str, since_date: str = None,
            type: str = None, last_knowledge_of_server: int = None) -> dict:
        """Returns all transactions for a specified account.

        Corresponds to the
        `/budgets/{budget_id}/accounts/{account_id}/transactions` endpoint.

        :param budget_id: The ID of the budget.
        :param account_id: The ID of the account.
        :param since_date: If specified, only transactions on or after this
            date will be included. The date should be ISO formatted
            (e.g. 2016-12-30).
        :param type: If specified, only transactions of the specified type will
            be included. 'uncategorized'and 'unapproved' are currently
            supported.
        :param last_knowledge_of_server: The starting server knowledge. If
            provided, only entities that have changed since
            last_knowledge_of_server will be included.
        :returns: A dict of all transactions for the requested account.
        """
        params = {}
        if last_knowledge_of_server is not None:
            params['last_knowledge_of_server'] = last_knowledge_of_server
        if since_date is not None:
            params['since_date'] = since_date
        if type is not None:
            params['type'] = type
        return await self._request(
            '/budgets/{}/accounts/{}/transactions'.format(
                budget_id, account_id), 'GET', params)

    async def category_transactions(
            self, budget_id: str, category_id: str, since_date: str = None,
            type: str = None, last_knowledge_of_server: int = None) -> dict:
        """Returns all transactions for a specified category.

        Corresponds to the
        `/budgets/{budget_id}/categories/{category_id}/transactions` endpoint.

        :param budget_id: The ID of the budget.
        :param category_id: The ID of the category.
        :param since_date: If specified, only transactions on or after this
            date will be included. The date should be ISO formatted
            (e.g. 2016-12-30).
        :param type: If specified, only transactions of the specified type will
            be included. 'uncategorized'and 'unapproved' are currently
            supported.
        :param last_knowledge_of_server: The starting server knowledge. If
            provided, only entities that have changed since
            last_knowledge_of_server will be included.
        :returns: A dict of all transactions for the requested category.
        """
        params = {}
        if last_knowledge_of_server is not None:
            params['last_knowledge_of_server'] = last_knowledge_of_server
        if since_date is not None:
            params['since_date'] = since_date
        if type is not None:
            params['type'] = type
        return await self._request(
            '/budgets/{}/categories/{}/transactions'.format(
                budget_id, category_id), 'GET', params)

    async def payee_transactions(
            self, budget_id: str, payee_id: str, since_date: str = None,
            type: str = None, last_knowledge_of_server: int = None) -> dict:
        """Returns all transactions for a specified payee.

        Corresponds to the
        `/budgets/{budget_id}/payees/{payee_id}/transactions` endpoint.

        :param budget_id: The ID of the budget.
        :param payee_id: The ID of the payee.
        :param since_date: If specified, only transactions on or after this
            date will be included. The date should be ISO formatted
            (e.g. 2016-12-30).
        :param type: If specified, only transactions of the specified type will
            be included. 'uncategorized'and 'unapproved' are currently
            supported.
        :param last_knowledge_of_server: The starting server knowledge. If
            provided, only entities that have changed since
            last_knowledge_of_server will be included.
        :returns: A dict of all transactions for the requested payee.
        """
        params = {}
        if last_knowledge_of_server is not None:
            params['last_knowledge_of_server'] = last_knowledge_of_server
        if since_date is not None:
            params['since_date'] = since_date
        if type is not None:
            params['type'] = type
        return await self._request(
            '/budgets/{}/payees/{}/transactions'.format(
                budget_id, payee_id), 'GET', params)

    async def scheduled_transactions(self, budget_id: str) -> dict:
        """Returns all scheduled transactions.

        Corresponds to the `/budgets/{budget_id}/scheduled_transactions`
        endpoint.

        :param budget_id: The ID of the budget.
        :returns: A dict of all scheduled transactions.
        """
        return await self._request(
            '/budgets/{}/scheduled_transactions'.format(budget_id), 'GET')

    async def scheduled_transaction(
            self, budget_id: str, scheduled_transaction_id: str) -> dict:
        """Returns all scheduled transactions.

        Corresponds to the
        `/budgets/{budget_id}/scheduled_transactions/{scheduled_transaction_id}`
        endpoint.

        :param budget_id: The ID of the budget.
        :param scheduled_transaction_id: The ID of the scheduled transaction.
        :returns: A dict of all scheduled transactions.
        """
        return await self._request(
            '/budgets/{}/scheduled_transactions/{}'.format(
                budget_id, scheduled_transaction_id), 'GET')
