import json
import logging
import re
from . import devopshelpers
from . import storagehandler
from . import config


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
            # If the build reason is schedule then skip it
            if build["reason"] == "schedule":
                logging.info("Skipping a scheduled build")
                continue
            if build["status"] != "completed":
                logging.info("Skipping build where status is not completed")
                continue
            else:
                logging.info("Getting build info for build: " + build["buildNumber"])
                buildInfo.append(getBuild(build))
    except:
        raise ValueError("Error in request to get build info from azure devops")
    
    try:
        storagehandler.store_dicts_in_table(buildInfo)
        return buildInfo
    except Exception as e:
        raise ValueError("Error in storing build info in azure table:" + str(e))


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

    # Get the source branch from the build dictionary
    if build["reason"] == "pullRequest":
        sourceBranch = getSourceBranchFromPullRequest(build)
    else:
        sourceBranch = build["sourceBranch"]

    # Using the source branch, get the work item id and work item info
    workItemId, workItemInfo = getWorkItemInfoFromBuild(sourceBranch)

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
    try:
        parameters = build["parameters"]
        parametersFixed = re.sub(r"\\", "", parameters)
        parametersJson = json.loads(parametersFixed)
        return parametersJson["system.pullRequest.sourceBranch"]
    except:
        logging.info("Error in getting source branch from pull request")
        return ""


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
        if build["reason"] == "individualCI":
            return build["triggerInfo"]["ci.message"]
        else:
            return ""
    except:
        logging.info("Error in getting ciMessage")


def getWorkItemId(branchIdentifier):
    """
    Given a branch identifier, returns the work item ID associated with that branch.
    The work item ID is extracted from the branch identifier using a regular expression.

    Args:
        branchIdentifier (str): A string containing the branch identifier.

    Returns:
        str: A string containing the work item ID associated with the branch.
    """
    logging.info("Getting work item id from branch identifier")
    logging.info(branchIdentifier)
    projectIdentifier = config.project_identifier
    regex = r"(?<="+projectIdentifier+"-)([1-9]\d+)"
    backup_regex = r"[1-9]\d{0,4}"
    if re.search(regex, branchIdentifier):
        workItemId = re.findall(regex, branchIdentifier)
        logging.info("First regex matched: " + workItemId[0])
        return workItemId[0]
    elif re.search(backup_regex, branchIdentifier):
        workItemId = re.findall(backup_regex, branchIdentifier)
        logging.info("Second regex matched: " + workItemId[0])
        return workItemId[0]
    else:
        logging.info("Used both regexs and could not get work item id")
        return ""

def getWorkItemInfoFromBuild(sourceBranch):
    """
    Given a source branch, returns the work item ID and information associated with that work item.
    Args:
        build (dict): A dictionary containing information about the build.
        sourceBranch (str): A string containing the source branch.

    Returns:
        tuple: A tuple containing the work item ID and information associated with that work item.
    """

    workItemId = getWorkItemId(sourceBranch)
    if workItemId == "":
        logging.info("No work item id found")
        return "", {}
    else:
        workItemInfo = getWorkItemInfo(workItemId)
    return workItemId, workItemInfo


# Get details from azure devops based on JSON payload
def getDetails(dict):
    # Get buildId from parsedValues dict
    repositoryId = dict["repositoryId"]

    # Get build info from buildId
    buildInfo = getBuildInfo(repositoryId)
    logging.info(buildInfo)

    # Return finalDict as JSON
    return json.dumps(buildInfo)
