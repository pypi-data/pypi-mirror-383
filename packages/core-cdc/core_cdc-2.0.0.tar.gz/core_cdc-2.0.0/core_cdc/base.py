# -*- coding: utf-8 -*-

"""
Base classes and types for CDC (Change Data Capture) 
operations. This module defines the core EventType enum 
and Record class used across all CDC processors to 
represent database change events.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Dict
from typing import Optional
from typing import Tuple

from core_mixins.compatibility import StrEnum


class EventType(StrEnum):
    """Enumeration of CDC event types."""

    GLOBAL = "GLOBAL"        # Event related to the processor itself.
    DDL_STATEMENT = "QUERY"  # Event for DDL statement (like create table, etc.).
    INSERT = "INSERT"        # Event for DML INSERT operation.
    UPDATE = "UPDATE"        # Event for DML UPDATE operation.
    DELETE = "DELETE"        # Event for DML DELETE operation.


class Record:
    """
    It provides a wrapper or common object useful for integration
    across services that needs to handle data replication
    via Change Data Capture producers and consumers...
    """

    def __init__(
        self,
        event_timestamp: int,
        event_type: EventType,
        record: Dict, service: str,
        source: str,
        position: int,
        primary_key: Tuple | str,
        schema_name: str,
        table_name: str,
        global_id: Optional[str],
        transaction_id: Optional[str],
    ) -> None:
        """
        It creates a new record with all the attributes required for streaming and
        replication using a Data Change Capture service...

        :param: global_id:
            Unique identifier. (like: Global Transaction Identifier 
            (gtid) in MySQL engine).
        
        :param: transaction_id: Identifier for the transaction. (like: xid in MySQL engine).
        :param event_timestamp: Timestamp when the record was generated.
        :param event_type: It specifies the operation that generated the event.
        :param record: The record (like a record/row in a database).

        :param service: The service from where the record came.
        :param source: The source from where the record was retrieved (like binlog file name).
        :param position: Record position in the source.

        :param: primary_key: Attributes to use to identify a record as unique.
        :param: schema_name: Schema from where the record was retrieved.
        :param: table: Table from where the record was retrieved.
        """

        self.global_id = global_id
        self.transaction_id = transaction_id

        self.event_timestamp = event_timestamp
        self.event_type = event_type
        self.record = record

        self.service = service
        self.source = source
        self.position = position

        self.primary_key = primary_key
        self.schema_name = schema_name
        self.table_name = table_name

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self) -> Dict:
        """
        It returns the JSON version of the record required to be streamed...

        :return: A dictionary that follows the below structure:

            Example::

                {
                    "global_id": "",
                    "transaction_id": "",
                    "event_timestamp": 1653685384,
                    "event_type": "INSERT | UPDATE | DELETE",
                    "service": "service-name",
                    "source": "binlog.000001 | FileName | Something",
                    "position": 8077,
                    "primary_key": "(str | tuple)",
                    "schema_name": "schema_name",
                    "table_name": "table_name",
                    "record": {
                        ...
                        // This is an example...
                        "id": "000-1",
                        "category": "Marketing",
                        "price": 100.0,
                        ...
                    }
                }
        """

        return {
            "global_id": self.global_id,
            "transaction_id": self.transaction_id,
            "event_timestamp": self.event_timestamp,
            "event_type": self.event_type.value,
            "service": self.service,
            "source": self.source,
            "position": self.position,
            "primary_key": self.primary_key,
            "schema_name": self.schema_name,
            "table_name": self.table_name,
            "record": {
                key: value.isoformat() if type(value) in (datetime, date) else value
                for key, value in self.record.items()
            }
        }
