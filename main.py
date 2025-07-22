"""
    SMWCentral Romhack detector
    author: @Sagiri721
"""
from presentation.ui import UI;
from settings import init_settings, app_config;
from core.constants import UI_MODES;

# Initialize settings
init_settings();

if __name__ == "__main__":

    # Start UI
    app: UI = UI_MODES[app_config["ui"]]();
    app.run();