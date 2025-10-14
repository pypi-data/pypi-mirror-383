# -*- coding: utf-8 -*-

"""
Snowflake target implementation for CDC data
replication.
"""

import re
from typing import List

from core_db.engines.snowflake_ import SnowflakeClient
from pymysqlreplication.event import QueryEvent  # type: ignore[import-untyped]

from core_cdc.base import Record
from .base import ITarget


class SnowflakeTarget(ITarget):
    """
    Processor for synchronization with Snowflake. Below an
    example of how you could automatically send data
    to Snowflake or execute DDL statements.

    .. code-block:: python

        import logging
        import os
        from pprint import pprint
        from typing import Any
        from typing import List

        from core_mixins.logger import get_logger
        from pymysqlreplication import BinLogStreamReader

        from core_cdc.base import Record
        from core_cdc.processors.mysql import MySqlBinlogProcessor
        from core_cdc.targets.snowflake import SnowflakeTarget

        cxn_params = {
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "passwd": "mysql_password"
        }

        logger = get_logger(
            log_level=int(os.getenv("LOGGER_LEVEL", str(logging.INFO))),
            reset_handlers=True)

        class CustomMySqlBinlogProcessor(MySqlBinlogProcessor):
            def process_dml_event(self, event: Any, **kwargs) -> List[Record]:
                recs = super().process_dml_event(event, **kwargs)
                logger.info("The following records will be processed...")

                for rec in recs:
                    pprint(rec.to_json())
                return recs

        class CustomTarget(SnowflakeTarget):
            def _save(self, records: List[Record], **kwargs):
                logger.info(f"Saving: {records}")

                query, params = self.client.get_merge_dml(
                    target=records[0].table_name,
                    columns=list(records[0].record.keys()),
                    pk_ids=["id"],
                    records=[rec.record for rec in records]
                )

                print(query)
                self.execute(f"USE SCHEMA {records[0].schema_name}")
                self.client.execute(query, params=params)
                self.client.commit()

            def execute(self, query: str):
                self.client.execute(query)

        try:
            ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT", "")
            USER = os.getenv("SNOWFLAKE_USER", "")
            PASSWORD = os.getenv("SNOWFLAKE_PASSWORD", "")
            DATABASE = os.getenv("SNOWFLAKE_DATABASE", "")
            SCHEMA = os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC")
            WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", "")
            ROLE = os.getenv("SNOWFLAKE_ROLE", "")

            CONF = {
                "account": ACCOUNT,
                "user": USER,
                "password": PASSWORD,
                "database": DATABASE,
                "schema": SCHEMA,
                "warehouse": WAREHOUSE,
                "role": ROLE,
            }

            target = CustomTarget(logger=logger, execute_ddl=True, send_data=True)
            target.init_client(**CONF)
            target.client.connect()

            target.client.execute(f"USE {CONF['database']}")

            stream = BinLogStreamReader(
                resume_stream=False,
                connection_settings=cxn_params,
                blocking=True,
                freeze_schema=False,
                server_id=1)

            processor = CustomMySqlBinlogProcessor(
                stream=stream,
                targets=[target],
                connection_settings=cxn_params,
                service=os.getenv("SERVICE_NAME", "Functional-Tests"),
                logger=logger)

            processor.execute()

        except Exception as error:
            logger.error(f"An error has been raised. Error: {error}.")
    ..
    """

    def init_client(self, **kwargs) -> None:
        """
        Expecting: host, user, password, account, database, warehouse, schema, role.
        https://docs.snowflake.com/en/user-guide/python-connector-example.html
        """

        self.client = SnowflakeClient(**kwargs)

    def _save(self, records: List[Record], **kwargs):
        """
        We are not implementing the mechanism to persist the data directly
        into the data warehouse because we believe decoupling (by sending the
        data to SQS queue or SNS topic) is a better solution. But you
        could modify the behavior or inherit the class...
        """

    @staticmethod
    def get_create_schema_statement(event: QueryEvent) -> str:
        return f"CREATE SCHEMA IF NOT EXISTS {event.schema.decode()};"

    @staticmethod
    def get_create_table_statement(event: QueryEvent) -> str:
        return SnowflakeTarget.transform_create_table_query(event.query.lower())

    @staticmethod
    def transform_create_table_query(query: str) -> str:
        """ Transform a MySQL query to a Snowflake one """

        mapper = [
            (r"`", ""),
            (r"create table", "create table if not exists"),
            (r"unique index \w+ \(+\w+ \w+\) \w+", ""),

            (r"not null", ""),
            (r"null", ""),

            # Not necessary because it's a replication...
            (r" generated always as[.]*(.*?)\)", ""),
            (r"auto_increment", ""),
            (r"unsigned", ""),
            (r"zerofill", ""),

            # Updating types...
            (r" blob", " binary"),
            (r" varbinary[.]*(.*?)\)", " binary"),
            (r" year[.]*(.*?)\)", " varchar(4)"),
            (r" json", " object"),
            (r" enum[.]*(.*?)\)", " varchar"),
            (r" set[.]*(.*?)\)", " varchar"),

            # Removing unnecessary blank spaces...
            (r"[ ]{2,}", " "),

            # Removing \n...
            (r"[\n]*,", ","),

            # Removing unnecessary commas...
            (r",,", ","),
            (r",[\n]*\)", ")")
        ]

        for pattern, replacement in mapper:
            regex = re.compile(pattern, re.MULTILINE)
            query = re.sub(regex, replacement, query)

        return query
