# IMPORT LIBRARIES -------------------------------------------------------------------------


import ctypes
import json
import struct
import time
import uuid
from ctypes import wintypes


from config import (
    CLIENT_ID,
    IMAGES,
    SHOW_SMALL_ICON,
    TOOL_NAMES,
    GENERIC_READ,
    GENERIC_WRITE,
    OPEN_EXISTING
)


# WINDOWS API SETUP ------------------------------------------------------------------------


kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)


CreateFileW = kernel32.CreateFileW
CreateFileW.argtypes = [
    wintypes.LPCWSTR,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.LPVOID,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.HANDLE,
]
CreateFileW.restype = wintypes.HANDLE


WriteFile = kernel32.WriteFile
WriteFile.argtypes = [
    wintypes.HANDLE,
    wintypes.LPVOID,
    wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD),
    wintypes.LPVOID,
]
WriteFile.restype = wintypes.BOOL


ReadFile = kernel32.ReadFile
ReadFile.argtypes = [
    wintypes.HANDLE,
    wintypes.LPVOID,
    wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD),
    wintypes.LPVOID,
]
ReadFile.restype = wintypes.BOOL


CloseHandle = kernel32.CloseHandle
CloseHandle.argtypes = [wintypes.HANDLE]


INVALID_HANDLE = wintypes.HANDLE(-1).value


# LOGGING ----------------------------------------------------------------------------------


def log(message):

    # Print a timestamped message
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


# DISCORD IPC ------------------------------------------------------------------------------


def connect_to_discord():

    # Find Discord's named IPC pipe and connect to it
    for pipe_number in range(10):
        pipe_name = rf"\\.\pipe\discord-ipc-{pipe_number}"

        handle = CreateFileW(
            pipe_name,
            GENERIC_READ | GENERIC_WRITE,
            0,
            None,
            OPEN_EXISTING,
            0,
            None,
        )

        if handle != INVALID_HANDLE:
            log(f"Connected to Discord (IPC {pipe_number})")
            return handle

    raise RuntimeError(
        "Could not connect to Discord. "
        "Make sure Discord is running."
    )


def send(handle, opcode, payload):

    # Send one IPC packet to Discord
    data = json.dumps(payload).encode("utf-8")
    header = struct.pack("<II", opcode, len(data))
    message = header + data

    buffer = ctypes.create_string_buffer(message)
    written = wintypes.DWORD()

    success = WriteFile(
        handle,
        buffer,
        len(message),
        ctypes.byref(written),
        None,
    )

    if not success:
        raise ConnectionError("Failed to send data to Discord.")


def read_exact(handle, size):

    # Read exactly 'size' bytes from Discord's IPC pipe
    data = b""

    while len(data) < size:
        chunk = ctypes.create_string_buffer(size - len(data))
        received = wintypes.DWORD()

        success = ReadFile(
            handle,
            chunk,
            size - len(data),
            ctypes.byref(received),
            None,
        )

        if not success or received.value == 0:
            raise ConnectionError("Discord closed the IPC pipe.")

        data += chunk.raw[:received.value]

    return data


def receive(handle):

    # Read one complete IPC message and decode its JSON
    header = read_exact(handle, 8)
    opcode, length = struct.unpack("<II", header)

    payload = read_exact(handle, length)

    return json.loads(payload)


def handshake(handle):

    # Perform the Discord IPC handshake
    send(
        handle,
        0,
        {
            "v": 1,
            "client_id": CLIENT_ID,
        },
    )

    response = receive(handle)

    if response.get("evt") != "READY":
        raise RuntimeError(f"Discord handshake failed: {response}")


# RICH PRESENCE ----------------------------------------------------------------------------


def set_presence(handle, tool, project, start_time):

    # Build and send the current KiCad Rich Presence
    if tool == "manager":
        details = "KiCad Manager"
        state = None
    else:
        details = f"Tool : {TOOL_NAMES[tool]}"
        state = f"Designing {project}" if project else None

    assets = {
        "large_image": IMAGES[tool],
        "large_text": TOOL_NAMES[tool],
    }

    if SHOW_SMALL_ICON and tool != "manager":
        assets.update({
            "small_image": "kicad_small_icon",
            "small_text": "KiCad EDA",
        })

    activity = {
        "type": 0,
        "details": details,
        "assets": assets,
        "timestamps": {
            "start": start_time,
        },
    }

    if state:
        activity["state"] = state

    send(
        handle,
        1,
        {
            "cmd": "SET_ACTIVITY",
            "args": {
                "pid": kernel32.GetCurrentProcessId(),
                "activity": activity,
            },
            "nonce": str(uuid.uuid4()),
        },
    )

    receive(handle)


def clear_presence(handle):

    # Remove the Rich Presence from Discord
    send(
        handle,
        1,
        {
            "cmd": "SET_ACTIVITY",
            "args": {
                "pid": kernel32.GetCurrentProcessId(),
                "activity": None,
            },
            "nonce": str(uuid.uuid4()),
        },
    )

    receive(handle)


# RPC CLASS -----------------------------------------------------------------------------------


class DiscordRPC:

    def __init__(self):

        # Initialize the Discord RPC connection
        self.handle = None


    def connect(self):

        # Connect to Discord and perform the handshake
        self.handle = connect_to_discord()

        handshake(self.handle)

        log("Discord RPC ready")

    def set_presence(self, tool, project, start_time,):

        # Set the Discord Rich Presence
        if self.handle is None:
            raise ConnectionError(
                "Discord RPC is not connected."
            )

        set_presence(
            self.handle,
            tool,
            project,
            start_time,
        )

    def clear_presence(self):

        # Clear the current Discord Rich Presence
        if self.handle is None:
            return

        clear_presence(
            self.handle
        )

    def close(self):

        # Close the Discord IPC connection
        if self.handle is not None:

            CloseHandle(
                self.handle
            )

            self.handle = None

            log("Discord IPC connection closed")
