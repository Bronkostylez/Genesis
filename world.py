"""Welt zurücksetzen und Pfade auf die Welt begrenzen."""

import shutil

from config import BASE_DIR, GENESIS_DIR

# ============================================================
# INSTANZ ZURÜCKSETZEN
# ============================================================

def reset_instance():

    if GENESIS_DIR.exists():
        shutil.rmtree(GENESIS_DIR)

    GENESIS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    source_main = BASE_DIR / "templates" / "world_main.py.txt"
    target_main = GENESIS_DIR / "main.py"

    shutil.copy2(
        source_main,
        target_main
    )


# ============================================================
# SICHERER PFAD
# ============================================================

def safe_path(relative_path):

    if relative_path is None:
        raise ValueError(
            "Kein Pfad angegeben."
        )

    relative_path = str(
        relative_path
    ).strip()

    if not relative_path:
        raise ValueError(
            "Kein Pfad angegeben."
        )

    candidate = (
        GENESIS_DIR / relative_path
    ).resolve()

    root = GENESIS_DIR.resolve()

    try:
        candidate.relative_to(root)

    except ValueError:
        raise ValueError(
            "Ungültiger Pfad außerhalb der Genesis-Welt."
        )

    return candidate

