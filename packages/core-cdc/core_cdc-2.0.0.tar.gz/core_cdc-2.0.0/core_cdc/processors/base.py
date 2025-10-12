# -*- coding: utf-8 -*-

"""
Base processor interface for CDC (Change Data Capture) 
implementations. This module defines the IProcessor abstract 
base class that all CDC processors must implement, along 
with common CRUD event types.
"""

from abc import abstractmethod
from logging import Logger
from typing import Any
from typing import Iterable
from typing import Iterator
from typing import List

from core_mixins.interfaces.factory import IFactory

from core_cdc.base import EventType, Record
from core_cdc.targets.base import ITarget

CRUD_EVENTS = (
    EventType.INSERT,
    EventType.UPDATE,
    EventType.DELETE,
)


class IProcessor(IFactory):
    """ Interface for all "Change Data Capture" implementations """

    def __init__(
        self,
        service: str,
        targets: List[ITarget],
        logger: Logger,
        events_to_stream: Iterable[EventType] = CRUD_EVENTS,
        add_event_timestamp: bool = False,
    ) -> None:
        """
        :param service: The name of the service that is doing the CDC process.
        :param events_to_stream: By default, insert, update and, delete operations will be streamed.
        :param logger: Logger used.

        :param add_event_timestamp:
            If True, the column event_timestamp will be added when a table is created. The column
            could be useful for UPSERT or MERGE operations.
        """

        self.service = service
        self.targets = targets
        self.events_to_stream = events_to_stream
        self.add_event_timestamp = add_event_timestamp
        self.logger = logger

    @classmethod
    def registration_key(cls) -> str:
        return cls.__name__

    def execute(self):
        """
        Execute the CDC processor to read and process
        events from the stream. This method processes DDL
        and DML events, forwarding them to
        configured targets.
        """

        self.logger.info("Reading events from the stream...")

        for event in self.get_events():
            event_type = self.get_event_type(event)

            if event_type == EventType.DDL_STATEMENT:
                for target in self.targets:
                    key = target.registration_key()
                    if target.execute_ddl:
                        try:
                            query = target.get_ddl_query(event)
                            target.execute(query)
                            self.logger.info(f"The below query was executed in: {key}.")
                            self.logger.info(query)

                            if self.add_event_timestamp:
                                if query.lower().count("create table"):
                                    schema, table = ITarget.get_schema_table_from_query(query)

                                    target.execute(
                                        target.get_add_column_ddl(
                                            schema=schema, table=table,
                                            column="event_timestamp",
                                            type_="bigint"
                                        )
                                    )

                        except Exception as error:
                            self.logger.error(f"[{key}] -- {error}")

            elif event_type in self.events_to_stream:
                for target in self.targets:
                    key = target.registration_key()
                    try:
                        records = self.process_dml_event(event)
                        target.save(records)

                        self.logger.info({
                            "target": key,
                            "number_of_records": len(records),
                            "event_type": event_type,
                            "schema": records[0].schema_name,
                            "table": records[0].table_name
                        })

                    except Exception as error:
                        self.logger.error(f"[{key}] -- {error}")

            else:
                try:
                    self.process_event(event)

                except Exception as error:
                    self.logger.error(f"Error: {error}")

    @abstractmethod
    def get_events(self) -> Iterator[Any]:
        """ It returns an iterator with the events to process """

    @abstractmethod
    def get_event_type(self, event: Any) -> EventType:
        """ It returns the event type """

    @abstractmethod
    def process_dml_event(self, event: Any, **kwargs) -> List[Record]:
        """ It processes the event and return the records to stream """

    def process_event(self, event: Any):
        """
        It should be implemented if another event (apart from DDL
        and DML) must be processed...
        """
