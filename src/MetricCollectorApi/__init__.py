import azure.functions as func
from . import devopshandler
from . import requesthandler
import logging


def main(req: func.HttpRequest) -> func.HttpResponse:
    # Get the JSON body of the request sent to func
    try:
        req = req.get_json()
    except Exception as e:
        return func.HttpResponse(str(e), status_code=400)
    # Pass the request to request handler to parse the JSON payload
    try:
        parsedValues = requesthandler.parseRequest(req)
    except Exception as e:
        return func.HttpResponse(str(e), status_code=400)
    # Pass the parsed values to devops handler to get more details from azure devops
    try:
        response = devopshandler.getDetails(parsedValues)
    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)
    return func.HttpResponse(response)
