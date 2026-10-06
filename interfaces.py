"""VIEW, CREATE, EDIT, DELETE und EXECUTE für die GENESIS-Welt."""

import shutil
import subprocess
import sys

from config import (GENESIS_DIR, MAX_VIEW_CHARS, EXECUTION_TIMEOUT, MAX_EXECUTION_OUTPUT)
from world import safe_path

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

