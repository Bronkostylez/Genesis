# GENESIS

GENESIS is a small experiment: give a local language model a folder, a few file operations, and no fixed task. Then watch what it does with them.

The model can write programs, run them, read the output, and try again. There is no score, unlock system, or predefined route through the experiment. The interesting part is whether useful structure comes out of those repeated decisions, or whether it just gets stuck repeating itself.

## What happens in a run

Starting GENESIS opens a simple Tkinter window. The host clears `genesis_instance` and puts a copy of the original host program inside it as `main.py`. Anything from the previous run is deleted.

Each turn, the model receives a file tree, the result of its last action, and a short action history. It answers with one JSON command:

- `view`: list a folder or read a file.
- `create`: make a file or folder.
- `edit`: replace a file's contents.
- `delete`: remove a file or folder.
- `execute`: run a Python file and get its output.
- `none`: take no action this turn.

The host checks the command, carries it out, and feeds the result back to the model. The window shows the decision, its short reason, the result, and the current file tree. The loop keeps going until you close the application.

The model uses Ollama locally. The default is `qwen2.5:7b`; the model name and API address are in `config.py`.

## Running it

You need Python with Tkinter, Ollama, and the model downloaded. There are no third-party Python packages to install.

```sh
ollama pull qwen2.5:7b
ollama serve
```

If Ollama is already running, you can skip `ollama serve`. In another terminal, from this repository:

```sh
python main.py
```

The included Visual Studio project also uses `main.py` as its start file.

## Code layout

The host is split by responsibility:

- `main.py`: starts the window and background thread.
- `config.py`: settings, paths, and limits.
- `instructions.py` and `schema.py`: the model's instructions and command format.
- `world.py` and `interfaces.py`: resetting the world, checking paths, and running file operations.
- `commands.py`: parsing, validation, and command dispatch.
- `state.py`: the file tree, history, and state sent to the model.
- `ollama_client.py`: requests to Ollama.
- `gui.py`: the window and log output.
- `runtime.py`: the development loop.

`templates/world_main.py.txt` keeps the original single-file program used to seed the model's world. The host uses the separate modules; the template keeps the starting world the same instead of leaving it with a launcher whose imports are missing.

See [REFACTOR.md](REFACTOR.md) for more on the split. Core tests run without Ollama or an open window:

```sh
python -m unittest discover -s tests -v
```

## Limits worth knowing

This is an experiment, not a secure sandbox. File operations reject paths outside the world folder, and executed Python files have a five-second timeout. But those Python files run with your user's permissions. They can access files, the network, or other resources outside that folder. A timeout and a working directory do not prevent that.

Run it in a disposable environment, not alongside files or credentials you care about. Don't put anything important in `genesis_instance`: the next start deletes it.

The model has no memory between runs. Within a run, its conversation and action history are limited. There is also no guarantee it will build anything useful. Repetition, broken programs, and dead ends are part of what this project is meant to expose.

