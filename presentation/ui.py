"""
This module contains the UI components for the presentation layer of the application.

author: @Sagiri721
"""

from abc import ABC, abstractmethod

from controller.hack_controller import HackController;

class UI(ABC):

    def __init__(self):

        from core.plugins.plugin_loader import load_plugins;
        self.plugins = load_plugins(self);

        self.controller: HackController = HackController();

    @abstractmethod
    def display_message(self, message: str):
        print(message)

    @abstractmethod
    def find_hack(self):
        self.display_message("Finding hack...")

    @abstractmethod
    def find_hack_manual(self):
        self.display_message("Finding hack manually...")

    @abstractmethod
    def run(self):
        print("Running the UI...")

    def get_plugins(self):
        return self.plugins;

    def plugin_event(self, plugin, event: str, *args):
        if hasattr(plugin, event):
            getattr(plugin, event)(*args);

    def plugin_event_all(self, event: str, *args):
        """
        Call the plugin event with the given name and arguments for all plugins.
        """
        for plugin in self.plugins:
            if hasattr(plugin, event):
                getattr(plugin, event)(*args);