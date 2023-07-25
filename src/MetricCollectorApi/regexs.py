import re
import logging


# Create def regular expression to get work item id from branch identifier
def getWorkItemId(branchIdentifier):
    # Create regular expression to get work item id from branch identifier e.g. dspp-1234-branch-name
    logging.info("Getting work item id from branch identifier")
    logging.info(branchIdentifier)
    regex = r"(?<=dspp-)(\d+)"
    backup_regex = r"\d{4}"
    # If search is true, return the work item id
    if re.search(regex, branchIdentifier):
        # Get the work item id from the branch identifier
        workItemId = re.findall(regex, branchIdentifier)
        logging.info("First regex matched: " + workItemId[0])
        # Return the work item id
        return workItemId[0]
    elif re.search(backup_regex, branchIdentifier):
        # Get the work item id from the branch identifier
        workItemId = re.findall(backup_regex, branchIdentifier)
        logging.info("Second regex matched: " + workItemId[0])
        # Return the work item id
        logging.info("Using backup regex to get work item id")
        return workItemId[0]
    else:
        logging.info("Used both regexs and could not get work item id")
        # Return an error 400 if the work item id cannot be found
        raise ValueError("Could not find work item id in branch identifier")
