from distutils import log
from pathlib import Path
from typing import Iterable, Sequence

import polib
from setuptools.command.build_py import build_py as _build_py
from setuptools.command.sdist import sdist as _sdist

_TRANSLATION_CODES = {
    "fr": "french",
    "ger": "german",
    "po": "polish",
    "rus": "russian",
    "sw": "swedish",
    "por": "brazilian_portuguese",
    "he": "hebrew",
    "es": "spanish",
    "it": "italian",
    "gl": "galician",
    "cz": "czech",
    "fi": "finnish",
    "hu": "hungarian",
    "nl": "dutch",
    "cs": "czech",
    "tur": "turkish",
    "hr": "croatian",
    "eo": "esperanto",
    "ltz": "luxembourgish",
}

_PO_PREFIXES: Sequence[str] = ("fretsonfire", "tutorial")



def _merge_catalogs(po_files: Iterable[Path]) -> polib.POFile | None:
    iterator = iter(po_files)
    try:
        first = next(iterator)
    except StopIteration:
        return None

    merged = polib.pofile(str(first))

    for po_path in iterator:
        catalog = polib.pofile(str(po_path))
        for entry in catalog:
            if entry.obsolete:
                continue
            if entry.msgid == "":  # header, merge metadata only
                merged.metadata.update({k: v for k, v in catalog.metadata.items() if v})
                continue

            existing = merged.find(entry.msgid, msgctxt=entry.msgctxt)
            if existing is None:
                cloned = polib.POEntry(
                    msgid=entry.msgid,
                    msgstr=entry.msgstr,
                    msgctxt=getattr(entry, "msgctxt", None),
                    msgid_plural=getattr(entry, "msgid_plural", None),
                )
                cloned.occurrences = list(getattr(entry, "occurrences", []) or [])
                cloned.flags = list(getattr(entry, "flags", []) or [])
                cloned.msgstr_plural = dict(getattr(entry, "msgstr_plural", {}) or {})
                cloned.comment = getattr(entry, "comment", "") or ""
                cloned.tcomment = getattr(entry, "tcomment", "") or ""
                cloned.previous_msgid = getattr(entry, "previous_msgid", None)
                cloned.previous_msgctxt = getattr(entry, "previous_msgctxt", None)
                cloned.previous_msgid_plural = getattr(entry, "previous_msgid_plural", None)
                cloned.encoding = getattr(entry, "encoding", None)
                cloned.obsolete = bool(getattr(entry, "obsolete", False))
                merged.append(cloned)
                continue

            if entry.msgstr:
                existing.msgstr = entry.msgstr
            if entry.msgid_plural:
                for idx, value in entry.msgstr_plural.items():
                    if value:
                        existing.msgstr_plural[idx] = value
                    elif idx not in existing.msgstr_plural:
                        existing.msgstr_plural[idx] = ""
            if entry.occurrences:
                seen = set(existing.occurrences)
                for occurrence in entry.occurrences:
                    if occurrence not in seen:
                        existing.occurrences.append(occurrence)
                        seen.add(occurrence)
            if entry.flags:
                existing_flags = set(existing.flags or [])
                existing.flags = sorted(existing_flags.union(entry.flags))
            entry_comment = entry.comment or ""
            if entry_comment:
                existing_comment = existing.comment or ""
                comments = [c for c in existing_comment.splitlines() if c]
                comments.extend(c for c in entry_comment.splitlines() if c)
                seen_comments: list[str] = []
                for comment in comments:
                    if comment not in seen_comments:
                        seen_comments.append(comment)
                existing.comment = "\n".join(seen_comments)
            entry_tcomment = entry.tcomment or ""
            if entry_tcomment:
                existing_tcomment = existing.tcomment or ""
                comments = [c for c in existing_tcomment.splitlines() if c]
                comments.extend(c for c in entry_tcomment.splitlines() if c)
                seen_comments = []
                for comment in comments:
                    if comment not in seen_comments:
                        seen_comments.append(comment)
                existing.tcomment = "\n".join(seen_comments)

    return merged


def compile_translations(project_root: Path, *, quiet: bool = False) -> list[Path]:
    """Compile gettext catalogs, returning the paths of generated files."""
    translations_dir = project_root / "src" / "fretsonfire" / "data" / "translations"
    if not translations_dir.exists():
        legacy_dir = project_root / "data" / "translations"
        if legacy_dir.exists():
            translations_dir = legacy_dir
        else:
            log.info("Translations directory %s not found; skipping catalog compilation.", translations_dir)
            return []

    generated: list[Path] = []

    for code, output_name in _TRANSLATION_CODES.items():
        po_candidates = [translations_dir / f"{prefix}_{code}.po" for prefix in _PO_PREFIXES]
        po_files = []
        for path in po_candidates:
            if path.is_file():
                po_files.append(path)
                continue
            fallback = project_root / path.name
            if fallback.is_file():
                po_files.append(fallback)
        
        if not po_files:
            continue

        catalog = _merge_catalogs(po_files)
        if catalog is None:
            continue

        mo_path = translations_dir / f"{output_name}.mo"
        mo_path.parent.mkdir(parents=True, exist_ok=True)
        catalog.save_as_mofile(str(mo_path))
        generated.append(mo_path)
        if not quiet:
            log.info("Compiled %s", mo_path.relative_to(project_root))

    return generated


class BuildPyWithTranslations(_build_py):
    """Custom build_py command that compiles translation catalogs."""

    def run(self) -> None:  # type: ignore[override]
        project_root = Path.cwd()
        compile_translations(project_root, quiet=self.verbose < 1)
        super().run()


class SDistWithTranslations(_sdist):
    """Ensure translations are compiled prior to creating an sdist."""

    def run(self) -> None:  # type: ignore[override]
        project_root = Path.cwd()
        compile_translations(project_root, quiet=self.verbose < 1)
        super().run()
