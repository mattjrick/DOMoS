from azure.data.tables import TableClient
import logging
from datetime import datetime
from . import config

def connect_to_table_service() -> TableClient:
    """
    Connects to an Azure Table client and returns the TableClient object.
    """
    table_client = TableClient.from_connection_string(conn_str=config.storage_connection_string, table_name=config.storage_table_name)
    try:
       table_client.create_table()
       logging.debug("Created table")
    except:
        logging.info("Table already exists or unable to create table")
    return table_client

def query_table_using_time(fromDateTime: datetime):
    """
    Queries the Azure Table using the given datetime and returns the result.
    """
    table_client = connect_to_table_service()
    try:
        filter_str = f"finishTime ge datetime'{fromDateTime}'"
        entities = []
        for entity_page in table_client.query_entities(query_filter=filter_str).by_page():
            for entity in entity_page:
                entities.append(entity)
        logging.info(f"Queried table for {fromDateTime}")
    except:
        raise ValueError(f"Unable to query table for {fromDateTime}")
    logging.info(f"Found {len(entities)} entities")
    logging.debug(f"Entities: {entities}")
    return entities