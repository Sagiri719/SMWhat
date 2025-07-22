import os;
import json;

from utils import resource_path, exists_or_dump;
from core.constants import DATAMAP_FILE, PLUGIN_CACHE_FILE;

persistent_data = {
    "hack_alias": {},
    "hack_stats": {},
}

plugin_data = {
    "plugin_data": {},
}

def init_persistence() -> None:
    """
    Initialize the persistence data map
    """

    global persistent_data;
    global plugin_data;

    persistent_data = exists_or_dump(persistent_data, DATAMAP_FILE);
    plugin_data = exists_or_dump(plugin_data, PLUGIN_CACHE_FILE);    

def save_data_map() -> None:
    """
    Save the data map to the file
    """

    global persistent_data;

    # Save the data map to the file
    with open(resource_path(DATAMAP_FILE), "w") as f:
        json.dump(persistent_data, f, indent=4);

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

def persist_plugin_data(plugin, key: str, data: any) -> None:
    """
    Persist data from the plugin
    """

    global plugin_data;

    # Check if the plugin data exists
    if plugin.get_name() not in plugin_data["plugin_data"]:
        plugin_data["plugin_data"][plugin.get_name()] = {};

    if key not in plugin_data["plugin_data"][plugin.get_name()]:
        plugin_data["plugin_data"][plugin.get_name()][key] = {};

    plugin_data["plugin_data"][plugin.get_name()][key] = data;
    with open(resource_path(PLUGIN_CACHE_FILE), "w") as f:
        json.dump(plugin_data, f, indent=4);
    
def get_plugin_data(plugin, key: str) -> any:
    """
    Get the plugin data from the data map
    """

    global plugin_data;

    # Check if the plugin data exists
    if plugin.get_name() in plugin_data["plugin_data"]:
        if key in plugin_data["plugin_data"][plugin.get_name()]:
            return plugin_data["plugin_data"][plugin.get_name()][key];
    
    return None;

def get_plugin_data_map(plugin) -> dict:
    """
    Get the plugin data map
    """

    global plugin_data;

    # Check if the plugin data exists
    if plugin.get_name() in plugin_data["plugin_data"]:
        return plugin_data["plugin_data"][plugin.get_name()];
    
    return {};