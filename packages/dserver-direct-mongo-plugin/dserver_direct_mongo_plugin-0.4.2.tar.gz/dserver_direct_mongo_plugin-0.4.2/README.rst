dserver Direct Mongo Plugin
===========================

.. |dtool| image:: https://github.com/livMatS/dserver-direct-mongo-plugin/blob/main/icons/22x22/dtool_logo.png?raw=True
    :height: 20px
    :target: https://github.com/livMatS/dserver-direct-mongo-plugin
.. |pypi| image:: https://img.shields.io/pypi/v/dserver-notification-plugin
    :target: https://pypi.org/project/dserver-direct-mongo-plugin/
.. |tag| image:: https://img.shields.io/github/v/tag/livMatS/dserver-direct-mongo-plugin
    :target: https://github.com/livMatS/dserver-direct-mongo-plugin/tags
.. |test| image:: https://img.shields.io/github/actions/workflow/status/livMatS/dserver-direct-mongo-plugin/test.yml?branch=main&label=tests
    :target: https://github.com/livMatS/dserver-direct-mongo-plugin/actions/workflows/test.yml
.. |zenodo| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.12701908.svg
    :target: https://doi.org/10.5281/zenodo.12701908

|dtool| |pypi| |tag| |test| |zenodo|

- GitHub: https://github.com/livMatS/dserver-direct-mongo-plugin
- PyPI: https://pypi.org/project/dserver-direct-mongo-plugin/
- Free software: MIT License


Features
--------

- Query datasets via mongo language
- Funnel datasets through aggregation pipelines


Introduction
------------

`dtool <https://dtool.readthedocs.io>`_ is a command line tool for packaging
data and metadata into a dataset. A dtool dataset manages data and metadata
without the need for a central database.

However, if one has to manage more than a hundred datasets it can be helpful
to have the datasets' metadata stored in a central server to enable one to
quickly find datasets of interest.

The `dservercore <https://github.com/jic-dtool/dservercore>`_
provides a web API for registering datasets' metadata
and provides functionality to lookup, list and search for datasets.

This plugin allows to submit plain mongo queries and aggregation pipelines
directly to the lookup server.


Configuration
-------------

Inform this plugin about the Mongo database to use by setting the environment
variables

.. code-block:: bash

    export DSERVER_MONGO_URI="mongodb://localhost:27017/"
    export DSERVER_MONGO_DB="dserver"
    export DSERVER_MONGO_COLLECTION="metadata"

If the Mongo search and retrieve plugins are used, then you may use the same
database, but must use a different collection.

Use

.. code-block:: bash

    export DSERVER_ALLOW_DIRECT_QUERY=true
    export DSERVER_ALLOW_DIRECT_AGGREGATION=false

to enable or disable direct mongo query and aggregation on this plugin.

ATTENTION: While direct queries respect user-wise access rights to database
entries on the lookup server level, there is no guarantee for aggregation
pipelines to do so per design. Don not enable direct aggregation in a production
environment.

Authentication
--------------

The dtool lookup server makes use of the authorized header to pass through the
JSON web token for authorization. Below we create environment variables for the
token and the header used in the following ``curl`` command samples

.. code-block:: console

    $ TOKEN=$(flask user token test-user)
    $ HEADER="Authorization: Bearer $TOKEN"

Refer to the core dcumentation of `dservercore <https://github.com/jic-dtool/dservercore>`_ for more information.

Direct query
------------

To look for a sepcific field ``key2: 42`` in a dataset's README.yml (provided
the file is properly YAML-formatted), use

.. code-block:: console

    $ curl -H "$HEADER" -H "Content-Type: application/json" -X POST \
        -d '{"query": {"readme.key2": 42}}' http://localhost:5000/mongo/query

Response content:

.. code-block:: JSON

    [
      {
        "base_uri": "s3://test-bucket",
        "created_at": 1683797360.056,
        "creator_username": "jotelha",
        "dtoolcore_version": "3.18.2",
        "frozen_at": 1683797362.855,
        "name": "test_dataset_2",
        "number_of_items": 1,
        "size_in_bytes": 19347,
        "tags": [],
        "type": "dataset",
        "uri": "s3://test-bucket/26785c2a-e8f8-46bf-82a1-cec92dbdf28f",
        "uuid": "26785c2a-e8f8-46bf-82a1-cec92dbdf28f"
      }
    ]

Next to the content of the ``README.yml``, other fields of the database-internal
dataset representation returned in the example above are directly queryable as
well. All queries are formulated in the MongoDB language.
The `MongoDB documenatation <https://www.mongodb.com/docs/manual/introduction/>`_
offers information on how to formulate queries. The
`list of available query operators <https://www.mongodb.com/docs/manual/reference/operator/query/>`_
is particularly useful. The following illustrates a few other possible
JSON-like query documents.

``'{"base_uri":{"$regex":"^s3"}}'`` will find all datasets whose base URI
matches the provided regular expression, here any ``s3``-prefixed string.

``{"readme.owners.name": {"$regex": "Testing User"}}`` will match any dataset
with a README field that contains the sub string ``Testing User``, such as

.. code-block:: YAML

    owners:
    - name: A user who does not match the search pattern
      username: test_user
    - name: Another Testing User matches the search pattern
      username: another_test_user


The query

.. code-block:: JSON

    {
      "creator_username": "jotelha",
      "readme.parameters.temperature": 298
    }

will match all datasets created by user ``jotelha`` and annotated with:

.. code-block:: YAML

    parameters:
      temperature: 298

in its ``README.yml``.


Direct aggregation
------------------

The following example of an aggregation pipeline identifies
and counts instances of the same dataset at different base URIs:

.. code-block:: console

    $ curl -H "$HEADER" -H "Content-Type: application/json" -X POST \
        -d '{"aggregation": [
                {
                    "$sort": {"base_uri": 1}
                }, {
                    "$group":  {
                        "_id": "$name",
                        "count": {"$sum": 1},
                        "available_at": {"$push": "$base_uri"}
                    }
                }, {
                    "$project": {
                        "name": "$_id",
                        "count": true,
                        "available_at": true,
                        "_id": false
                    }
                }, {
                    "$sort": {"name": 1}
                }
            ]
        }' http://localhost:5000/mongo/aggregate

Response content:

.. code-block:: JSON

    [
      {
        "available_at": [
          "s3://test-bucket"
        ],
        "count": 1,
        "name": "test_dataset_1"
      },
      {
        "available_at": [
          "s3://test-bucket",
          "smb://test-share"
        ],
        "count": 2,
        "name": "test_dataset_2"
      }
    ]


Testing
-------

Running unit tests with ``pytest`` requires a healthy lookup server installation
and the availability of required services such as databases. Please refer to
the core
`dservercore <https://github.com/jic-dtool/dservercore>`_
for setup instructions.
