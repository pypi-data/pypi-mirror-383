# -*- coding: utf-8 -*-

"""
MySQL target implementation for CDC data
replication.
"""

from typing import List

from core_db.engines.mysql import MySQLClient

from core_cdc.base import Record
from .base import ITarget


class MySQLTarget(ITarget):
    """
    This is the processor for synchronization with another MySQL instance. This capability
    is provided because even if the replication process is done outside this service
    is required to apply the DDL statements to keep the structure up to date...
    """

    def init_client(self, **kwargs) -> None:
        """
        Expecting at least: host, user, password, database
        More information: https://pymysql.readthedocs.io/en/latest/user/index.html
        """

        self.client = MySQLClient(**kwargs)

    def _save(self, records: List[Record], **kwargs):
        """
        We are not implementing the mechanism to persist the data directly
        into the database because we believe decoupling (by sending the
        data to SQS queue or SNS topic) is a better solution. But you
        could modify the behavior or inherit the class...

        Possible solutions:
          * self.client.get_insert_dml(...)
          * self.client.get_merge_dml(...)
        """
