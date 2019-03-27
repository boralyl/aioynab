aioynab
=======
|build| |docs|

YNAB_ API client implemented using python 3 asyncio.

Install
-------

aioynab can easily be installed using pip:

.. code-block:: bash

    $ pip install aioynab

Quick Start
-----------

.. code-block:: python

    import asyncio

    from aioynab.client import Client


    loop = asyncio.get_event_loop()
    client = Client('ynab-api-key')
    budgets = loop.run_until_complete(client.budgets()))
    budget_id = budgets['budgets'][0]['budget_id']
    accounts = loop.run_until_complete(client.accounts(budget_id))
    account_id = accounts['accounts'][0]['account_id']
    transactions = loop.run_until_complete(client.account_transactions(budget_id, account_id))


.. _ynab: https://api.youneedabudget.com/

.. |build| image:: https://api.travis-ci.com/boralyl/aioynab.svg?branch=master
    :alt: Build Status
    :scale: 100%
    :target: https://travis-ci.org/boralyl/aioynab

.. |docs| image:: https://readthedocs.org/projects/aioynab/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://aioynab.readthedocs.io/en/latest/?badge=latest
