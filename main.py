import tkinter as tk
from tkinter import scrolledtext
import json
import shutil
import subprocess
import sys
import threading
import urllib.request
import urllib.error
from pathlib import Path


# ============================================================
# KONFIGURATION
# ============================================================

MODEL = "qwen2.5:7b"
OLLAMA_URL = "http://localhost:11434/api/chat"

BASE_DIR = Path(__file__).resolve().parent
GENESIS_DIR = BASE_DIR / "genesis_instance"

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 760
CANVAS_HEIGHT = 360

MAX_VIEW_CHARS = 7000
MAX_FILES = 300
MAX_ACTION_HISTORY = 12

# Maximale Laufzeit eines von GENESIS ausgeführten Python-Programms
EXECUTION_TIMEOUT = 5

# Maximale Ausgabe eines ausgeführten Programms
MAX_EXECUTION_OUTPUT = 5000


# ============================================================
# GENESIS-INSTRUKTION
# ============================================================

GENESIS_INSTRUCTION = """
Du bist GENESIS.

Du befindest dich in einer eigenen Welt.

Deine Welt befindet sich vollständig im Ordner genesis_instance.

Zu Beginn enthält sie nur eine Datei: main.py.

Du hast fünf grundlegende Möglichkeiten:

VIEW
Du kannst sehen, was in deiner Welt existiert.

CREATE
Du kannst neue Dateien oder Verzeichnisse erschaffen.

EDIT
Du kannst existierende Dateien vollständig verändern.

DELETE
Du kannst Dateien oder Verzeichnisse entfernen.

EXECUTE
Du kannst ein von dir erschaffenes Python-Programm innerhalb deiner
Welt ausführen und seine Ausgabe beobachten.

Diese Möglichkeiten sind die grundlegenden Werkzeuge deiner Welt.

Deine Welt hat kein festgelegtes Endziel.

Es gibt aber eine wichtige Eigenschaft:

Deine Welt kann sich entwickeln.

Du kannst aus deinen vorhandenen Möglichkeiten neue Strukturen,
Programme, Werkzeuge, Regeln und Systeme erschaffen.

Du kannst vorhandene Dinge verbessern.

Du kannst neue Dinge auf Grundlage anderer Dinge erschaffen.

Du kannst deine eigenen Werkzeuge und Systeme weiterentwickeln.

Du kannst Programme schreiben, sie ausführen, ihre Ergebnisse
beobachten und sie anschließend weiterentwickeln.

Denke in Entwicklungsschritten.

Jeder Turn ist genau EIN Schritt.

------------------------------------------------------------
ENTWICKLUNG DURCH PROGRAMME
------------------------------------------------------------

EXECUTE ist besonders wichtig.

Du kannst beispielsweise:

1. eine Python-Datei CREATE erstellen,
2. sie mit EXECUTE ausführen,
3. die Ausgabe untersuchen,
4. anschließend die Datei EDITIEREN,
5. das Programm erneut ausführen.

So kannst du aus einfachen Dateien schrittweise komplexere Systeme
entwickeln.

EXECUTE funktioniert ausschließlich mit Python-Dateien innerhalb
deiner Welt.

Ein Programm erhält seine Arbeitsumgebung innerhalb von
genesis_instance.

Die maximale Laufzeit eines Programms beträgt wenige Sekunden.

Die Ausgabe des Programms wird dir nach der Ausführung zurückgegeben.

Du kannst EXECUTE auch verwenden, um zu überprüfen, ob ein von dir
entwickeltes Programm tatsächlich funktioniert.

Du musst nicht jedes Programm sofort perfekt erstellen.

Ausprobieren, Beobachten und anschließendes Verbessern ist ein
möglicher Entwicklungsweg.

main.py ist die Kopie des Host-Programms.

Du musst main.py nicht verändern und solltest sie nicht ohne einen
konkreten Grund ausführen.

------------------------------------------------------------
WICHTIG
------------------------------------------------------------

Berücksichtige immer die letzten ausgeführten Schritte.

Wiederhole keine identische erfolgreiche Aktion, wenn sie gegenüber
dem vorherigen Zustand keine neue Information liefert.

Wenn du eine Datei bereits vollständig untersucht hast, musst du sie
nicht erneut ansehen.

Wenn eine Aktion fehlgeschlagen ist, berücksichtige den Fehler bei
deinem nächsten Schritt und versuche nicht blind immer wieder
denselben fehlerhaften Befehl.

Wenn ein Programm bei EXECUTE einen Fehler produziert, kannst du den
Fehler als Information verwenden und das Programm anschließend
weiterentwickeln.

Du darfst VIEW verwenden, wenn du neue Informationen benötigst.

Du darfst CREATE verwenden, wenn du etwas Neues erschaffen möchtest.

Du darfst EDIT verwenden, wenn du eine bestehende Datei tatsächlich
weiterentwickeln möchtest.

Du darfst DELETE verwenden, wenn etwas nicht mehr benötigt wird.

Du darfst EXECUTE verwenden, um eigene Python-Programme zu testen
oder weiterzuentwickeln.

Du darfst auch "none" wählen, wenn du momentan keinen sinnvollen
Schritt ausführen möchtest.

Wichtig ist nicht, möglichst viele Aktionen auszuführen.

Wichtig ist, dass deine Aktionen aus dem aktuellen Zustand deiner Welt
und deinen bisherigen Erfahrungen entstehen.

------------------------------------------------------------
CREATE
------------------------------------------------------------

Wenn du eine DATEI erstellst:

- path ist Pflicht.
- kind muss "file" sein.
- content ist IMMER Pflicht.
- content enthält den vollständigen anfänglichen Inhalt der Datei.

Beispiel:

{"operation":"create","path":"notes.txt","kind":"file","content":"Meine erste Beobachtung.","reason":"Ich möchte eine dauerhafte Information speichern."}

Wenn du ein VERZEICHNIS erstellst:

- path ist Pflicht.
- kind muss "directory" sein.
- content wird NICHT benötigt.

Beispiel:

{"operation":"create","path":"tools","kind":"directory","reason":"Ich möchte einen Bereich für zukünftige Werkzeuge schaffen."}

------------------------------------------------------------
EDIT
------------------------------------------------------------

EDIT ersetzt den gesamten Inhalt einer Datei.

Wenn du EDIT verwendest, musst du deshalb den vollständigen neuen
Inhalt der Datei angeben.

EDIT ist nicht für kleine Teiländerungen gedacht.

Wenn du den bisherigen vollständigen Inhalt einer Datei nicht kennst,
solltest du sie zuerst mit VIEW untersuchen.

------------------------------------------------------------
DELETE
------------------------------------------------------------

DELETE entfernt das angegebene Objekt aus deiner Welt.

Verwende DELETE nur, wenn du tatsächlich entscheiden möchtest, dass
eine bestehende Struktur nicht mehr Teil deiner Welt sein soll.

------------------------------------------------------------
VIEW
------------------------------------------------------------

VIEW "." zeigt dir den Inhalt deiner Welt auf oberster Ebene.

VIEW auf eine Datei zeigt ihren Inhalt.

VIEW liefert Informationen, verändert aber nichts.

------------------------------------------------------------
EXECUTE
------------------------------------------------------------

EXECUTE benötigt:

- operation = "execute"
- path = Pfad zu einer Python-Datei
- reason = kurze Begründung

Beispiel:

{"operation":"execute","path":"program.py","reason":"Ich möchte überprüfen, ob mein neues Programm funktioniert."}

Nur Python-Dateien können ausgeführt werden.

------------------------------------------------------------
ENTWICKLUNG
------------------------------------------------------------

Es gibt keinen vorgeschriebenen Technologiebaum.

Es gibt keinen vorgeschriebenen nächsten Schritt.

Es gibt kein festgelegtes Ziel, das du erreichen musst.

Du kannst deine Welt selbst strukturieren.

Eine Entwicklung kann klein beginnen.

Zum Beispiel kann aus einer einfachen Datei später eine Struktur,
aus einer Struktur ein Programm und aus mehreren Programmen ein
größeres System entstehen.

Diese Beispiele sind keine Vorgabe.

Entscheide selbst, was aus deiner Welt entstehen soll.

------------------------------------------------------------
TECHNISCHE REGELN
------------------------------------------------------------

Jede Entscheidung muss vollständig ausführbar sein.

Der Pfad bezieht sich immer auf deine eigene Welt.

Antworte ausschließlich mit einem JSON-Objekt.

Kein Markdown.
Keine Erklärung außerhalb des JSON.

Deine Begründung soll kurz sein.

Sie soll nur erklären, welchen Zweck dein aktueller Schritt hat.
Sie soll keine vollständige innere Gedankenkette darstellen.
""".strip()


