""" App constants"""
import logging;
from presentation.gui import GuiApp; 

LOGGING_LEVEL = logging.DEBUG;

LOG_FILE = "logs/smwhat.log";
PLUGIN_FOLDER = "plugins"; # Folder where plugins are stored
LICESE_FILE = "LICENSE";
SETTINGS_FILE = "settings.json";
DATAMAP_FILE = "persistence\data.json";
PLUGIN_CACHE_FILE = "persistence\plugin_data.json"; # File to store plugin cache

UI_MODES = [GuiApp]; # List of UI modes available
FALLBACK_LANG = 'en'; # Default language to use when translation is not found

BASE_URL = "https://www.smwcentral.net/ajax.php"  # Base URL for the SMWC API
HACK_SECTION = "smwhacks"; # Name of the section to query for hacks

TIMEOUT = 10  # Timeout for requests

SUPPORTED_LANGUAGES = ["en", "pt", "jp"];

ACTIVE_MONITOR_SLEEP_DELAY = 1; # The amount of time to wait before checking for active monitor again

VERSION = "1.0.1";
CHANGELOG = [
    {
        "version": "0.1.0",
        "date": "8/05/2025",
        "changes": [
            "Initial release",
            "SMWC API integration",
            "Discord Rich Presence integration",
            "Emulator searching",
            "Romhack searching and identification",
        ]
    },
    {
        "version": "1.0.0",
        "date": "10/05/2025",
        "changes": [
            "Plugin system",
            "Added DiscordRCP plugin"
            "Added HackTimer plugin"
        ]
    },
    {
        "version": "1.0.1",
        "date": "10/05/2025",
        "changes": [
            "Added MarqueeLabel for long hack names",
        ]
    }
];