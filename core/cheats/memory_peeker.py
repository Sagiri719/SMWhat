""" Peek the emulator memory """
import logging
import json
import threading

from core.cheats.memory_domains import Domains
from core.win32com import query_cheat_server;

logger = logging.getLogger(__name__);

# List of watching threads
watching_threads = [];

def get_rom_name() -> str:
    """Get the name of the ROM currently loaded in the emulator."""
    command = f"rmn";
    try:
        
        res = query_cheat_server(command);
        if res == "Null":
            logger.error("Failed to get ROM name: No response from server.");
            return None;

        if res.startswith("ERR:"):
            logger.error(f"Failed to get ROM name: {res}");
            return None;

        return res.strip();

    except Exception as e:
        logger.error(f"Failed to get ROM name: {e}");
        return None;

def read_memory_address(address: int, domain: Domains) -> int:
    """Read a memory address from the emulator."""
    command = f"read {domain.value} {address}";

    try:

        res = query_cheat_server(command);
        if res == "Null":
            logger.error("Failed to read memory address: No response from server.");
            return None;

        if res.startswith("ERR:"):
            logger.error(f"Failed to read memory address: {res}");
            return None;

        response_object = json.loads(res);
        byte_array = response_object.get("data", []);
        
        return int.from_bytes(byte_array, byteorder='little');

    except Exception as e:
        logger.error(f"Failed to read memory address: {e}");
        return None;

def watch_memory_address(address: int, domain: Domains, callback, delay=0.1) -> None:
    """Watch a memory address in the emulator and call the callback when it changes."""

    def watch_address(address: int, domain: Domains, callback, delay) -> None:
        
        logger.info(f"Starting to watch memory address {address} in domain {domain.value} from thread {threading.current_thread().name}");
        previous_value: int = -1;
        while True:
            value = read_memory_address(address, domain);
            if value is not None:
                
                if value != previous_value:
                    callback(value);
                
                previous_value = value;
            else:
                logger.error(f"Failed to read memory address {address} in domain {domain.value}");

            threading.Event().wait(delay);
    
    watcher_thread = threading.Thread(target=watch_address, args=(address, domain, callback, delay), daemon=True);
    watcher_thread.start();
    watching_threads.append(watcher_thread);

def kill_watching_threads() -> None:
    """Kill all watching threads."""
    for thread in watching_threads:
        if thread.is_alive():
            logger.info(f"Killing watching thread: {thread.name}");
            thread.join(timeout=0.1); # Wait for the thread to finish if it's still running with a tomeout
    watching_threads.clear();
    logger.info("All watching threads have been killed.");

def read_memory_bulk(address: int, size: int, domain: Domains) -> bytearray:
    """Read a memory address array from the emulator."""
    command = f"read {domain.value} {address} {size}";

    try:

        res = query_cheat_server(command);
        if res == "Null":
            logger.error("Failed to read memory address: No response from server.");
            return None;

        if res.startswith("ERR:"):
            logger.error(f"Failed to read memory address: {res}");
            return None;

        response_object = json.loads(res);
        byte_array = response_object.get("data", []);
        
        buffer = bytearray();
        for byte in byte_array:
            buffer.append(byte);

        return buffer;

    except Exception as e:
        logger.error(f"Failed to read memory address: {e}");
        return None;