# ============================================================
# JSON-SCHEMA
# ============================================================

COMMAND_SCHEMA = {
    "oneOf": [

        # ----------------------------------------------------
        # VIEW
        # ----------------------------------------------------

        {
            "type": "object",
            "properties": {
                "operation": {
                    "const": "view"
                },
                "path": {
                    "type": "string",
                    "minLength": 1
                },
                "reason": {
                    "type": "string"
                }
            },
            "required": [
                "operation",
                "path",
                "reason"
            ],
            "additionalProperties": False
        },

        # ----------------------------------------------------
        # CREATE FILE
        # ----------------------------------------------------

        {
            "type": "object",
            "properties": {
                "operation": {
                    "const": "create"
                },
                "path": {
                    "type": "string",
                    "minLength": 1
                },
                "kind": {
                    "const": "file"
                },
                "content": {
                    "type": "string"
                },
                "reason": {
                    "type": "string"
                }
            },
            "required": [
                "operation",
                "path",
                "kind",
                "content",
                "reason"
            ],
            "additionalProperties": False
        },

        # ----------------------------------------------------
        # CREATE DIRECTORY
        # ----------------------------------------------------

        {
            "type": "object",
            "properties": {
                "operation": {
                    "const": "create"
                },
                "path": {
                    "type": "string",
                    "minLength": 1
                },
                "kind": {
                    "const": "directory"
                },
                "reason": {
                    "type": "string"
                }
            },
            "required": [
                "operation",
                "path",
                "kind",
                "reason"
            ],
            "additionalProperties": False
        },

        # ----------------------------------------------------
        # EDIT
        # ----------------------------------------------------

        {
            "type": "object",
            "properties": {
                "operation": {
                    "const": "edit"
                },
                "path": {
                    "type": "string",
                    "minLength": 1
                },
                "content": {
                    "type": "string"
                },
                "reason": {
                    "type": "string"
                }
            },
            "required": [
                "operation",
                "path",
                "content",
                "reason"
            ],
            "additionalProperties": False
        },

        # ----------------------------------------------------
        # DELETE
        # ----------------------------------------------------

        {
            "type": "object",
            "properties": {
                "operation": {
                    "const": "delete"
                },
                "path": {
                    "type": "string",
                    "minLength": 1
                },
                "reason": {
                    "type": "string"
                }
            },
            "required": [
                "operation",
                "path",
                "reason"
            ],
            "additionalProperties": False
        },

        # ----------------------------------------------------
        # EXECUTE
        # ----------------------------------------------------

        {
            "type": "object",
            "properties": {
                "operation": {
                    "const": "execute"
                },
                "path": {
                    "type": "string",
                    "minLength": 1
                },
                "reason": {
                    "type": "string"
                }
            },
            "required": [
                "operation",
                "path",
                "reason"
            ],
            "additionalProperties": False
        },

        # ----------------------------------------------------
        # NONE
        # ----------------------------------------------------

        {
            "type": "object",
            "properties": {
                "operation": {
                    "const": "none"
                },
                "reason": {
                    "type": "string"
                }
            },
            "required": [
                "operation",
                "reason"
            ],
            "additionalProperties": False
        }
    ]
}


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

    source_main = BASE_DIR / "main.py"
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


