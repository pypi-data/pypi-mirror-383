# -*- coding: utf-8 -*-

"""
MongoDB Change Streams processor for Change Data Capture
services.
"""

from abc import abstractmethod
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List

from bson.objectid import ObjectId
from bson.timestamp import Timestamp
from pymongo.change_stream import ChangeStream
from pymongo.errors import ConnectionFailure
from pymongo.errors import CursorNotFound
from pymongo.errors import OperationFailure
from pymongo.errors import PyMongoError

from core_cdc.base import Record, EventType
from core_cdc.processors.base import IProcessor


class MongoDbStreamProcessor(IProcessor):
    """
    It processes the events from the MongoDB Stream.

    A change stream is a real-time stream of database changes that flows from your
    database to your application. With change streams, your applications can react—in real
    time—to data changes in a single collection, a database, or even an entire
    deployment. For apps that rely on notifications of changing data, change
    streams are critical.

    More information:
    https://www.mongodb.com/basics/change-streams
    """

    def __init__(
        self,
        stream: ChangeStream,
        save_full_event: bool = True,
        **kwargs,
    ) -> None:
        """
        :param stream: DatabaseChangeStream object.
        :param save_full_event: If True, all the event will be streamed,
            otherwise only fullDocument.

        To create a stream you can use:
            * db.collection.watch()
            * db.watch()

        Example:
            pipeline = [
                {'$match': {'operationType': 'insert'}},
                {'$match': {'operationType': 'replace'}}
            ]
            MongoDbStreamProcessor(
                stream = MongoClient(...)["database"].<collection>.watch(pipeline)
            )

        Resume Token Storage:
            Subclasses must implement save_resume_token() to persist resume tokens.
            This enables stream recovery after interruptions or application restarts.

            Common storage patterns:
              * File-based: Simple JSON file storage
              * Database: Store in relational or NoSQL database
              * Redis/Cache: Fast in-memory storage with persistence
              * Cloud storage: S3, GCS, Azure Blob for distributed systems

            Example implementation:
                class MyProcessor(MongoDbStreamProcessor):
                    def save_resume_token(self, token):
                        # File-based storage
                        with open('resume_token.json', 'w') as f:
                            json.dump(token, f)

        More information...
          * https://www.mongodb.com/basics/change-streams
          * https://www.mongodb.com/docs/manual/changeStreams/#open-a-change-stream
          * https://www.mongodb.com/docs/manual/reference/method/db.watch/#db.watch--
        """

        super().__init__(**kwargs)
        self.save_full_event = save_full_event
        self.stream = stream

    def _validate_event(self, event: Dict) -> bool:
        """
        Validates that a MongoDB change stream event has all required fields.

        Required fields for all events:
        - _id: Resume token
        - operationType: Type of operation
        - ns: Namespace (db and collection)
        - clusterTime: Timestamp of the operation

        :param event: MongoDB change stream event
        :return: True if valid, False otherwise
        """
        required_fields = ["_id", "operationType", "ns", "clusterTime"]

        for field in required_fields:
            if field not in event:
                self.logger.error(
                    f"Invalid event: missing required field '{field}'. "
                    f"Event: {event}"
                )
                return False

        # Validate ns structure (must have 'db' and 'coll' for collection operations)
        ns = event.get("ns")
        if not isinstance(ns, dict):
            self.logger.error(
                f"Invalid event: 'ns' must be a dict. "
                f"Got: {type(ns).__name__}. Event: {event}"
            )
            return False

        # For collection-level operations, ns must have db and coll
        operation_type = event.get("operationType")
        if operation_type not in ("dropDatabase", "invalidate"):
            if "db" not in ns or "coll" not in ns:
                self.logger.error(
                    f"Invalid event: 'ns' missing 'db' or 'coll' for operation '{operation_type}'. "
                    f"Event: {event}"
                )
                return False

        # Validate documentKey exists for document-level operations
        if operation_type in ("insert", "update", "replace", "delete"):
            if "documentKey" not in event:
                self.logger.error(
                    f"Invalid event: '{operation_type}' operation missing 'documentKey'. "
                    f"Event: {event}"
                )
                return False

        return True

    def get_events(self) -> Iterator[Any]:
        """
        Iterates through MongoDB change stream events with error handling.

        Handles common MongoDB errors:
        - ConnectionFailure: Network issues, auto-reconnect attempts
        - CursorNotFound: Cursor expired (common in long-running streams)
        - OperationFailure: Server-side errors (permissions, invalid operations)
        - PyMongoError: Catch-all for other PyMongo exceptions

        :yields: Change stream events
        :raises: Re-raises exceptions after logging for caller to handle
        """
        try:
            for event in self.stream:
                try:
                    # Validate event structure before processing
                    if not self._validate_event(event):
                        self.logger.warning(
                            f"Skipping invalid event due to validation failure. "
                            f"Operation: {event.get('operationType', 'unknown')}, "
                            f"Resume token: {event.get('_id', 'N/A')}"
                        )
                        continue

                    # Extract event details for logging
                    op_type = event.get('operationType')
                    ns = event.get('ns', {})
                    db_name = ns.get('db', 'unknown')
                    coll_name = ns.get('coll', 'unknown')
                    doc_id = event.get('documentKey', {}).get('_id', 'N/A')

                    # Info-level logging for received events
                    self.logger.info(
                        f"Received event: {op_type} on {db_name}.{coll_name}, "
                        f"document: {doc_id}"
                    )

                    # Debug-level: Log full event structure for troubleshooting
                    self.logger.debug(f"Full event data: {event}")

                    # Debug-level: Log transaction info if present
                    if event.get("lsid") and event.get("txnNumber"):
                        self.logger.debug(
                            f"Event is part of transaction: "
                            f"lsid={event['lsid']}, txnNumber={event['txnNumber']}"
                        )

                    cluster_time = event.get("clusterTime")
                    if isinstance(cluster_time, Timestamp):
                        event["clusterTime"] = cluster_time.time
                    else:
                        event["clusterTime"] = None

                    # Debug-level: Log timestamp conversion
                    self.logger.debug(
                        f"Event timestamp: clusterTime={event['clusterTime']}, "
                        f"wallTime={event.get('wallTime', 'N/A')}"
                    )

                    yield event

                    # Save resume token for recovery
                    resume_token = event["_id"]
                    self.save_resume_token(resume_token)
                    self.logger.debug(f"Resume token saved: {resume_token}")

                except (KeyError, AttributeError, TypeError) as error:
                    # Handle malformed event data with detailed context
                    self.logger.error(
                        f"Malformed event data encountered: {error}. "
                        f"Operation: {event.get('operationType', 'unknown')}, "
                        f"Namespace: {event.get('ns', 'N/A')}, "
                        f"Resume token: {event.get('_id', 'N/A')}. "
                        f"Skipping event.",
                        exc_info=True
                    )
                    continue

        except ConnectionFailure as error:
            # Network issues, connection lost, auto-reconnect failed
            self.logger.error(
                f"Connection to MongoDB failed: {error}. "
                f"Check network connectivity and MongoDB server status."
            )
            raise

        except CursorNotFound as error:
            # Cursor expired (change stream idle too long)
            self.logger.error(
                f"Change stream cursor not found: {error}. "
                f"The cursor may have expired. Use resume tokens to continue from last position."
            )
            raise

        except OperationFailure as error:
            # Server-side operation errors (permissions, invalid query, etc.)
            self.logger.error(
                f"MongoDB operation failed: {error}. "
                f"Check permissions and change stream configuration."
            )
            raise

        except PyMongoError as error:
            # Catch-all for other PyMongo errors
            self.logger.error(f"PyMongo error while reading change stream: {error}")
            raise

        except Exception as error:
            # Unexpected errors
            self.logger.error(f"Unexpected error in change stream: {error}", exc_info=True)
            raise

    def get_event_type(self, event: Dict) -> EventType:
        """
        Maps MongoDB change stream operation types to CDC EventType.

        DML Operations (Data Manipulation):
        - insert -> INSERT
        - replace, update -> UPDATE
        - delete -> DELETE

        DDL Operations (Data Definition):
        - drop, dropDatabase, rename -> DDL_STATEMENT
        - create, createIndexes, dropIndexes, modify -> DDL_STATEMENT
        - shardCollection, refineCollectionShardKey, reshardCollection -> DDL_STATEMENT

        Special Operations:
        - invalidate -> GLOBAL (stream invalidated, requires restart)
        - Other unknown operations -> GLOBAL

        :param event: MongoDB change stream event
        :return: Corresponding EventType
        """
        opt_type = event.get("operationType")

        # DML Operations
        if opt_type == "insert":
            return EventType.INSERT

        if opt_type in ("replace", "update"):
            return EventType.UPDATE

        if opt_type == "delete":
            return EventType.DELETE

        # DDL Operations
        if opt_type in (
            "drop",           # Collection dropped
            "dropDatabase",   # Database dropped
            "rename",         # Collection renamed
            "create",         # Collection created (4.2+)
            "createIndexes",  # Indexes created (4.2+)
            "dropIndexes",    # Indexes dropped (4.2+)
            "modify",         # Collection modified (4.2+)
            "shardCollection",              # Collection sharded (4.4+)
            "refineCollectionShardKey",     # Shard key refined (4.4+)
            "reshardCollection",            # Collection resharded (5.0+)
        ):
            self.logger.info(f"DDL operation detected: {opt_type}")
            return EventType.DDL_STATEMENT

        # Special Operations
        if opt_type == "invalidate":
            # Invalidate closes the stream - requires restart with startAfter
            self.logger.warning(
                "Invalidate event received. Change stream is now invalid. "
                "This typically occurs after drop, dropDatabase, or rename operations. "
                "Use startAfter (not resumeAfter) to restart the stream."
            )
            return EventType.GLOBAL

        # Unknown/Future Operations
        self.logger.warning(f"Unknown operation type: {opt_type}. Treating as GLOBAL event.")
        return EventType.GLOBAL

    def process_dml_event(self, event: Any, **kwargs) -> List[Record]:
        event_type = self.get_event_type(event)

        self.logger.debug(f"Processing DML event of type: {event_type}")

        # Extract transaction metadata if present
        # lsid (logical session ID) + txnNumber uniquely identify a transaction
        transaction_id = None
        if event.get("lsid") and event.get("txnNumber"):
            # Combine lsid and txnNumber to create unique transaction identifier
            lsid_id = event["lsid"].get("id") if isinstance(event["lsid"], dict) else event["lsid"]
            transaction_id = f"{lsid_id}:{event['txnNumber']}"
            self.logger.debug(f"Event belongs to transaction: {transaction_id}")

        # Use wallTime (MongoDB 6.0+) as preferred timestamp, fallback to clusterTime
        # wallTime is a DateTime value, clusterTime is already converted to Unix timestamp
        event_timestamp = event.get("clusterTime")  # Already converted in get_events()
        if event.get("wallTime"):
            # wallTime is a datetime object, convert to Unix timestamp
            wall_time = event["wallTime"]
            if hasattr(wall_time, "timestamp"):
                event_timestamp = int(wall_time.timestamp())
            self.logger.debug(f"Using wallTime for event timestamp: {event_timestamp}")

        metadata = {
            "global_id": None,
            "transaction_id": transaction_id,
            "event_timestamp": event_timestamp,
            "event_type": event_type,
            "service": self.service,
            "source": None,
            "position": 0,
            "primary_key": "_id",
            "schema_name": event["ns"]["db"],
            "table_name": event["ns"]["coll"]
        }

        self.logger.debug(
            f"Event metadata: db={metadata['schema_name']}, "
            f"table={metadata['table_name']}, timestamp={metadata['event_timestamp']}"
        )

        # Safely convert documentKey._id to string if it's an ObjectId
        if event.get("documentKey") and "_id" in event["documentKey"]:
            doc_key_id = event["documentKey"]["_id"]
            if isinstance(doc_key_id, ObjectId):
                self.logger.debug(
                    f"Converting documentKey._id from ObjectId "
                    f"to string: {doc_key_id}."
                )

                event["documentKey"]["_id"] = str(doc_key_id)

        # Safely convert fullDocument._id to string if it's an ObjectId
        if event.get("fullDocument") and "_id" in event["fullDocument"]:
            full_doc_id = event["fullDocument"]["_id"]
            if isinstance(full_doc_id, ObjectId):
                self.logger.debug(
                    f"Converting fullDocument._id from ObjectId "
                    f"to string: {full_doc_id}."
                )

                event["fullDocument"]["_id"] = str(full_doc_id)

        # Log warning if UPDATE operation is missing fullDocument
        if event_type == EventType.UPDATE and not event.get("fullDocument"):
            doc_id = event.get("documentKey", {}).get("_id", "unknown")
            # Also log updateDescription if available
            update_desc = event.get("updateDescription", {})
            updated_fields = update_desc.get("updatedFields", {})
            removed_fields = update_desc.get("removedFields", [])

            self.logger.warning(
                f"UPDATE event for document {doc_id} missing fullDocument. "
                f"UpdateDescription: {len(updated_fields)} fields updated, "
                f"{len(removed_fields)} fields removed. "
                f"Consider enabling 'full_document=\"updateLookup\"' in watch() options "
                f"to include complete documents in UPDATE events."
            )

            # Debug: Log actual field changes
            if updated_fields or removed_fields:
                self.logger.debug(
                    f"Field changes - Updated: {list(updated_fields.keys())}, "
                    f"Removed: {removed_fields}"
                )

        # Debug: Log final record size
        record_data = event if self.save_full_event else event.get("fullDocument", {})
        self.logger.debug(f"Creating record with {len(record_data)} top-level fields")

        return [
            Record(
                record=record_data,
                **metadata
            )
        ]

    @abstractmethod
    def save_resume_token(self, token):
        """
        It stores the token that can be used to resume the
        process in a certain point. Subclasses must implement this
        method to provide their own storage mechanism (e.g., file,
        database, cache, etc.).

        :param token: The resume token from MongoDB change stream (_id field).
        """
