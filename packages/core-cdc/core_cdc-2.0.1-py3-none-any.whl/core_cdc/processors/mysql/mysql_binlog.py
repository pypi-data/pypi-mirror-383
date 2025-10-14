# -*- coding: utf-8 -*-

"""
MySQL BinLog processor for Change Data Capture
services.
"""

from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional

from core_db.engines.mysql import MySQLClient
from core_mixins.utils import to_one_line
from pymysqlreplication import BinLogStreamReader  # type: ignore[import-untyped]
from pymysqlreplication.event import GtidEvent  # type: ignore[import-untyped]
from pymysqlreplication.event import QueryEvent
from pymysqlreplication.event import RotateEvent
from pymysqlreplication.event import XidEvent
from pymysqlreplication.row_event import DeleteRowsEvent  # type: ignore[import-untyped]
from pymysqlreplication.row_event import UpdateRowsEvent
from pymysqlreplication.row_event import WriteRowsEvent

from core_cdc.base import Record, EventType
from core_cdc.processors.base import IProcessor


class MySqlBinlogProcessor(IProcessor):
    """
    It processes the events from the BinLog files.

    The binary log contains “events” that describe database changes such as table creation
    operations or changes to table data. It also contains events for statements that potentially
    could have made changes (for example, a DELETE which matched no rows), unless row-based
    logging is used. The binary log also contains information about how long each
    statement took that updated data.

    More information:
    https://dev.mysql.com/doc/refman/8.0/en/binary-log.html
    """

    def __init__(
        self,
        stream: BinLogStreamReader,
        connection_settings: Optional[Dict] = None,
        **kwargs,
    ) -> None:
        """
        https://python-mysql-replication.readthedocs.io/en/stable/binlogstream.html
        :param stream: BinLogStreamReader object.
        """

        super().__init__(**kwargs)
        self.stream = stream

        # To keep the tracking of the processed elements...
        self.log_file = None
        self.log_pos = None
        self.gtid = None
        self.xid = None

        # Keeping track of schemas in cause are not available within
        # the event.rows information...
        self._schema_cache: Dict[str, List[str]] = {}

        self.connection_settings = connection_settings

    def get_events(self) -> Iterator[Any]:
        for event in self.stream:
            self.logger.info(f"Received event: {event.__class__.__name__}.")
            self.log_file, self.log_pos = self.stream.log_file, self.stream.log_pos
            self.logger.info(f"File: {self.log_file}, Position: {self.log_pos}.")

            if isinstance(event, QueryEvent):
                query: str = to_one_line(event.query.lower())
                if query.count("alter table") and event.table_map:
                    # Table schema has changed, we must update `_schema_cache`...
                    entry = list(event.table_map.values())[0]

                    self._fetch_table_columns(
                        schema=entry.schema,
                        table=entry.table,
                    )

            yield event

            if self.log_pos is not None:
                self._update_log_pos(self.log_pos)

    def get_event_type(self, event: Any) -> EventType:
        if isinstance(event, QueryEvent):
            return EventType.DDL_STATEMENT

        if isinstance(event, WriteRowsEvent):
            return EventType.INSERT

        if isinstance(event, UpdateRowsEvent):
            return EventType.UPDATE

        if isinstance(event, DeleteRowsEvent):
            return EventType.DELETE

        return EventType.GLOBAL

    def process_event(self, event: Any, **kwargs):
        if isinstance(event, GtidEvent):
            self.gtid = event.gtid

        elif isinstance(event, XidEvent):
            self.xid = event.xid

        elif isinstance(event, RotateEvent):
            self.logger.info(f"NEXT FILE: {event.next_binlog}. POSITION: {event.position}.")
            self._update_log_file(event.next_binlog)
            self._update_log_pos(event.position)

    def process_dml_event(self, event: Any, **kwargs) -> List[Record]:
        metadata = {
            "global_id": self.gtid,
            "transaction_id": self.xid,
            "event_timestamp": event.timestamp,
            "event_type": "",
            "service": self.service,
            "source": self.log_file,
            "position": self.log_pos,
            "primary_key": event.primary_key,
            "schema_name": event.schema,
            "table_name": event.table
        }

        # Attribute that contains the rows...
        attr = "values"

        if isinstance(event, WriteRowsEvent):
            metadata["event_type"] = EventType.INSERT

        if isinstance(event, DeleteRowsEvent):
            metadata["event_type"] = EventType.DELETE

        if isinstance(event, UpdateRowsEvent):
            metadata["event_type"] = EventType.UPDATE
            attr = "after_values"

        # Handle case where event.rows might be None
        if not event.rows:
            return []

        return [
            Record(
                record=self._map_values_to_columns(
                    row.get(attr, {}),
                    event.schema,
                    event.table,
                ),
                **metadata,
            )
            for row in event.rows
        ]

    def _map_values_to_columns(
        self,
        values: Dict,
        schema: str,
        table: str,
    ) -> Dict:
        """
        Map UNKNOWN_COL* keys to actual column names.

        :param values: Dictionary with potentially UNKNOWN_COL keys
        :param schema: Database/schema name
        :param table: Table name
        :return: Dictionary with proper column names
        """

        keys = list(values.keys())
        if not any(str(k).startswith("UNKNOWN_COL") for k in keys):
            return values

        cache_key = f"{schema}.{table}"
        if cache_key in self._schema_cache:
            columns = self._schema_cache[cache_key]

        else:
            columns = self._fetch_table_columns(schema, table)

        if not columns:
            self.logger.warning(f"Could not map columns for `{schema}.{table}`.")
            return values

        mapped = {}
        for idx, col_name in enumerate(columns):
            unknown_key = f"UNKNOWN_COL{idx}"
            if unknown_key in values:
                mapped[col_name] = values[unknown_key]

            # Fallback: use positional mapping...
            elif idx < len(keys):
                mapped[col_name] = values[keys[idx]]

        return mapped

    def _fetch_table_columns(
        self,
        schema: str,
        table: str,
    ) -> List[str]:
        """
        Fetch column names from the database for a specific table.

        :param schema: Database/schema name
        :param table: Table name
        :return: List of column names in order
        """

        cache_key = f"{schema}.{table}"

        if not self.connection_settings:
            self.logger.warning(
                f"No connection_settings provided. Cannot fetch schema for {cache_key}"
            )
            return []

        try:
            with MySQLClient(**self.connection_settings) as client:
                query = """
                    SELECT COLUMN_NAME
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                    ORDER BY ORDINAL_POSITION"""

                client.execute(query, params=(schema, table))
                columns = [row[0] for row in client.fetch_all()]
                self.logger.info(f"Fetched {len(columns)} columns for {cache_key}: {columns}")
                self._schema_cache[cache_key] = columns
                return columns

        except Exception as error:
            self.logger.error(f"Failed to fetch columns for {cache_key}: {error}")
            return []

    def _update_log_file(self, log_file_name: str):
        """ It updates the log_file name """

    def _update_log_pos(self, position: int):
        """ It updates the log_file position """
