# Dateiaufteilung

Start wie bisher mit `python main.py` oder über das vorhandene Visual-Studio-Projekt.
Python mit Tkinter, ein laufendes Ollama und `qwen2.5:7b` werden weiterhin benötigt.

| Datei | Aufgabe |
| --- | --- |
| `main.py` | Startet Oberfläche und Hintergrund-Thread. |
| `config.py` | Modell, URL, Pfade, Fenstergröße und Limits. |
| `instructions.py` | Bisherige Anweisung an das Modell. |
| `schema.py` | Bisheriges JSON-Schema für Modellantworten. |
| `world.py` | Welt zurücksetzen und sichere Pfade prüfen. |
| `interfaces.py` | Dateien ansehen, erstellen, bearbeiten, löschen und Python ausführen. |
| `commands.py` | Antworten parsen, Befehle prüfen und Operationen auswählen. |
| `state.py` | Weltbaum, Aktionshistorie und Zusammenfassung fürs Modell. |
| `ollama_client.py` | Kommunikation mit Ollama. |
| `gui.py` | Unveränderte Tkinter-Oberfläche und Log-/Status-Ausgabe. |
| `runtime.py` | Die bisherige GENESIS-Schleife. |
| `templates/world_main.py.txt` | Unveränderte bisherige Startdatei für die simulierte Welt. |

## Warum gibt es noch die große Vorlage?

GENESIS kopiert beim Zurücksetzen bisher den gesamten eigenen Code als einzige
`main.py` in `genesis_instance`. Würde dort nur der neue kleine Startpunkt landen,
wären die importierten Module nicht vorhanden und die sichtbare Welt wäre anders.
Die Vorlage erhält deshalb den bisherigen Inhalt dieser Welt-Datei exakt.
Der Host selbst verwendet die getrennten Module. Die Vorlage ist nur eine Ressource,
kein zweiter Host-Startpunkt.

`Projekt Genesis.pyproj` enthält die neuen Module und die Vorlage; `main.py`
bleibt seine Startdatei. Modell-Anweisung, Schema, Limits, Oberflächenaufbau und
Entwicklungsschleife wurden nicht umgeschrieben. Das Importieren von `main` startet
jetzt nicht mehr automatisch die Anwendung; das normale Starten tut es weiterhin.

Tests: `python -m unittest discover -s tests -v`.
Die Tests benötigen kein laufendes Ollama und kein geöffnetes Fenster.

