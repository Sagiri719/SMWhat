"""
This module contains the UI components for the presentation layer of the application.

author: @Sagiri721
"""

class UI:

    def __init__(self):
        pass

    def display_message(self, message: str):
        print(message)

    def find_hack(self):
        self.display_message("Finding hack...")

    def find_hack_manual(self):
        self.display_message("Finding hack manually...")

    def set_presence(self):
        self.display_message("Setting presence...")

    def destroy_presence(self):
        self.display_message("Destroying presence...")

    def run(self):
        print("Running the UI...")