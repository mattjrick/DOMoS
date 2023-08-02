import openai
import logging
from . import config


def set_openai_api():
    """
    Sets the openai client with the api key and api type.
    """
    openai.api_key = config.openai_api_key
    openai.api_base = config.openai_api_base
    openai.api_type = "azure"
    openai.api_version = "2023-05-15"

import json

def get_openai_response(data: list, message: str):
    set_openai_api()
    deployment_name = config.openai_deployment_name

    try:
        response = openai.ChatCompletion.create(
            engine=deployment_name,
            messages=[
                {"role": "system", "content": "You are going to be sent a subset of build data as a JSON formatted list from Azure DevOps pipelines, the user will be expecting you to answer questions about this data."},
                {"role": "system", "content": json.dumps(data)},
                {"role": "user", "content": message},
            ])
        
        logging.info(f"OpenAI response: {response}")
        return response['choices'][0]['message']['content']
    except Exception as e:
        raise ValueError(f"Unable to get OpenAI response: {e}")