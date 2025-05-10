""" 
Controller pattern to seperate the logic from the presentation
"""

from core.hack_content import HackContent
import threading;

class HackController:

    def __init__(self):
            
        self.hack: HackContent = None;
        self.hack_image_dimensions = (200, 200);

        self.monitor_thread: threading.Thread = None;
        self.monitor_stop_event: threading.Event = None;

        self.plugin_controls = {
            "next": "<Left>",
            "previous": "<Right>",
        };

    def get_hack(self) -> HackContent:
        return self.hack;