# -*- coding: utf-8 -*-

"""
Base target interface for CDC data replication.
"""

from __future__ import annotations

import re
from abc import ABC
from abc import abstractmethod
from logging import Logger
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple

from core_mixins.interfaces.factory import IFactory
from core_mixins.utils import to_one_line
from pymysqlreplication.event import QueryEvent  # type: ignore[import-untyped]

from core_cdc.base import Record


class ITarget(IFactory, ABC):
    """
    This is the base class for the specific implementations of
    the targets the data will be sent or replicated. A target could
    be a database, queue, topic, data warehouse, etc...
    """

    def __init__(
        self,
        logger: Logger,
        execute_ddl: bool = False,
        send_data: bool = False,
        **kwargs,
    ) -> None:
        self.client: Optional[Any] = None
        self.execute_ddl = execute_ddl
        self.send_data = send_data
        self.logger = logger

    @classmethod
    def registration_key(cls) -> str:
        """Return the registration key for this target class."""
        return cls.__name__

    def init_client(self, **kwargs) -> None:
        """ The target's implementations must implement this method """

    def connect(self) -> None:
        """Connect to the target client if available."""
        if self.client:
            self.client.connect()

    def get_ddl_query(self, event: QueryEvent) -> str:
        """
        Each engine could use a different query for DDL operations...
        :return: The query or None if not supported.
        """

        # sql_statement = sub(r"/\*.*?\*/", "", event.query.lower()).strip()
        sql_statement = to_one_line(event.query.lower())

        if sql_statement.count("create schema") or sql_statement.count("create database"):
            return self.get_create_schema_statement(event)

        if sql_statement.count("drop schema") or sql_statement.count("drop database"):
            return self.get_drop_schema_statement(event)

        if sql_statement.count("create table"):
            return self.get_create_table_statement(event)

        if sql_statement.count("alter table"):
            return self.get_alter_table_statement(event)

        if sql_statement.count("drop table"):
            return self.get_drop_table_statement(event)

        return sql_statement

    @staticmethod
    def get_add_column_ddl(schema: str, table: str, column: str, type_: str) -> str:
        """ Returns the DDL to add a new column """
        return f"ALTER TABLE `{schema}`.`{table}` ADD COLUMN `{column}` {type_};"

    @staticmethod
    def get_create_schema_statement(event: QueryEvent) -> str:
        """Get the DDL statement for creating a schema."""
        return event.query

    @staticmethod
    def get_drop_schema_statement(event: QueryEvent) -> str:
        """Get the DDL statement for dropping a schema."""
        return event.query

    @staticmethod
    def get_create_table_statement(event: QueryEvent) -> str:
        """Get the DDL statement for creating a table."""
        return event.query

    @staticmethod
    def get_alter_table_statement(event: QueryEvent) -> str:
        """Get the DDL statement for altering a table."""
        return event.query

    @staticmethod
    def get_schema_table_from_query(query: str) -> Tuple[str, str]:
        """ Returns schema, table from query using Regex """

        # TODO if the query does not contains "`" this will not work...
        match = re.compile("`[a-z_]+`.`[a-z_]+`").search(query)
        if match is None:
            raise ValueError(f"Could not extract schema and table from query: {query}")

        data = match.group(0)
        schema, table = data.replace("`", "").split(".")
        return schema, table

    @staticmethod
    def get_drop_table_statement(event: QueryEvent) -> str:
        """Get the DDL statement for dropping a table."""
        return event.query

    def execute(self, query: str):
        """Execute a query using the target client."""
        if self.client:
            self.client.execute(query)

    def save(self, records: List[Record], **kwargs):
        """Save records to the target if send_data is enabled."""

        if self.send_data:
            self._save(records, **kwargs)
            self.logger.info(f"{len(records)} records were sent to: {self.registration_key()}!")

    @abstractmethod
    def _save(self, records: List[Record], **kwargs):
        """ Specific implementation to store the data into the Engine """

    def close(self):
        """ Implement it if is required to release or close resources """
