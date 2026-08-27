# KiCad DISCORD RPC CONFIGURATION ----------------------------------------------------------


# Windows Constants **DON'T CHANGE
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3

# Discord Application ID
CLIENT_ID = "1538923681781260339"

# How often the program checks for KiCad/window changes.
CHECK_EVERY = 0.5

# Discord Rich Presence asset keys.
IMAGES = {
    "manager": "kicad_icon",
    "pcb": "pcb_icon",
    "schematic": "schematic_icon",
}

# RPC Tool names.
TOOL_NAMES = {
    "manager": "KiCad Manager",
    "pcb": "PCB Design",
    "schematic": "Schematic Editor",
}

# Show the small KiCad logo in the bottom-right of the Rich Presence image.
SHOW_SMALL_ICON = True
