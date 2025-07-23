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
        self.last_pause_time = -1;

    def start(self):
        logger.info("HackClock started");

    def cleanup(self):
        
        # Save the current time
        self.resume_clock(); # Resume to take into account pause time when closing
        self.persist_current_time();

    def get_save_name(self) -> str:
        return self.last_hack.title;

    last_hack = None;
    def on_hack_start(self, hack): 

        self.start_time = time.time();
        self.is_paused = False;

        # Start the clock update loop
        self.last_hack = hack;

        # Check if we have saved data from the last session
        data = self.get_persisted_data(self.get_save_name());
        if data is None:
            self.persist_data(self.get_save_name(), {"time": 0});
        else:
            # Get the last saved time
            last_time = data["time"];
            logger.info(f"Last saved time: {last_time} for {self.get_save_name()}");
            self.start_time -= last_time;
    
        self.update_clock();

    def persist_current_time(self):

        if self.last_hack is None:
            logger.warning("Hack is None, skipping time persistence");
            return;

        elapsed_time = time.time() - self.start_time;
        logger.info(f"Persisting time: {elapsed_time} for {self.get_save_name()}");
        self.persist_data(self.get_save_name(), {"time": elapsed_time});

    def on_hack_exit(self):
        
        # Save the current time
        self.persist_current_time();

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

        my_menu.add_command(label="Pause/Resume Hack Clock", command=self.toggle_pause, accelerator="Ctrl+P");
        self.query_root().bind("<Control-p>", lambda event: self.toggle_pause());

        my_menu.add_command(label="Reset Hack Clock", command=self.reset_clock);
        my_menu.add_command(label="Edit Clock value", command=self.open_clock_editor);

        my_menu.add_separator();

        my_menu.add_command(label="Consult hack clock table", command=lambda: self.open_clock_table());

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
            self.last_pause_time = time.time();

        self.pause_text.set("Resume" if self.is_paused else "Pause");

        # Safety save
        self.persist_current_time();

    def resume_clock(self):
        
        if self.last_pause_time != -1:
            self.start_time += time.time() - self.last_pause_time;
            self.last_pause_time = -1;

        self.is_paused = False;

    def reset_clock(self):
        self.start_time = time.time();
        self.is_paused = False;
        self.last_pause_time = -1;

        # Reset the clock display
        self.clock_timer.set("0:00:00");
        self.pause_text.set("Pause");

        # Persist the reset time
        self.persist_current_time();

    def open_clock_table(self):

        # Create the clock table window
        clock_table_window = tkinter.Toplevel(self.query_root());
        clock_table_window.title("Hack Clock Table");
        clock_table_window.geometry("400x300");

        # Create the ClockTable 
        frame = tkinter.Frame(clock_table_window);
        frame.pack(pady=10, padx=10);

        clock_label = tkinter.Label(frame, text="Hack Clock Table");
        clock_label.config(font=("Arial", 12));
        clock_label.pack(side=tkinter.TOP, pady=5);

        clock_table = tkinter.Listbox(frame, width=80, height=20);

        data_map: dict = self.get_plugin_data_map();
        for key, value in data_map.items():
            clock_table.insert(1, f"{key}:\t { str(timedelta(seconds=round(value.get('time', 0))))}");

        clock_table.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True);

    def open_clock_editor(self):
        time_parts: list[int];

        def save_clock_value(popup, hours, minutes, seconds):
            """
            Save the clock value from the editor popup.
            """
            # Convert to total seconds
            total_seconds = int(hours * 3600 + minutes * 60 + seconds);
            self.start_time = time.time() - total_seconds;

            # Update the clock display
            self.clock_timer.set(str(timedelta(seconds=total_seconds)).split(".")[0]);
            self.persist_current_time();
            popup.destroy();

        # Get current time
        if self.start_time != -1:
            
            elapsed_time = time.time() - self.start_time;

            elapsed_time_str = str(timedelta(seconds=elapsed_time));
            time_parts = elapsed_time_str.split(":");
        else:
            logger.warning("Cannot open clock editor, clock is not running");
            return;

        # Open popup window to modify the clock value
        popup = tkinter.Toplevel(self.query_root());
        popup.title("Clock editor");
        popup.geometry("250x100");

        frame = tkinter.Frame(popup);
        frame.pack(pady=10, padx=10);

        hours = tkinter.DoubleVar(value=float(time_parts[0]));
        minutes = tkinter.DoubleVar(value=float(time_parts[1]));
        seconds = tkinter.DoubleVar(value=float(time_parts[2]));

        label = tkinter.Label(frame, text=f'Set hack clock value:');
        label.config(font=("Arial", 12));
        label.pack(side=tkinter.TOP, pady=5);

        hour_spinner = tkinter.Spinbox(frame, from_=0, to=int(24 * 365), width=5, textvariable=hours, state="readonly");
        minute_spinner = tkinter.Spinbox(frame, from_=0, to=59, width=5, textvariable=minutes, state="readonly");
        second_spinner = tkinter.Spinbox(frame, from_=0, to=59, width=5, textvariable=seconds, state="readonly");

        hour_spinner.pack(side=tkinter.LEFT, padx=5);
        minute_spinner.pack(side=tkinter.LEFT, padx=5);
        second_spinner.pack(side=tkinter.LEFT, padx=5);

        save_button = tkinter.Button(frame, text="Save", command=lambda: save_clock_value(popup, hours.get(), minutes.get(), seconds.get()));
        save_button.pack(side=tkinter.LEFT, padx=5);
