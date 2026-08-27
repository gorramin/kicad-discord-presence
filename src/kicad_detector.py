# IMPORT LIBRARIES -------------------------------------------------------------------------


import ctypes
from ctypes import wintypes
import re
import psutil


# WINDOWS API CONFIGURATION ----------------------------------------------------------------


user32 = ctypes.WinDLL("user32", use_last_error=True)

GetForegroundWindow = user32.GetForegroundWindow
GetForegroundWindow.restype = wintypes.HWND

GetWindowTextW = user32.GetWindowTextW
GetWindowTextLengthW = user32.GetWindowTextLengthW

EnumWindows = user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(
    wintypes.BOOL,
    wintypes.HWND,
    wintypes.LPARAM
)

IsWindowVisible = user32.IsWindowVisible
IsWindowVisible.argtypes = [wintypes.HWND]
IsWindowVisible.restype = wintypes.BOOL


# KICAD AND ACTIVE WINDOW DETECTION ----------------------------------------------------------------


def get_open_kicad_tools():

    # Return the currently open KiCad tool
    tools = []

    def callback(hwnd, lParam):

        if not IsWindowVisible(hwnd):
            return True

        length = GetWindowTextLengthW(hwnd)

        if length == 0:
            return True

        buffer = ctypes.create_unicode_buffer(length + 1)

        GetWindowTextW(
            hwnd,
            buffer,
            length + 1
        )

        title = buffer.value

        tool = get_tool_from_title(title)

        if tool and tool not in tools:
            tools.append(tool)

        return True

    EnumWindows(
        EnumWindowsProc(callback),
        0
    )

    return tools


def get_active_window_title():

    # Return the title of the currently focused window
    hwnd = GetForegroundWindow()

    if not hwnd:
        return ""

    length = GetWindowTextLengthW(hwnd)

    if length == 0:
        return ""

    buffer = ctypes.create_unicode_buffer(length + 1)

    GetWindowTextW(
        hwnd,
        buffer,
        length + 1,
    )

    return buffer.value


def kicad_is_running():

    # Return True if kicad.exe is currently running
    for process in psutil.process_iter(["name"]):
        try:
            name = process.info["name"]

            if name and name.lower() == "kicad.exe":
                return True

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return False


def get_tool_from_title(title):

    # Identify the KiCad application from its window title
    title = title.lower()
    pcbIsActive = "pcb editor" in title or "pcbnew" in title 
    schemIsActive = "schematic editor" in title or "eeschema" in title

    if pcbIsActive:
        return "pcb"

    if schemIsActive:
        return "schematic"

    if "kicad" in title:
        return "manager"

    return None


def get_project_name(title):

    # Extract the project name from a KiCad window title
    name = re.split(r"\s[—-]\s", title)[0].strip()

    name = re.sub(
        r"\.kicad_(pcb|sch|pro|prl)$",
        "",
        name,
        flags=re.IGNORECASE,
    )

    return name


def detect_kicad_state(last_tool, last_project):

    # Detect the current KiCad state
    if not kicad_is_running():
        return None, None

 
    title = get_active_window_title()

    active_tool = get_tool_from_title(title)

    open_tools = get_open_kicad_tools()

    if active_tool in ("pcb", "schematic"):

        project = get_project_name(title)

        return active_tool, project

    if active_tool == "manager":

        if "pcb" in open_tools or "schematic" in open_tools:

            if last_tool in ("pcb", "schematic"):
                return last_tool, last_project

            if "pcb" in open_tools:
                return "pcb", None

            if "schematic" in open_tools:
                return "schematic", None

        return "manager", None

    if last_tool in ("pcb", "schematic"):
        return last_tool, last_project

    if "pcb" in open_tools:
        return "pcb", None

    if "schematic" in open_tools:
        return "schematic", None

    if "manager" in open_tools:
        return "manager", None

    return None, None
