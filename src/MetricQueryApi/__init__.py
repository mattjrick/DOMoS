import azure.functions as func
from . import requesthandler
from . import storagehandler
from . import openaihandler


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function entry point. Parses the incoming HTTP request and returns a response.

    Args:
        req (func.HttpRequest): The incoming HTTP request with a JSON body.

    Returns:
        func.HttpResponse: If the request is invalid, returns a 400 response. Otherwise, returns a 200 response with body content.
    """

    # Get the request and validate it against request handler returning 400 if incorrect
    try:
        parsedValues = requesthandler.parse_request(req.get_json())
    except Exception as e:
        return func.HttpResponse(str(e), status_code=400)

    # Try to query the table using the requested timerange
    try:
        data = storagehandler.query_table_using_time(parsedValues["fromDateTime"])
    except Exception as e:
        return func.HttpResponse(str(e), status_code=400)
    
    try:
        response = openaihandler.get_openai_response(data, parsedValues["message"])
    except Exception as e:
        return func.HttpResponse(str(e), status_code=400)


    return func.HttpResponse(response, status_code=200)
