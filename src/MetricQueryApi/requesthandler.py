from datetime import datetime
import os
import requests
import logging
from . import config

# The JSON payload that is sent to the webhook must be in the correct format for the webhook to be able to parse it.
# The JSON payload must contain the following fields and types
# {
#   "message": string,
#   "fromDateTime": datetime,
# }


# Create def to parse the JSON payload, check correct types and return the values
def parse_request(req):
    parsedValues = {}
    try:
        for key in req.keys():
            if key in req:
                if isinstance(req[key], (str, datetime.fromisoformat)):
                    parsedValues[key] = req[key]
                else:
                    logging.info(f"Incorrect type for {key} in request")
    except:
        raise ValueError(f"Request was not formatted correctly")
    logging.info(parsedValues)
    return parsedValues

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
        raise exit("Response from endpoint was not in JSON format")
    # Return the response
    return data