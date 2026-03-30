"""Terminology memory utilities for maintaining glossary consistency."""

import re
from pathlib import Path

TERMINOLOGY_PATH = Path(__file__).parent.parent / "memory" / "terminology.md"

# Matches lines of the form: | Spanish term | English term | ... |
_TABLE_ROW_RE = re.compile(
    r"^\|\s*(?P<source>[^|]+?)\s*\|\s*(?P<target>[^|]+?)\s*\|"
)


def load_terminology() -> dict[str, str]:
    """Load the terminology glossary from the memory file.

    Returns:
        A mapping of source (Spanish) terms to their established English
        translations.  Returns an empty dict if the file does not exist or
        contains no table rows.
    """
    if not TERMINOLOGY_PATH.exists():
        return {}

    glossary: dict[str, str] = {}
    for line in TERMINOLOGY_PATH.read_text(encoding="utf-8").splitlines():
        match = _TABLE_ROW_RE.match(line)
        if match:
            source = match.group("source").strip()
            target = match.group("target").strip()
            # Skip header/separator rows
            if source.lower() in ("spanish", "---", "term", "") or target.startswith("-"):
                continue
            glossary[source] = target
    return glossary


def update_terminology(source_text: str, translated_text: str) -> None:
    """Detect potential new terms and append them to the glossary.

    The function performs a lightweight heuristic scan: it looks for
    parenthetical glosses of the form ``término (term)`` in the translated
    text, where the word inside the parentheses is English and the preceding
    word is the Spanish original.  Any pair that is not already present in the
    glossary is appended as a new table row.

    Args:
        source_text: Original Spanish text.
        translated_text: Translated English text.
    """
    existing = load_terminology()

    # Heuristic: capture patterns like "word (Word)" that suggest a bilingual
    # gloss introduced by the translator.
    pattern = re.compile(r"(\b[A-Za-zÀ-ÿ]+\b)\s+\(([A-Za-z][A-Za-z\s\-]+?)\)")
    new_terms: dict[str, str] = {}
    for match in pattern.finditer(translated_text):
        spanish_candidate = match.group(1)
        english_candidate = match.group(2).strip()
        if spanish_candidate not in existing and spanish_candidate not in new_terms:
            new_terms[spanish_candidate] = english_candidate

    if not new_terms:
        return

    current_content = (
        TERMINOLOGY_PATH.read_text(encoding="utf-8")
        if TERMINOLOGY_PATH.exists()
        else ""
    )
    rows = "\n".join(
        f"| {src} | {tgt} | Auto-detected |"
        for src, tgt in new_terms.items()
    )
    updated_content = current_content.rstrip("\n") + "\n" + rows + "\n"
    TERMINOLOGY_PATH.write_text(updated_content, encoding="utf-8")
