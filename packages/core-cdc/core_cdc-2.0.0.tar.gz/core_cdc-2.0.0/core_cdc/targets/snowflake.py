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
    """ Processor for synchronization with Snowflake """

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
        return f"CREATE IF NOT EXIST SCHEMA {event.schema.decode()};"

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
            (r"[ ]{2,}", ""),

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
