"""Entwicklungsschleife: Modell fragen, Entscheidung ausführen und Zustand aktualisieren."""

import json

from commands import parse_command, validate_command, execute_interface
from gui import update_status, write_log
from instructions import GENESIS_INSTRUCTION
from ollama_client import ask_genesis
from state import world_summary, add_action_history, get_world_tree
from world import reset_instance

# ============================================================
# GENESIS LOOP
# ============================================================

def genesis_loop():

    try:

        reset_instance()

        action_history = []

        messages = [
            {
                "role": "system",
                "content": GENESIS_INSTRUCTION
            },
            {
                "role": "user",
                "content": world_summary(
                    {
                        "ok": True,
                        "interface": "initialization",
                        "message": "Die Welt wurde erschaffen."
                    },
                    action_history
                )
            }
        ]

        turn = 0

        while True:

            turn += 1

            update_status(
                f"GENESIS – Turn {turn}"
            )

            try:

                raw_response = ask_genesis(
                    messages
                )

                command = parse_command(
                    raw_response
                )

                valid, error = validate_command(
                    command
                )

                if not valid:

                    result = {
                        "ok": False,
                        "interface": "validation",
                        "error": error
                    }

                else:

                    result = execute_interface(
                        command
                    )

            except Exception as e:

                command = {
                    "operation": "none",
                    "reason": "Technischer Fehler."
                }

                result = {
                    "ok": False,
                    "interface": "error",
                    "error": str(e)
                }

            add_action_history(
                action_history,
                turn,
                command,
                result
            )

            operation = command.get(
                "operation",
                "unknown"
            )

            reason = command.get(
                "reason",
                ""
            )

            command_text = json.dumps(
                command,
                ensure_ascii=False,
                indent=2
            )

            result_text = json.dumps(
                result,
                ensure_ascii=False,
                indent=2
            )

            tree = get_world_tree()

            log_text = (
                "\n"
                + "=" * 50
                + "\n"
                + f" GENESIS – TURN {turn}\n"
                + "=" * 50
                + "\n\n"
                + "ENTSCHEIDUNG\n\n"
                + command_text
                + "\n\n"
                + "-" * 44
                + "\n\n"
                + "KURZE BEGRÜNDUNG\n\n"
                + reason
                + "\n\n"
                + "-" * 44
                + "\n\n"
                + "ERGEBNIS\n\n"
                + result_text
                + "\n\n"
                + "=" * 44
                + "\n\n"
                + "AKTUELLER ENTWICKLUNGSSTAND\n\n"
                + tree
                + "\n"
            )

            write_log(
                log_text
            )

            # ------------------------------------------------
            # Modellkontext aktualisieren
            # ------------------------------------------------

            messages.append({
                "role": "assistant",
                "content": command_text
            })

            messages.append({
                "role": "user",
                "content": world_summary(
                    result,
                    action_history
                )
            })

            # ------------------------------------------------
            # Kontext begrenzen
            # ------------------------------------------------

            if len(messages) > 22:

                messages = (
                    [messages[0]]
                    + messages[-21:]
                )


    except Exception as e:

        update_status(
            f"GENESIS Fehler: {e}"
        )

        write_log(
            "\n\nFATALER FEHLER:\n"
            + str(e)
            + "\n"
        )

