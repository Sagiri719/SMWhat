import logging;
import settings;
import json;

from utils import resource_path;

logger = logging.getLogger(__name__);

FALLBACK_LANG = 'en';

def import_translation(lang: str) -> dict:
    """Import the translation file for the given language."""
    
    fallback_translation: dict = {};
    with open(resource_path(f'presentation/languages/{FALLBACK_LANG}.json'), 'r', encoding='utf-8') as f:
        fallback_translation = json.load(f);

    file: str = f'presentation/languages/{lang}.json';
    try:

        with open(resource_path(file), 'r', encoding='utf-8') as f:
            translation = json.load(f);

        # Use fallback to fill in missing keys
        for key, value in fallback_translation.items():
            if key not in translation:
                translation[key] = value;

    except FileNotFoundError:
        logger.error(f"Translation file for '{lang}' not found. Falling back to '{FALLBACK_LANG}'.");
        translation = fallback_translation;

    except json.JSONDecodeError:
        logger.exception(f"Error decoding JSON for '{lang}'. Falling back to '{FALLBACK_LANG}'.");
        translation = fallback_translation;

    return translation;

def t(key) -> str:
    """Translate the given key using the current language."""
    return settings.app_config["language"].get(key, key);