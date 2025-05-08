"""
Talk to the SMWC API to get hack information.
"""

import requests;
import logging;

from core.end_points import Endpoints;

logger = logging.getLogger(__name__);

BASE_URL = "https://www.smwcentral.net/ajax.php"  # Base URL for the SMWC API
TIMEOUT = 10  # Timeout for requests

HACK_SECTION = "smwhacks";

def query_by_hack_name(name: str) -> list:

    params = {
        "a": Endpoints.SECTION_LIST.value,
        "s": HACK_SECTION,
        "u": 0,
        "f[name]": name
    }

    response = requests.get(BASE_URL, params=params, timeout=TIMEOUT);
    logger.debug(f"Request URL: {response.url}"); 

    if response.status_code == 200:
        data = response.json();
        
        if data["data"] is None or len(data["data"]) == 0:
            return [];

        return data["data"];

    raise requests.exceptions.HTTPError(
        f"Request failed with status code {response.status_code}"
    );