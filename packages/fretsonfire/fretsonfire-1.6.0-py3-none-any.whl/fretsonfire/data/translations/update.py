#!/usr/bin/env python3

import subprocess
from pathlib import Path

translations = {
  "fr":  "french",
  "ger": "german",
  "po":  "polish",
  "rus": "russian",
  "sw":  "swedish",
  "por": "brazilian_portuguese",
  "he":  "hebrew",
  "es":  "spanish",
  "it":  "italian",
  "gl":  "galician",
  "cz":  "czech",
  "fi":  "finnish",
  "hu":  "hungarian",
  "nl":  "dutch",
  "cs":  "czech",
  "tur": "turkish",
  "hr":  "croatian",
  "eo":  "esperanto",
  "ltz": "luxembourgish",
}

files = ["fretsonfire", "tutorial"]

translation_dir = Path(__file__).resolve().parent

for lang_id, lang_name in translations.items():
  print(f"{lang_name}:", end=" ")
  po_files = [translation_dir / f"{fn}_{lang_id}.po" for fn in files]
  try:
    msgcat = subprocess.run(
      ["msgcat", *map(str, po_files)],
      check=True,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
    )
    subprocess.run(
      ["msgfmt", "-", "-o", str(translation_dir / f"{lang_name}.mo")],
      input=msgcat.stdout,
      check=True,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
    )
  except FileNotFoundError as exc:
    print(f"error missing tool: {exc.filename}")
  except subprocess.CalledProcessError as exc:
    print(f"error {exc.returncode}")
  else:
    print("ok")
