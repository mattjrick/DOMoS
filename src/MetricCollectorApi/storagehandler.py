from azure.data.tables import TableClient
import logging
from . import config

def connect_to_table_service() -> TableClient:
    """
    Connects to an Azure Table  client and returns the TableClient object.
    """
    table_client = TableClient.from_connection_string(conn_str=config.storage_connection_string, table_name=config.storage_table_name)
    try:
       table_client.create_table()
       logging.debug("Created table")
    except:
        logging.info("Table already exists or unable to create table")
    return table_client

def store_dicts_in_table(data_list: list):
    """
    Stores a list of dictionaries in an Azure Table using batch operations.
    """
    table_client = connect_to_table_service()
    operations = []
    for i, data in enumerate(data_list):
        operation = ('upsert', data)
        operations.append(operation)
        if (i+1) % 99 == 0 or (i+1) == len(data_list):
            try:
                table_client.submit_transaction(operations)
                operations = []
            except Exception as e:
                logging.info(operations)                
                logging.info(str(e))

