"""
Where to find SMWhat plugins
Temporally, this is a placeholder for the plugin repository.
"""

plugin_repository: dict = {

};

def get_plugin_info(plugin_name):
    """
    Get the plugin information from the repository.
    """
    
    return plugin_repository.get(plugin_name, None);