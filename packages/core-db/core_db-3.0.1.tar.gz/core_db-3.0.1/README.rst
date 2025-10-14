core-db
===============================================================================

This project/library contains common elements related to database engines and 
provides clients to simplify the connections...

===============================================================================

.. image:: https://img.shields.io/pypi/pyversions/core-db.svg
    :target: https://pypi.org/project/core-db/
    :alt: Python Versions

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://gitlab.com/bytecode-solutions/core/core-db/-/blob/main/LICENSE
    :alt: License

.. image:: https://gitlab.com/bytecode-solutions/core/core-db/badges/release/pipeline.svg
    :target: https://gitlab.com/bytecode-solutions/core/core-db/-/pipelines
    :alt: Pipeline Status

.. image:: https://readthedocs.org/projects/core-db/badge/?version=latest
    :target: https://readthedocs.org/projects/core-db/
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

Install required libraries.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    pip install .
..

Optional libraries.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    pip install '.[all]'  # For all...
    pip install '.[mysql]'
    pip install '.[postgres]'
    pip install '.[oracle]'
    pip install '.[mongo]'
    pip install '.[mssql]'
    pip install '.[snowflake]'
    pip install '.[db2]'
..

Check tests and coverage.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    python manager.py run-tests
    python manager.py run-coverage
    python manager.py run-tests --test-type functional --pattern "*.py"  # To execute functional tests you must have ready the servers and the configurations.
..


Clients
---------------------------------------

Postgres
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from core_db.engines.postgres import PostgresClient

    with PostgresClient(conninfo=f"postgresql://postgres:postgres@localhost:5432/test") as client:
        client.execute("SELECT version() AS version;")
        print(client.fetch_one()[0])
..

Mongo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from core_db.engines.mongo import MongoClient

    client = MongoClient(**{"host": "host", "database": "db"})
    client.connect()
    print(client.test_connection())
..

MsSql
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from core_db.engines.mssql import MsSqlClient

    with MsSqlClient(
            dsn="DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=master;UID=SA;PWD=sOm3str0ngP@33w0rd;Encrypt=no",
            autocommit=True, timeout=5) as client:

        client.execute("SELECT @@VERSION AS 'version';")
        print(list(client.fetch_records()))
..

Oracle
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from core_db.engines.oracle import OracleClient

    with OracleClient(user="...", password="...", dsn=f"{host}:{port}/{service_name}") as client:
        res = client.execute("SELECT * FROM ...")
        for x in client.fetch_all():
            print(x)
..

MySQL
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from core_db.engines.mysql import MySQLClient

    with MySQLClient(host="localhost", user="root", password="SomePassword") as client:
        client.execute("SELECT * FROM ...;")
        for x in client.fetch_all():
            print(x)
..

IBM DB2
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from core_db.engines.db2 import Db2Client

    dsn_hostname, dsn_port, dsn_database = "localhost", "50000", "sample"
    dsn_uid, dsn_pwd = "db2inst1", "SomePassword"

    dsn = (
        f"DATABASE={dsn_database};"
        f"HOSTNAME={dsn_hostname};"
        f"PORT={dsn_port};"
        f"PROTOCOL=TCPIP;"
        f"UID={dsn_uid};"
        f"PWD={dsn_pwd};"
    )

    with Db2Client(dsn=dsn, user="", password="") as client:
        client.execute("select * from department FETCH FIRST 2 ROWS ONLY;")
        print(client.fetch_one())
        print(client.fetch_record())
..

Snowflake
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from core_db.engines.snowflake_ import SnowflakeClient

    config = {
        "user": "username",
        "password": "password",
        "account": "account_name",
        "warehouse": "warehouse_name",
        "database": "database_name",
        "schema": "schema_name"
    }

    with SnowflakeClient(**config) as client:
        client.execute("SELECT CURRENT_VERSION();")
        print(client.fetch_one())
..

Testing Clients Locally
---------------------------------------

We can test the clients locally by executing the below commands that are required to install
dependencies, run Docker containers and perform a series of query execution in the database engine
to ensure it's working as expected.

PostgreSQL
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    docker run \
      --env=POSTGRES_PASSWORD=postgres \
      --env=PGDATA=/var/lib/postgresql/data \
      --volume=/var/lib/postgresql/data \
      -p 5432:5432 -d postgres:12.18-bullseye
..

