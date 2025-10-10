# Frets on Fire Installation Guide

This document describes how to install and run the modern Python 3 build of
Frets on Fire. For detailed contributor workflows and platform-specific
packaging notes, see `doc/BUILDING.md`.

## Prerequisites

* Python 3.13 (match the version declared in `pyproject.toml`)
* A C/C++ build toolchain for your platform
* SDL2, OpenGL, and audio development libraries supplied by your operating
  system

Typical system packages:

* Debian / Ubuntu:
  `sudo apt install python3-venv python3-dev libsdl2-dev libsdl2-mixer-dev libsdl2-ttf-dev libogg-dev`
* Fedora:
  `sudo dnf install python3-devel SDL2-devel SDL2_mixer-devel SDL2_ttf-devel libogg-devel`
* macOS (Homebrew):
  `brew install python sdl2 sdl2_mixer sdl2_ttf`
* Windows:
  Install Python from python.org (add it to PATH) and the "Desktop development
  with C++" workload from Visual Studio Build Tools.

Python dependencies—`pygame`, `PyOpenGL`, `numpy`, `Pillow`, and
`pyasyncore`—are resolved automatically when you install the project with
`pip`.

## Install from PyPI

1. Upgrade pip:

       python3 -m pip install --upgrade pip
2. Install the published package:

       python3 -m pip install fretsonfire
3. Launch the game:

       python3 -m fretsonfire

   or run the console script `fretsonfire` that pip installs.

## Run from Source

1. Clone the repository:

       git clone https://github.com/sildur/fretsonfire.git
       cd fretsonfire
2. Create a virtual environment:

       python3 -m venv .venv
       source .venv/bin/activate    # Windows: .venv\Scripts\activate
3. Install dependencies in editable mode:

       python -m pip install --upgrade pip
       python -m pip install -e .
4. Start the game:

       python -m fretsonfire

   You can still run the legacy entry point if needed:

       python -m fretsonfire.FretsOnFire

## Run the Test Suite

Install the optional test tools:

    python -m pip install -e .[tests]

Execute the tests with SDL's dummy drivers so no real window or audio device is
required:

```
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m pytest
```

## Update Translations

Translation catalogs (`*.mo`) are compiled automatically when you build the
package (`python -m build`). To force a rebuild without creating new
artifacts:

```
python -m pip install polib
python -m fretsonfire._build compile_translations
```

The generated files live under `src/fretsonfire/data/translations/`.

## Build Distributions

To produce source and wheel archives for PyPI:

```
python -m pip install --upgrade pip build
python -m build
```

Artifacts appear in the `dist/` directory.

For platform-native bundles (Debian/RPM packages, macOS DMG, Windows EXE) use
[Briefcase](https://briefcase.readthedocs.io/):

```
python -m pip install briefcase
make build
```

The Makefile dispatches to `python -m build` and the appropriate Briefcase
targets for your host OS. Refer to `doc/BUILDING.md` for additional options and
troubleshooting.

## Additional Resources

* `README.md` – gameplay overview and troubleshooting tips
* `doc/BUILDING.md` – full contributor setup, linting, testing, and packaging
  guide

If you encounter missing dependencies or build failures, recheck the
prerequisite packages above and rerun the installation steps.
