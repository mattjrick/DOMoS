import logging

# The JSON payload that is sent to the webhook must be in the correct format for the webhook to be able to parse it.
# The JSON payload must contain the following fields and types
# {
#   "buildId": int,
#   "branchIdentifier": string,
#   "technologyTypes": list"
# }


# Create def to parse the JSON payload from the webhook, check correct types and return the values
def parseRequest(req):
    parsedValues = {}
    try:
        for key in ["repositoryId"]:
            if key in req:
                if isinstance(req[key], (str)):
                    parsedValues[key] = req[key]
                else:
                    logging.info(f"Incorrect type for {key} in request")
    except:
        raise ValueError(f"Request was not formatted correctly in request")
    logging.info(parsedValues)
    return parsedValues
