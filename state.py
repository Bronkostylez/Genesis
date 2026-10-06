"""Weltbaum, Aktionshistorie und Modell-Zusammenfassung."""

import json

from config import GENESIS_DIR, MAX_FILES, MAX_ACTION_HISTORY

# ============================================================
# WELTBAUM
# ============================================================

def get_world_tree():

    lines = []
    file_counter = 0

    def walk(directory, prefix=""):

        nonlocal file_counter

        if file_counter >= MAX_FILES:
            return

        try:

            children = sorted(
                directory.iterdir(),
                key=lambda p: (
                    not p.is_dir(),
                    p.name.lower()
                )
            )

        except Exception:

            return

        for child in children:

            if file_counter >= MAX_FILES:
                break

            if child.is_dir():

                lines.append(
                    f"{prefix}[DIR] {child.name}/"
                )

                walk(
                    child,
                    prefix + "    "
                )

            else:

                file_counter += 1

                try:
                    size = child.stat().st_size
                except Exception:
                    size = 0

                lines.append(
                    f"{prefix}[FILE] {child.name} ({size} Bytes)"
                )

    walk(GENESIS_DIR)

    if file_counter >= MAX_FILES:

        lines.append(
            "...[Dateiliste begrenzt]..."
        )

    if not lines:

        return "[LEER]"

    return "\n".join(lines)


# ============================================================
# AKTIONSHISTORIE
# ============================================================

def format_action_history(action_history):

    if not action_history:

        return "Noch keine vorherigen Schritte."

    lines = []

    for entry in action_history[-MAX_ACTION_HISTORY:]:

        turn = entry["turn"]
        operation = entry["operation"]
        path = entry.get("path", "")
        status = entry["status"]

        if path:
            action = f"{operation.upper()} {path}"
        else:
            action = operation.upper()

        lines.append(
            f"Turn {turn}: {action} -> {status}"
        )

    return "\n".join(lines)


def add_action_history(
    action_history,
    turn,
    command,
    result
):

    operation = command.get(
        "operation",
        "unknown"
    )

    path = command.get(
        "path",
        ""
    )

    status = (
        "erfolgreich"
        if result.get("ok")
        else "fehlgeschlagen"
    )

    action_history.append({
        "turn": turn,
        "operation": operation,
        "path": path,
        "status": status
    })

    if len(action_history) > MAX_ACTION_HISTORY:

        del action_history[
            :-MAX_ACTION_HISTORY
        ]


# ============================================================
# WELTZUSTAND FÜR GENESIS
# ============================================================

def world_summary(
    last_result,
    action_history
):

    tree = get_world_tree()

    history = format_action_history(
        action_history
    )

    result_text = json.dumps(
        last_result,
        ensure_ascii=False,
        indent=2
    )

    changed = (
        last_result.get("interface")
        in {
            "create",
            "edit",
            "delete"
        }
        and last_result.get("ok")
    )

    return f"""
AKTUELLER ZUSTAND DER WELT

{tree}

LETZTES ERGEBNIS

{result_text}

LETZTE SCHRITTE

{history}

WELT VERÄNDERT DURCH LETZTEN SCHRITT:
{"JA" if changed else "NEIN"}

DENKE DARAN:

- Wiederhole keine identische erfolgreiche Aktion ohne neuen Grund.
- Wiederhole fehlgeschlagene Aktionen nicht blind.
- Wenn ein Programm einen Fehler erzeugt hat, kannst du diesen Fehler
  untersuchen und das Programm verbessern.
- CREATE + EXECUTE + EDIT + EXECUTE kann ein möglicher
  Entwicklungszyklus sein.
- Es gibt keinen vorgeschriebenen Technologiebaum.
- Es gibt kein vorgeschriebenes Endziel.

Wähle jetzt genau EINEN nächsten Schritt.
""".strip()

