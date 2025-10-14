core-cdc (CDC a.k.a Change Data Capture)
===============================================================================

It provides the core mechanism and required resources to 
implement "Change Data Capture" services...

===============================================================================


.. image:: https://img.shields.io/pypi/pyversions/core-cdc.svg
    :target: https://pypi.org/project/core-cdc/
    :alt: Python Versions

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://gitlab.com/bytecode-solutions/core/core-cdc/-/blob/main/LICENSE
    :alt: License

.. image:: https://gitlab.com/bytecode-solutions/core/core-cdc/badges/release/pipeline.svg
    :target: https://gitlab.com/bytecode-solutions/core/core-cdc/-/pipelines
    :alt: Pipeline Status

.. image:: https://readthedocs.org/projects/core-cdc/badge/?version=latest
    :target: https://readthedocs.org/projects/core-cdc/
    :alt: Docs Status

.. image:: https://img.shields.io/badge/security-bandit-yellow.svg
    :target: https://github.com/PyCQA/bandit
    :alt: Security

|

Execution Environment
---------------------------------------

Install libraries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    pip install --upgrade pip
    pip install virtualenv
..

Create the Python Virtual Environment.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    virtualenv --python={{python-version}} .venv
    virtualenv --python=python3.11 .venv
..

Activate the Virtual Environment.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    source .venv/bin/activate
..

Install required libraries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    pip install .
..

Optional libraries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    pip install '.[all]'  # For all...
    pip install '.[mysql]'
    pip install '.[mongo]'
    pip install '.[snowflake]'
..

Check tests and coverage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    python manager.py run-tests
    python manager.py run-tests --test-type integration
    python manager.py run-coverage

    # Having the docker containers up and running you can execute the functional
    # tests that ensure the CDC services are working as expected...
    python manager.py run-tests --test-type functional --pattern "*.py"
..

|

Engines
---------------------------------------

The following database engines have CDC implementations:

Fully Implemented
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**MySQL** - Binary Log (BinLog) based CDC
    - Uses ``mysql-replication`` library
    - Captures INSERT, UPDATE, DELETE operations
    - Supports DDL events (CREATE, ALTER, DROP)
    - Fallback mechanism for column name resolution
    - See: `core_cdc/processors/mysql/ <core_cdc/processors/mysql/>`_

**MongoDB** - Change Streams based CDC
    - Uses native MongoDB Change Streams
    - Captures INSERT, UPDATE, DELETE operations
    - Requires replica set configuration
    - Real-time event streaming
    - See: `core_cdc/processors/mongo/ <core_cdc/processors/mongo/>`_

In Development
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**MS SQL Server** - Abstract base class defined
    - See: `core_cdc/processors/mssql.py <core_cdc/processors/mssql.py>`_

**Oracle** - Abstract base class defined
    - See: `core_cdc/processors/oracle.py <core_cdc/processors/oracle.py>`_
