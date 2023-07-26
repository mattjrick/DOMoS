import json
import logging
import re
from . import devopshelpers
from . import regexs
from . import storagehandler
from . import config


def getPullRequestInfo(pullRequestId):
    """
    Get the pull request info from azure devops based on pull request id

    Args:
    pullRequestId (int): The ID of the pull request

    Returns:
    dict: The JSON payload containing the pull request info
    """
    # Construct URL for querying azure devops pull request API
    url = devopshelpers.constructURL("pullRequest", pullRequestId)

    # Send request to azure devops and return JSON payload
    response = devopshelpers.sendRequest(url)

    # Return the response
    return response


def getBuildInfo(repositoryId):
    """
    Get the build info from azure devops based on repository id

    Args:
    repositoryId (int): The ID of the repository

    Returns:
    list: A list of dictionaries containing the build info
    """
    # Construct URL for querying azure devops build API
    url = devopshelpers.constructURL("build", repositoryId)
    logging.info(url)

    # Send request to azure devops and return JSON payload
    response = devopshelpers.sendRequest(url)

    # Loop through the response and get the build info
    try:
        # Declare the list to store build info
        buildInfo = []

        # Iterate through the response and append the build info to the list
        for build in response["value"]:
            buildInfo.append(getBuild(build))
    except:
        raise ValueError("Error in request to get build info from azure devops")
    
    try:
        storagehandler.store_dicts_in_table(buildInfo)
        return buildInfo
    except Exception as e:
        raise ValueError("Error in storing build info in azure table:" + str(e))


def getSourceBranchFromPullRequest(build):
    """
    Get the source branch from the pull request build

    Args:
    build (dict): The build dictionary

    Returns:
    str: The source branch of the pull request
    """
    parameters = build["parameters"]
    parametersFixed = re.sub(r"\\", "", parameters)
    parametersJson = json.loads(parametersFixed)
    return parametersJson["system.pullRequest.sourceBranch"]


def getCiMessageFromBuild(build):
    """
    Get the CI message from the build

    Args:
    build (dict): The build dictionary

    Returns:
    str: The CI message of the build
    """
    try:
        if build["reason"] == "pullRequest":
            return build["sourceVersion"]
        else:
            return build["triggerInfo"]["ci.message"]
    except:
        logging.debug("Error in getting ciMessage")


def getWorkItemInfoFromBuild(build, sourceBranch):
    """
    Get the work item info from the build

    Args:
    build (dict): The build dictionary
    sourceBranch (str): The source branch of the build

    Returns:
    tuple: A tuple containing the work item ID and the work item info dictionary
    """
    try:
        if build["reason"] == "individualCI":
            workItemIdentifier = build["triggerInfo"]["ci.message"]
        else:
            workItemIdentifier = sourceBranch
        workItemId = regexs.getWorkItemId(workItemIdentifier)
        workItemInfo = getWorkItemInfo(workItemId)
        return workItemId, workItemInfo
    except:
        workItemId = ""
        workItemInfo = {}
        raise ValueError("Could not find work item id in branch identifier")


def getWorkItemInfo(workItemId):
    """
    Get the work item info from azure devops based on work item id

    Args:
    workItemId (int): The ID of the work item

    Returns:
    dict: The JSON payload containing the work item info
    """
    # Construct URL for querying azure devops work item API
    url = devopshelpers.constructURL("workItem", workItemId)

    # Send request to azure devops and return JSON payload
    response = devopshelpers.sendRequest(url)

    if "System.Parent" in response["fields"]:
        parentWorkItemId = response["fields"]["System.Parent"]
        parentWorkItemTitle = response["fields"]["System.Title"]
    else:
        parentWorkItemId = None
        parentWorkItemTitle = None
    try:
        workItemInfo = {
            "title": response["fields"]["System.Title"],
            "workItemType": response["fields"]["System.WorkItemType"],
            "parentWorkItemId": parentWorkItemId,
            "parentWorkItemTitle": parentWorkItemTitle,
        }
        logging.info(workItemInfo)
    except:
        raise ValueError("Error in request to get work item info from azure devops")
    return workItemInfo


def getBuild(build):
    """
    Get the build info from the build dictionary

    Args:
    build (dict): The build dictionary

    Returns:
    dict: A dictionary containing the build info
    """
    if build["reason"] == "pullRequest":
        sourceBranch = getSourceBranchFromPullRequest(build)
    else:
        sourceBranch = build["sourceBranch"]

    workItemId, workItemInfo = getWorkItemInfoFromBuild(build, sourceBranch)

    ciMessage = getCiMessageFromBuild(build)

    return {
        "PartitionKey": build["repository"]["name"],
        "RowKey": build["buildNumber"],
        "sourceBranch": sourceBranch,
        "pipelineName": build["definition"]["name"],
        "repositoryId": build["repository"]["id"],
        "result": build["result"],
        "queueTime": build["queueTime"],
        "startTime": build["startTime"],
        "finishTime": build["finishTime"],
        "buildReason": build["reason"],
        "ciMessage": ciMessage,
        "requestedFor": build["requestedFor"]["displayName"],
        "workItemId": workItemId,
        **workItemInfo,
    }


