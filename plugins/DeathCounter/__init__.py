import tkinter;
import time;

from core.plugins.plugin import Plugin
from core.cheats.memory_peeker import watch_memory_address
from core.cheats.memory_domains import Domains

import logging

logger = logging.getLogger(__name__);

class DeathCounter(Plugin):
    """
    Death counter for SMWhat.
    This plugin provides functionality to keep track of the number of deaths you've had in a romhack.
    """

    is_supported = False;
    server_connected = False;

    cheat_server_reconnect_interval = 5;
    PLAYER_ANIMATION_TRIGGER_STATE_ADDRESS = 0x000071;
    DYING_STATE = 0x09;

    def __init__(self, config, ui):
        super().__init__(config, ui);

    def on_emulator_changed(self):
        self.check_for_support();

    def check_for_support(self):

        # Check for support
        emulator = self.query_emulator();
        logger.info(f"Checking for support with emulator: {emulator}");
        if not emulator is None and emulator.support_cheat_server:
            self.is_supported = True;
        else:
            self.is_supported = False;

        if hasattr(self, "death_counter_label") and self.death_counter_label is not None:
            text: str = "Open a hack to start counting deaths." if self.is_supported else "This plugin is not supported by the current emulator.";
            self.death_counter_label.config(text=text);

    def start(self):

        self.deathCounter = tkinter.IntVar();
        logger.info("DeathCounterPlugin started");

        # Check for support
        self.check_for_support();

        # Should retry connection to the cheat server
        self.should_reconnect = tkinter.BooleanVar();
        
        should_reconnect = self.get_persisted_data("should_reconnect");
        if should_reconnect is None:
            should_reconnect = False;
            self.persist_data("should_reconnect", should_reconnect);

        self.should_reconnect.set(should_reconnect);

    def cleanup(self):
        pass;

    def on_hack_start(self, hack): 

        if not self.test_cheats():
            self.death_counter_label.config(text="Failed to connect to the cheat server.");
            if self.should_reconnect.get():
                logger.warning("Failed to connect to the cheat server. Will retry in 5 seconds.");
                self.ui.root.after(self.cheat_server_reconnect_interval * 1000, lambda: self.on_hack_start(hack));
            return;

        self.update_death_counter();
        watch_memory_address(self.PLAYER_ANIMATION_TRIGGER_STATE_ADDRESS, Domains.WORK_RAM, self.watch_player_animation_trigger_state_address, delay=0.02);

    def on_hack_exit(self):
        
        self.deathCounter.set(0);
        self.update_death_counter();

        self.check_for_support();

    def define_menu_options(self, my_menu):
        my_menu.add_checkbutton(label="Reconnect to Cheat Server", variable=self.should_reconnect, command=lambda: self.persist_data("should_reconnect", self.should_reconnect.get()));

    def pack_ui(self, frame: tkinter.Frame):

        text: str = "Open a hack to start counting deaths." if self.is_supported else "This plugin is not supported by the current emulator.";
        
        self.death_counter_label = tkinter.Label(frame, text=text);
        self.death_counter_label.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER);

    def update_death_counter(self):

        if not self.is_supported:
            return;

        death_text : str = f"Deaths: {self.deathCounter.get()}"
        self.death_counter_label.config(text=death_text);

    def watch_player_animation_trigger_state_address(self, new_value: int):
        
        if new_value == self.DYING_STATE:
            self.deathCounter.set(self.deathCounter.get() + 1);
            self.update_death_counter();