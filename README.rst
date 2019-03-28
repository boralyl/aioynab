aioynab
=======
|build| |docs| |codecov|

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

Documentation
-------------

Consult the docs_ for further information.

.. _ynab: https://api.youneedabudget.com/

.. _docs: https://aioynab.readthedocs.io/en/latest/?badge=latest

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
