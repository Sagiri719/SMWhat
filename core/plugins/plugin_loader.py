import os
import json
import importlib.util

from utils import resource_path;
from core.constants import PLUGIN_FOLDER;
import core.plugins.plugin as plugin_base;

import logging

logger = logging.getLogger(__name__);

def get_all_plugins(plugin_dir: str, root) -> list:
    """
    Get all plugins from the plugin directory.
    """

    plugins: list[plugin_base.Plugin] = [];
    plugin_directory = resource_path(plugin_dir);
    for plugin_folder in os.listdir(plugin_dir):

        path = os.path.join(plugin_directory, plugin_folder);
        name = os.path.basename(path);

        # Check if the plugin folder contains a __init__.py file
        init_file = os.path.join(path, "__init__.py");
        config_file = os.path.join(path, "plugin.json");
        if os.path.isdir(path) and os.path.isfile(init_file) and os.path.isfile(config_file):

            logger.debug(f"Found plugin folder: {name}");

            plugin_config = json.load(open(config_file));
            logger.debug(f"{plugin_config.get('name')}({plugin_config.get('version')}) loaded");

            # Check if dependencies are met
            dependencies = plugin_config.get("dependencies", []);
            
            # Load the plugin module
            # Create module specification
            # Needed to load a module from a file
            spec = importlib.util.spec_from_file_location(name, init_file);
            # Create an empty python module from the specification
            plugin_module = importlib.util.module_from_spec(spec);
            # Executes the module 
            spec.loader.exec_module(plugin_module);

            entry_point: str = plugin_config.get("entry_point");

            if entry_point != None and hasattr(plugin_module, entry_point):
                
                plugin_class = getattr(plugin_module, entry_point);

                # Check if the class is a subclass of Plugin
                if issubclass(plugin_class, plugin_base.Plugin):    
                    logger.debug(f"Adding pluggin class: {plugin_class}");
                    plugins.append(plugin_class(plugin_config, root));

            else:
                logger.warning(f"Plugin {name} does not have the entry point {entry_point}. Skipping.");
                continue;

        else:
            logger.debug(f"Skipping non-plugin folder: {name}. Missing __init__.py or plugin.json file.");
            continue;

    # Sort plugins by priority
    plugins.sort(key=lambda p: p.config.get("priority", 999), reverse=False);

    return plugins;

def load_plugins(root):
    plugins = get_all_plugins(PLUGIN_FOLDER, root);
    logger.info(f"Loaded {len(plugins)} plugins.");
    return plugins;