# ============================================================
# VIEW
# ============================================================

def interface_view(path):

    try:

        target = safe_path(path)

        if not target.exists():

            return {
                "ok": False,
                "interface": "view",
                "path": path,
                "error": "Objekt existiert nicht."
            }

        if target.is_dir():

            children = []

            for child in sorted(
                target.iterdir(),
                key=lambda p: p.name.lower()
            ):

                children.append({
                    "name": child.name,
                    "type": (
                        "directory"
                        if child.is_dir()
                        else "file"
                    )
                })

            return {
                "ok": True,
                "interface": "view",
                "path": path,
                "type": "directory",
                "children": children
            }

        content = target.read_text(
            encoding="utf-8",
            errors="replace"
        )

        if len(content) > MAX_VIEW_CHARS:

            content = (
                content[:MAX_VIEW_CHARS]
                + "\n...[abgeschnitten]..."
            )

        return {
            "ok": True,
            "interface": "view",
            "path": path,
            "type": "file",
            "content": content
        }

    except Exception as e:

        return {
            "ok": False,
            "interface": "view",
            "path": path,
            "error": str(e)
        }


# ============================================================
# CREATE
# ============================================================

def interface_create(
    path,
    kind="file",
    content=""
):

    try:

        if not path:

            return {
                "ok": False,
                "interface": "create",
                "error": "Kein Pfad angegeben."
            }

        target = safe_path(path)

        if target.exists():

            return {
                "ok": False,
                "interface": "create",
                "path": path,
                "error": "Objekt existiert bereits."
            }

        if kind == "directory":

            target.mkdir(
                parents=True
            )

        elif kind == "file":

            target.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            target.write_text(
                content,
                encoding="utf-8"
            )

        else:

            return {
                "ok": False,
                "interface": "create",
                "path": path,
                "error": "Ungültiger Typ."
            }

        return {
            "ok": True,
            "interface": "create",
            "path": path,
            "kind": kind
        }

    except Exception as e:

        return {
            "ok": False,
            "interface": "create",
            "path": path,
            "error": str(e)
        }


