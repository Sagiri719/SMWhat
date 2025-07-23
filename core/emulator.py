class Emulator:

    def __init__(self, display_name, window_name, hack_name_getter):
        self.display_name = display_name
        self.window_name = window_name.lower()
        self.hack_name_getter = hack_name_getter

# Emulator definition
snes9x = Emulator("Snes9x", "Snes9x", lambda wname: wname.split(" - ")[0]);
bizhawk = Emulator("BizHawk (recommended)", "BizHawk", lambda wname: wname.split("[SNES]")[0].strip());

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