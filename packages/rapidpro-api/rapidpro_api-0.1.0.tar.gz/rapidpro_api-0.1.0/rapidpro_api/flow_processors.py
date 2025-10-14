import copy
import logging
from .time_utils import get_iso_date_strings

def process_flow(flow, metadata=None):
    """
    Process a flow object to extract relevant information.
    
    Args:
        flow (dict): The flow object containing details about the flow.
        
    Returns:
        dict: Processed flow information with relevant fields.
    Example:
        >>> flow = {
        ...     "uuid": "12345",
        ...     "name": "Sample Flow",
                "type": "message",
                "archived": False,
        ...     "labels": [],
        ...     "expires": 4320,
        ...     "created_on": "2023-10-01T12:00:00Z",
        ...     "runs": {
        ...         "active": 1,
        ...         "completed": 2,
        ...         "waiting": 0,
        ...         "interrupted": 0,
        ...         "expired": 0,
        ...         "failed": 0
        ...     }
        ...     "results": []
        ... }
        >>> metadata = {"source": "API"}
        >>> processed_flow = process_flow(flow, metadata)
        >>> print(processed_flow)
        {
            'uuid': '12345',
            'name': 'Sample Flow',
            'type': 'message',
            'archived': False,
            'labels': [],
            'expires': 4320,
            'created_on': '2023-10-01T12:00:00Z',
            'created_on_year': '2023',
            'created_on_month': '2023-10',
            'created_on_day': '2023-10-01',
            'active': 1,
            'completed': 2,
            'waiting': 0,
            'interrupted': 0,
            'expired': 0,
            'failed': 0,
            'source': 'API' 
        }

    """
    # Validate the contact is a dictionary
    if not isinstance(flow, dict):
        logging.error("Contact is not a dictionary")
        raise ValueError("Contact is not a dictionary")

    # Validate the contact has a uuid
    if not flow.get("uuid"):
        logging.warning("Contact does not have a uuid")

    # flattern runs
    processed = copy.deepcopy(flow)
    processed.update(flow.get("runs", {}))
    # remove runs, node_uuids and results
    processed.pop("runs", None)

    # add metadata if provided
    if metadata:
        processed.update(metadata)
    # add the dates for created_ond
    try:
      y, m, d = get_iso_date_strings(flow.get("created_on", ""))
      processed["created_on_year"] = y
      processed["created_on_month"] = m 
      processed["created_on_day"] = d 
    except (ValueError, KeyError) as e:
      logging.warning("created_on (%s) is invalid for uuid %s. Error: %s", flow.get("created_on", "<not found>"), flow.get("uuid", ""), e)
    return processed


def process_flow_results(flow, metadata=None):
    """
    Process the results of a flow to extract relevant information.
    Args:
        flow (dict): The flow object containing details about the flow.
        metadata (dict, optional): Additional metadata to include in the processed results.
    Returns:
        list: Processed flow results with relevant fields.
    Example:
    >>> flow = {
          "uuid": "12345",
          "name": "Sample Flow",
          "type": "message",
          "archived: False,
          "labels": [],
          "expires": 4320,
          "created_on": "2023-10-01T12:00:00Z",
        "results": [
              {
                "key": "report",
                "name": "Report",
                "categories": ["Report", "Other"],
                "node_uuids": ["12345"]
              }
              {
                "key": "report",
                "name": "Report",
                "categories": ["Report", "Other"],
                "node_uuids": ["12345"]
              }
            }
        ]  
        >>> metadata = {"source": "API"}
        >>> processed_results = process_flow_results(flow, metadata) 
        >>> print(processed_results)
        [
            {
                'uuid': '12345',
                'name': 'Sample Flow',
                'key': 'report',
                'name': 'Report',
                'categories': ['Report', 'Other'],
                'node_uuids': ['12345'],
                'source': 'API'
            }
        ]
    """
    processed_results = []
    for result in flow.get("results", []):
        processed_result = process_flow(result, metadata)
        # add the flow uuid and name to the result
        processed_result["uuid"] = flow.get("uuid", "")
        processed_result["name"] = flow.get("name", "")
        processed_results.append(processed_result)
    return processed_results