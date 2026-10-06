"""Entscheidungen parsen, prüfen und an die passende Operation weitergeben."""

import json

from interfaces import (interface_view, interface_create, interface_edit, interface_delete, interface_execute)

# ============================================================
# VALIDIERUNG
# ============================================================

def validate_command(command):

    if not isinstance(command, dict):

        return (
            False,
            "Die Entscheidung muss ein JSON-Objekt sein."
        )

    operation = command.get("operation")

    valid_operations = {
        "view",
        "create",
        "edit",
        "delete",
        "execute",
        "none"
    }

    if operation not in valid_operations:

        return (
            False,
            "Ungültige Operation."
        )

    if operation == "view":

        if not command.get("path"):

            return (
                False,
                "VIEW benötigt path."
            )

    elif operation == "create":

        if not command.get("path"):

            return (
                False,
                "CREATE benötigt path."
            )

        kind = command.get("kind")

        if kind not in {
            "file",
            "directory"
        }:

            return (
                False,
                "CREATE benötigt kind=file oder kind=directory."
            )

        if kind == "file":

            if "content" not in command:

                return (
                    False,
                    "CREATE eines Files benötigt content."
                )

            if not isinstance(
                command["content"],
                str
            ):

                return (
                    False,
                    "content muss ein String sein."
                )

    elif operation == "edit":

        if not command.get("path"):

            return (
                False,
                "EDIT benötigt path."
            )

        if "content" not in command:

            return (
                False,
                "EDIT benötigt content."
            )

        if not isinstance(
            command["content"],
            str
        ):

            return (
                False,
                "content muss ein String sein."
            )

    elif operation == "delete":

        if not command.get("path"):

            return (
                False,
                "DELETE benötigt path."
            )

    elif operation == "execute":

        if not command.get("path"):

            return (
                False,
                "EXECUTE benötigt path."
            )

        if not str(
            command["path"]
        ).lower().endswith(".py"):

            return (
                False,
                "EXECUTE unterstützt nur Python-Dateien."
            )

    if not command.get("reason"):

        return (
            False,
            "Jede Entscheidung benötigt reason."
        )

    return (
        True,
        None
    )


# ============================================================
# AUSFÜHRUNG
# ============================================================

def execute_interface(command):

    operation = command["operation"]

    if operation == "view":

        return interface_view(
            command["path"]
        )

    if operation == "create":

        return interface_create(
            command["path"],
            command["kind"],
            command.get("content", "")
        )

    if operation == "edit":

        return interface_edit(
            command["path"],
            command["content"]
        )

    if operation == "delete":

        return interface_delete(
            command["path"]
        )

    if operation == "execute":

        return interface_execute(
            command["path"]
        )

    if operation == "none":

        return {
            "ok": True,
            "interface": "none"
        }

    return {
        "ok": False,
        "error": "Unbekannte Operation."
    }


# ============================================================
# COMMAND PARSEN
# ============================================================

def parse_command(content):

    try:

        return json.loads(
            content
        )

    except json.JSONDecodeError:

        start = content.find("{")
        end = content.rfind("}")

        if start != -1 and end != -1:

            try:

                return json.loads(
                    content[start:end + 1]
                )

            except json.JSONDecodeError:
                pass

        raise ValueError(
            "Die Antwort konnte nicht als JSON gelesen werden."
        )
