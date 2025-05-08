"""
    SMWCentral Discord Rich Presence
    author: @Sagiri721
"""
import sys
import os

from presentation.ui import UI;
from settings import init_settings, app_config, ui_modes;

# Initialize settings
init_settings();

if __name__ == "__main__":

    # Start UI
    app: UI = ui_modes[app_config["ui"]]();
    app.run();

    # window_name: str = get_emulator_window(snes9x);
    # if (window_name != ""):
        
    #     print("Snes9x was detected!");
    #     # Get the name of the romhack
    #     window_name = window_name.split(" - ")[0];
    #     print("Romhack name: " + window_name);

    #     hack = get_hack_by_name(window_name);

    #     if hack is None:
    #         print("Hack not found in SMWC database! Please report this to the developer.");
    #         exit();
        
    #     print("\n###############################\n");
        
    #     name: str = str(hack.name);
    #     authors: str = (", ".join(str(a.name) for a in hack.authors));

    #     print(f'Hack id: {str(hack.id)}\nHack name: {name}\nHack authors: {authors}');
    #     answer = input("Is this the hack you're playing? [Y/n]");

    #     if answer.lower() == "y":
            
    #         start_presence_for(hack);

    #     else:
    #         print("Closing....");
    #         exit();

    # else: print("Snes9x was not detected! Closing...");