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

    # Identify the data sources needed to query
    try:
        sources = openaihandler.get_data_sources(parsedValues["message"])
    except Exception as e:
        return func.HttpResponse(str(e), status_code=400)
    
    # Send queries for the data sources
    try:
        dataset = openaihandler.send_data_source_query(sources, parsedValues["message"])
    except Exception as e:
        return func.HttpResponse(str(e), status_code=400)

    #TODO: Normalise / rationalisation of the data sources

    # Query the data sources
    #try:
    #    response = openaihandler.query_dataset_with_message(dataset, message=parsedValues["message"])
    #except Exception as e:
    #    return func.HttpResponse(str(e), status_code=400)


    return func.HttpResponse(str(dataset), status_code=200)
