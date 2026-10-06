"""Tkinter-Oberfläche und thread-sichere Status-/Log-Ausgabe."""

import tkinter as tk
from tkinter import scrolledtext

from config import WINDOW_WIDTH, WINDOW_HEIGHT, CANVAS_HEIGHT

# ============================================================
# GUI
# ============================================================

root = tk.Tk()

root.title(
    "GENESIS"
)

root.geometry(
    f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
)

root.configure(
    bg="black"
)

canvas = tk.Canvas(
    root,
    width=WINDOW_WIDTH,
    height=CANVAS_HEIGHT,
    bg="black",
    highlightthickness=0
)

canvas.pack(
    fill="x"
)

square_size = 40

square = canvas.create_rectangle(
    WINDOW_WIDTH // 2 - square_size // 2,
    CANVAS_HEIGHT // 2 - square_size // 2,
    WINDOW_WIDTH // 2 + square_size // 2,
    CANVAS_HEIGHT // 2 + square_size // 2,
    fill="white",
    outline=""
)

status_label = tk.Label(
    root,
    text="GENESIS wird gestartet...",
    fg="white",
    bg="black",
    font=("Consolas", 12)
)

status_label.pack(
    pady=8
)

log = scrolledtext.ScrolledText(
    root,
    bg="#111111",
    fg="white",
    insertbackground="white",
    font=("Consolas", 10),
    wrap="word"
)

log.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

log.configure(
    state="disabled"
)


def write_log(text):

    def update():

        log.configure(
            state="normal"
        )

        log.insert(
            "end",
            text
        )

        log.see(
            "end"
        )

        log.configure(
            state="disabled"
        )

    root.after(
        0,
        update
    )


def update_status(text):

    root.after(
        0,
        lambda: status_label.config(
            text=text
        )
    )
