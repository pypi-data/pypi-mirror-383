# -*- coding: utf-8 -*-

"""
MS SQL Server CDC processor (placeholder for
future implementation).
"""

from abc import ABC

from core_cdc.processors.base import IProcessor


class MsSqlProcessor(IProcessor, ABC):  # pylint: disable=line-too-long
    """
    Change Data Capture (CDC) is a feature provided by Microsoft SQL Server to capture
    and track changes made to tables at the database level. It is designed to efficiently
    identify and record changes to data, making it a powerful tool for applications
    that require real-time or near-real-time data integration, synchronization,
    and auditing. Here are some key points
    about SQL Server Change Data Capture:

    1. **Purpose:**
       - **Data Integration:** CDC facilitates the integration of data between different systems and databases by capturing changes at the source.
       - **Synchronization:** It allows keeping multiple databases in sync by identifying and applying changes made to one database to another.
       - **Auditing:** CDC provides a reliable and efficient way to audit changes to data, tracking who made the change and when.

    2. **How it Works:**
       - CDC works by enabling change tracking on selected tables. When enabled, SQL Server maintains change tables to store the details of changes made to the tracked tables.
       - The change tables store information about INSERTs, UPDATEs, and DELETEs, including the columns affected and the corresponding values before and after the change.

    3. **Configuration:**
       - To use CDC, you need to enable it at the database level and then enable it for specific tables.
       - Enabling CDC involves creating the required system tables and stored procedures for change tracking.
       - Once enabled, SQL Server automatically populates change tables with the details of changes made to the tracked tables.

    4. **Querying Changes:**
       - After CDC is enabled, you can query the change tables to retrieve information about changes made to tracked tables.
       - The `cdc.fn_cdc_get_all_changes_<capture_instance>` function is commonly used to retrieve changes for a specific capture instance.

    5. **Retention Period:**
       - CDC allows you to specify a retention period for change data. After this period, older change data is automatically purged.

    6. **Integration with ETL and Replication:**
       - CDC is often used in conjunction with Extract, Transform, Load (ETL) processes to capture changes at the source and propagate them to a data warehouse or another database.
       - It is also integrated with SQL Server Replication to capture and replicate changes to other SQL Server instances.

    7. **Security Considerations:**
       - CDC respects SQL Server security settings, ensuring that only authorized users can access the change data.

    Here's a basic example of enabling CDC for a table:

    SQL Example::

        -- Enable CDC at the database level
        EXEC sys.sp_cdc_enable_db;

    SQL Example::

        -- Enable CDC for a specific table
        EXEC sys.sp_cdc_enable_table
          @source_schema = 'dbo',
          @source_name   = 'YourTableName',
          @role_name     = 'cdc_admin';

    Once CDC is enabled, you can query the change tables to retrieve
    information about the changes made to the tracked table. Keep in mind that
    using CDC introduces some overhead, and you should carefully consider the
    impact on performance and storage when enabling it. It's a powerful
    feature for scenarios requiring change tracking, but it may not be
    necessary for every application.
    """
