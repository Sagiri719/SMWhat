import os;
import json;

from utils import resource_path;

DATAMAP_FILE = "persistence\data.json"

persistent_data = {
    "hack_alias": {},
    "hack_stats": {},
}

def init_persistence() -> None:
    """
    Initialize the persistence data map
    """

    global persistent_data;

    # Check if the data file exists
    if not os.path.exists(resource_path(DATAMAP_FILE)):
        # Create the data file
        with open(resource_path(DATAMAP_FILE), "w") as f:
            json.dump(persistent_data, f);
    else:
        # Load the data file
        with open(resource_path(DATAMAP_FILE), "r") as f:
            persistent_data = json.load(f);
    

def save_data_map() -> None:
    """
    Save the data map to the file
    """

    global persistent_data;

    # Save the data map to the file
    with open(resource_path(DATAMAP_FILE), "w") as f:
        json.dump(persistent_data, f);

def save_hack_alias(window_name: str, hack_name: str) -> None:
    """
    Save the hack alias to the data map
    """

    persistent_data["hack_alias"][window_name] = hack_name;
    save_data_map();

def get_hack_alias(window_name: str) -> str:
    """
    Get the hack alias from the data map
    """

    if window_name in persistent_data["hack_alias"]:
        return persistent_data["hack_alias"][window_name];
    
    return None;