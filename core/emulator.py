class Emulator:

    def __init__(self, display_name, window_name, hack_name_getter, support_cheat_server=False):
        self.display_name = display_name;
        self.window_name = window_name.lower();
        self.hack_name_getter = hack_name_getter;
        self.support_cheat_server = support_cheat_server;

    def __str__(self):
        return f"{self.window_name} (supports cheat server: {self.support_cheat_server})";

def snes9x_name_getter(window_name: str) -> str:
    if " - " in window_name:
        return window_name.split(" - ")[0];
    return None;

def bizhawk_name_getter(window_name: str) -> str:
    
    if "[SNES]" in window_name:
        return window_name.split("[SNES]")[0].strip();
    return None;

# Emulator definition
snes9x = Emulator("Snes9x", "Snes9x", lambda wname: snes9x_name_getter(wname), False);
bizhawk = Emulator("BizHawk (recommended)", "BizHawk", lambda wname: bizhawk_name_getter(wname), True);

emulator_list = [
    snes9x,
    bizhawk
];

def get_emulator_by_name(name):
    """
    Get the emulator by name.
    """
    for emulator in emulator_list:
        if emulator.display_name.lower() == name.lower():
            return emulator
    return None;