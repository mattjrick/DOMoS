import os
import requests
import logging
from . import config


# Send request to azure devops and return JSON payload


def sendRequest(url):
    # Get the azure devops personal access token from the environment variables
    token = os.environ["TOKEN"]
    # Create the authorization header for the request
    headers = {"Authorization": "Basic " + config.auth}
    logging.info(headers)
    # Send the request to azure devops and store the response
    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        raise ValueError(e)
    # Parse the response as JSON
    try:
        data = response.json()
    except:
        logging.info("Response not parseable: " + str(response.content))
        logging.info("Status code of response was: " + str(response.status_code))
        raise exit("Response from Azure DevOps was not in JSON format")
    # Return the response
    return data


# Construct URL for querying different azure devops APIs
def constructURL(apiType, id):
    # Friendly map of apiTypes
    apiTypes = {
        "pullRequest": {"apiPath": "git/pullRequests/" + id, "options": []},
        "workItem": {
            "apiPath": "wit/workItems/" + id,
            "options": ["&$expand=relations"],
        },
        "build": {
            "apiPath": "build/builds",
            "options": ["&repositoryId=" + id, "&repositoryType=TfsGit"],
        },
    }
    # Construct the base URL for azure devops metrics queries based on the apiTypes map
    url = (
        "https://dev.azure.com/"
        + os.environ["ORGANIZATION"]
        + "/"
        + os.environ["PROJECT"]
        + "/_apis/"
        + apiTypes[apiType]["apiPath"]
        + "?api-version=7.0"
        + "".join(apiTypes[apiType]["options"])
    )
    # Return the URL as string
    return url
