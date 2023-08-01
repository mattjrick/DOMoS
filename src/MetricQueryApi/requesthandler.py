from datetime import datetime
import logging

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
