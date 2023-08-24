import openai
import logging
from datetime import datetime
from . import config
from . import requesthandler


def set_openai_api():
    """
    Sets the openai client with the api key and api type.
    """
    openai.api_key = config.openai_api_key
    openai.api_base = config.openai_api_base
    openai.api_type = "azure"
    openai.api_version = "2023-05-15"

import json

def get_openai_response(prompts: list):
    set_openai_api()
    deployment_name = config.openai_deployment_name

    try:
        response = openai.ChatCompletion.create(
            engine=deployment_name,
            messages=prompts)
        
        logging.info(f"OpenAI response: {response}")
        return response['choices'][0]['message']['content']
    except Exception as e:
        raise ValueError(f"Unable to get OpenAI response: {e}")
    
def get_data_sources(message: str):
    """
    Gets the data source list from OpenAI.
    """

    sources = get_openai_response([
                {"role": "system", "content": f"""Respond only with ["Work", "Build", "Service"] formatted as shown in a list for the user message, the list can have multiple items where the confidence is high that they will contain relevant information. Re-process this for the previous user message."""},
                {"role": "user", "content": f"""What are the best data sources for {message}?"""},
            ])
    
    sources_list = json.loads(sources)
    return sources_list

def send_data_source_query(sources: list, message: str):
    """
    Builds the query for the data sources.
    """
    dataset = []
    for source in sources:
        logging.info(f"Source: {source}")
        if source == "Work":
            system = "Azure DevOps Boards"
        if source == "Build":
            system = "Azure DevOps Pipelines"
            get_source_url = get_openai_response([
                    {"role": "system", "content": f"""You are tasked with building an API query to retrieve information that may contain answers to the user question. You should respond only in JSON format with the following fields: requestMethod, URL and a query if the requestMethod for the API is POST. Organization should be replaced with: {config.organization} and Project is: {config.project}.
                    Context:
                    - The user is asking for information that can be retrieved from {system}
                    - The date is {datetime.now().strftime("%Y-%m-%d")}
                    - The latest API version for Azure Devops is 7.0
                    - A date range can be set by using minTime=Y-M-D
                    """},
                    {"role": "user", "content": f"""{message}"""},
            ])
        if source == "Service":
            system = "JIRA Service Desk"
        logging.info(f"{get_source_url}")
        get_source_json = json.loads(get_source_url)
        # Handle when the query parameter does not exist in the get_source_json
        try:
            query = get_source_json['query']
        except:
            query = ""
        dataset.append(requesthandler.sendRequest(get_source_json['requestMethod'], get_source_json['URL'], query))
    return dataset

def query_dataset_with_message(dataset: json, message: str):
    """
    Queries the dataset with the message.
    """
    query = get_openai_response([
                {"role": "system", "content": f"""You are going to be sent a dataset as a JSON object and your job is to query the dataset with the message and return the result"""},
                {"role": "user", "content": dataset},
                {"role": "user", "content": message},
        ])
    return query