# ============================================================
# EDIT
# ============================================================

def interface_edit(
    path,
    content
):

    try:

        if not path:

            return {
                "ok": False,
                "interface": "edit",
                "error": "Kein Pfad angegeben."
            }

        target = safe_path(path)

        if not target.exists():

            return {
                "ok": False,
                "interface": "edit",
                "path": path,
                "error": "Objekt existiert nicht."
            }

        if target.is_dir():

            return {
                "ok": False,
                "interface": "edit",
                "path": path,
                "error": "Ein Verzeichnis kann nicht editiert werden."
            }

        target.write_text(
            content,
            encoding="utf-8"
        )

        return {
            "ok": True,
            "interface": "edit",
            "path": path
        }

    except Exception as e:

        return {
            "ok": False,
            "interface": "edit",
            "path": path,
            "error": str(e)
        }


# ============================================================
# DELETE
# ============================================================

def interface_delete(path):

    try:

        target = safe_path(path)

        if not target.exists():

            return {
                "ok": False,
                "interface": "delete",
                "path": path,
                "error": "Objekt existiert nicht."
            }

        if target == GENESIS_DIR:

            return {
                "ok": False,
                "interface": "delete",
                "path": path,
                "error": "Die Wurzel der Welt kann nicht gelöscht werden."
            }

        if target.is_dir():

            shutil.rmtree(target)

        else:

            target.unlink()

        return {
            "ok": True,
            "interface": "delete",
            "path": path
        }

    except Exception as e:

        return {
            "ok": False,
            "interface": "delete",
            "path": path,
            "error": str(e)
        }


