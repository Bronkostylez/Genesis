"""Anfragen an die lokale Ollama-API."""

import json
import urllib.request
import urllib.error

from config import MODEL, OLLAMA_URL
from schema import COMMAND_SCHEMA

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

