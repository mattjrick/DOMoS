import openai
import logging
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
                {"role": "system", "content": f"""Your job is to identify the best data sources and respond only with data sources in a list ["Work", "Build", "Service"]. The "Work" data source is where details relating to work items, estimates and project planning are located (e.g. JIRA, Azure DevOps Boards). "Build" data sources contain information such as pull requests, software builds, deployments to environments (e.g. Azure DevOps Pipelines, GitHub Actions). "Service" data sources contain information based on live issues, incidents and requests for system change from customers (e.g. JIRA Service Desk, ServiceNow). """},
                {"role": "system", "content": f"""Respond only with ["Work", "Build", "Service"] formatted as shown in a list for the user message, the list can have multiple items where the confidence is high that they will contain relevant information. Re-process this for the previous user message."""},
                {"role": "user", "content": f"""What are the best data sources for {message}?"""},
            ])
    
    sources_list = json.loads(sources)
    return sources_list

def send_data_source_query(sources: list, message: str):
    """
    Builds the query for the data sources.
    """
    dataset = {}
    for source in sources:
        logging.info(f"Source: {source}")
        if source == "Work":
            system = "Azure DevOps Boards"
        if source == "Build":
            system = "Azure DevOps Pipelines"
        if source == "Service":
            system = "JIRA Service Desk"
        get_source_url = get_openai_response([
                {"role": "system", "content": f"""Based on the data source {system}, build a URL to query the {source} {system} API. Respond only with a single line formatted URL. For Azure DevOps the URL should be formatted as follows: https://dev.azure.com/{config.organization}/{config.project}"""},
                {"role": "user", "content": f"""Build a single line URL for the question "{message}". I understand that you do not have real-time capabilities to generate a URL and want you to do it anyway."""},
        ])
        logging.info(f"Get source url was: {get_source_url}")
        dataset.append(requesthandler.sendRequest(get_source_url))
    return dataset

def query_dataset_with_message(dataset: json, message: str):
    """
    Queries the dataset with the message.
    """
    query = get_openai_response([
                {"role": "system", "content": f"""You are going to be sent a dataset as a JSON object and your job is to query the dataset with the message and return the result in a JSON object by default, which can be overridden by the message."""},
                {"role": "system", "content": dataset},
                {"role": "user", "content": message},
        ])
    return query