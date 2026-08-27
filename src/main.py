# IMPORT LIBRARIES -------------------------------------------------------------------------


import threading
import time

from config import CHECK_EVERY
from discord_rpc import DiscordRPC
from kicad_detector import detect_kicad_state
from tray import TrayApp


# APPLICATION STATE -----------------------------------------------------------------------


running = True

rpc = DiscordRPC()

previous_state = None
start_time = int(time.time())


# FUNCTIONS -------------------------------------------------------------------------------


def stop_application():

    # Exit
    global running

    running = False

    print("\nStopping...")

    rpc.close()


def rpc_worker(tray):

    # Discord and KiCad worker 
    global previous_state
    global start_time

    while running:

        # Try to connect to Discord if we are not connected
        if rpc.handle is None:

            tray.set_discord_status("Connecting...")

            try:

                print("[Discord] Connecting...")

                rpc.connect()

                print("[Discord] Connected.")

                tray.set_discord_status("Connected")

                # Start a new Rich Presence timer
                start_time = int(time.time())

                # Force the current KiCad state to be sent
                previous_state = None

            except Exception as e:

                print(
                    f"[Discord] Connection failed: {e}"
                )

                tray.set_discord_status("Disconnected")

                print(
                    f"[Discord] Retrying in {CHECK_EVERY} seconds..."
                )

                time.sleep(CHECK_EVERY)

                continue

        # Detect the current KiCad state
        state = detect_kicad_state(
            previous_state[0] if previous_state else None,
            previous_state[1] if previous_state else None
        )


        # Update tray KiCad status
        tool, project = state

        if tool is None:
            tray.set_kicad_status("Not running")

        else:

            if project:

                tray.set_kicad_status(
                    f"{tool}: {project}"
                )

            else:

                tray.set_kicad_status(tool)

        # Only update Discord when KiCad state changes
        if state != previous_state:

            print(
                f"[EVENT] KiCad state changed: "
                f"[TOOL : {tool} | PROJECT : {project}]"
            )

            try:

                if tool is None:

                    rpc.clear_presence()

                    start_time = int(time.time())

                else:

                    rpc.set_presence(
                        tool,
                        project,
                        start_time
                    )

                previous_state = state

            except Exception as e:

                print(
                    f"[Discord] Connection lost: {e}"
                )

                tray.set_discord_status(
                    "Disconnected"
                )

                rpc.close()

                # The next loop will try to reconnect
                continue

        time.sleep(CHECK_EVERY)


# MAIN ------------------------------------------------------------------------------------


def main():

    tray = TrayApp(
        stop_application
    )

    worker = threading.Thread(
        target=rpc_worker,
        args=(tray,),
        daemon=True
    )

    worker.start()

    # Run the Windows tray application
    tray.run()


if __name__ == "__main__":
    main()


