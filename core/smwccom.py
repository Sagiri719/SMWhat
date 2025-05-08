"""
Communication with the SMW Central API and website.
"""

import logging;
import requests;
import bs4;
import re;

import json;

import core.api as SMWC;

from persistence.persistence import get_hack_alias;
import utils;

SMW_IMAGE_BASE = "https://dl.smwcentral.net/image";
VERSION_REGEX = r"(?:v|version)?\s*(\d+\.\d+(?:\.\d+)?)";

def sanitize_rom_name(rom_name: str) -> str:

    # Attemp to get clean hack name (remove version)
    clean_name: str = re.sub(VERSION_REGEX, "", rom_name).strip();
    clean_name = clean_name.replace("-", " ").replace("_", " ").strip();

    if "  " in clean_name:
        place: int = clean_name.index("  ");
        clean_name = clean_name[:place].strip();

    return clean_name;

def get_hack_by_name(hack_name: str):
    """ Get the hack from smwcentral by loose name """

    # Search for aliases first
    window_name = utils.get_window_rom_name();
    alias: str = get_hack_alias(window_name);

    if alias is not None:
        #print(f"Found alias: {alias} for {window_name}");
        hack_name = alias;

    # Finding romhack information from smw central
    clean_name = sanitize_rom_name(hack_name);
        
    # Find results from search
    #results = get_section_list(Section.SMW.HACKS, filters=filter_param);
    results = SMWC.query_by_hack_name(clean_name);

    if len(results) <= 0:
        return None;

    # Get the first hack
    #return results.data[0];

    # Find closest match
    closest_match: int = -1;
    closest_hack: File = results[0];
    for hack in results:
        
        dist: int = utils.levenshtein_distance(hack["name"], clean_name);
        #print(f"Distance: {dist} for {hack.name} vs {clean_name}");

        if dist < closest_match or closest_match == -1:
            closest_match = dist;
            closest_hack = hack;

    from presentation.hack_content import map_hack_content;
    return map_hack_content(closest_hack);

def search_for_hack(name) -> list:
    """ Search for a hack by name """

    # Find results from search
    results = SMWC.query_by_hack_name(name);

    if len(results) <= 0:
        return None;

    # Map results to HackContent
    from presentation.hack_content import map_hack_content;
    results = [map_hack_content(hack) for hack in results];

    return results;

def get_hack_images(id: int) -> str:
    """ Get the screenshots of a hack """

    url:str = "https://www.smwcentral.net/?p=section&a=details&id=" + str(id);
    logging.info(url);
    document = requests.get(url);

    # Get all links where title is image
    soup = bs4.BeautifulSoup(document.text, "html.parser");
    script_tag = soup.find("script", text=re.compile(r"SMWCentral\.Slideshow\.onLoad"));

    # Extract the JavaScript object as a string
    script_content = script_tag.string;

    # Use regular expressions to extract the JavaScript object from the script content
    pattern = re.compile(r"SMWCentral\.Slideshow\.onLoad\s*=\s*(\[{.*?}\]);", re.DOTALL);
    match = pattern.search(script_content);

    if match:
        # This is dumb, but we need to replace single quotes with double quotes to make the JSON valid
        json_data = match.group(1).replace("'", "\"").replace("element", "\"element\"").replace("images", "\"images\"");    
        data = json.loads(json_data);
        
        # Get the first element of 'images'
        first_image_url = data[0]['images'][0];
        return first_image_url;

    return "";