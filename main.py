"""Startpunkt von GENESIS. Starten mit: python main.py"""

import threading


def main():
    # Die GUI wird erst beim Start aufgebaut, nicht beim Import von main.
    from gui import root
    from runtime import genesis_loop

    thread = threading.Thread(target=genesis_loop, daemon=True)
    thread.start()
    root.mainloop()


if __name__ == "__main__":
    main()

