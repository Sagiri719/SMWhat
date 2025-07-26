"""
Plugin class that provides a common interface for all plugins.
"""

from abc import ABC, abstractmethod
from core.hack_content import HackContent
from core.win32com import test_server_connection;
from presentation.ui import UI
from persistence.persistence import get_plugin_data, persist_plugin_data, get_plugin_data_map
import settings

class Plugin(ABC):

    def __init__(self, config: dict, ui: UI):
        """
        Initialize the plugin with the given configuration.
        :param config: Dictionary containing the plugin configuration.
        """
        self.config = config;
        self.ui = ui;

    @abstractmethod
    def cleanup(self):
        """
        Cleanup the plugin.
        """

    def __str__(self):
        return self.name

    def get_name(self):
        return self.config["name"];

    def get_version(self):
        return self.config["version"];

    def display_message(self, message: str):
        """
        Display a message in the UI.
        """
        self.ui.display_message(message);

    def query_hack(self) -> HackContent:
        """
        Query the current hack being played
        """
        return self.ui.controller.get_hack();

    def persist_data(self, key: str, data: any):
        """
        Persist data from the plugin
        """
        persist_plugin_data(self, key, data);

    def get_persisted_data(self, key: str):
        """
        Get persisted data from the plugin
        """
        return get_plugin_data(self, key);

    def get_plugin_data_map(self):
        """
        Get the plugin data map
        """
        return get_plugin_data_map(self);

    def query_root(self):
        """
        Query the root of the UI
        """
        if hasattr(self.ui, "root"):
            return self.ui.root;
        
        return None;

    def query_menu_bar(self):
        """
        Query the menubar of the UI
        """
        if hasattr(self.ui, "menubar"):
            return self.ui.menubar;
        
        return None;

    def query_emulator(self):
        """
        Query what emulator is being used.
        """
        return settings.app_config.get("emulator", None);

    def test_cheats(self, retries=1, delay=0.5) -> bool:
        """
        Test the connection to the cheat server.
        This method should be overridden by subclasses to provide specific server connection logic.
        """
        return test_server_connection(retries, delay);

    @abstractmethod
    def start(self):
        """
        Start the plugin.
        """

    @abstractmethod
    def on_hack_start(self, hack: HackContent):
        """
        Called when a hack is found.
        """

    @abstractmethod
    def on_hack_exit(self):
        """
        Called when the hack is exited.
        """

    @abstractmethod
    def define_menu_options(self, my_menu):
        """
        Define the menu options for the plugin.
        This method should be overridden by subclasses to provide specific menu options.
        """

    @abstractmethod
    def pack_ui(self, my_frame):
        """
        Pack the UI elements for the plugin.
        This method should be overridden by subclasses to provide specific UI elements.
        """

    # Optional methods that can be overridden by subclasses
    def on_emulator_changed(self):
        """
        Called when the emulator is changed.
        This method should be overridden by subclasses to handle emulator changes.
        """
        pass;