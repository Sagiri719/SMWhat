import os;
import sys;

def resource_path(relative_path):
    """ Get the absolute path to the resource"""

    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def levenshtein_distance(s1, s2):
    """
    Calculate the Levenshtein distance between two strings.
    """
    
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def get_window_rom_name() -> str:
    """ Get the name of the rom from the emulator window name"""
        
    from core.win32com import get_emulator_window;
    import settings;

    window_name: str = get_emulator_window(settings.app_config["emulator"]);

    if (window_name != ""):
        window_name = settings.app_config["emulator"].hack_name_getter(settings.app_config["emulator"].hack_name_getter(window_name));

    return window_name;

def get_app_license() -> str:
    """ Get the license of the app from the license file"""
    import settings;
    with open(settings.LICESE_FILE, "r") as f:
        return f.read();

def get_app_version() -> str:
    import settings;
    return f'SMWhat v{settings.VERSION} by Sagiri';

def get_source_code() -> str:
    return "https://github.com/Sagiri721/SMWhat";

def get_icon():
    return resource_path("res/icon.ico");