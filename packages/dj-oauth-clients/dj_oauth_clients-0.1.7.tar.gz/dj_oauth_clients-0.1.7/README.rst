=============================
Django Oauth2 Clients
=============================

.. image:: https://badge.fury.io/py/dj-oauth-clients.svg
    :target: https://badge.fury.io/py/dj-oauth-clients

.. image:: https://travis-ci.org/kverdecia/dj-oauth-clients.svg?branch=master
    :target: https://travis-ci.org/kverdecia/dj-oauth-clients

.. image:: https://codecov.io/gh/kverdecia/dj-oauth-clients/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/kverdecia/dj-oauth-clients

Django app for handling oauth2 clients.

Documentation
-------------

The full documentation is at https://dj-oauth-clients.readthedocs.io.

Quickstart
----------

Install Django Oauth2 Clients::

    pip install dj-oauth-clients

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'oauth_clients.apps.OauthClientsConfig',
        ...
    )

Add Django Oauth2 Clients's URL patterns:

.. code-block:: python

    from oauth_clients import urls as oauth_clients_urls


    urlpatterns = [
        ...
        url(r'^', include(oauth_clients_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
