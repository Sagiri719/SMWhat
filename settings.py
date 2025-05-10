import os;
import json;
import logging;
import datetime;

from core.emulator import snes9x, emulator_list, Emulator, get_emulator_by_name;
from presentation.translations import import_translation;
from persistence.persistence import init_persistence;

from core.constants import *
from utils import resource_path;

logger = logging.getLogger(__name__);

app_config = {
    "emulator": snes9x,
    "ui": 0,
    "lang": "en",
    "language": None,
    "debug": True,
}

def init_settings():
    global app_config;

    # Load settings from file
    load_settings_from_file();

    # Initilaize logging information
    init_logging();

    # Load language
    app_config["language"] = import_translation(app_config["lang"]);
    logger.info(f"Language set to {app_config['lang']}");

    # Get persistence data
    init_persistence();

def init_logging():

    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs");

    # Set up logging
    handlers = [logging.FileHandler(LOG_FILE)]
    if app_config["debug"]:
        handlers.append(logging.StreamHandler());

    logging.basicConfig(
        level=LOGGING_LEVEL,
        handlers=handlers
    );
    logger.info("\n\nApp started at " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"));


def load_settings_from_file():
    global app_config;

    if os.path.exists(resource_path(SETTINGS_FILE)):

        logger.info("Loading settings from settings.json...");

        with open(resource_path(SETTINGS_FILE), "r") as f:
            app_config = json.load(f);

        # Check if the emulator is valid
        for emulator in emulator_list:
            if emulator.display_name == app_config["emulator"]:
                app_config["emulator"] = emulator;
                break;

        if type(app_config["emulator"]) == str:
            logger.error("Nonsupported emulator in settings.json! Defaulting to Snes9x.");
            app_config["emulator"] = snes9x;

        # Check if the UI mode is valid
        if app_config["ui"] >= len(UI_MODES):
            logger.error("Nonsupported UI mode in settings.json! Defaulting to GUI.");
            app_config["ui"] = 0;

def change_language(lang):
    global app_config;

    # Check if the language is valid
    if lang not in ["en", "pt", "jp"]:
        logger.error("Nonsupported language! Defaulting to English.");
        lang = "en";

    app_config["lang"] = lang;
    app_config["language"] = import_translation(lang);
    logger.info(f"Language changed to {lang}");

    save_settings_to_file();

def change_emulator(emulator):
    global app_config;
    
    if type(emulator) == Emulator:
        app_config["emulator"] = emulator;
    else:
        logger.error("Nonsupported emulator! Defaulting to Snes9x.");
        return;

    logger.info(f"Emulator changed to {emulator.display_name}");
    save_settings_to_file();

def save_settings_to_file():
    global app_config;

    logger.info("Saving settings to settings.json...");

    with open(resource_path(SETTINGS_FILE), "w") as f:
        json.dump({
            "emulator": app_config["emulator"].display_name,
            "ui": app_config["ui"],
            "lang": app_config["lang"],
            "debug": app_config["debug"],
        }, f);

    logger.info("Settings saved.");

def clear_logs():
    global LOG_FILE;

    if os.path.exists(LOG_FILE):
        with open(resource_path(LOG_FILE), "w") as f:
            f.write("");
        logger.info("Logs cleared.");
    else:
        logger.error("Log file does not exist.");