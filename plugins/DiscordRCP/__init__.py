import tkinter;
import time;

from plugins.DiscordRCP.discordcom import start_presence_for;
from core.plugins.plugin import Plugin

import logging

logger = logging.getLogger(__name__);

class DiscordRCPPlugin(Plugin):
    """
    Discord Rich Presence Plugin for SMWhat.
    This plugin provides functionality to update the Discord Rich Presence status based on the romhack that's currently running.
    """

    COOLDOWN_TIME = 10; 
    last_cooldown = 0; 

    def __init__(self, config, ui):
        super().__init__(config, ui);
        self.discord_rpc = None;

    def start(self):
        logger.info("DiscordRCPPlugin started");

    def cleanup(self):
        self.destroy_presence(message = False);

    def on_hack_start(self, hack): 
        pass;

    def on_hack_exit(self):
        pass;

    def define_menu_options(self, my_menu):

        # Add menu items
        my_menu.add_command(label="Set Presence", command=self.set_presence);
        my_menu.add_command(label="Destroy Presence", command=self.destroy_presence);

    def pack_ui(self, frame: tkinter.Frame):
        
        self.toggle_text = tkinter.StringVar(frame, "Toggle Discord Rich Presence on");
        self.toggle_button = tkinter.Button(frame, textvariable=self.toggle_text, command=self.toggle_presence);

        self.toggle_button.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER);

    def toggle_presence(self):

        if self.discord_rpc is None:
            if self.set_presence():
                self.toggle_text.set("Toggle Discord Rich Presence off");
        else:
            if self.destroy_presence(False):
                self.toggle_text.set("Toggle Discord Rich Presence on");

    def set_presence(self) -> bool:

        # Check for cooldown
        if time.time() - self.last_cooldown < self.COOLDOWN_TIME:

            remaining_seconds = round(self.COOLDOWN_TIME - (time.time() - self.last_cooldown));
            self.display_message("You're in coolddown, wait " + str(remaining_seconds) + " more seconds before trying again.");
            logger.error("Error starting Discord Rich Presence: Cooldown active");

            return False;
        
        hack = self.query_hack();
        if hack is None:
            logger.error("Error starting Discord Rich Presence: Hack not found");
            self.display_message("Error starting Discord Rich Presence: Hack not found");
            return False;

        if self.discord_rpc is not None:
            logger.error("Error starting Discord Rich Presence: Already set");
            self.display_message("Error starting Discord Rich Presence: Already set");
            return False;

        # Start the presence
        self.discord_rpc = start_presence_for(hack);
        if self.discord_rpc is None:
            logger.error("Error starting Discord Rich Presence: Failed to start");
            self.display_message("Error starting Discord Rich Presence: Failed to start");
            return False;

        self.last_cooldown = time.time();

        return True;

    def destroy_presence(self, message = True) -> bool:

        if self.discord_rpc is not None:

            self.discord_rpc.close();
            self.discord_rpc = None;
            if message:
                self.display_message("Discord Rich Presence destroyed");
                logger.info("Discord Rich Presence destroyed");

            return True;
        else:
            logger.error("Error destroying Discord Rich Presence: No presence found");
            if message:
                self.display_message("Error destroying Discord Rich Presence: No presence found");
