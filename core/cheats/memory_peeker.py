""" Peek the emulator memory """
import logging
from core.cheats.memory_domains import Domains
from core.win32com import query_cheat_server;

logger = logging.getLogger(__name__);

def get_rom_name() -> str:
    """Get the name of the ROM currently loaded in the emulator."""
    command = f"rmn";
    try:
        
        res = query_cheat_server(command);
        if res == "Null":
            logger.error("Failed to get ROM name: No response from server.");
            return None;

        if res.startswith("Error:"):
            logger.error(f"Failed to get ROM name: {res}");
            return None;

        return res.strip();

    except Exception as e:
        logger.error(f"Failed to get ROM name: {e}");
        return None;

def read_memory_address(address: int, domain: Domains) -> int:
    """Read a memory address from the emulator."""
    command = f"READ {domain.value} {address}";