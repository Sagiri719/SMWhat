"""
Communicate with Windows api to find emulator window

author: @Sagiri721
"""

import os;
import win32gui;
import win32process;
import psutil
import time
import threading
import logging
import socket;

from core.emulator import Emulator;

logger = logging.getLogger(__name__);

def get_pid_from_window_title(window_title: str) -> int:

    def winEnumHandler(hwnd, ctx):

        if win32gui.IsWindowVisible(hwnd):
            
            if window_title in win32gui.GetWindowText(hwnd):
                # Get the process ID
                _, pid = win32process.GetWindowThreadProcessId(hwnd);
                ctx.append(pid);
                
    # Get all open windows
    pids: list = [];
    win32gui.EnumWindows(winEnumHandler, pids);
    return pids[0] if len(pids) > 0 else -1;

def get_emulator_window(emu: Emulator) -> str:

    """Get the window name of a given emulator"""
    processes: list = [];
    def winEnumHandler(hwnd, ctx):

        if win32gui.IsWindowVisible(hwnd):
            name: str = win32gui.GetWindowText(hwnd);
            if(name.strip() != ""): processes.append(name);

    # Get all open windows
    win32gui.EnumWindows(winEnumHandler, None);
    # Find 
    proc_list: list = [p for p in processes if emu.window_name in p.lower()];
    window_name: str = "" if len(proc_list) == 0 else proc_list[0];

    return window_name;

def monitor_process_async(pid, on_exit, stop_event) -> threading.Thread:
    from core.constants import ACTIVE_MONITOR_SLEEP_DELAY;

    def monitor():
        try:
            process = psutil.Process(pid)
            while process.is_running() and process.status() != psutil.STATUS_ZOMBIE:
                if stop_event.is_set():
                    logger.info(f"Stopping process monitor for {pid}");
                    return;
                time.sleep(ACTIVE_MONITOR_SLEEP_DELAY);
            on_exit();
        except psutil.NoSuchProcess:
            logger.exception(f"Process {pid} doesn't exist anymore?");
            on_exit();

    thread = threading.Thread(target=monitor, daemon=True);
    thread.start();
    return thread;

def test_server_connection(retries: int = 3, delay: float = 0.5) -> bool:
    """Test if the server is reachable"""

    from core.constants import CHEAT_SERVER_HOST, CHEAT_SERVER_PORT
    for attempt in range(retries):
        try:
            with socket.create_connection((CHEAT_SERVER_HOST, CHEAT_SERVER_PORT), timeout=delay):
                logger.info("Server is reachable");
                return True
        except (socket.timeout, ConnectionRefusedError) as e:
            logger.warning(f"Attempt {attempt + 1}/{retries} failed: {e}")
            time.sleep(delay)

    logger.error("Failed to connect to the server after multiple attempts");
    return False;

def query_cheat_server(message: str):
    """Query the cheat server"""

    from core.constants import CHEAT_SERVER_HOST, CHEAT_SERVER_PORT
    with socket.create_connection((CHEAT_SERVER_HOST, CHEAT_SERVER_PORT), timeout=5) as sock:
        sock_file = sock.makefile(mode='rw');

        sock_file.write(message + "\n");
        sock_file.flush();

        response = sock_file.readline().strip();
        return response;