# IMPORT LIBRARIES -------------------------------------------------------------------------


import os
import sys
import threading
import webbrowser

import pystray
from PIL import Image


# FIX PATH ISSUE  -------------------------------------------------------------------------


def resource_path(relative_path):

    if getattr(sys, "frozen", False):
        # **This for  PyInstaller
        base_path = sys._MEIPASS
    else:
        # **This for Normal Python execution
        base_path = os.path.dirname(
            os.path.abspath(__file__)
        )

    return os.path.join(
        base_path,
        relative_path
    )


# TRAY CLASS  -------------------------------------------------------------------------


class TrayApp:

    def __init__(self, on_exit):

        # Initialize
        self.on_exit = on_exit
        self.icon = None

        self.discord_status = "Waiting..."
        self.kicad_status = "Waiting..."

        self.lock = threading.Lock()



    def set_discord_status(self, status):

        # Update the Discord status
        with self.lock:
            self.discord_status = status

        self._update_menu()

    def set_kicad_status(self, status):

        # Update the KiCad status
        with self.lock:
            self.kicad_status = status

        self._update_menu()

    def _get_discord_status(self):

        # Return the current Discord status
        with self.lock:
            return self.discord_status

    def _get_kicad_status(self):

        # Return the current KiCad status
        with self.lock:
            return self.kicad_status

    def _update_menu(self):

        # Update the system tray menu
        if self.icon is not None:
            self.icon.menu = self._create_menu()

    def _create_menu(self):

        # Create the system tray menu
        return pystray.Menu(

            pystray.MenuItem(
                f"Discord: {self._get_discord_status()}",
                None,
                enabled=False
            ),

            pystray.MenuItem(
                f"KiCad: {self._get_kicad_status()}",
                None,
                enabled=False
            ),

            pystray.Menu.SEPARATOR,

            pystray.MenuItem(
                "View Source Code on GitHub",
                self.open_github
            ),

            pystray.Menu.SEPARATOR,

            pystray.MenuItem(
                "Exit",
                self._exit
            )
        )

    def _exit(self, icon, item):

        # Exit the application
        self.on_exit()

        icon.stop()

    def run(self):

        # Start the system tray application
        icon_path = resource_path(
            "assets/kicad-rpc-icon.ico"
        )

        image = Image.open(icon_path)

        self.icon = pystray.Icon(
            "KiCad RPC",
            image,
            "KiCad Discord RPC",
            self._create_menu()
        )

        self.icon.run()

    def open_github(self, icon, item):

        # Open the project GitHub repository
        webbrowser.open(
            "https://github.com/gorramin/kicad-discord-presence"
        )
