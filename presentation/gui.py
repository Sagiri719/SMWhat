import logging;

from presentation.ui import UI

import tkinter
from tkinter import messagebox
from tkinter import ttk 

from core.win32com import get_emulator_window, get_pid_from_window_title, monitor_process_async;
from core.smwccom import get_hack_by_name, search_for_hack;
from core.discordcom import start_presence_for;
from core.emulator import emulator_list, get_emulator_by_name, Emulator;

from PIL import Image, ImageTk
import requests
from io import BytesIO
from threading import Event
import webbrowser

from presentation.hack_content import HackContent;
from presentation.translations import t;

import utils;
import persistence.persistence as persistence;
import settings;

logger = logging.getLogger(__name__);

class GuiApp(UI):

    dimensions = (500, 320)
    name = "SMWhat"
    style = {
        "control_bg": "lightgrey",
        "control_size": 200,

        "hackframe_bg": "white",
        "hackframe_size": dimensions[0],
    }

    contents = {
        "hack_name": None, # StringVar
        "hack": None, # HackContent
        "hack_image_dimensions": (200, 200),
    }

    rcp = None;
    monitor_thread = None;
    monitor_stop_event = None;

    def __init__(self):

        super().__init__();
        self.root = tkinter.Tk();
        self.root.title(self.name);
        self.root.geometry(f"{self.dimensions[0]}x{self.dimensions[1]}");
        self.root.resizable(False, False);

        self.root.iconbitmap(utils.get_icon());

        # Create UI
        self.init_menu();
        self.init_control_frame();
        self.init_hack_frame();
        self.init_status_bar();

        self.pack_and_bind();

    def init_control_frame(self):

        self.control_frame = tkinter.Frame(self.root, width=self.style["control_size"], height=self.dimensions[1], bg=self.style["control_bg"]);
        self.control_frame.pack(side=tkinter.LEFT, fill=tkinter.Y);

        # Find hack button
        self.fyh_label = tkinter.Label(self.control_frame, text=t("find_hack_label"), bg=self.style["control_bg"]);
        self.find_button = tkinter.Button(self.control_frame, text=t("find_hack_button"), command=self.find_hack);
        self.wrong_hack = tkinter.Button(self.control_frame, text=t("wrong_hack"), command=self.find_hack_manual, bg=self.style["control_bg"], state=tkinter.DISABLED);

        # Discord rich presence label
        self.start_discord_label = tkinter.Label(self.control_frame, text=t("discord"), bg=self.style["control_bg"]);        
        self.button_frame = tkinter.Frame(self.control_frame, bg=self.style["control_bg"]);

        self.start_discord_button = tkinter.Button(self.button_frame, text=t("start"), command=self.set_presence);
        self.stop_discord_button = tkinter.Button(self.button_frame, text=t("stop"), command=self.destroy_presence);

        # Emulator combobox
        self.emulator_label = tkinter.Label(self.control_frame, text=t("emulator"), bg=self.style["control_bg"]);
        self.emulator_combobox = tkinter.ttk.Combobox(self.control_frame, values=list(map(lambda e: e.display_name, emulator_list)), state="readonly");
        
        # Set default value for emulator combobox
        self.emulator_combobox.set(settings.app_config["emulator"].display_name);

    def init_hack_frame(self):

        self.hack_frame = tkinter.Frame(self.root, width=self.dimensions[0], height=self.style["hackframe_size"], bg=self.style["hackframe_bg"]);
        self.hack_frame.pack(side=tkinter.RIGHT, fill=tkinter.BOTH, expand=True);

        # Create label for hack name
        self.contents["hack_name"] = tkinter.StringVar(self.root, value=t("hack_name"));

        self.hack_name_label = tkinter.Label(self.hack_frame, textvariable=self.contents["hack_name"], bg=self.style["hackframe_bg"], wraplength=250, justify=tkinter.CENTER);
        self.hack_name_label.config(font=("Helvetica", 14));

        # Create image for hack
        self.hack_image = ImageTk.PhotoImage(Image.new("RGB", self.contents["hack_image_dimensions"], color="white"));

        # Create label for hack image
        self.hack_image_label = tkinter.Label(self.hack_frame, image=self.hack_image, bg=self.style["hackframe_bg"]);

    def init_status_bar(self):
        self.status_var = tkinter.StringVar(self.control_frame, value=utils.get_app_version());
        self.status_bar = tkinter.Label(self.control_frame, textvariable=self.status_var, bg=self.style["control_bg"]);

    RESET_BAR_DELAY = 5000; # 5 seconds
    def set_status_bar(self, text: str):
        self.status_var.set(text);
        self.root.after(self.RESET_BAR_DELAY, lambda: self.status_var.set(utils.get_app_version()));

    def init_menu(self):

        self.menubar = tkinter.Menu(self.root);

        # File menu
        self.file_menu = tkinter.Menu(self.menubar, tearoff=0);
        self.file_menu.add_command(label=t("exit"), command=self.root.quit);

        # Language menu
        self.language_menu = tkinter.Menu(self.menubar, tearoff=0);
        self.language_menu.add_command(label="English", command=lambda: self.set_language("en"));
        self.language_menu.add_command(label="Português", command=lambda: self.set_language("pt"));
        self.language_menu.add_command(label="日本語", command=lambda: self.set_language("jp"));

        # Help menu
        self.help_menu = tkinter.Menu(self.menubar, tearoff=0);
        self.help_menu.add_command(label=t("source"), command=lambda: webbrowser.open(utils.get_source_code()));
        self.help_menu.add_command(label=t("about"), command=lambda: self.display_message(utils.get_app_version_message()));

        # Data menu
        self.data_menu = tkinter.Menu(self.menubar, tearoff=0);
        self.data_menu.add_command(label=t("forget"));
        self.data_menu.add_command(label=t("reset"));
        self.data_menu.add_command(label=t("clear_logs"), command=lambda: settings.clear_logs());

        # Set the menu bar
        self.root.config(menu=self.menubar);

        # Add menus to the menu bar
        self.menubar.add_cascade(label=t("file"), menu=self.file_menu);
        self.menubar.add_cascade(label=t("data"), menu=self.data_menu);
        self.menubar.add_cascade(label=t("language"), menu=self.language_menu);
        self.menubar.add_cascade(label=t("help"), menu=self.help_menu);

    def set_language(self, lang: str):

        settings.change_language(lang);

        # Reload app
        self.root.destroy();
        self.__init__();

    def pack_and_bind(self):
        
        self.hack_name_label.pack(pady=10);
        self.fyh_label.pack(padx= 15, pady=10);
        self.find_button.pack(padx = 15, pady=5);
        self.hack_image_label.pack(padx=15, pady=3);
        self.wrong_hack.pack(pady=10);
        self.start_discord_label.pack(pady=10);
        self.button_frame.pack();
        self.start_discord_button.pack(side=tkinter.LEFT, fill=tkinter.X, expand=True);
        self.stop_discord_button.pack(side=tkinter.RIGHT, fill=tkinter.X, expand=True);

        self.emulator_label.pack(pady=10);
        self.emulator_combobox.pack(padx=10);

        self.emulator_combobox.bind("<<ComboboxSelected>>", self.on_emulator_select);

        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close);

        self.status_bar.pack(side=tkinter.BOTTOM, fill=tkinter.X);

    def on_close(self):

        if self.monitor_stop_event:
            self.monitor_stop_event.set()
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        
        self.root.destroy();

    def display_message(self, message: str):
        messagebox.showinfo("Message", message)

    def on_emulator_select(self, event: tkinter.Event):
        
        selected_emulator = self.emulator_combobox.get();
        emulator: Emulator = get_emulator_by_name(selected_emulator);

        if emulator is None:
            self.display_message(t("emulator_not_found"));
            return;
        
        # Save the selected emulator
        settings.change_emulator(emulator);        

    def set_presence(self):

        if self.contents["hack"] is None:
            self.display_message(t("no_hack"));
            return;

        if self.rcp is not None:
            self.display_message(t("rp_already_active"));
            return;

        self.set_status_bar(t("rp_starting"));
        self.rcp = start_presence_for(self.contents["hack"]);

        if self.rcp is None:
            self.display_message(t("rp_error"));
            return;
        self.display_message(t("rp_success"));

    def destroy_presence(self, message = True):
        
        if self.rcp is None:
            if message:
                self.display_message(t("rp_not_active"));
            return;

        try:

            self.rcp.close();
            self.rcp = None;

            self.display_message(t("rp_disable"));

        except Exception as e:
            logger.exception("Error while closing presence: " + str(e));
            self.display_message(t("rp_error_closing"));

    def load_image(self, url: str):

        self.set_status_bar(t("loading_image"));

        logger.info("Loading image from URL: " + url);
        response = requests.get(url);
        image_data = BytesIO(response.content);

        img = Image.open(image_data);

        # Resize the image to fit the label
        aspect_ratio = img.width / img.height;
        new_width = self.contents["hack_image_dimensions"][0];
        new_height = int(new_width / aspect_ratio);

        img = img.resize((new_width, new_height));

        self.hack_image = ImageTk.PhotoImage(img);
        self.hack_image_label.config(image=self.hack_image);
        self.hack_image_label.image = self.hack_image;  # Keep a reference to avoid garbage collection

    def find_hack(self):

        window_name: str = utils.get_window_rom_name();

        if window_name != "":

            hack = get_hack_by_name(window_name);

            if hack is None:
                self.display_message(t("hack_not_found"));
                self.find_hack_manual();
                return;
            
            self.contents["hack"] = hack;
            self.set_hack();

        else:
            self.display_message(f'{settings.app_config["emulator"].display_name} {t("not_detected")}');

    def set_hack(self):

            if self.rcp is not None:
                self.destroy_presence(False);

            window_name: str = get_emulator_window(settings.app_config["emulator"]);    
        
            self.contents["hack_name"].set(self.contents["hack"].__str__());

            self.load_image(self.contents["hack"].image_url);

            self.start_discord_button.config(state=tkinter.NORMAL);
            self.stop_discord_button.config(state=tkinter.NORMAL);

            self.wrong_hack.config(state=tkinter.NORMAL);

            # Set up process monitoring
            if self.monitor_stop_event:
                self.monitor_stop_event.set()
                if self.monitor_thread:
                    self.monitor_thread.join(timeout=2)
            
            pid: int = get_pid_from_window_title(window_name);
            if pid != -1:
                # Start async monitoring
                self.monitor_stop_event = Event();
                self.monitor_thread = monitor_process_async(pid, self.on_emulator_close, self.monitor_stop_event);
            else:
                self.display_message(t("monitoring_error"));

    def on_emulator_close(self):
        
        self.destroy_presence(False);
        self.display_message(t("not_detected"));

        # Redefine hack info
        self.contents["hack"] = None;
        self.contents["hack_name"].set(t("hack_name"));

        # Reset hack image
        self.hack_image = ImageTk.PhotoImage(Image.new("RGB", self.contents["hack_image_dimensions"], color="white"));
        self.hack_image_label.config(image=self.hack_image);
        self.hack_image_label.image = self.hack_image;

        # Reset start button
        self.start_discord_button.config(state=tkinter.DISABLED);
        self.stop_discord_button.config(state=tkinter.DISABLED);
        self.wrong_hack.config(state=tkinter.DISABLED);

    def find_hack_manual(self):

        hack_cache = [];

        def search_hacks():

            self.set_status_bar(t("hack_searching"));
            button.config(state=tkinter.DISABLED);
            entry.config(state=tkinter.DISABLED);

            name = entry.get();
            hacks = search_for_hack(name);
            if hacks == None or len(hacks) == 0:
                self.display_message(t("hack_not_found"));
                # Close popup
                popup.destroy();

                return;
            
            # Clear listbox
            result_list.delete(0, tkinter.END);
            hack_cache.clear();

            # Show results
            for hack in hacks:
                hack_cache.append(hack);
                result_list.insert(tkinter.END, hack.__str__());

            button.config(state=tkinter.NORMAL);
            entry.config(state=tkinter.NORMAL);

        def select_hack(event):

            self.set_status_bar(t("hack_fetch"));

            # Get selected hack
            selection = result_list.curselection();
            if len(selection) == 0:
                return;

            # Set hack
            self.contents["hack"] = hack_cache[selection[0]];
            self.set_hack();

            # Save the alias 
            window_name: str = get_emulator_window(settings.app_config["emulator"]);
            if (window_name != ""):

                # Get the name of the romhack
                window_name = settings.app_config["emulator"].hack_name_getter(settings.app_config["emulator"].hack_name_getter(window_name));
                persistence.save_hack_alias(window_name, self.contents["hack"].title);

            # Close popup
            popup.destroy();

        # Open popup window to enter hack name
        popup = tkinter.Toplevel(self.root);
        popup.title(t("manual_find"));
        popup.geometry("300x300");

        frame = tkinter.Frame(popup);
        frame.pack(pady=10, padx=10);

        # Create label and entry for hack name
        label = tkinter.Label(frame, text=t("hack_name2"));
        entry = tkinter.Entry(frame);
        button = tkinter.Button(frame, text=t("ok"), command=search_hacks);

        result_list = tkinter.Listbox(popup);

        # Add scrollbar to listbox
        scrollbar = tkinter.Scrollbar(result_list);
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y);
        result_list.config(yscrollcommand=scrollbar.set);
        scrollbar.config(command=result_list.yview);
        result_list.pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True);
        
        label.pack(side=tkinter.LEFT);
        entry.pack(side=tkinter.LEFT, padx=5);
        button.pack(side=tkinter.LEFT, padx=5);

        # Bind enter key to search_hacks
        entry.bind("<Return>", lambda event: search_hacks());
        popup.bind("<Escape>", lambda event: popup.destroy());

        result_list.bind("<Double-1>", select_hack);

    def run(self):
        self.root.mainloop()