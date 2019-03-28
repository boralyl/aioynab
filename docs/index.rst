aioynab
=======
|pypi| |pythonversions| |docs| |build| |codecov|

YNAB_ API client implemented using python 3 asyncio.

Install
-------

aioynab can easily be installed using pip:

.. code-block:: bash

    $ pip install aioynab

Quick Start
-----------

First create a personal access token in your `YNAB account <https://app.youneedabudget.com/settings/developer>`_.
Create a client with that value like the example below.

.. code-block:: python

    import asyncio

    from aioynab.client import Client


    loop = asyncio.get_event_loop()
    client = Client('ynab-personal-access-token')
    budgets = loop.run_until_complete(client.budgets()))
    budget_id = budgets['budgets'][0]['budget_id']
    accounts = loop.run_until_complete(client.accounts(budget_id))
    account_id = accounts['accounts'][0]['account_id']
    transactions = loop.run_until_complete(client.account_transactions(budget_id, account_id))


Return Values
-------------

The return values from all client functions return the value of the `data` key
of the YNAB response.  For example, the following YNAB response from the `/user`
endpoint:

.. code-block:: json

    {
      "data": {
        "user": {
          "id": "1a2f3f4e-5c01-4678-8134-c11e278fa111"
          }
        }
    }

Would result in the following return value when calling the `user` method:

.. code-block:: python

    >>> client = Client('access-token')
    >>> client.user()
    {'user': {'id': '1a2f3f4e-5c01-4678-8134-c11e278fa111'}}


Consult the `YNAB API endpoint documentation <https://api.youneedabudget.com/v1>`_
for the schema of the response for each endpoint that the client interacts with.

Module Documentation
--------------------

.. automodule:: aioynab.client
    :members:
    :private-members:
    :show-inheritance:

.. include:: ../CHANGELOG.rst

.. _ynab: https://api.youneedabudget.com/

.. |build| image:: https://api.travis-ci.com/boralyl/aioynab.svg?branch=master
    :alt: Build Status
    :scale: 100%
    :target: https://travis-ci.org/boralyl/aioynab

.. |docs| image:: https://readthedocs.org/projects/aioynab/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://aioynab.readthedocs.io/en/latest/?badge=latest

.. |codecov| image:: https://codecov.io/gh/boralyl/aioynab/branch/master/graph/badge.svg
    :alt: Code Coverage
    :scale: 100%
    :target: https://codecov.io/gh/boralyl/aioynab

.. |pypi| image:: https://badge.fury.io/py/aioynab.svg
    :alt: Pypi
    :scale: 100%
    :target: https://pypi.org/project/aioynab/

.. |pythonversions| image:: https://img.shields.io/pypi/pyversions/aioynab.svg
    :alt: Python Versions
    :scale: 100%
    :target: https://pypi.org/project/aioynab/
