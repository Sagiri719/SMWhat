"""
Communicate with Windows api to find emulator window

author: @Sagiri721
"""

import os;
import win32gui;
import win32process;
import win32pipe;
import win32file;
import psutil
import time
import threading
import logging

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

def query_namedpipe_server(message: str):
    
    """Query the named pipe server for the active emulator"""
    NAMEDPIPE_SERVER_NAME = "SMWhatCheatsPipe";

    pipe_name = f"\\\\.\\pipe\\{NAMEDPIPE_SERVER_NAME}";    
    handle = win32file.CreateFile(
        pipe_name,
        win32file.GENERIC_READ | win32file.GENERIC_WRITE,
        0,  # No sharing
        None,  # Default security attributes
        win32file.OPEN_EXISTING,
        0,  # No special attributes
        None  # No template file
    );

    try:
        # Write message to the named pipe server
        if message:
            win32file.WriteFile(handle, (message + "\n").encode('utf-8'));
            logger.info(f"Sent message to named pipe server: {message}");
        else:
            logger.warning("No message provided to send to named pipe server");

        # Read data from the pipe
        data = win32file.ReadFile(handle, 1024);
        if data:
            
            print(f"message: {data}")

        else:
            logger.warning("No data received from named pipe server");
            return None;
    except Exception as e:
        logger.exception(f"Error reading from named pipe server: {e}");
        return None;
    finally:
        win32file.CloseHandle(handle);