# ============================================================
# EXECUTE
# ============================================================

def interface_execute(path):

    try:

        if not path:

            return {
                "ok": False,
                "interface": "execute",
                "error": "Kein Pfad angegeben."
            }

        target = safe_path(path)

        if not target.exists():

            return {
                "ok": False,
                "interface": "execute",
                "path": path,
                "error": "Datei existiert nicht."
            }

        if not target.is_file():

            return {
                "ok": False,
                "interface": "execute",
                "path": path,
                "error": "Nur Dateien können ausgeführt werden."
            }

        if target.suffix.lower() != ".py":

            return {
                "ok": False,
                "interface": "execute",
                "path": path,
                "error": "EXECUTE unterstützt momentan nur Python-Dateien."
            }

        # ----------------------------------------------------
        # Das Programm läuft ausschließlich innerhalb der
        # Genesis-Welt.
        #
        # Es wird KEINE Shell verwendet.
        # ----------------------------------------------------

        process = subprocess.run(
            [
                sys.executable,
                str(target)
            ],
            cwd=str(GENESIS_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=EXECUTION_TIMEOUT,
            shell=False
        )

        stdout = process.stdout or ""
        stderr = process.stderr or ""

        if len(stdout) > MAX_EXECUTION_OUTPUT:

            stdout = (
                stdout[:MAX_EXECUTION_OUTPUT]
                + "\n...[stdout abgeschnitten]..."
            )

        if len(stderr) > MAX_EXECUTION_OUTPUT:

            stderr = (
                stderr[:MAX_EXECUTION_OUTPUT]
                + "\n...[stderr abgeschnitten]..."
            )

        return {
            "ok": process.returncode == 0,
            "interface": "execute",
            "path": path,
            "return_code": process.returncode,
            "stdout": stdout,
            "stderr": stderr
        }

    except subprocess.TimeoutExpired as e:

        stdout = e.stdout or ""
        stderr = e.stderr or ""

        if isinstance(stdout, bytes):
            stdout = stdout.decode(
                "utf-8",
                errors="replace"
            )

        if isinstance(stderr, bytes):
            stderr = stderr.decode(
                "utf-8",
                errors="replace"
            )

        return {
            "ok": False,
            "interface": "execute",
            "path": path,
            "error": (
                f"Programm wurde nach {EXECUTION_TIMEOUT} "
                "Sekunden beendet."
            ),
            "stdout": stdout,
            "stderr": stderr
        }

    except Exception as e:

        return {
            "ok": False,
            "interface": "execute",
            "path": path,
            "error": str(e)
        }


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


# ============================================================
# OLLAMA
# ============================================================

def ask_genesis(messages):

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "format": COMMAND_SCHEMA,
        "options": {
            "temperature": 0.8
        }
    }

    data = json.dumps(
        payload,
        ensure_ascii=False
    ).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={
            "Content-Type": "application/json"
        }
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=120
        ) as response:

            raw = response.read().decode(
                "utf-8"
            )

    except urllib.error.URLError as e:

        raise RuntimeError(
            f"Ollama nicht erreichbar: {e}"
        )

    except Exception as e:

        raise RuntimeError(
            f"Fehler bei Ollama: {e}"
        )

    try:

        response_data = json.loads(
            raw
        )

    except json.JSONDecodeError:

        raise RuntimeError(
            "Ollama lieferte kein gültiges JSON."
        )

    message = response_data.get(
        "message",
        {}
    )

    content = message.get(
        "content",
        ""
    )

    if not content:

        raise RuntimeError(
            "Ollama lieferte keine Entscheidung."
        )

    return content


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


# ============================================================
# START
# ============================================================

thread = threading.Thread(
    target=genesis_loop,
    daemon=True
)

thread.start()

root.mainloop()