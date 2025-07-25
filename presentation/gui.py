import logging;

from presentation.ui import UI

import tkinter
from tkinter import messagebox
from tkinter import ttk 

from core.win32com import get_emulator_window, get_pid_from_window_title, monitor_process_async, query_cheat_server;
from core.smwccom import get_hack_by_name, search_for_hack;
from core.emulator import emulator_list, get_emulator_by_name, Emulator;

from PIL import Image, ImageTk
import requests
from io import BytesIO
from threading import Event
import webbrowser

from core.hack_content import HackContent;
from presentation.translations import t;
from presentation.components.marquee_label import MarqueeLabel;

import utils;
import persistence.persistence as persistence;
import settings;

logger = logging.getLogger(__name__);

class GuiApp(UI):

    dimensions = (500, 350)
    name = "SMWhat"
    style = {
        "control_bg": "lightgrey",
        "control_size": 200,

        "hackframe_bg": "white",
        "hackframe_size": dimensions[0],

        "plugin_bg": "white",
        "plugin_size": dimensions[0],
    }

    hack_name: tkinter.StringVar;

    def __init__(self):

        super().__init__();

        self.root = tkinter.Tk();
        self.root.title(self.name);
        self.root.geometry(f"{self.dimensions[0]}x{self.dimensions[1]}");
        self.root.resizable(False, False);

        self.root.grid_rowconfigure(0, weight=1);
        self.root.grid_rowconfigure(1, weight=1);
        self.root.grid_columnconfigure(1, weight=1);

        self.root.iconbitmap(utils.get_icon());

        # Tell plugins to start
        self.plugin_event_all("start");

        # Create UI
        self.init_menu();
        self.init_control_frame();
        self.init_hack_frame();
        self.init_status_bar();
        self.init_plugin_frame();

        self.pack_and_bind();

    def init_control_frame(self):

        self.control_frame = tkinter.Frame(self.root, width=self.style["control_size"], height=self.dimensions[1], bg=self.style["control_bg"]);
        self.control_frame.grid(row=0, column=0, rowspan=2, sticky="nsew");

        # Find hack button
        self.fyh_label = tkinter.Label(self.control_frame, text=t("find_hack_label"), bg=self.style["control_bg"]);
        self.find_button = tkinter.Button(self.control_frame, text=t("find_hack_button"), command=self.find_hack);
        self.wrong_hack = tkinter.Button(self.control_frame, text=t("wrong_hack"), command=self.find_hack_manual, bg=self.style["control_bg"], state=tkinter.DISABLED);

        # Emulator combobox
        self.emulator_label = tkinter.Label(self.control_frame, text=t("emulator"), bg=self.style["control_bg"]);
        self.emulator_combobox = tkinter.ttk.Combobox(self.control_frame, values=list(map(lambda e: e.display_name, emulator_list)), state="readonly");
        
        # Set default value for emulator combobox
        self.emulator_combobox.set(settings.app_config["emulator"].display_name);

    def init_hack_frame(self):

        self.right_frame = tkinter.Frame(self.root, bg=self.style["hackframe_bg"]);
        self.right_frame.grid(row=0, column=1, rowspan=2, sticky="nsew");

        self.right_frame.grid_rowconfigure(0, weight=4)  # More space for hack_frame
        self.right_frame.grid_rowconfigure(1, weight=1)  # Less space for plugin_frame
        self.right_frame.grid_columnconfigure(0, weight=1)

        self.hack_frame = tkinter.Frame(self.right_frame, width=self.style["hackframe_size"], height=self.dimensions[1], bg=self.style["hackframe_bg"]);
        self.hack_frame.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True);

        # Create label for hack name
        self.hack_name = tkinter.StringVar(self.root, value=t("hack_name"));

        self.hack_name_label =  MarqueeLabel(
            master=self.hack_frame,
            text=self.hack_name,
            font=("Helvetica", 14),
            speed=100
        )
        
        # Create image for hack
        self.hack_image = ImageTk.PhotoImage(Image.new("RGB", self.controller.hack_image_dimensions, color="white"));

        # Create label for hack image
        self.hack_image_label = tkinter.Label(self.hack_frame, image=self.hack_image, bg=self.style["hackframe_bg"]);

    def init_status_bar(self):
        self.status_var = tkinter.StringVar(self.control_frame, value=utils.get_app_version());
        self.status_bar = tkinter.Label(self.control_frame, textvariable=self.status_var, bg=self.style["control_bg"]);

    RESET_BAR_DELAY = 5000; # 5 seconds
    def set_status_bar(self, text: str):
        self.status_var.set(text);
        self.root.after(self.RESET_BAR_DELAY, lambda: self.status_var.set(utils.get_app_version()));

    def init_plugin_frame(self):
        
        self.plugin_frames = [];

        self.plugin_frame = tkinter.Frame(self.right_frame, width=self.style["plugin_size"], height=self.dimensions[1], bg=self.style["plugin_bg"]);
        self.plugin_frame.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True);

        self.plugin_name_frame = tkinter.Frame(self.plugin_frame, width=self.style["plugin_size"], height=self.dimensions[1], bg=self.style["plugin_bg"]);

        for plugin in self.plugins:

            template_frame = tkinter.Frame(self.plugin_frame,width=self.style["plugin_size"], height=self.dimensions[1], bg=self.style["plugin_bg"]);
            template_frame.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True);

            content_frame = tkinter.Frame(template_frame, bg=self.style["plugin_bg"]);
            content_frame.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True);

            plugin.pack_ui(content_frame);

            plugin_label = tkinter.Label(template_frame, text=f'{plugin.get_name()} (v{plugin.get_version()})', bg=self.style["plugin_bg"], font=("Helvetica", 8));
            plugin_label.pack(side=tkinter.BOTTOM, fill=tkinter.X);

            self.plugin_frames.append(template_frame);

        self.active_plugin_index = 0;
        self.show_plugin(self.active_plugin_index);

        # Add plugin window controls
        self.root.bind(self.controller.plugin_controls["next"], lambda event: self.show_plugin((self.active_plugin_index + 1) % len(self.plugin_frames)));
        self.root.bind(self.controller.plugin_controls["previous"], lambda event: self.show_plugin((self.active_plugin_index - 1) % len(self.plugin_frames)));

    def show_plugin(self, index: int):

        # Hide all plugin frames
        for i, frame in enumerate(self.plugin_frames):
            if i == index:
                frame.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True);
            else:
                frame.pack_forget();

        self.active_plugin_index = index;

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
        self.help_menu.add_command(label=t("instructions"));
        self.help_menu.add_command(label=t("source"), command=lambda: webbrowser.open(utils.get_source_code()));
        self.help_menu.add_command(label=t("about"), command=lambda: self.display_message(utils.get_app_version()));

        # Data menu
        self.data_menu = tkinter.Menu(self.menubar, tearoff=0);
        self.data_menu.add_command(label=t("forget"), command=lambda: self.forget_hack_aliases());
        self.data_menu.add_command(label=t("reset"), command=lambda: self.reset_settings());
        self.data_menu.add_command(label=t("clear_logs"), command=lambda: self.clear_logs());

        # Plugins menu
        self.plugins_menu = tkinter.Menu(self.menubar, tearoff=0);

        # Add plugins to the menu
        for plugin in self.plugins:

            menu = tkinter.Menu(self.plugins_menu, tearoff=0);
            
            plugin.define_menu_options(menu);
            self.plugins_menu.add_cascade(label=plugin.get_name(), menu=menu);

        # Set the menu bar
        self.root.config(menu=self.menubar);

        # Add menus to the menu bar
        self.menubar.add_cascade(label=t("file"), menu=self.file_menu);
        self.menubar.add_cascade(label=t("data"), menu=self.data_menu);
        self.menubar.add_cascade(label=t("language"), menu=self.language_menu);
        self.menubar.add_cascade(label=t("plugins"), menu=self.plugins_menu);
        self.menubar.add_cascade(label=t("help"), menu=self.help_menu);

    def clear_logs(self):
        settings.clear_logs();
        self.display_message(t("logs_cleared"));

    def reset_settings(self):
        pass;

    def forget_hack_aliases(self):
        pass;

    def set_language(self, lang: str):

        settings.change_language(lang);

        # Reload app
        self.root.destroy();
        self.__init__();

    def pack_and_bind(self):
        
        self.fyh_label.pack(padx= 15, pady=10);
        self.find_button.pack(padx = 15, pady=5);
        self.hack_image_label.pack(padx=15, pady=3);
        self.wrong_hack.pack(pady=10);

        self.emulator_label.pack(pady=10);
        self.emulator_combobox.pack(padx=10);

        self.emulator_combobox.bind("<<ComboboxSelected>>", self.on_emulator_select);

        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close);

        self.status_bar.pack(side=tkinter.BOTTOM, fill=tkinter.X);

    def on_close(self):

        # Trigger plugin event for closing
        self.plugin_event_all("cleanup");

        if self.controller.monitor_stop_event:
            self.controller.monitor_stop_event.set()
        if self.controller.monitor_thread:
            self.controller.monitor_thread.join(timeout=2)
        
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

    def load_image(self, url: str):

        self.set_status_bar(t("loading_image"));

        logger.info("Loading image from URL: " + url);
        response = requests.get(url);
        image_data = BytesIO(response.content);

        img = Image.open(image_data);

        # Resize the image to fit the label
        aspect_ratio = img.width / img.height;
        new_height = self.controller.hack_image_dimensions[1];
        new_width = int(new_height * aspect_ratio);

        img = img.resize((new_width, new_height));

        self.hack_image = ImageTk.PhotoImage(img);
        self.hack_image_label.config(image=self.hack_image);
        self.hack_image_label.image = self.hack_image;  # Keep a reference to avoid garbage collection

    def find_hack(self):

        # query_namedpipe_server("READ WRAM 0x7E0010");

        window_name: str = utils.get_window_rom_name();

        if window_name != "" and window_name is not None:

            hack = get_hack_by_name(window_name);

            if hack is None:
                self.display_message(t("hack_not_found"));
                self.find_hack_manual();
                return;
            
            self.controller.hack = hack;
            self.set_hack();

        else:
            self.display_message(f'{settings.app_config["emulator"].display_name} {t("not_detected").lower()}');

    def set_hack(self):

        self.plugin_event_all("on_hack_start", self.controller.hack);

        window_name: str = get_emulator_window(settings.app_config["emulator"]);    

        self.hack_name.set(self.controller.hack.__str__());

        self.load_image(self.controller.hack.image_url);
        self.wrong_hack.config(state=tkinter.NORMAL);

        # Set up process monitoring
        if self.controller.monitor_stop_event:
            self.controller.monitor_stop_event.set()
            if self.controller.monitor_thread:
                self.controller.monitor_thread.join(timeout=2)
        
        pid: int = get_pid_from_window_title(window_name);
        if pid != -1:
            # Start async monitoring
            self.controller.monitor_stop_event = Event();
            self.controller.monitor_thread = monitor_process_async(pid, self.on_emulator_close, self.controller.monitor_stop_event);
        else:
            self.display_message(t("monitoring_error"));

    def on_emulator_close(self):
        
        self.plugin_event_all("on_hack_exit");

        self.display_message(t("not_detected"));

        # Redefine hack info
        self.controller.hack = None;
        self.hack_name.set(t("hack_name"));

        # Reset hack image
        self.hack_image = ImageTk.PhotoImage(Image.new("RGB", self.controller.hack_image_dimensions, color="white"));
        self.hack_image_label.config(image=self.hack_image);
        self.hack_image_label.image = self.hack_image;

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
            self.controller.hack = hack_cache[selection[0]];
            self.set_hack();

            # Save the alias 
            window_name: str = get_emulator_window(settings.app_config["emulator"]);
            if (window_name != ""):

                # Get the name of the romhack
                window_name = settings.app_config["emulator"].hack_name_getter(settings.app_config["emulator"].hack_name_getter(window_name));
                persistence.save_hack_alias(window_name, self.controller.hack.title);

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