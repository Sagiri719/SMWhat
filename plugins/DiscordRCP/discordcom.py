import logging

from core.hack_content import HackContent

import time
from pypresence import Presence

logger = logging.getLogger(__name__);

CLIENT_ID = '1280548436843958282';

def start_presence_for(hack: HackContent) -> Presence:

    try:

        # Hack information
        image: str = hack.image_url;
        name: str = hack.title;
        authors: str = hack.author_as_string();

        # Setup discord
        RPC = Presence(CLIENT_ID);
        RPC.connect();

        RPC.update(state=f"By {authors}", details=f"Playing {name}", large_image=image)
        logger.info(f"Started Discord Rich Presence for {name} by {authors}");

        return RPC;
    except:
        return None;