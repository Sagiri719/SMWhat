import tkinter;
import time;

from PIL import Image, ImageTk

from core.plugins.plugin import Plugin
from core.cheats.memory_peeker import watch_memory_address
from core.cheats.memory_domains import Domains
from utils import resource_path

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

    def cleanup(self):
        if self.last_hack is not None:
            self.persist_death_counter();

    def get_save_name(self) -> str:
        return self.last_hack.title;

    last_hack = None;
    def on_hack_start(self, hack): 

        self.last_hack = hack;

        if not self.test_cheats():
            self.death_counter_label.config(text="Failed to connect to the cheat server.");
            return;

        data = self.get_persisted_data(self.get_save_name());
        if data is None:
            self.persist_data(self.get_save_name(), {"deaths": 0});
        else:
            last_deaths = data["deaths"];
            logger.info(f"Last saved deaths: {last_deaths} for {self.get_save_name()}");
            self.deathCounter.set(last_deaths);

        self.update_death_counter();
        watch_memory_address(self.PLAYER_ANIMATION_TRIGGER_STATE_ADDRESS, Domains.WORK_RAM, self.watch_player_animation_trigger_state_address, delay=0.02);

    def on_hack_exit(self):

        self.persist_death_counter();
        
        self.deathCounter.set(0);
        self.update_death_counter();

        self.check_for_support();

        self.last_hack = None;

    def define_menu_options(self, my_menu):
        pass;

    def pack_ui(self, frame: tkinter.Frame):

        self.content_frame = tkinter.Frame(frame);

        text: str = "Open a hack to start counting deaths." if self.is_supported else "This plugin is not supported by the current emulator.";

        pil_image = Image.open(resource_path("plugins\\DeathCounter\\res\\death.png"));
        pil_image = pil_image.resize((21, 32));
        self.skull_image = ImageTk.PhotoImage(pil_image);

        self.skull_image_label = tkinter.Label(self.content_frame, image=self.skull_image);
        self.death_counter_label = tkinter.Label(self.content_frame, text=text);
        self.death_counter_label.config(font=("Arial", 18));

        self.skull_image_label.pack(side=tkinter.LEFT);
        self.death_counter_label.pack(side=tkinter.RIGHT, padx=5, pady=5);

        self.content_frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER);

    def update_death_counter(self):

        death_text : str = f"{self.deathCounter.get()}"
        self.death_counter_label.config(text=death_text);

    def watch_player_animation_trigger_state_address(self, new_value: int):
        
        if new_value == self.DYING_STATE:
            self.deathCounter.set(self.deathCounter.get() + 1);
            self.persist_death_counter(False);

            self.update_death_counter();

    def persist_death_counter(self, message=True):

        if not self.is_supported or self.last_hack is None:
            return;

        data = self.get_persisted_data(self.get_save_name());

        data["deaths"] = self.deathCounter.get();
        self.persist_data(self.get_save_name(), data);

        if message:
            logger.info(f"Persisted death counter: {data['deaths']} for {self.get_save_name()}");