MySQL
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    docker run \
      --env=MYSQL_ROOT_PASSWORD=mysql_password \
      --volume=/var/lib/mysql \
      -p 3306:3306 \
      --restart=no \
      --runtime=runc \
      -d mysql:latest
..

Oracle
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    docker pull container-registry.oracle.com/database/express:latest
    docker container create -it --name OracleSQL -p 1521:1521 -e ORACLE_PWD=oracle_password container-registry.oracle.com/database/express:latest
    docker start OracleSQL
..

.. image:: ./assets/OracleCxn.png
    :alt: How to connect to Oracle

MsSQL
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    docker pull mcr.microsoft.com/mssql/server:2022-latest

    docker run\
      -e "ACCEPT_EULA=Y" \
      -e "MSSQL_SA_PASSWORD=sOm3str0ngP@33w0rd" \
      -p 1433:1433 --name MsSQL --hostname MsSQL \
      -d mcr.microsoft.com/mssql/server:2022-latest

    docker start MsSQL
    sudo /bin/bash ./scripts/install_mssql_driver.sh
..

DB2
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Driver Installation - Debian-based and Ubuntu-based Distributions
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

More information: https://ibmi-oss-docs.readthedocs.io/en/latest/odbc/installation.html

.. code-block:: shell

    curl https://public.dhe.ibm.com/software/ibmi/products/odbc/debs/dists/1.1.0/ibmi-acs-1.1.0.list | sudo tee /etc/apt/sources.list.d/ibmi-acs-1.1.0.list
    sudo apt update
    sudo apt install ibm-iaccess
..

Create environment file ``.env_db2``:

.. code-block:: text

    LICENSE=accept
    DB2INSTANCE=db2inst1
    DB2INST1_PASSWORD=SomePassword
    DBNAME=sample
    BLU=false
    ENABLE_ORACLE_COMPATIBILITY=false
    UPDATEAVAIL=NO
    TO_CREATE_SAMPLEDB=false
    REPODB=false
    IS_OSXFS=false
    PERSISTENT_HOME=true
    HADR_ENABLED=false
    ETCD_ENDPOINT=
    ETCD_USERNAME=
    ETCD_PASSWORD=
..

Run DB2 container:

.. code-block:: shell

    docker pull icr.io/db2_community/db2

    docker run \
      -h db2server \
      --name db2server \
      --restart=always \
      --detach \
      --privileged=true \
      -p 50000:50000 \
      --env-file .env_db2 \
      --shm-size=4g \
      icr.io/db2_community/db2
..

Create sample database:

.. code-block:: shell

    docker exec -ti db2server bash -c "su - db2inst1"
    db2sampl -force -sql
..

**Note:** DB2 databases can take several minutes to fully start up and be ready to accept connections.

Expected output:

.. code-block:: text

    [db2inst1@db2server ~]$ db2sampl -force -sql
      Creating database "SAMPLE"...
      Connecting to database "SAMPLE"...
      Creating tables and data in schema "DB2INST1"...
      'db2sampl' processing complete.
..

Alternative DB2 setup:

.. code-block:: shell

    docker run \
      -d --name=db2 \
      --privileged=true \
      -e DB2INST1_PASSWORD=SomePassword \
      -e LICENSE=accept \
      -p 50000:50000 ibmcom/db2
..

MongoDB
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, let's create a local cluster to test the example using Docker:

.. code-block:: shell

    docker network create mongoCluster
    docker run -d --rm -p 27017:27017 --name mongo1 --network mongoCluster mongo:5 mongod --replSet myReplicaSet --bind_ip localhost,mongo1
    docker run -d --rm -p 27018:27017 --name mongo2 --network mongoCluster mongo:5 mongod --replSet myReplicaSet --bind_ip localhost,mongo2
    docker run -d --rm -p 27019:27017 --name mongo3 --network mongoCluster mongo:5 mongod --replSet myReplicaSet --bind_ip localhost,mongo3

    docker exec -it mongo1 mongosh --eval "rs.initiate({
     _id: \"myReplicaSet\",
     members: [
       {_id: 0, host: \"mongo1\"},
       {_id: 1, host: \"mongo2\"},
       {_id: 2, host: \"mongo3\"}
     ]
    })"
..

Check the cluster status:

.. code-block:: shell

    docker ps
    docker exec -it mongo1 mongosh --eval "rs.status()"
..