def getSourceBranchFromPullRequest(build):
    """
    Given a build dictionary, returns the source branch associated with the pull request.
    The source branch is extracted from the build's parameters dictionary.

    Args:
        build (dict): A dictionary containing information about the build.

    Returns:
        str: A string containing the source branch associated with the pull request.
    """
    parameters = build["parameters"]
    parametersFixed = re.sub(r"\\", "", parameters)
    parametersJson = json.loads(parametersFixed)
    return parametersJson["system.pullRequest.sourceBranch"]


def getCiMessageFromBuild(build):
    """
    Given a build dictionary, returns the CI message associated with that build.
    If the build reason is "pullRequest", the source version is returned.
    Otherwise, the CI message is taken from the build's triggerInfo.

    Args:
        build (dict): A dictionary containing information about the build.

    Returns:
        str: A string containing the CI message associated with the build.
    """
    try:
        if build["reason"] == "pullRequest":
            return build["sourceVersion"]
        else:
            return build["triggerInfo"]["ci.message"]
    except:
        logging.debug("Error in getting ciMessage")

# Create def regular expression to get work item id from branch identifier
def getWorkItemId(branchIdentifier):
    # Create regular expression to get work item id from branch identifier e.g. dspp-1234-branch-name
    logging.info("Getting work item id from branch identifier")
    logging.info(branchIdentifier)
    projectIdentifier = config.project_identifier
    regex = r"(?<="+projectIdentifier+"-)(\d+)"
    # If search is true, return the work item id
    if re.search(regex, branchIdentifier):
        # Get the work item id from the branch identifier
        workItemId = re.findall(regex, branchIdentifier)
        logging.info("First regex matched: " + workItemId[0])
        # Return the work item id
        return workItemId[0]
    else:
        logging.info("Used both regexs and could not get work item id")
        # Return an error 400 if the work item id cannot be found
        raise ValueError("Could not find work item id in branch identifier")

def getWorkItemInfoFromBuild(build, sourceBranch):
    """
    Given a build and a source branch, returns the work item ID and information associated with that work item.
    If the build reason is "individualCI", the work item identifier is taken from the build's triggerInfo.
    Otherwise, the work item identifier is taken from the source branch.
    Args:
        build (dict): A dictionary containing information about the build.
        sourceBranch (str): A string containing the source branch.

    Returns:
        tuple: A tuple containing the work item ID and information associated with that work item.

    Raises:
        ValueError: If the work item ID cannot be found in the branch identifier.
    """
    try:
        if build["reason"] == "individualCI":
            workItemIdentifier = build["triggerInfo"]["ci.message"]
        else:
            workItemIdentifier = sourceBranch
        workItemId = getWorkItemId(workItemIdentifier)
        workItemInfo = getWorkItemInfo(workItemId)
        return workItemId, workItemInfo
    except:
        workItemId = ""
        workItemInfo = {}
        raise ValueError("Could not find work item id in branch identifier")


def getWorkItemInfo(workItemId):
    # Construct URL for querying azure devops work item API
    url = devopshelpers.constructURL("workItem", workItemId)

    # Send request to azure devops and return JSON payload
    response = devopshelpers.sendRequest(url)

    if "System.Parent" in response["fields"]:
        parentWorkItemId = response["fields"]["System.Parent"]
        parentWorkItemTitle = response["fields"]["System.Title"]
    else:
        parentWorkItemId = None
        parentWorkItemTitle = None
    try:
        workItemInfo = {
            "title": response["fields"]["System.Title"],
            "workItemType": response["fields"]["System.WorkItemType"],
            "parentWorkItemId": parentWorkItemId,
            "parentWorkItemTitle": parentWorkItemTitle,
        }
        logging.info(workItemInfo)
    except:
        raise ValueError("Error in request to get work item info from azure devops")
    return workItemInfo


# Get details from azure devops based on JSON payload
def getDetails(dict):
    # Get buildId from parsedValues dict
    repositoryId = dict["repositoryId"]

    # Get build info from buildId
    buildInfo = getBuildInfo(repositoryId)
    logging.info(buildInfo)

    # Return finalDict as JSON
    return json.dumps(buildInfo)
