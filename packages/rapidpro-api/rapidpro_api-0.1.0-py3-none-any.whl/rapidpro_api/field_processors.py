import copy

def process_field(field, metadata:dict=None):
    """
    Processes a field object. Merges with metadata.
    
    Args:
        field (dict): The field object to process.
        metadata (dict, optional): Additional metadata to merge with the field object.
        
    Returns:
        dict: The processed field object.
    Example: 
        group ={
            "key": "reporters",
            "name": "Reporters",
            "type": text,
        }
        metadata = {
            "workspace_code": "test_workspace"
        }
        processed_group = process_group(group, metadata)
        # will return {
            "key": "reporters",
            "name": "Reporters",
            "type": text,
            "workspace_code": "test_workspace"
        }
    """
    result = copy.deepcopy(field)
    # Merge with metadata
    if metadata:
        result.update(metadata)
    return result