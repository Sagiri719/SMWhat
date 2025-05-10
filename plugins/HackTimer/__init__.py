import tkinter;
import time;
from datetime import datetime, timedelta;

from core.plugins.plugin import Plugin

import logging

logger = logging.getLogger(__name__);

class HackClock(Plugin):
    """
    Hack Clock Plugin for SMWhat.
    The plugin keeps track of the time spent on a hack.
    """

    def __init__(self, config, ui):
        super().__init__(config, ui); 

        self.is_paused = False;
        self.start_time = -1;

    def start(self):
        logger.info("HackClock started");

    def cleanup(self):
        pass;

    def on_hack_start(self, hack): 

        self.start_time = time.time();
        self.is_paused = False;
        
        # Start the clock update loop
        self.update_clock();

    def on_hack_exit(self):
        
        self.start_time = -1;
        self.is_paused = False;

        # Reset the clock display
        self.clock_timer.set("00:00:00");
        self.pause_text.set("Pause");

    def update_clock(self):

        if self.start_time != -1 and not self.is_paused:
            
            elapsed_time = time.time() - self.start_time;

            elapsed_time_str = str(timedelta(seconds=elapsed_time));
            self.clock_timer.set(elapsed_time_str.split(".")[0]);

        # Schedule the next update
        self.query_root().after(1000, self.update_clock);

    def define_menu_options(self, my_menu):

        pass;

    def pack_ui(self, frame: tkinter.Frame):
        
        self.clock_frame = tkinter.Frame(frame);

        self.clock_timer = tkinter.StringVar(self.clock_frame, "00:00:00");

        self.clock_label = tkinter.Label(self.clock_frame, textvariable=self.clock_timer);
        self.clock_label.config(font=("Arial", 22));
        
        self.pause_text = tkinter.StringVar(self.clock_frame, "Pause");
        self.pause_button = tkinter.Button(self.clock_frame, textvariable=self.pause_text, command=self.toggle_pause);
        
        self.clock_label.pack(side=tkinter.LEFT);
        self.pause_button.pack(side=tkinter.RIGHT, padx=5, pady=5);

        self.clock_frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER);

    def toggle_pause(self):
        if self.is_paused:
            self.resume_clock();
            self.is_paused = False;
        else:
            self.is_paused = True;

        self.pause_text.set("Resume" if self.is_paused else "Pause");

    def resume_clock(self):
        self.start_time = time.time() - (time.time() - self.start_time);
        self.is_paused = False;